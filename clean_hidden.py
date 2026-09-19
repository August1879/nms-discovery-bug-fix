import json

print("Loading and sanitizing save file...")
with open('full_save.json', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

content = content.replace('\\', '\\\\').replace('\\\\"', '\\"')
content = "".join(ch for ch in content if ord(ch) >= 32 or ch in '\n\r\t')
data = json.loads(content, strict=False)

records = data.get("DiscoveryManagerData", {}).get("DiscoveryData-v1", {}).get("Store", {}).get("Record", [])
print(f"Original record count: {len(records)}")

cleaned_records = []
removed_count = 0

for r in records:
    # Filter out any record containing the 'F': 1 hidden flag
    if r.get("FL", {}).get("F") == 1:
        removed_count += 1
    else:
        cleaned_records.append(r)

print(f"Successfully wiped {removed_count} removed systems from the cache!")

if removed_count > 0:
    data["DiscoveryManagerData"]["DiscoveryData-v1"]["Store"]["Record"] = cleaned_records
    
    print("Saving to clean_save.json...")
    with open("clean_save.json", "w", encoding="utf-8") as out:
        json.dump(data, out, separators=(',', ':'))
    print("Done! Import 'clean_save.json' into Goatfungus to apply the fix.")