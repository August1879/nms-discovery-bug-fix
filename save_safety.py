"""Shared, lossless JSON I/O and discovery cleanup for exported saves."""

import datetime
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path


def load_json(path):
    original = Path(path).read_bytes()
    if not original:
        raise ValueError("The selected JSON file is empty.")
    
    # Sanitize invalid raw backslashes left by in-game custom names
    # Added negative lookbehind (?<!\\) to prevent altering valid double-backslash file paths
    decoded_text = original.decode("utf-8-sig")
    decoded_text = re.sub(r'(?<!\\)\\(?![nrtbf"\\/u])', r'\\\\', decoded_text)

    def reject_constant(value):
        raise ValueError(f"Invalid JSON constant: {value}")

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"Non-finite JSON number: {value}")
        return number

    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    data = json.loads(decoded_text, parse_constant=reject_constant,
                      parse_float=finite_float, object_pairs_hook=unique_keys)
    if not isinstance(data, dict):
        raise ValueError("The exported JSON must contain an object at the root.")
    return data, original


def discovery_records(data, cache_only=False):
    try:
        cache = data if cache_only else data["DiscoveryManagerData"]
        records = cache["DiscoveryData-v1"]["Store"]["Record"]
    except (KeyError, TypeError) as exc:
        raise ValueError("The export has no discovery record list.") from exc
    if not isinstance(records, list):
        raise ValueError("The discovery record list has an unexpected format.")
    return records


def require_owner(records, username):
    if not username or not any(
        isinstance(record, dict)
        and isinstance(record.get("OWS"), dict)
        and isinstance(record["OWS"].get("USN"), str)
        and record["OWS"]["USN"].casefold() == username.casefold()
        for record in records
    ):
        raise ValueError("No discovery records match that username. Check spelling and old usernames before deleting anything.")


def optimize_data(data, username, whitelist, options, update_reserves=True):
    """Change an in-memory save and return exact removed records and added wonders."""
    records = discovery_records(data)
    require_owner(records, username)
    cache = data["DiscoveryManagerData"]["DiscoveryData-v1"]
    player = data.get("BaseContext", {}).get("PlayerStateData")
    if options["paradise"]:
        if not isinstance(player, dict):
            raise ValueError("The export has no PlayerStateData for Paradise records.")
        wonders = player.get("WonderPlanetRecords", [])
        if not isinstance(wonders, list):
            raise ValueError("WonderPlanetRecords has an unexpected format.")
    else:
        wonders = []

    existing_ids = set()
    for wonder in wonders:
        if not isinstance(wonder, dict):
            raise ValueError("WonderPlanetRecords has an unexpected format.")
        generation_id = wonder.get("GenerationID", [])
        if isinstance(generation_id, list) and len(generation_id) == 2:
            existing_ids.add(tuple(map(str, generation_id)))

    kept, removed, added = [], [], []
    protected = 0
    names = {name.casefold() for name in whitelist}
    owner_name = username.casefold()
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not all(isinstance(record.get(key), dict) for key in ("DD", "OWS")):
            raise ValueError(f"Discovery record {index} has an unexpected format.")
        detail = record["DD"]
        record_owner = record["OWS"].get("USN", "")
        record_name = detail.get("N", "")
        if not isinstance(record_owner, str) or not isinstance(record_name, str):
            raise ValueError(f"Discovery record {index} has an unexpected name or owner.")
        record_type = detail.get("DT", "")
        mine = record_owner.casefold() == owner_name
        foreign = bool(record_owner) and not mine

        if options["paradise"] and mine and record_type == "Planet":
            address, values = detail.get("UA"), detail.get("VP", [])
            if address and isinstance(values, list) and values:
                generation_id = (str(address), str(values[0]))
                if generation_id not in existing_ids:
                    added.append({"GenerationID": list(generation_id), "WonderStatValue": 0.0, "SeenInFrontend": False})
                    existing_ids.add(generation_id)

        flags = record.get("FL", {})
        if not isinstance(flags, dict):
            raise ValueError(f"Discovery record {index} has unexpected flags.")
        hidden_system = record_type == "SolarSystem" and flags.get("F") == 1
        should_remove = (
            (options["hidden"] and hidden_system)
            or (foreign and (options["all"] or (
                options["fauna"] and record_type == "Animal"
                or options["flora"] and record_type == "Flora"
                or options["mineral"] and record_type == "Mineral"
            )))
        )
        whitelisted = record_owner.casefold() in names or record_name.casefold() in names
        if should_remove and whitelisted:
            protected += 1
            kept.append(record)
        elif should_remove:
            removed.append((index, record_type, record_name, record_owner))
        else:
            kept.append(record)

    if removed:
        cache["Store"]["Record"] = kept
        if update_reserves:
            cache["ReserveStore"] = len(kept)
            cache["ReserveManaged"] = len(kept)
    if added:
        player["WonderPlanetRecords"] = wonders + added
    return removed, added, protected


def write_output(source, data, original, output_name):
    """Save a byte-for-byte backup and refuse to replace any existing output."""
    source = Path(source)
    output = source.with_name(output_name)
    if os.path.lexists(output):
        raise FileExistsError(f"{output} already exists. Move or rename it before running again.")

    staged_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=source.parent,
                                         prefix=".optimized_", suffix=".tmp", delete=False) as staged:
            staged_path = Path(staged.name)
            json.dump(data, staged, separators=(",", ":"), allow_nan=False)
            staged.flush()
            os.fsync(staged.fileno())

        expected_digest = hashlib.sha256(original).digest()

        def check_source():
            with open(source, "rb") as current:
                if hashlib.file_digest(current, "sha256").digest() != expected_digest:
                    raise ValueError("The selected export changed during review. Reload it and review the changes again.")

        check_source()

        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup = source.with_name(f"{source.stem}_backup_{stamp}{source.suffix}")
        backup_created = False
        output_published = False
        staged_stat = staged_path.stat()
        try:
            with open(backup, "xb") as backup_file:
                backup_created = True
                backup_file.write(original)
            check_source()  # Also catch changes while the backup was written.
            if os.name == "nt":
                os.rename(staged_path, output)  # Windows refuses an existing destination.
            else:
                os.link(staged_path, output)  # Exclusive publication on POSIX.
            output_published = True
            check_source()  # Catch a change during publication.
        except BaseException:
            try:
                if output_published:
                    try:
                        output_stat = output.stat(follow_symlinks=False)
                    except FileNotFoundError:
                        pass
                    else:
                        if os.path.samestat(staged_stat, output_stat):
                            output.unlink()
            finally:
                if backup_created:
                    backup.unlink(missing_ok=True)
            raise
        return backup, output
    finally:
        if staged_path is not None:
            staged_path.unlink(missing_ok=True)
