import json
import os

PROSPECTS_FILE = "modules/05_deploiement_et_lancement/prospects_batch_1.json"
RELANCES_DIR = "modules/06_commercial_et_emails/relances"
OUTPUT_JSON = "modules/06_commercial_et_emails/sequences_relances.json"

os.makedirs(RELANCES_DIR, exist_ok=True)

with open(PROSPECTS_FILE, "r", encoding="utf-8") as f:
    prospects = json.load(f)

metier_query_map = {
    "Plombier": "plombier",
    "Plombier Chauffagiste": "plombier chauffagiste",
    "Serrurier": "serrurier"
}

relances_data = []

for p in prospects:
    idx = p["index"]
    dirigeant_part = f" {p['dirigeant']}" if p.get("dirigeant") else ""
    metier_q = metier_query_map.get(p["metier"], p["metier"].lower())
    stripe_url = f"https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201?client_reference_id={p['client_reference_id']}"
    
    # J+3
    subject_j3 = f"Re: Fiche Google {p['business_name']} (remarque rapide)"
    body_j3 = f"""Bonjour{dirigeant_part},

Je fais suite à mon message concernant votre visibilité à {p['city']}.

Faites ce test rapide depuis votre téléphone : tapez simplement "{metier_q} {p['city']}" sur Google.

Regardez les 3 premiers artisans qui s'affichent sur la carte. Ils ne sont pas forcément meilleurs sur le terrain, mais ils cumulent 3 critères techniques que votre fiche n'a pas encore validés.

Le résultat ? Chaque semaine, des particuliers qui ont besoin d'un dépannage ou d'un devis appellent ces 3 fiches en priorité.

Pour 49 € (l'équivalent de 20 minutes d'intervention), vous avez entre les mains le diagnostic exact pour surclasser ces concurrents et verrouiller vos positions :

👉 **Télécharger votre audit complet** :
{stripe_url}

Bonne fin de semaine à vous sur vos chantiers.

Bien cordialement,

**Corentin — AutoBiz IA**  
Observatoire de la Visibilité Locale
"""

    # J+7
    subject_j7 = f"Dernier message / {p['business_name']}"
    body_j7 = f"""Bonjour{dirigeant_part},

Je me permets ce dernier mot et je ne vous relancerai plus ensuite.

Si votre carnet de rendez-vous à {p['city']} est déjà complet pour les 6 prochains mois sans avoir besoin de nouveaux appels, c'est une excellente nouvelle, ne changez rien.

En revanche, si vous constatez des périodes creuses ou que vous souhaitez que votre fiche Google devienne une source régulière d'appels entrants qualifiés, votre rapport d'audit reste disponible ici :

👉 **Accéder à votre audit complet (49 €)** :
{stripe_url}

Je vous souhaite une excellente continuation dans votre activité.

Bien cordialement,

**Corentin — AutoBiz IA**  
Observatoire de la Visibilité Locale
"""

    file_j3 = os.path.join(RELANCES_DIR, f"lead_{idx:02d}_J3.md")
    with open(file_j3, "w", encoding="utf-8") as fj3:
        fj3.write(body_j3)
        
    file_j7 = os.path.join(RELANCES_DIR, f"lead_{idx:02d}_J7.md")
    with open(file_j7, "w", encoding="utf-8") as fj7:
        fj7.write(body_j7)
        
    relances_data.append({
        "index": idx,
        "business_name": p["business_name"],
        "primary_email": p["primary_email"],
        "client_reference_id": p["client_reference_id"],
        "stripe_url": stripe_url,
        "j3": {
            "subject": subject_j3,
            "body_file": file_j3,
            "body_preview": body_j3[:150] + "..."
        },
        "j7": {
            "subject": subject_j7,
            "body_file": file_j7,
            "body_preview": body_j7[:150] + "..."
        }
    })

with open(OUTPUT_JSON, "w", encoding="utf-8") as out_f:
    json.dump(relances_data, out_f, indent=2, ensure_ascii=False)

print(f"Generated relances for {len(relances_data)} prospects.")
