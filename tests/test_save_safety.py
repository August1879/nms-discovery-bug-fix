import json
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from save_safety import load_json, optimize_data, write_output


ROOT = Path(__file__).resolve().parents[1]


def record(kind, name, owner, hidden=False, **detail):
    return {"DD": {"DT": kind, "N": name, **detail}, "OWS": {"USN": owner}, "FL": {"F": int(hidden)}}


def save(records):
    return {"DiscoveryManagerData": {"DiscoveryData-v1": {
        "Store": {"Record": records}, "ReserveStore": len(records), "ReserveManaged": len(records)
    }}, "BaseContext": {"PlayerStateData": {"WonderPlanetRecords": []}},
            "Other": {"unicode": "Café", "slash": "a\\b", "newline": "a\nb"}}


class SaveSafetyTests(unittest.TestCase):
    def test_original_escapes_and_bom_survive_backup_and_output(self):
        records = [record("SolarSystem", "Mine", "Player"), record("Animal", "Other", "Else")]
        raw = b"\xef\xbb\xbf" + json.dumps(save(records), ensure_ascii=True).encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            source.write_bytes(raw)
            data, original = load_json(source)
            options = dict(hidden=False, fauna=True, flora=False, mineral=False, all=False, paradise=False)
            removed, added, _ = optimize_data(data, "player", set(), options)
            self.assertEqual([(1, "Animal", "Other", "Else")], removed)
            self.assertEqual([], added)
            backup, output = write_output(source, data, original, "optimized_save.json")
            self.assertEqual(raw, source.read_bytes())
            self.assertEqual(raw, backup.read_bytes())
            self.assertEqual(json.loads(raw.decode("utf-8-sig"))["Other"], json.loads(output.read_text())["Other"])
            self.assertEqual(1, data["DiscoveryManagerData"]["DiscoveryData-v1"]["ReserveStore"])

    def test_invalid_encoding_and_json_fail_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            for raw, error in ((b'{"x":"\xff"}', UnicodeDecodeError),
                               (b'{"x":', json.JSONDecodeError), (b'{"x":NaN}', ValueError),
                               (b'{"x":1e400}', ValueError), (b'{"x":1,"x":2}', ValueError)):
                source.write_bytes(raw)
                with self.assertRaises(error):
                    load_json(source)
            self.assertEqual([source.name], [path.name for path in Path(directory).iterdir()])

    def test_owner_validation_hidden_scope_and_direct_whitelist(self):
        records = [record("SolarSystem", "Home", "Player", True),
                   record("Animal", "Own animal", "Player", True),
                   record("Animal", "Foreign animal", "Else"),
                   record("Planet", "Child", "Else")]
        options = dict(hidden=False, fauna=True, flora=False, mineral=False, all=False, paradise=False)
        data = save(records)
        with self.assertRaisesRegex(ValueError, "No discovery records match"):
            optimize_data(data, "typo", set(), options)
        self.assertEqual(4, len(data["DiscoveryManagerData"]["DiscoveryData-v1"]["Store"]["Record"]))

        options["hidden"] = True
        removed, _, protected = optimize_data(data, "PLAYER", {"foreign animal"}, options)
        self.assertEqual([(0, "SolarSystem", "Home", "Player")], removed)
        self.assertEqual(1, protected)
        self.assertEqual([records[1], records[2], records[3]], data["DiscoveryManagerData"]["DiscoveryData-v1"]["Store"]["Record"])

    def test_missing_paradise_destination_is_an_error(self):
        data = save([record("Planet", "Mine", "Player", UA="addr", VP=[1])])
        del data["BaseContext"]
        options = dict(hidden=False, fauna=False, flora=False, mineral=False, all=False, paradise=True)
        with self.assertRaisesRegex(ValueError, "PlayerStateData"):
            optimize_data(data, "Player", set(), options)

    def test_paradise_adds_once_and_preserves_existing_wonders(self):
        data = save([record("Planet", "Mine", "Player", UA="addr", VP=[1])])
        existing = {"GenerationID": ["old", "2"], "SeenInFrontend": True}
        wonders = data["BaseContext"]["PlayerStateData"]["WonderPlanetRecords"]
        wonders.append(existing)
        options = dict(hidden=False, fauna=False, flora=False, mineral=False, all=False, paradise=True)

        removed, added, _ = optimize_data(data, "Player", set(), options)
        self.assertEqual([], removed)
        self.assertEqual([["addr", "1"]], [wonder["GenerationID"] for wonder in added])
        self.assertEqual([existing, *added], data["BaseContext"]["PlayerStateData"]["WonderPlanetRecords"])

        _, added_again, _ = optimize_data(data, "Player", set(), options)
        self.assertEqual([], added_again)
        self.assertEqual([existing, *added], data["BaseContext"]["PlayerStateData"]["WonderPlanetRecords"])

    def test_existing_output_and_symlink_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            source.write_text("{}")
            target = Path(directory) / "important.txt"
            target.write_text("keep")
            output = Path(directory) / "optimized_save.json"
            try:
                output.symlink_to(target)
            except OSError:
                pass  # Some Windows filesystems do not permit symlinks.
            else:
                with self.assertRaises(FileExistsError):
                    write_output(source, {}, source.read_bytes(), output.name)
                self.assertEqual("keep", target.read_text())
                self.assertEqual(3, len(list(Path(directory).iterdir())))
                output.unlink()
            output.write_text("previous result")
            with self.assertRaises(FileExistsError):
                write_output(source, {}, source.read_bytes(), output.name)
            self.assertEqual("previous result", output.read_text())

    def test_backup_collision_does_not_replace_original_backup(self):
        class FixedDatetime(datetime):
            @classmethod
            def now(cls):
                return cls(2026, 9, 23, 12, 0, 0)

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            source.write_text("{}")
            with patch("save_safety.datetime.datetime", FixedDatetime):
                backup, _ = write_output(source, {}, source.read_bytes(), "first.json")
                with self.assertRaises(FileExistsError):
                    write_output(source, {}, source.read_bytes(), "second.json")
            self.assertEqual(b"{}", backup.read_bytes())
            self.assertFalse((Path(directory) / "second.json").exists())

    def test_changed_export_is_rejected_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            source.write_text('{"version":1}')
            data, original = load_json(source)
            source.write_text('{"version":2}')
            with self.assertRaisesRegex(ValueError, "changed during review"):
                write_output(source, data, original, "optimized_save.json")
            self.assertEqual([source.name], [path.name for path in Path(directory).iterdir()])

    def test_export_changed_after_first_check_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            source.write_text('{"version":1}')
            data, original = load_json(source)
            real_digest = hashlib.file_digest
            calls = 0

            def change_after_check(file, digest):
                nonlocal calls
                result = real_digest(file, digest)
                calls += 1
                if calls == 1:
                    source.write_text('{"version":2}')
                return result

            with patch("save_safety.hashlib.file_digest", change_after_check):
                with self.assertRaisesRegex(ValueError, "changed during review"):
                    write_output(source, data, original, "optimized_save.json")
            self.assertEqual(2, calls)
            self.assertEqual([source.name], [path.name for path in Path(directory).iterdir()])

    def test_export_changed_during_publication_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            source.write_text('{"version":1}')
            data, original = load_json(source)
            publish_name = "rename" if os.name == "nt" else "link"
            real_publish = getattr(os, publish_name)

            def change_during_publish(staged, output):
                source.write_text('{"version":2}')
                return real_publish(staged, output)

            with patch(f"save_safety.os.{publish_name}", change_during_publish):
                with self.assertRaisesRegex(ValueError, "changed during review"):
                    write_output(source, data, original, "optimized_save.json")
            self.assertEqual('{"version":2}', source.read_text())
            self.assertEqual([source.name], [path.name for path in Path(directory).iterdir()])

    def test_stale_cleanup_preserves_replaced_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            source.write_text('{"version":1}')
            data, original = load_json(source)
            output = Path(directory) / "optimized_save.json"
            publish_name = "rename" if os.name == "nt" else "link"
            real_publish = getattr(os, publish_name)

            def replace_after_publish(staged, destination):
                real_publish(staged, destination)
                source.write_text('{"version":2}')
                output.unlink()
                output.write_text("another process's output")

            with patch(f"save_safety.os.{publish_name}", replace_after_publish):
                with self.assertRaisesRegex(ValueError, "changed during review"):
                    write_output(source, data, original, output.name)
            self.assertEqual("another process's output", output.read_text())
            self.assertEqual({source.name, output.name}, {path.name for path in Path(directory).iterdir()})

    def test_failed_serialization_does_not_publish_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            source.write_text("{}")

            def interrupted_dump(data, file, **kwargs):
                file.write('{"incomplete":')
                raise OSError("simulated write failure")

            with patch("save_safety.json.dump", interrupted_dump):
                with self.assertRaisesRegex(OSError, "simulated write failure"):
                    write_output(source, {}, source.read_bytes(), "optimized_save.json")
            self.assertEqual([source.name], [path.name for path in Path(directory).iterdir()])

    def test_cli_cancel_writes_nothing(self):
        data = save([record("SolarSystem", "Mine", "Player"), record("Animal", "Other", "Else")])
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full_save.json"
            source.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, str(ROOT / "discovery_optimizer.py")],
                                    input="2\nPlayer\nNO\n", text=True, capture_output=True, cwd=directory)
            self.assertEqual(0, result.returncode)
            self.assertIn("Cancelled before writing", result.stdout)
            self.assertEqual([source.name], [path.name for path in Path(directory).iterdir()])

    def test_cli_menu_cancel_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(ROOT / "discovery_optimizer.py")],
                                    input="4\n", text=True, capture_output=True, cwd=directory)
            self.assertEqual(0, result.returncode)
            self.assertIn("Exiting.", result.stdout)
            self.assertEqual([], list(Path(directory).iterdir()))

    def test_cache_filter_uses_owner_field_not_username_elsewhere(self):
        records = [record("Animal", "Mine", "Player"), record("Animal", "Player in its name", "Else")]
        cache = {"DiscoveryData-v1": {"Store": {"Record": records}}}
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "discoveries.json"
            source.write_text(json.dumps(cache))
            result = subprocess.run([sys.executable, str(ROOT / "fix_cache.py")],
                                    input="Player\nDELETE\n", text=True, capture_output=True, cwd=directory)
            self.assertEqual(0, result.returncode, result.stderr)
            output = json.loads((Path(directory) / "discoveries_fixed.json").read_text())
            self.assertEqual([records[0]], output["DiscoveryData-v1"]["Store"]["Record"])

    def test_legacy_cli_preserves_its_reserve_fields(self):
        data = save([record("SolarSystem", "Mine", "Player"), record("Animal", "Other", "Else")])
        cache = data["DiscoveryManagerData"]["DiscoveryData-v1"]
        cache["ReserveStore"], cache["ReserveManaged"] = 9, 10
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "full_save.json").write_text(json.dumps(data))
            result = subprocess.run([sys.executable, str(ROOT / "discovery_optimizer.py")],
                                    input="2\nPlayer\nDELETE\n", text=True, capture_output=True, cwd=directory)
            self.assertEqual(0, result.returncode, result.stderr)
            output = json.loads((Path(directory) / "optimized_save.json").read_text())
            result_cache = output["DiscoveryManagerData"]["DiscoveryData-v1"]
            self.assertEqual((9, 10), (result_cache["ReserveStore"], result_cache["ReserveManaged"]))


if __name__ == "__main__":
    unittest.main()
