import json

print("Loading save data...")
with open('full_save.json', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

content = content.replace('\\', '\\\\').replace('\\\\"', '\\"')
content = "".join(ch for ch in content if ord(ch) >= 32 or ch in '\n\r\t')
data = json.loads(content, strict=False)

records = data.get("DiscoveryManagerData", {}).get("DiscoveryData-v1", {}).get("Store", {}).get("Record", [])

f_count = 0
for r in records:
    if r.get("DD", {}).get("DT") == "SolarSystem":
        if "F" in r.get("FL", {}):
            f_count += 1

print(f"\nTotal systems marked with 'F' (Removed) flag: {f_count}")
if f_count > 1:
    print("Success! The count increased, proving 'F' is the Removed flag!")
elif f_count == 1:
    print("Count is still 1. Did you export the new save file after hiding a second system?")