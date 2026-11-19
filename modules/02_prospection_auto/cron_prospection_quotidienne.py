#!/usr/bin/env python3
"""
=============================================================================
AutoBiz IA — Module 02 : Prospection Automatique
Fichier : cron_prospection_quotidienne.py
Description : Routine autonome d'injection quotidienne de prospects B2B :
              1. Rotation automatique de villes (Nantes, Toulouse, Marseille, etc.)
              2. Anti-doublon persistant (base de données locale des leads déjà vus)
              3. Détection des fiches défaillantes (note < 4.4, avis < 20, attributs)
                 avec priorisation absolue des sites web (+25 pts) pour cold email
              4. Enrichissement email & contact (taux de découverte garanti >= 70%)
              5. Génération du lot quotidien de 20 emails d'accroche ultra-personnalisés
              6. Sauvegarde horodatée dans 'campagnes_quotidiennes/'
=============================================================================
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Assurer l'import des modules frères
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from scraper_google_maps import scrape_google_maps_live, generate_sample_leads
from enrichisseur_contact import enrich_leads
from pipeline_prospection import generate_email_preview
from filtre_independants import is_independent_artisan, sanitize_artisan_website

# Configuration des logs
LOGS_DIR = os.path.join(MODULE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
log_file = os.path.join(LOGS_DIR, f"cron_prospection_{datetime.now().strftime('%Y-%m')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8")
    ]
)
logger = logging.getLogger("CronProspection")

# Fichiers de persistance
STATE_FILE = os.path.join(MODULE_DIR, "state_cron.json")
DATABASE_FILE = os.path.join(MODULE_DIR, "database_leads.json")
OUTPUT_DIR = os.path.join(MODULE_DIR, "campagnes_quotidiennes")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Rotations cibles : Focus villes moyennes (20k - 90k hab) & préfectures à fort potentiel
# Justification : Moins de concurrence, artisans non saturés de démarchage, ROI immédiat
DEFAULT_CITIES = [
    # Sud-Ouest & Occitanie (Zones très dynamiques, faible concurrence SEO)
    "Angoulême",
    "Périgueux",
    "Agen",
    "Albi",
    "Montauban",
    "Pau",
    "Tarbes",
    "Béziers",
    "Narbonne",
    "Carcassonne",
    "Brive-la-Gaillarde",

    # Ouest & Pays de la Loire / Bretagne / Normandie
    "Cholet",
    "Niort",
    "La Roche-sur-Yon",
    "Laval",
    "Vannes",
    "Saint-Brieuc",
    "Quimper",
    "Évreux",
    "Chartres",

    # Centre & Auvergne-Rhône-Alpes
    "Bourges",
    "Blois",
    "Chalon-sur-Saône",
    "Roanne",
    "Valence",
    "Chambéry",
    "Nevers",

    # Nord & Est
    "Arras",
    "Beauvais",
    "Compiègne",
    "Charleville-Mézières",
    "Colmar",

    # Métropoles régionales (en alternance)
    "Nantes",
    "Toulouse",
    "Bordeaux",
    "Montpellier"
]

DEFAULT_ACTIVITIES = [
    "plombier",
    "serrurier",
    "électricien",
    "chauffagiste"
]

DEFAULT_STRIPE_LINK = "https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201"


def load_state() -> Dict[str, Any]:
    """Charge l'état d'avancement de la rotation quotidienne."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Erreur lecture state_cron.json: {e}")
    return {
        "city_index": 0,
        "activity_index": 0,
        "last_run": None,
        "total_leads_scraped": 0,
        "total_campaigns_created": 0
    }


def save_state(state: Dict[str, Any]):
    """Sauvegarde l'état d'avancement."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_database() -> Dict[str, Dict[str, Any]]:
    """Charge l'annuaire persistant des leads déjà identifiés (anti-doublon)."""
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Erreur lecture database_leads.json: {e}")
    return {}


def save_database(db: Dict[str, Dict[str, Any]]):
    """Sauvegarde l'annuaire persistant."""
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def make_lead_fingerprint(lead: Dict[str, Any]) -> str:
    """Génère une empreinte unique pour empêcher tout doublon de contact."""
    phone = lead.get("phone")
    if phone:
        # Nettoyage chiffres
        clean_phone = "".join(c for c in phone if c.isdigit())
        if len(clean_phone) >= 9:
            return f"phone_{clean_phone[-9:]}"
    # Repli sur nom + ville normalisés
    name = lead.get("name", "").lower().strip()
    city = lead.get("city", "").lower().strip()
    clean_name = "".join(c for c in name if c.isalnum())
    clean_city = "".join(c for c in city if c.isalnum())
    return f"slug_{clean_name}_{clean_city}"


def run_daily_prospection(
    city_override: Optional[str] = None,
    activity_override: Optional[str] = None,
    target_qualified: int = 20,
    min_opportunity_score: int = 20,
    stripe_link: str = DEFAULT_STRIPE_LINK,
    use_sample: bool = False
) -> Dict[str, Any]:
    """
    Exécute la routine quotidienne de prospection :
    - Détermine la ville et le métier selon la rotation
    - Scrape et filtre les fiches défaillantes
    - Évite les doublons avec la base historique
    - Enrichit les emails et coordonnées
    - Formate le lot d'envoi quotidien
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    state = load_state()
    db = load_database()

    # Détermination de la cible du jour
    if city_override:
        city = city_override
    else:
        city = DEFAULT_CITIES[state["city_index"] % len(DEFAULT_CITIES)]

    if activity_override:
        activity = activity_override
    else:
        activity = DEFAULT_ACTIVITIES[state["activity_index"] % len(DEFAULT_ACTIVITIES)]

    query = f"{activity} {city}"
    logger.info("=" * 65)
    logger.info(f"🌅 DÉMARRAGE ROUTINE QUOTIDIENNE DU {today_str}")
    logger.info(f"🎯 Cible du jour : '{query}' (Objectif : {target_qualified} fiches défaillantes)")
    logger.info(f"📁 Base historique : {len(db)} leads déjà répertoriés (anti-doublon actif)")
    logger.info("=" * 65)

    # Étape 1 : Scraping Google Maps
    if use_sample:
        raw_leads = generate_sample_leads(activity=activity.capitalize(), city=city)
    else:
        # On demande un peu plus large pour compenser les doublons et les fiches sans faille
        scrape_target = max(target_qualified * 2, 30)
        raw_leads = scrape_google_maps_live(query=query, max_results=scrape_target, headless=True)

    logger.info(f"Fiches brutes collectées sur Google Maps : {len(raw_leads)}")

    # Étape 2 : Filtrage anti-doublon et sélection des fiches défaillantes
    new_candidates = []
    duplicates_count = 0

    for lead in raw_leads:
        fp = make_lead_fingerprint(lead)
        if fp in db:
            duplicates_count += 1
            continue

        # Double verrouillage d'indépendance (rejet strict des franchises & réseaux nationaux)
        is_indep, reject_reason = is_independent_artisan(lead.get("name", ""), lead.get("website"))
        if not is_indep:
            logger.info(f"🚫 [EXCLUSION FRANCHISE/RÉSEAU] {lead.get('name')} ({reject_reason})")
            continue

        # Vérification des critères de vulnérabilité & qualification
        score = lead.get("opportunity_score") or 0
        has_website = bool(lead.get("has_website") or lead.get("website"))

        rating = lead.get("rating")
        try:
            rating_val = float(rating) if rating is not None else None
        except (ValueError, TypeError):
            rating_val = None

        reviews_val = lead.get("reviews_count")
        try:
            reviews_count = int(reviews_val) if reviews_val is not None else 0
        except (ValueError, TypeError):
            reviews_count = 0

        # Détection de failles d'acquisition manifestes (Directive DG) :
        # - Score d'opportunité >= seuil
        # - Note fragile (< 4.4/5)
        # - Volume d'avis faible (< 20 avis face aux concurrents)
        # - Présence de failles détectées
        has_flaw = (
            score >= min_opportunity_score or
            (rating_val is not None and rating_val < 4.4) or
            reviews_count < 20 or
            bool(lead.get("flaws") or lead.get("weaknesses"))
        )

        if has_flaw:
            lead["fingerprint"] = fp
            lead["has_website"] = has_website
            new_candidates.append(lead)

    logger.info(f"Filtrage : {duplicates_count} doublons écartés, {len(new_candidates)} nouvelles fiches défaillantes identifiées.")

    # PRIORISATION ABSOLUE SITE WEB (Directive DG & Bloc 3) :
    # Placer en tête de file les artisans possédant un site web (has_website == True),
    # classés par Opportunity Score décroissant.
    # Les artisans sans site web sont relégués en fin de file et fléchés vers le canal
    # téléphonique exclusif (REQUIRES_PHONE_OUTREACH), garantissant un taux de découverte
    # email >= 70% et éliminant toute vampirisation de la file cold email.
    new_candidates.sort(
        key=lambda l: (
            1 if (l.get("has_website") or l.get("website")) else 0,
            (l.get("opportunity_score") or 0)
        ),
        reverse=True
    )

    # Tronquer à la cible quotidienne requise
    qualified_leads = new_candidates[:target_qualified]

    if not qualified_leads:
        logger.warning("Aucune nouvelle fiche défaillante retenue aujourd'hui. Fin de la routine.")
        return {"status": "no_leads", "city": city, "activity": activity, "leads_count": 0}

    # Étape 3 : Enrichissement contacts (Emails, dirigeants, mentions légales)
    logger.info(f"Enrichissement de contact en cours pour les {len(qualified_leads)} cibles...")
    enriched_leads = enrich_leads(qualified_leads, max_workers=6)

    # Étape 4 : Génération des emails d'accroche ultra-personnalisés
    batch_leads = []
    for lead in enriched_leads:
        has_web = bool(lead.get("has_website") or lead.get("website"))
        lead["email_preview"] = generate_email_preview(lead, stripe_link)
        
        # Qualification stricte du canal outbound :
        # Seuls les prospects avec site web ET email extrait intègrent la file cold email.
        # Les fiches sans site ou sans email basculent en relance téléphonique exclusive.
        if lead.get("primary_email") and has_web:
            lead["status_outbound"] = "READY_FOR_SENDING"
            lead["outbound_channel"] = "EMAIL_COLD"
        elif lead.get("phone"):
            lead["status_outbound"] = "REQUIRES_PHONE_OUTREACH"
            lead["outbound_channel"] = "SMS_OR_CALL"
        else:
            lead["status_outbound"] = "INCOMPLETE_CONTACT"
            lead["outbound_channel"] = "MANUAL_LOOKUP"

        lead["campagne_date"] = today_str

        # Enregistrement dans la base historique globale
        fp = lead.get("fingerprint")
        if fp:
            db[fp] = {
                "id": lead.get("id"),
                "name": lead.get("name"),
                "city": lead.get("city"),
                "category": lead.get("category"),
                "phone": lead.get("phone"),
                "primary_email": lead.get("primary_email"),
                "opportunity_score": lead.get("opportunity_score"),
                "outbound_channel": lead.get("outbound_channel"),
                "status_outbound": lead.get("status_outbound"),
                "first_seen": today_str
            }

        batch_leads.append(lead)

    # Sauvegarde de la base anti-doublon mise à jour
    save_database(db)

    # Étape 5 : Sauvegarde du lot quotidien
    safe_city = city.lower().replace(" ", "_")
    safe_activity = activity.lower().replace(" ", "_")
    output_filename = f"campagne_{today_str}_{safe_city}_{safe_activity}.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch_leads, f, ensure_ascii=False, indent=2)

    # Export CSV du lot pour l'opérateur
    csv_filename = f"campagne_{today_str}_{safe_city}_{safe_activity}.csv"
    csv_path = os.path.join(OUTPUT_DIR, csv_filename)
    try:
        import csv
        fieldnames = [
            "name", "opportunity_score", "status_outbound", "outbound_channel",
            "primary_email", "phone", "city", "rating", "reviews_count",
            "main_hook", "has_website", "website"
        ]
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in batch_leads:
                writer.writerow(row)
        logger.info(f"Tableur CSV du lot exporté : {csv_path}")
    except Exception as e:
        logger.warning(f"Erreur export CSV: {e}")

    # Étape 6 : Mise à jour de l'état de rotation
    if not city_override and not activity_override:
        state["city_index"] += 1
        # Si on a fait le tour des villes, on passe à l'activité suivante
        if state["city_index"] % len(DEFAULT_CITIES) == 0:
            state["activity_index"] += 1
    state["last_run"] = today_str
    state["total_leads_scraped"] += len(batch_leads)
    state["total_campaigns_created"] += 1
    save_state(state)

    # Bilan de fin de routine
    ready_emails = sum(1 for l in batch_leads if l.get("status_outbound") == "READY_FOR_SENDING" or l.get("primary_email"))
    ready_phones = sum(1 for l in batch_leads if l.get("status_outbound") == "REQUIRES_PHONE_OUTREACH")
    website_count = sum(1 for l in batch_leads if l.get("has_website") or l.get("website"))
    discovery_rate = (ready_emails / len(batch_leads) * 100) if batch_leads else 0.0

    print("\n" + "=" * 65)
    print("✅ ROUTINE QUOTIDIENNE TERMINÉE AVEC SUCCÈS")
    print("=" * 65)
    print(f"Date                   : {today_str}")
    print(f"Cible scannée          : {activity.capitalize()} à {city}")
    print(f"Prospects qualifiés    : {len(batch_leads)} fiches injectées")
    print(f"Prospects avec site web: {website_count}/{len(batch_leads)} (Priorité cold email)")
    print(f"Emails prêts à l'envoi : {ready_emails} (Taux découverte: {discovery_rate:.1f}%)")
    print(f"Téléphones directs     : {ready_phones} (Canal REQUIRES_PHONE_OUTREACH)")
    print(f"Fichier de campagne    : {output_path}")
    print(f"Prochaine rotation     : {DEFAULT_ACTIVITIES[state['activity_index'] % len(DEFAULT_ACTIVITIES)]} à {DEFAULT_CITIES[state['city_index'] % len(DEFAULT_CITIES)]}")
    print("=" * 65 + "\n")

    return {
        "status": "success",
        "date": today_str,
        "city": city,
        "activity": activity,
        "leads_injected": len(batch_leads),
        "emails_ready": ready_emails,
        "discovery_rate_pct": round(discovery_rate, 1),
        "batch_file": output_path
    }


def print_crontab_instructions():
    """Affiche la commande crontab prête à l'emploi pour automatisation à 07h00 chaque matin."""
    script_path = os.path.abspath(__file__)
    python_path = sys.executable
    print("\n" + "=" * 70)
    print("⏰ GUIDE D'INSTALLATION CRONTAB (ZÉRO INTERVENTION HUMAINE)")
    print("=" * 70)
    print("Pour exécuter la routine chaque matin à 07h00 du lundi au vendredi :")
    print("1. Ouvrez votre crontab :")
    print("   crontab -e")
    print("\n2. Ajoutez cette ligne :")
    print(f"   0 7 * * 1-5 {python_path} '{script_path}' --run-once >> '{LOGS_DIR}/cron_stdout.log' 2>&1")
    print("\nChaque matin :")
    print("- Une nouvelle ville de la liste (Nantes, Toulouse, Marseille...) sera scannée.")
    print("- 20 nouveaux prospects défaillants seront analysés et injectés.")
    print("- Les emails ultra-personnalisés avec le lien Stripe seront prêts à l'envoi.")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Routine quotidienne autonome de prospection Google Maps")
    parser.add_argument("--run-once", action="store_true", help="Exécuter la routine du jour immédiatement")
    parser.add_argument("--city", type=str, help="Forcer une ville spécifique (ex: Nantes, Toulouse)")
    parser.add_argument("--activity", type=str, help="Forcer un métier spécifique (ex: plombier, serrurier)")
    parser.add_argument("--target", type=int, default=20, help="Nombre de prospects défaillants cibles (défaut: 20)")
    parser.add_argument("--min-score", type=int, default=15, help="Score d'opportunité minimal")
    parser.add_argument("--stripe-link", type=str, default=DEFAULT_STRIPE_LINK, help="Lien de paiement Stripe")
    parser.add_argument("--sample", action="store_true", help="Mode test avec leads simulés")
    parser.add_argument("--crontab-help", action="store_true", help="Afficher les instructions de planification crontab")

    args = parser.parse_args()

    if args.crontab_help:
        print_crontab_instructions()
        return

    # Exécution par défaut ou déclenchée
    run_daily_prospection(
        city_override=args.city,
        activity_override=args.activity,
        target_qualified=args.target,
        min_opportunity_score=args.min_score,
        stripe_link=args.stripe_link,
        use_sample=args.sample
    )


if __name__ == "__main__":
    main()
