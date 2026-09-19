import json
import sys

# --- MANUALLY ENTER YOUR IN-GAME USERNAME HERE ---
my_username = "YOUR_IN_GAME_NAME" 

# Fails the script if the user forgot to add their name
if my_username == "YOUR_IN_GAME_NAME" or not my_username.strip():
    print("ERROR: You must edit this script and replace 'YOUR_IN_GAME_NAME' with your actual No Man's Sky username on line 5 before running.")
    sys.exit(1)

with open('discoveries.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

records = data['DiscoveryData-v1']['Store']['Record']

# This converts each record to text and checks if your username is inside it
filtered_records = [r for r in records if my_username in str(r)]

data['DiscoveryData-v1']['Store']['Record'] = filtered_records

print(f"Reduced records from {len(records)} to {len(filtered_records)}.")
print("Saved clean cache to discoveries_fixed.json")

with open('discoveries_fixed.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2)git add fix_cache.py
git commit -m "Added safety check to fail if username is not provided"