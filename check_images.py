import json
import os

with open(r"d:\works\Almedicus\histology-bot\bot_data.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

base = r"d:\works\Almedicus\histology-exam"
preps_ok = sum(1 for p in data['preparations'] if os.path.exists(os.path.join(base, p['micro_image'])))
schemes_ok = sum(1 for s in data['schemes'] if os.path.exists(os.path.join(base, s['image'])))

print(f"Preparations images found: {preps_ok} / {len(data['preparations'])}")
print(f"Schemes images found: {schemes_ok} / {len(data['schemes'])}")
