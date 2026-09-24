from save_safety import discovery_records, load_json

print("Loading save data...")
data, _ = load_json('full_save.json')
records = discovery_records(data)

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
