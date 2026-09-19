import json
import sys

print("Loading and sanitizing save file...")
with open('full_save.json', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

content = content.replace('\\', '\\\\').replace('\\\\"', '\\"')
content = "".join(ch for ch in content if ord(ch) >= 32 or ch in '\n\r\t')
data = json.loads(content, strict=False)

records = data.get("DiscoveryManagerData", {}).get("DiscoveryData-v1", {}).get("Store", {}).get("Record", [])

print("\n--- NMS Discovery Cache Optimizer ---")
print("1: Wipe 'Hidden' Systems (Systems you pressed 'F' to hide)")
print("2: Wipe Foreign Flora, Fauna, and Minerals (Keep foreign planets/systems)")
print("3: Wipe ALL Foreign Discoveries (Everything discovered by other players)")
print("4: Cancel and exit")

choice = input("\nEnter choice (1-4): ").strip()
if choice not in ['1', '2', '3']:
    print("Exiting.")
    sys.exit()

# Dynamic username input so others can use your script easily
my_username = input("Enter your exact in-game username (Press Enter for 'augustdheart0'): ").strip()
if not my_username:
    my_username = "augustdheart0"

cleaned_records = []
removed_count = 0

print("\nScanning cache...")
for r in records:
    dt = r.get("DD", {}).get("DT", "")
    usn = r.get("OWS", {}).get("USN", "")
    
    is_hidden = r.get("FL", {}).get("F") == 1
    is_foreign = (usn != my_username and usn != "")

    # Apply the chosen filter
    if choice == '1' and is_hidden:
        removed_count += 1
    elif choice == '2' and dt in ["Animal", "Flora", "Mineral"] and is_foreign:
        removed_count += 1
    elif choice == '3' and is_foreign:
        removed_count += 1
    else:
        cleaned_records.append(r)

print(f"Successfully wiped {removed_count} records!")

if removed_count > 0:
    data["DiscoveryManagerData"]["DiscoveryData-v1"]["Store"]["Record"] = cleaned_records
    
    print("Saving to optimized_save.json...")
    with open("optimized_save.json", "w", encoding="utf-8") as out:
        json.dump(data, out, separators=(',', ':'))
    print("Done! Import 'optimized_save.json' into Goatfungus.")
else:
    print("No matching records found to remove.")