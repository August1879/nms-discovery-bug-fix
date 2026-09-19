import json

with open('discoveries.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

record_count = len(data['DiscoveryData-v1']['Store']['Record'])
print(f"Total discovery records: {record_count}")