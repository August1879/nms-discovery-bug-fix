import json

# --- MANUALLY ENTER YOUR IN-GAME USERNAME HERE ---
my_username = "augustdheart0" 

with open('discoveries.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

records = data['DiscoveryData-v1']['Store']['Record']

# This converts each record to text and checks if your username is inside it
filtered_records = [r for r in records if my_username in str(r)]

data['DiscoveryData-v1']['Store']['Record'] = filtered_records

print(f"Reduced records from {len(records)} to {len(filtered_records)}.")
print("Saved clean cache to discoveries_fixed.json")

with open('discoveries_fixed.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2)