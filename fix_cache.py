from save_safety import discovery_records, load_json, require_owner, write_output

my_username = input("Enter your in-game username: ").strip()
if not my_username:
    raise SystemExit("A username is required.")

data, original = load_json('discoveries.json')
records = discovery_records(data, cache_only=True)
require_owner(records, my_username)

filtered_records, removed = [], []
for index, record in enumerate(records):
    if not isinstance(record, dict) or not isinstance(record.get('OWS'), dict) or not isinstance(record['OWS'].get('USN'), str) or not isinstance(record.get('DD'), dict):
        raise ValueError(f"Discovery record {index} has an unexpected format.")
    if record['OWS']['USN'].casefold() == my_username.casefold():
        filtered_records.append(record)
    else:
        removed.append((index, record))
if not removed:
    raise SystemExit("No foreign records found. No output was written.")

print(f"Will remove {len(removed)} of {len(records)} records:")
for index, record in removed:
    detail = record.get('DD', {})
    print(f"  #{index}: {detail.get('DT', '')!r}, {detail.get('N', '')!r}, owner {record['OWS']['USN']!r}")
if input("Type DELETE to write the result: ").strip() != "DELETE":
    print("Cancelled before writing any files.")
    raise SystemExit(0)

data['DiscoveryData-v1']['Store']['Record'] = filtered_records
print(f"Reduced records from {len(records)} to {len(filtered_records)}.")
backup, output = write_output('discoveries.json', data, original, 'discoveries_fixed.json')
print(f"Original backup: {backup}\nClean cache: {output}")
