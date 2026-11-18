#!/usr/bin/env python3
"""
=============================================================================
AutoBiz IA — Module 02 : Prospection Automatique
Fichier : pipeline_prospection.py
Description : Pipeline d'orchestration de bout en bout :
              1. Scraping Google Maps (0 €)
              2. Calcul de l'Opportunity Score
              3. Enrichissement email & mentions légales
              4. Génération des messages d'accroche ultra-personnalisés
=============================================================================
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

from scraper_google_maps import scrape_google_maps_live, generate_sample_leads, export_leads_csv
from enrichisseur_contact import enrich_leads

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("PipelineProspection")


def generate_email_preview(lead: Dict[str, Any], stripe_payment_link: str) -> Dict[str, str]:
    """Génère le texte finalisé de l'email d'accroche personnalisé pour ce prospect."""
    nom = lead.get("name", "votre établissement")
    dirigeant = lead.get("dirigeant")
    ville = lead.get("city", "votre secteur")
    metier = lead.get("category", "artisan").lower()
    faille = lead.get("main_hook", "l'absence d'optimisation de vos avis clients")
    salutation = f"Bonjour M./Mme {dirigeant}" if dirigeant else "Bonjour"

    subject = f"Fiche Google {nom} (remarque rapide)"
    
    body = f"""{salutation},

En regardant les fiches des {metier}s sur Google Maps à {ville}, je suis tombé sur votre établissement {nom}.

Un point précis a attiré mon attention : {faille}.

Voici le diagnostic rapide en 3 constats :
1. Sur smartphone, Google met en avant les 3 premiers résultats locaux. Votre configuration actuelle vous fait perdre entre 25% et 40% des appels au profit de vos confrères directs.
2. Vos avis récents ne bénéficient pas d'une réponse optimisée selon les critères de l'algorithme Google (qui favorise les mots-clés d'intervention dans les réponses).
3. Deux modifications simples dans vos paramètres de fiche permettraient de sécuriser votre position locale dès cette semaine.

J'ai compilé l'audit correctif complet de votre fiche (analyse concurrentielle à {ville}, plan d'action en 7 étapes et modèles de réponses prêts à l'emploi) :

👉 Débloquer votre audit complet et votre plan d'action (49 €) :
{stripe_payment_link}?ref={lead.get('id', 'lead')}

(Rapport généré immédiatement après règlement, garanti satisfait ou remboursé sous 14 jours si vous n'obtenez pas de résultat concret).

Bien cordialement,

Corentin — AutoBiz IA
Observatoire de la Visibilité Locale
P.S. : Si vous ne souhaitez plus recevoir nos analyses locales, répondez simplement "Stop"."""

    return {
        "subject": subject,
        "recipient_email": lead.get("primary_email"),
        "recipient_name": nom,
        "body": body
    }


def run_pipeline(
    query: str,
    max_results: int = 15,
    min_score: int = 25,
    stripe_link: str = "https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201",
    use_sample: bool = False,
    output_file: str = "campagne_outbound.json"
):
    """Exécute l'intégralité du pipeline de prospection."""
    logger.info("🚀 Lancement du Pipeline de Prospection Automatique...")

    # Étape 1 : Scraping ou échantillon
    if use_sample:
        raw_leads = generate_sample_leads(activity="Plombier", city="Lyon")
    else:
        raw_leads = scrape_google_maps_live(query=query, max_results=max_results, headless=True)

    if not raw_leads:
        logger.warning("Aucun prospect extrait. Fin du pipeline.")
        return

    # Étape 2 : Enrichissement des contacts
    enriched_leads = enrich_leads(raw_leads, max_workers=5)

    # Étape 3 : Filtrage et génération des emails d'accroche
    campaign_leads = []
    for lead in enriched_leads:
        # Générer le texte de l'email
        email_preview = generate_email_preview(lead, stripe_link)
        lead["email_preview"] = email_preview

        # Qualification
        is_ready = bool(lead.get("primary_email")) and lead.get("opportunity_score", 0) >= min_score
        lead["ready_for_outbound"] = is_ready
        campaign_leads.append(lead)

    # Tri par score d'opportunité décroissant
    campaign_leads.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)

    # Sauvegarde
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(campaign_leads, f, ensure_ascii=False, indent=2)

    # Rapport de campagne
    ready_count = sum(1 for l in campaign_leads if l.get("ready_for_outbound"))
    logger.info(f"✅ Campagne prête enregistrée dans '{output_file}'.")
    logger.info(f"🔥 {ready_count}/{len(campaign_leads)} prospects qualifiés avec email prêt à l'envoi.")

    return campaign_leads


def main():
    parser = argparse.ArgumentParser(description="Pipeline complet de prospection automatique B2B")
    parser.add_argument("-q", "--query", type=str, default="plombier Lyon", help="Requête de recherche locale")
    parser.add_argument("-m", "--max-results", type=int, default=10, help="Nombre max de fiches")
    parser.add_argument("--min-score", type=int, default=20, help="Score minimum d'opportunité")
    parser.add_argument("--stripe-link", type=str, default="https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201", help="Lien de paiement Stripe")
    parser.add_argument("--sample", action="store_true", help="Utiliser des données de test")
    parser.add_argument("-o", "--output", type=str, default="campagne_outbound.json", help="Fichier de sortie")

    args = parser.parse_args()

    run_pipeline(
        query=args.query,
        max_results=args.max_results,
        min_score=args.min_score,
        stripe_link=args.stripe_link,
        use_sample=args.sample,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
