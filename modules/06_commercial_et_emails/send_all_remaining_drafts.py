import os
import subprocess
import time
import json
from datetime import datetime

STATUS_FILE = "modules/06_commercial_et_emails/STATUS.md"

drafts_to_send = [
    {"index": 2, "name": "Napoléon Plomberie Climatisation Bordeaux", "email": "contact@napoleon-plomberie.com", "draft_id": "r3712715305897923005"},
    {"index": 3, "name": "Cafonso Serrurier - Bordeaux", "email": "caciano.afonso028@gmail.com", "draft_id": "r8057644660971937040"},
    {"index": 4, "name": "MGB Serrurier Bordeaux", "email": "mgb33000@gmail.com", "draft_id": "r-1045859492103988605"},
    {"index": 5, "name": "Clés Stop Dépanne - Serrurier Bordeaux", "email": "clesstop.contact@gmail.com", "draft_id": "r730020868108101404"},
    {"index": 6, "name": "B&L Plomberie Bordeaux", "email": "louis.barlemont@gmail.com", "draft_id": "r-1826172810489495482"},
    {"index": 7, "name": "Serrurerie Bacci", "email": "contact@serrurerie-bacci.com", "draft_id": "r-6339637393749250096"},
    {"index": 8, "name": "SERLOCK", "email": "contact@serlock.fr", "draft_id": "r6292932204389700902"},
    {"index": 9, "name": "Serrurerie Bordelaise", "email": "contact@serrurerie-bordelaise.com", "draft_id": "r-2420920977434393447"},
    {"index": 10, "name": "Abeille Services - Serrurier Bordeaux", "email": "contact@abeille-depannage.com", "draft_id": "r-4028389936230671436"},
    {"index": 11, "name": "JT 33 Serrurier Bordeaux", "email": "torresj33@outlook.fr", "draft_id": "r5763244780750355691"},
    {"index": 12, "name": "PENA - Fermetures, Serrurier, Sécurité, Point Fort Fichet, Bordeaux", "email": "info@pena-serrurerie.com", "draft_id": "r866630625780553770"},
    {"index": 13, "name": "Selfcity Bordeaux - Plombier Chauffagiste Climatisation", "email": "contact@selfcity.fr", "draft_id": "r7570738293888826837"},
    {"index": 14, "name": "BL Plomberie", "email": "contact@blplomberie.fr", "draft_id": "r-7315529635629523232"},
    {"index": 15, "name": "MK Plomberie - Plombier à Lyon", "email": "contact@mk-plomberie.com", "draft_id": "r3734607042295180284"}
]

env = os.environ.copy()
env["AGY_ACCOUNT"] = "vumavuma148@gmail.com"

results = [
    {"index": 1, "name": "Bicycl'eau Plombier à vélo - William", "email": "contact@bicycleau.fr", "status": "Envoyé", "msg_id": "1a1f05a89be6118b", "timestamp": "18/11/2026 21:30"}
]

for item in drafts_to_send:
    idx = item["index"]
    d_id = item["draft_id"]
    print(f"[{idx}/15] Sending to {item['name']} ({item['email']})...")
    
    cmd = ["gmail", "mutate", "send-draft", d_id]
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if res.returncode == 0:
        msg_id = ""
        for line in res.stdout.splitlines():
            if "Message ID:" in line:
                msg_id = line.split("Message ID:")[-1].strip()
        print(f" -> SENT OK (Message ID: {msg_id})")
        results.append({
            "index": idx,
            "name": item["name"],
            "email": item["email"],
            "status": "Envoyé",
            "msg_id": msg_id,
            "timestamp": now_str
        })
    else:
        print(f" -> ERROR: {res.stderr.strip()}")
        results.append({
            "index": idx,
            "name": item["name"],
            "email": item["email"],
            "status": "Erreur",
            "msg_id": res.stderr.strip(),
            "timestamp": now_str
        })
    
    if idx < 15:
        time.sleep(7)

log_path = "modules/06_commercial_et_emails/envois_batch_1.json"
with open(log_path, "w", encoding="utf-8") as lf:
    json.dump(results, lf, indent=2, ensure_ascii=False)

print(f"=== EXPÉDITION TERMINÉE : {len(results)}/15 emails traités. ===")
