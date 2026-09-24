from save_safety import discovery_records, load_json

data, _ = load_json('discoveries.json')

record_count = len(discovery_records(data, cache_only=True))
print(f"Total discovery records: {record_count}")
