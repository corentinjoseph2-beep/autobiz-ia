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

# Import du filtre d'indépendants
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

try:
    from filtre_independants import is_independent_artisan, sanitize_artisan_website
except ImportError:
    # Repli de sécurité si import direct
    def is_independent_artisan(name, web=None): return True, None
    def sanitize_artisan_website(web): return web


def calculate_opportunity_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule l'Opportunity Score (0 à 100) et qualifie le prospect B2B.
    
    Barème révisé (Directive DG - Inversion Priorité Site Web & Ciblage Fort ROI) :
    1. Bonus Site Web (+25 pts si has_website == True) :
       Investissement digital existant, forte valeur perçue et email extractible à 80%+.
       Si aucun site (has_website == False) : score réduit à +10 pts max et fléchage vers
       le canal 'REQUIRES_PHONE_OUTREACH' pour ne pas vampiriser la file cold email.
    2. Note globale fragile (+30 pts) :
       rating < 4.4/5 ou avis négatifs récents non traités.
    3. Volume d'avis insuffisant (+25 pts) :
       reviews_count < 20 face aux concurrents de la zone locale.
    4. Complétude & Attributs (+15 pts) :
       Absence d'attributs clés, photos récentes ou publications.
    """
    score = 0
    weaknesses = []
    hooks = []
    score_breakdown = {}

    rating = data.get("rating")
    if rating is not None:
        try:
            rating = float(rating)
        except (ValueError, TypeError):
            rating = None

    reviews_count = data.get("reviews_count")
    if reviews_count is not None:
        try:
            reviews_count = int(reviews_count)
        except (ValueError, TypeError):
            reviews_count = 0
    else:
        reviews_count = 0

    has_website = bool(data.get("has_website") or data.get("website"))
    phone = data.get("phone")
    city = data.get("city", "votre secteur")

    # 1. Éligibilité Site Web : Inversion de priorité (+25 pts avec site vs +10 pts max sans site)
    if has_website:
        score += 25
        score_breakdown["website_contactability_bonus"] = 25
    else:
        score += 10
        score_breakdown["no_website_outreach_penalty"] = 10
        weaknesses.append({
            "code": "AUCUN_SITE_WEB",
            "titre": "Aucun site internet relié à la fiche Google",
            "impact": "Absence d'email extractible : prospection digitale compromise, appel direct requis.",
            "urgence": "Contact Téléphonique Uniquement"
        })
        hooks.append(f"votre fiche Google ne renvoie vers aucun site internet, ce qui redirige directement vos prospects vers vos concurrents directs à {city}")

    # 2. Note globale fragile (< 4.4/5) ou avis négatifs récents (+30 pts)
    has_fragile_rating = (rating is not None and rating < 4.4)
    has_negative_reviews = bool(data.get("recent_negative_reviews") or data.get("has_negative_reviews"))
    if has_fragile_rating or has_negative_reviews:
        score += 30
        score_breakdown["fragile_rating_or_negative_reviews"] = 30
        if rating is not None and rating < 4.0:
            weaknesses.append({
                "code": "NOTE_CRITIQUE",
                "titre": f"Note globale critique ({rating}/5)",
                "impact": "Moins de 15% des utilisateurs contactent un établissement sous la barre de 4 étoiles.",
                "urgence": "Critique"
            })
            hooks.append(f"votre note actuelle de {rating}/5 vous place en dessous de la moyenne locale, ce qui freine immédiatement les nouveaux appels")
        elif rating is not None and rating < 4.4:
            weaknesses.append({
                "code": "NOTE_FRAGILE",
                "titre": f"Note fragile ({rating}/5)",
                "impact": "Un seul avis 1 étoile supplémentaire peut faire basculer la fiche sous les standards de confiance locaux.",
                "urgence": "Élevée"
            })
            hooks.append(f"votre note de {rating}/5 reste très exposée : le moindre avis négatif peut faire chuter votre classement dans les 3 premiers résultats Maps à {city}")
        else:
            weaknesses.append({
                "code": "AVIS_NEGATIFS_RECENTS",
                "titre": "Avis négatifs récents non traités",
                "impact": "Les avis négatifs récents sans réponse professionnelle pénalisent directement la conversion.",
                "urgence": "Moyenne"
            })
            hooks.append(f"des avis récents non optimisés sur votre fiche Google freinent la confiance des prospects à {city}")

    # 3. Volume d'avis insuffisant (< 20 avis face aux concurrents de la zone) (+25 pts)
    if reviews_count < 20:
        score += 25
        score_breakdown["low_reviews_count"] = 25
        if reviews_count < 5:
            weaknesses.append({
                "code": "AVIS_QUASI_INEXISTANTS",
                "titre": f"Volume d'avis insuffisant ({reviews_count} avis)",
                "impact": "Google pénalise le référencement local des fiches avec peu de retours d'expérience récents.",
                "urgence": "Élevée"
            })
            hooks.append(f"avec seulement {reviews_count} avis clients, Google privilégie automatiquement vos confrères plus actifs dans le pack local à {city}")
        else:
            weaknesses.append({
                "code": "VOLUME_AVIS_FAIBLE",
                "titre": f"Preuve sociale limitée ({reviews_count} avis face aux concurrents)",
                "impact": "Visibilité locale bridée face aux concurrents locaux disposant de plus de 20 à 30 avis.",
                "urgence": "Moyenne"
            })
            hooks.append(f"votre volume de {reviews_count} avis limite votre montée dans les premières positions de recherche à {city}")

    # 4. Absence d'attributs clés, photos récentes ou posts (+15 pts)
    missing_attributes = (
        data.get("missing_attributes") is True or
        data.get("missing_key_attributes") is True or
        data.get("has_attributes") is False or
        data.get("has_photos") is False or
        (data.get("photos_count") is not None and data.get("photos_count") < 5) or
        data.get("has_recent_posts") is False or
        data.get("recent_posts") is False or
        data.get("missing_photos_posts") is True or
        not phone or
        data.get("address") in (None, "Non précisée")
    )
    if missing_attributes:
        score += 15
        score_breakdown["missing_attributes_photos"] = 15
        weaknesses.append({
            "code": "ATTRIBUTS_PHOTOS_MANQUANTS",
            "titre": "Fiche incomplète (attributs clés, photos ou posts récents manquants)",
            "impact": "Les fiches sans photos récentes ou attributs détaillés perdent jusqu'à 30% d'engagement client.",
            "urgence": "Moyenne"
        })
        hooks.append(f"votre fiche Google manque d'attributs clés et de photos récentes pour convertir les recherches locales à {city}")

    # Plafonner le score à 100
    opportunity_score = min(100, score)

    # Angle d'accroche personnalisé principal
    main_hook = hooks[0] if hooks else "l'optimisation de vos avis clients et du pack local Google Maps"

    # Canal recommandé et qualification
    is_qualified = opportunity_score >= 30
    outbound_channel = "EMAIL_COLD" if has_website else "REQUIRES_PHONE_OUTREACH"

    return {
        "opportunity_score": opportunity_score,
        "is_qualified_lead": is_qualified,
        "weaknesses_count": len(weaknesses),
        "weaknesses": weaknesses,
        "flaws": weaknesses,  # alias interface contract PROJECT.md
        "score_breakdown": score_breakdown,
        "main_hook": main_hook,
        "has_website": has_website,
        "outbound_channel_recommended": outbound_channel,
        "requires_phone_outreach": not has_website
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

        # Test d'indépendance (rejet franchises / réseaux / annuaires)
        is_indep, reject_reason = is_independent_artisan(name, website_url)

        # Nettoyage URL : si lien annuaire ou intermédiaire, pas de site web propre
        clean_website = sanitize_artisan_website(website_url)
        has_website = bool(clean_website)

        base_data = {
            "id": f"lead_{index}_{int(time.time())}",
            "name": name,
            "category": category,
            "rating": rating,
            "reviews_count": reviews_count,
            "address": address or "Non précisée",
            "city": city,
            "phone": phone,
            "website": clean_website,
            "has_website": has_website,
            "is_independent": is_indep,
            "rejection_reason": reject_reason,
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
    headless: bool = True,
    only_independents: bool = True
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

                        # Filtrage strict des franchises et réseaux
                        if only_independents and not parsed.get("is_independent", True):
                            logger.info(f"🚫 [EXCLUSION FRANCHISE/RÉSEAU] {parsed['name']} ({parsed.get('rejection_reason')})")
                            continue

                        leads.append(parsed)
                        logger.info(
                            f"[{len(leads)}/{max_results}] Détecté (Artisan Indépendant) : {parsed['name']} | "
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
    Générateur de 20 prospects réalistes pour démonstration et tests hors-ligne immédiats.
    Comprend une majorité de fiches avec site web (prioritaires cold email) et des fiches sans site (phone-only).
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
        },
        {
            "name": f"Atelier Rénovation {city}",
            "category": activity,
            "rating": 4.2,
            "reviews_count": 14,
            "address": f"25 Rue Victor Hugo, 69002 {city}",
            "city": city,
            "phone": "04 78 45 12 34",
            "website": "https://atelier-renov-artisan.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample5"
        },
        {
            "name": f"Services Pro {activity}",
            "category": activity,
            "rating": 4.0,
            "reviews_count": 6,
            "address": f"17 Cours Gambetta, 69003 {city}",
            "city": city,
            "phone": "04 72 98 76 54",
            "website": "https://services-pro-habitat.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample6"
        },
        {
            "name": f"SOS {activity} Rapide",
            "category": activity,
            "rating": 3.9,
            "reviews_count": 18,
            "address": f"5 Rue de Marseille, 69007 {city}",
            "city": city,
            "phone": "06 99 88 77 66",
            "website": "https://sos-artisan-depannage.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample7"
        },
        {
            "name": f"Compagnons du Bâtiment {city}",
            "category": activity,
            "rating": 4.3,
            "reviews_count": 9,
            "address": f"42 Quai Saint-Antoine, 69002 {city}",
            "city": city,
            "phone": "04 78 33 22 11",
            "website": "https://compagnons-batiment-local.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample8"
        },
        {
            "name": f"Artisan Martin & Associés",
            "category": activity,
            "rating": 4.2,
            "reviews_count": 15,
            "address": f"9 Rue Garibaldi, 69006 {city}",
            "city": city,
            "phone": "06 11 22 33 44",
            "website": "https://artisan-martin-expert.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample9"
        },
        {
            "name": f"Chrono {activity} Intervention",
            "category": activity,
            "rating": 4.1,
            "reviews_count": 12,
            "address": f"31 Rue de Créqui, 69006 {city}",
            "city": city,
            "phone": "06 22 33 44 55",
            "website": "https://chrono-artisan-service.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample10"
        },
        {
            "name": f"Technique Confort Énergie",
            "category": activity,
            "rating": 4.3,
            "reviews_count": 8,
            "address": f"50 Avenue Maréchal Foch, 69006 {city}",
            "city": city,
            "phone": "04 78 77 88 99",
            "website": "https://technique-confort-energie.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample11"
        },
        {
            "name": f"Région Confort {activity}",
            "category": activity,
            "rating": 4.0,
            "reviews_count": 5,
            "address": f"11 Rue Paul Bert, 69003 {city}",
            "city": city,
            "phone": "06 33 44 55 66",
            "website": "https://region-confort-artisanat.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample12"
        },
        {
            "name": f"Artisans Réunis {city}",
            "category": activity,
            "rating": 4.2,
            "reviews_count": 16,
            "address": f"6 Place Bellecour, 69002 {city}",
            "city": city,
            "phone": "04 78 66 55 44",
            "website": "https://artisans-reunis-habitat.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample13"
        },
        {
            "name": f"Bâtiment Pro Solutions",
            "category": activity,
            "rating": 4.1,
            "reviews_count": 11,
            "address": f"18 Rue Vauban, 69006 {city}",
            "city": city,
            "phone": "06 44 55 66 77",
            "website": "https://batiment-pro-solutions.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample14"
        },
        {
            "name": f"Azur Habitat Dépanne",
            "category": activity,
            "rating": 4.3,
            "reviews_count": 13,
            "address": f"2 Rue Grenette, 69002 {city}",
            "city": city,
            "phone": "06 55 66 77 88",
            "website": "https://azur-habitat-depanne.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample15"
        },
        {
            "name": f"Poly Services Habitat",
            "category": activity,
            "rating": 4.2,
            "reviews_count": 10,
            "address": f"77 Cours Lafayette, 69006 {city}",
            "city": city,
            "phone": "04 78 88 99 00",
            "website": "https://polyservices-pro.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample16"
        },
        {
            "name": f"Urgence Dépannage Express",
            "category": activity,
            "rating": 3.7,
            "reviews_count": 19,
            "address": f"13 Rue Cuvier, 69006 {city}",
            "city": city,
            "phone": "07 11 22 33 44",
            "website": None,
            "has_website": False,
            "google_maps_url": "https://maps.google.com/?cid=sample17"
        },
        {
            "name": f"Artisan Bernard Local",
            "category": activity,
            "rating": 4.3,
            "reviews_count": 17,
            "address": f"8 Rue Duguesclin, 69006 {city}",
            "city": city,
            "phone": "06 77 88 99 00",
            "website": "https://artisan-bernard-direct.fr",
            "has_website": True,
            "google_maps_url": "https://maps.google.com/?cid=sample18"
        },
        {
            "name": f"Dépannage & Travaux Express",
            "category": activity,
            "rating": 3.5,
            "reviews_count": 25,
            "address": f"22 Rue Franklin, 69002 {city}",
            "city": city,
            "phone": "07 22 33 44 55",
            "website": None,
            "has_website": False,
            "google_maps_url": "https://maps.google.com/?cid=sample19"
        },
        {
            "name": f"Allo {activity} Service",
            "category": activity,
            "rating": 4.2,
            "reviews_count": 4,
            "address": f"19 Rue Vendôme, 69003 {city}",
            "city": city,
            "phone": "06 88 99 00 11",
            "website": None,
            "has_website": False,
            "google_maps_url": "https://maps.google.com/?cid=sample20"
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
        "has_website", "outbound_channel_recommended", "main_hook", "google_maps_url"
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
