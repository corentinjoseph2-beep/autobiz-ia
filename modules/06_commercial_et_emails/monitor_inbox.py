#!/usr/bin/env python3
"""
Script de surveillance de boîte de réception Gmail et de gestion des relances (Bloc 6).
Compatible avec le plugin Gmail Antigravity (compte: vumavuma148@gmail.com).
"""

import json
import subprocess
import os
import sys
from datetime import datetime

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PROSPECTS_FILE = os.path.join(WORKSPACE_ROOT, "modules/05_deploiement_et_lancement/prospects_batch_1.json")
STATUS_FILE = os.path.join(WORKSPACE_ROOT, "modules/06_commercial_et_emails/STATUS.md")
HISTORY_FILE = os.path.join(WORKSPACE_ROOT, "modules/06_commercial_et_emails/historique_echanges.md")
RELANCES_JSON = os.path.join(WORKSPACE_ROOT, "modules/06_commercial_et_emails/sequences_relances.json")

def run_gmail_cli(args):
    """Exécute une commande de l'outil CLI Gmail officiel Antigravity."""
    cmd = ["gmail"] + args
    env = os.environ.copy()
    env["AGY_ACCOUNT"] = "vumavuma148@gmail.com"
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    return res

def scan_inbox_for_replies():
    """Vérifie si l'un des 15 prospects a répondu."""
    if not os.path.exists(PROSPECTS_FILE):
        print(f"Erreur : fichier {PROSPECTS_FILE} introuvable.")
        return []

    with open(PROSPECTS_FILE, "r", encoding="utf-8") as f:
        prospects = json.load(f)

    emails = [p["primary_email"] for p in prospects if p.get("primary_email")]
    emails_query = " OR ".join([f"from:{e}" for e in emails])
    full_query = f"({emails_query})"

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Vérification de la boîte Gmail (vumavuma148@gmail.com)...")
    res = run_gmail_cli(["readonly", "search", full_query, "--max", "15", "--json"])
    
    if res.returncode != 0:
        print(f"Erreur lors de l'exécution de gmail CLI: {res.stderr}")
        return []

    try:
        messages = json.loads(res.stdout) if res.stdout.strip() else []
    except json.JSONDecodeError:
        messages = []

    print(f"-> {len(messages)} message(s) détecté(s) provenant des prospects.")
    return messages

def update_status_dashboard(replied_emails=None):
    """Met à jour le statut dans STATUS.md avec la date de scan."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    replied_emails = replied_emails or []
    
    if not os.path.exists(STATUS_FILE):
        return

    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Remplacer la dernière vérification
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("- **Dernière mise à jour**"):
            new_lines.append(f"- **Dernière mise à jour** : {now_str}")
        elif line.startswith("- **Dernier scan boîte**"):
            new_lines.append(f"- **Dernier scan boîte** : {now_str} ({len(replied_emails)} réponse(s) active(s))")
        else:
            new_lines.append(line)

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

def record_interaction(sender, subject, snippet):
    """Enregistre un nouveau message reçu dans historique_echanges.md."""
    now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    entry = f"""
### 📩 Réponse reçue le {now_str}
- **De** : `{sender}`
- **Objet** : {subject}
- **Extrait** :
> {snippet}
- **Statut** : 🚨 Action requise — formulation de réponse commerciale en cours.
"""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"Interaction enregistrée pour {sender} dans historique_echanges.md")

def check_general_unread():
    """Vérifie également les 5 derniers emails non-lus généraux pour parer à tout changement d'adresse."""
    res = run_gmail_cli(["readonly", "search", "is:unread", "--max", "5", "--json"])
    if res.returncode == 0:
        try:
            return json.loads(res.stdout) if res.stdout.strip() else []
        except json.JSONDecodeError:
            return []
    return []

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--scan"
    
    if mode in ["--scan", "-s"]:
        replies = scan_inbox_for_replies()
        if replies:
            print("🚨 ATTENTION : Réponse(s) détectée(s) !")
            for m in replies:
                print(f" - De: {m.get('from')} | Objet: {m.get('subject')}")
                record_interaction(m.get('from', ''), m.get('subject', ''), m.get('snippet', ''))
            update_status_dashboard([m.get('from') for m in replies])
        else:
            print("✅ Aucune nouvelle réponse de prospect pour le moment.")
            update_status_dashboard([])
            
    elif mode == "--check-unread":
        unread = check_general_unread()
        print(f"Total non-lus récents: {len(unread)}")
        for u in unread:
            print(f"- {u.get('from')} : {u.get('subject')}")
