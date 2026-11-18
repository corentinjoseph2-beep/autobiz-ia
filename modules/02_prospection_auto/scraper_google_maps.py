#!/usr/bin/env python3
"""
=============================================================================
AutoBiz IA — Module 02 : Prospection Automatique
Fichier : scraper_google_maps.py
Description : Scraper gratuit et autonome de fiches Google Maps sans API payante.
              Extrait les établissements, évalue leur score de vulnérabilité
              (Opportunity Score) et génère l'angle d'accroche personnalisé.
=============================================================================
"""

import argparse
import json
import logging
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ScraperGoogleMaps")


def calculate_opportunity_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule l'Opportunity Score (0 à 100) et liste les failles détectées.
    Plus le score est élevé, plus le prospect a un besoin urgent de notre audit.
    """
    score = 0
    weaknesses = []
    hooks = []

    rating = data.get("rating")
    reviews_count = data.get("reviews_count", 0)
    has_website = data.get("has_website", False)
    phone = data.get("phone")

    # 1. Absence de site Web relié à la fiche (+35 pts)
    if not has_website:
        score += 35
        weaknesses.append({
            "code": "AUCUN_SITE_WEB",
            "titre": "Aucun site internet relié à la fiche Google",
            "impact": "Jusqu'à 45% des prospects abandonnent s'ils ne trouvent pas de page de présentation ou de tarifs.",
            "urgence": "Critique"
        })
        hooks.append(f"votre fiche Google ne renvoie vers aucun site internet, ce qui redirige directement vos prospects vers vos concurrents directs à {data.get('city', 'votre secteur')}")

    # 2. Note globale faible ou moyenne
    if rating is not None:
        if rating < 4.0:
            score += 35
            weaknesses.append({
                "code": "NOTE_CRITIQUE",
                "titre": f"Note globale critique ({rating}/5)",
                "impact": "Moins de 15% des utilisateurs contactent un établissement sous la barre de 4 étoiles.",
                "urgence": "Critique"
            })
            hooks.append(f"votre note actuelle de {rating}/5 vous place en dessous de la moyenne locale, ce qui freine immédiatement les nouveaux appels")
        elif rating <= 4.3:
            score += 20
            weaknesses.append({
                "code": "NOTE_MOYENNE",
                "titre": f"Note fragile ({rating}/5)",
                "impact": "Un seul avis 1 étoile supplémentaire peut faire basculer la fiche sous les 4.0.",
                "urgence": "Moyenne"
            })
            hooks.append(f"votre note de {rating}/5 reste très exposée : le moindre avis négatif peut faire chuter votre classement dans les 3 premiers résultats Maps")

    # 3. Volume d'avis insuffisant (< 15 avis)
    if reviews_count < 5:
        score += 25
        weaknesses.append({
            "code": "AVIS_QUASI_INEXISTANTS",
            "titre": f"Volume d'avis insuffisant ({reviews_count} avis)",
            "impact": "Google pénalise le référencement local des fiches avec peu de retours d'expérience récents.",
            "urgence": "Élevée"
        })
        hooks.append(f"avec seulement {reviews_count} avis clients, Google privilégie automatiquement vos confrères plus actifs dans le pack local")
    elif reviews_count < 15:
        score += 15
        weaknesses.append({
            "code": "VOLUME_AVIS_FAIBLE",
            "titre": f"Preuve sociale limitée ({reviews_count} avis)",
            "impact": "Visibilité locale bridée face aux concurrents disposant de plus de 30 avis.",
            "urgence": "Moyenne"
        })
        hooks.append(f"votre volume de {reviews_count} avis limite votre montée dans les premières positions de recherche à {data.get('city', 'votre ville')}")

    # 4. Absence de téléphone renseigné
    if not phone:
        score += 15
        weaknesses.append({
            "code": "TELEPHONE_MANQUANT",
            "titre": "Numéro de téléphone direct non affiché",
            "impact": "Impossibilité pour les utilisateurs mobiles de cliquer pour appeler en urgence.",
            "urgence": "Critique"
        })

    # Plafonner le score à 100
    opportunity_score = min(100, score)

    # Angle d'accroche personnalisé principal
    main_hook = hooks[0] if hooks else "l'optimisation de vos avis clients et du pack local Google Maps"

    return {
        "opportunity_score": opportunity_score,
        "is_qualified_lead": opportunity_score >= 30,
        "weaknesses_count": len(weaknesses),
        "weaknesses": weaknesses,
        "main_hook": main_hook
    }


def parse_place_card(card_element, index: int, default_city: str) -> Optional[Dict[str, Any]]:
    """
    Extrait les données d'une carte d'établissement depuis le flux Google Maps.
    """
    try:
        text = card_element.inner_text()
        if not text or len(text.strip()) < 5:
            return None

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return None

        # Le nom est généralement dans la première ligne
        name = lines[0]
        # Si la 2ème ligne est identique au titre (cas fréquent sur Maps)
        if len(lines) > 1 and lines[1] == name:
            sub_lines = lines[2:]
        else:
            sub_lines = lines[1:]

        # Extraction de la note et du nombre d'avis (ex: 4,1(172) ou 4.5 (24))
        rating = None
        reviews_count = 0
        rating_match = re.search(r'(\d[,\.]\d)\s*\(([\d\s\xa0]+)\)', text)
        if rating_match:
            rating = float(rating_match.group(1).replace(",", "."))
            reviews_count = int(re.sub(r'\D', '', rating_match.group(2)))

        # Extraction du numéro de téléphone français
        phone = None
        phone_match = re.search(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s\.\-]*\d{2}){4}', text)
        if phone_match:
            phone = re.sub(r'\s+', ' ', phone_match.group(0)).strip()

        # Liens hypertextes (Maps + Site Web externe)
        google_maps_url = None
        website_url = None
        links = card_element.locator("a").all()

        for link in links:
            href = link.get_attribute("href") or ""
            if "/maps/place/" in href:
                google_maps_url = href
            elif href.startswith("http") and "google.com" not in href:
                # Élimine les liens internes Google
                website_url = href

        # Détection de la catégorie et de l'adresse
        category = "Professionnel"
        address = None
        for line in sub_lines:
            if "·" in line:
                parts = [p.strip() for p in line.split("·")]
                category = parts[0]
                if len(parts) > 1 and not address:
                    address = parts[1]
                break

        # Extraction / inférence de la ville
        city = default_city
        if address:
            # Recherche code postal ou nom de ville
            cp_match = re.search(r'\b\d{5}\s+([A-Za-zÀ-ÿ\-]+)', address)
            if cp_match:
                city = cp_match.group(1)

        has_website = bool(website_url)

        base_data = {
            "id": f"lead_{index}_{int(time.time())}",
            "name": name,
            "category": category,
            "rating": rating,
            "reviews_count": reviews_count,
            "address": address or "Non précisée",
            "city": city,
            "phone": phone,
            "website": website_url,
            "has_website": has_website,
            "google_maps_url": google_maps_url,
            "scraped_at": datetime.utcnow().isoformat() + "Z"
        }

        # Calcul automatique de vulnérabilité & score
        analysis = calculate_opportunity_score(base_data)
        base_data.update(analysis)

        return base_data

    except Exception as e:
        logger.debug(f"Erreur lors du parsing d'une carte: {e}")
        return None


def scrape_google_maps_live(
    query: str,
    max_results: int = 20,
    headless: bool = True
) -> List[Dict[str, Any]]:
    """
    Scrape en direct Google Maps avec Playwright Headless (0 € de coût API).
    Gère les bandeaux de consentement, le défilement infini et la pagination.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright n'est pas installé. Lancez: pip install playwright && playwright install")
        return []

    leads: List[Dict[str, Any]] = []
    seen_names = set()

    # Déterminer la ville par défaut depuis la requête (ex: "plombier Lyon 3" -> "Lyon")
    city_guess = "Secteur local"
    words = query.split()
    if len(words) > 1:
        city_guess = words[-1].capitalize()

    logger.info(f"Démarrage du scraping Google Maps pour la requête : '{query}' (Max {max_results} cibles)")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        context = browser.new_context(
            locale="fr-FR",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/maps/search/{encoded_query}?hl=fr"

        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(2500)

            # Gestion du bandeau de consentement Google RGPD
            consent_buttons = ["Tout accepter", "Accepter tout", "J'accepte", "I agree", "Accept all"]
            for btn_text in consent_buttons:
                try:
                    btn = page.locator(f'button:has-text("{btn_text}")')
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        logger.info(f"Bandeau de consentement accepté ({btn_text}).")
                        page.wait_for_timeout(2000)
                        break
                except Exception:
                    pass

            # Trouver le conteneur scrollable des résultats
            feed = page.locator('div[role="feed"]')
            if feed.count() == 0:
                logger.warning("Conteneur feed introuvable. Tentative de capture directe des articles.")

            # Boucle de défilement pour charger les établissements
            previous_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 15

            while len(leads) < max_results and scroll_attempts < max_scroll_attempts:
                cards = page.locator('div[role="article"]').all()

                for idx, card in enumerate(cards):
                    if len(leads) >= max_results:
                        break
                    parsed = parse_place_card(card, len(leads) + 1, city_guess)
                    if parsed and parsed["name"] not in seen_names:
                        seen_names.add(parsed["name"])
                        leads.append(parsed)
                        logger.info(
                            f"[{len(leads)}/{max_results}] Détecté : {parsed['name']} | "
                            f"Note: {parsed['rating']}/5 ({parsed['reviews_count']} avis) | "
                            f"Site: {'Oui' if parsed['has_website'] else 'NON ❌'} | "
                            f"Score vulnérabilité: {parsed['opportunity_score']}/100"
                        )

                if len(leads) >= max_results:
                    break

                # Défilement vers le bas
                if feed.count() > 0:
                    feed.evaluate("el => el.scrollBy(0, 1500)")
                else:
                    page.mouse.wheel(0, 1500)

                page.wait_for_timeout(1800)

                # Vérification de fin de liste
                if "Vous avez atteint la fin de la liste" in page.content():
                    logger.info("Fin des résultats atteinte sur Google Maps.")
                    break

                if len(cards) == previous_count:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                    previous_count = len(cards)

        except Exception as e:
            logger.error(f"Erreur durant l'exécution du navigateur : {e}")
        finally:
            browser.close()

    logger.info(f"Scraping terminé. {len(leads)} fiches récupérées avec succès.")
    return leads


def generate_sample_leads(activity: str = "Plombier", city: str = "Lyon") -> List[Dict[str, Any]]:
    """
    Générateur de prospects réalistes pour démonstration et tests hors-ligne immédiats.
    """
    samples = [
        {
            "name": f"{activity} Express {city} Centre",
            "category": activity,
            "rating": 3.8,
            "reviews_count": 11,
            "address": f"14 Rue de la République, 69002 {city}",
            "city": city,
            "phone": "04 78 22 14 09",
            "website": None,
            "has_website": False,
            "google_maps_url": "https://maps.google.com/?cid=sample1"
        },
        {
            "name": f"Artisan {activity} & Fils",
            "category": activity,
            "rating": 4.1,
            "reviews_count": 7,
            "address": f"88 Avenue Jean Jaurès, 69007 {city}",
            "city": city,
            "phone": "06 12 34 56 78",
            "website": "http://artisan-plombier-fils.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample2"
        },
        {
            "name": f"Dépannage 24/7 {city}",
            "category": activity,
            "rating": 3.4,
            "reviews_count": 23,
            "address": f"12 Boulevard des Belges, 69006 {city}",
            "city": city,
            "phone": "07 65 43 21 00",
            "website": None,
            "has_website": False,
            "google_maps_url": "https://maps.google.com/?cid=sample3"
        },
        {
            "name": f"Élite Confort {activity}",
            "category": activity,
            "rating": 4.9,
            "reviews_count": 184,
            "address": f"3 Rue Mercière, 69002 {city}",
            "city": city,
            "phone": "04 72 00 11 22",
            "website": "https://elite-confort.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample4"
        }
    ]

    leads = []
    for idx, sample in enumerate(samples, 1):
        sample["id"] = f"lead_demo_{idx}"
        sample["scraped_at"] = datetime.utcnow().isoformat() + "Z"
        analysis = calculate_opportunity_score(sample)
        sample.update(analysis)
        leads.append(sample)

    return leads


def export_leads_csv(leads: List[Dict[str, Any]], filepath: str):
    """Exporte les leads au format CSV tabulé prêt pour Excel ou Google Sheets."""
    import csv
    if not leads:
        return
    fieldnames = [
        "name", "opportunity_score", "is_qualified_lead", "category",
        "rating", "reviews_count", "city", "phone", "website",
        "has_website", "main_hook", "google_maps_url"
    ]
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for lead in leads:
            writer.writerow(lead)
    logger.info(f"Export CSV enregistré dans : {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Scraper Google Maps gratuit & Détecteur d'opportunités d'audit B2B")
    parser.add_argument("-q", "--query", type=str, help="Requête de recherche (ex: 'plombier Lyon', 'serrurier Bordeaux')")
    parser.add_argument("--activity", type=str, default="plombier", help="Activité cible si requêtes multiples")
    parser.add_argument("--cities", type=str, help="Liste de villes séparées par des virgules (ex: 'Lyon,Marseille,Lille')")
    parser.add_argument("-m", "--max-results", type=int, default=15, help="Nombre max de fiches par recherche")
    parser.add_argument("-o", "--output", type=str, default="leads_maps.json", help="Fichier JSON de sortie")
    parser.add_argument("--export-csv", type=str, help="Chemin d'export CSV optionnel")
    parser.add_argument("--min-score", type=int, default=25, help="Score d'opportunité minimal pour qualification")
    parser.add_argument("--filter-qualified", action="store_true", help="Ne garder que les leads avec opportunité avérée")
    parser.add_argument("--no-headless", action="store_true", help="Afficher le navigateur pendant l'exécution")
    parser.add_argument("--sample", action="store_true", help="Générer des données de test réalistes sans lancer de scraping")

    args = parser.parse_args()

    # Mode démo/sample
    if args.sample:
        logger.info("Génération d'un jeu de données de test...")
        leads = generate_sample_leads(activity=args.activity, city="Lyon")
    elif args.cities:
        city_list = [c.strip() for c in args.cities.split(",") if c.strip()]
        all_leads = []
        for city in city_list:
            full_query = f"{args.activity} {city}"
            city_leads = scrape_google_maps_live(
                query=full_query,
                max_results=args.max_results,
                headless=not args.no_headless
            )
            all_leads.extend(city_leads)
            time.sleep(2)  # Pause anti-blocage
        leads = all_leads
    elif args.query:
        leads = scrape_google_maps_live(
            query=args.query,
            max_results=args.max_results,
            headless=not args.no_headless
        )
    else:
        # Requête par défaut
        default_query = "plombier Lyon"
        logger.info(f"Aucune requête fournie. Utilisation de la requête par défaut : '{default_query}'")
        leads = scrape_google_maps_live(
            query=default_query,
            max_results=args.max_results,
            headless=not args.no_headless
        )

    # Filtrage éventuel
    if args.filter_qualified:
        before = len(leads)
        leads = [l for l in leads if l.get("opportunity_score", 0) >= args.min_score]
        logger.info(f"Filtrage appliqué (Score >= {args.min_score}) : {len(leads)}/{before} leads retenus.")

    # Tri par score d'opportunité décroissant
    leads.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)

    # Sauvegarde JSON
    output_path = os.path.abspath(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ {len(leads)} leads sauvegardés dans : {output_path}")

    # Export CSV si demandé
    if args.export_csv:
        export_leads_csv(leads, os.path.abspath(args.export_csv))

    # Résumé de la session
    high_potential = sum(1 for l in leads if l.get("opportunity_score", 0) >= 50)
    no_site = sum(1 for l in leads if not l.get("has_website"))
    critical_ratings = sum(1 for l in leads if l.get("rating") and l.get("rating") < 4.0)

    print("\n" + "=" * 60)
    print("🎯 BILAN DU SOURCING DE PROSPECTS GOOGLE MAPS")
    print("=" * 60)
    print(f"Total fiches extraites        : {len(leads)}")
    print(f"Haute urgence d'audit (>= 50) : {high_potential} établissements")
    print(f"Sans site web relié           : {no_site} établissements (perte nette de clients)")
    print(f"Note critique (< 4.0/5)       : {critical_ratings} établissements")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
