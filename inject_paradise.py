import json

print("Loading and sanitizing save file...")
with open('full_save.json', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

content = content.replace('\\', '\\\\').replace('\\\\"', '\\"')
content = "".join(ch for ch in content if ord(ch) >= 32 or ch in '\n\r\t')
data = json.loads(content, strict=False)

ps = data.get("BaseContext", {}).get("PlayerStateData", {})
existing_wonders = ps.get("WonderPlanetRecords", [])

# Track existing IDs so we don't duplicate planets you already have pinned
existing_ids = set()
for w in existing_wonders:
    gen_id = w.get("GenerationID", [])
    if len(gen_id) == 2:
        existing_ids.add((gen_id[0], gen_id[1]))

records = data.get("DiscoveryManagerData", {}).get("DiscoveryData-v1", {}).get("Store", {}).get("Record", [])

my_username = "augustdheart0"
new_wonders = []

print("Scanning discovery cache for your planets...")
for r in records:
    dd = r.get("DD", {})
    ows = r.get("OWS", {})
    
    # Filter for Planets discovered by YOU
    if dd.get("DT") == "Planet" and ows.get("USN") == my_username:
        ua = dd.get("UA")
        vp = dd.get("VP", [])
        
        if ua and len(vp) > 0:
            gen_tuple = (str(ua), str(vp[0]))
            if gen_tuple not in existing_ids:
                # Create the new Wonder Record
                new_wonders.append({
                    "GenerationID": [str(ua), str(vp[0])],
                    "WonderStatValue": 0.0,  # The game engine will auto-calculate this!
                    "SeenInFrontend": False
                })
                existing_ids.add(gen_tuple)

print(f"Found {len(new_wonders)} new planets to inject!")

if new_wonders:
    ps["WonderPlanetRecords"] = existing_wonders + new_wonders
    
    print("Saving to new_save.json...")
    with open("new_save.json", "w", encoding="utf-8") as out:
        json.dump(data, out, separators=(',', ':'))
    print("Done! Import 'new_save.json' back into Goatfungus.")
else:
    print("No new planets to add.")