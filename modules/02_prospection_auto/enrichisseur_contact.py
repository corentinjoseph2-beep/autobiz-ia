#!/usr/bin/env python3
"""
=============================================================================
AutoBiz IA — Module 02 : Prospection Automatique
Fichier : enrichisseur_contact.py
Description : Extracteur d'adresses emails professionnelles et de données légales
              depuis les sites web d'artisans/commerçants (0 € d'outils payants).
              Crawl la page d'accueil, la page contact et les mentions légales.
=============================================================================
"""

import argparse
import concurrent.futures
import json
import logging
import os
import re
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
import urllib.request
import ssl

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("EnrichisseurContact")

# Regex email RFC-like
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Regex mentions légales : SIREN / SIRET
SIRET_REGEX = re.compile(r'\b\d{3}[\s\.]?\d{3}[\s\.]?\d{3}[\s\.]?\d{5}\b|\b\d{14}\b')
SIREN_REGEX = re.compile(r'\b\d{3}[\s\.]?\d{3}[\s\.]?\d{3}\b')

# Domaines et faux-positifs à exclure obligatoirement
BLACKLIST_DOMAINS = {
    "example.com", "domain.com", "votredomaine.fr", "wixpress.com",
    "sentry.io", "wordpress.org", "wix.com", "schema.org", "googleapis.com",
    "cloudflare.com", "bootstrap.com", "gravatar.com", "local.host",
    "prestashop.com", "shopify.com", "google.com", "facebook.com"
}

BLACKLIST_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js",
    ".woff", ".woff2", ".ttf", ".eot", ".ico", ".mp4", ".pdf"
)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


def sanitize_url(raw_url: str) -> Optional[str]:
    """Nettoie et valide l'URL du site web."""
    if not raw_url:
        return None
    url = raw_url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url


def is_valid_email(email: str) -> bool:
    """Vérifie si un email extrait n'est pas un fichier ou un placeholder."""
    email_clean = email.lower().strip()
    if any(email_clean.endswith(ext) for ext in BLACKLIST_EXTENSIONS):
        return False
    domain = email_clean.split("@")[-1]
    if domain in BLACKLIST_DOMAINS:
        return False
    if "example" in email_clean or "votre-nom" in email_clean:
        return False
    return True


def fetch_page_content(url: str, timeout: int = 7) -> Optional[str]:
    """Récupère le contenu HTML d'une page avec gestion des erreurs SSL et timeouts."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "text/plain" not in content_type:
                return None
            html_bytes = response.read(300_000)  # Limite à 300 Ko pour rapidité
            return html_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.debug(f"Échec accès {url}: {e}")
        return None


def extract_emails_from_html(html: str) -> Set[str]:
    """Extrait les emails depuis le HTML (liens mailto + texte brut)."""
    found: Set[str] = set()

    # 1. Liens mailto
    mailto_matches = re.findall(r'href=["\']mailto:([^"?\'>\s]+)', html, re.IGNORECASE)
    for m in mailto_matches:
        cand = m.split("?")[0].strip()
        if EMAIL_REGEX.match(cand) and is_valid_email(cand):
            found.add(cand.lower())

    # 2. Recherche générale regex
    # Remplacement des entités courantes pour éviter les masquages simples
    cleaned_html = html.replace("[at]", "@").replace("[arobase]", "@").replace("(at)", "@")
    text_matches = EMAIL_REGEX.findall(cleaned_html)
    for cand in text_matches:
        if is_valid_email(cand):
            found.add(cand.lower())

    return found


def extract_manager_and_siret(html: str) -> Dict[str, Optional[str]]:
    """Tente de repérer le gérant et le numéro SIREN/SIRET dans les mentions légales."""
    info = {"siret": None, "siren": None, "dirigeant": None}

    # SIRET
    siret_match = SIRET_REGEX.search(html)
    if siret_match:
        info["siret"] = re.sub(r'[\s\.]', '', siret_match.group(0))

    # SIREN
    siren_match = SIREN_REGEX.search(html)
    if siren_match and not info["siret"]:
        info["siren"] = re.sub(r'[\s\.]', '', siren_match.group(0))

    # Dirigeant / Gérant
    dir_match = re.search(r'(?:Directeur de la publication|Responsable de la publication|Gérant|Directeur)\s*[:\-]\s*([A-Za-zÀ-ÿ\s]{3,35})', html, re.IGNORECASE)
    if dir_match:
        cand_name = dir_match.group(1).strip()
        # Élimination des bruits HTML
        cand_name = re.sub(r'<[^>]+>', '', cand_name).split('\n')[0].strip()
        if len(cand_name) > 3 and not cand_name.lower().startswith("sas") and not cand_name.lower().startswith("sarl"):
            info["dirigeant"] = cand_name

    return info


def find_subpage_links(base_url: str, html: str) -> List[str]:
    """Détecte les pages /contact et /mentions-legales."""
    keywords = ["contact", "mentions-legales", "mentions_legales", "mentions", "legal", "a-propos", "coordonnees"]
    found_urls = []

    hrefs = re.findall(r'href=["\']([^"\'>#\s]+)["\']', html, re.IGNORECASE)
    parsed_base = urllib.parse.urlparse(base_url)

    for href in hrefs:
        lower = href.lower()
        if any(kw in lower for kw in keywords):
            full_url = urllib.parse.urljoin(base_url, href)
            parsed = urllib.parse.urlparse(full_url)
            # Rester sur le même domaine
            if parsed.netloc == parsed_base.netloc and full_url not in found_urls and full_url != base_url:
                found_urls.append(full_url)

    # Prioriser mentions-legales et contact
    found_urls.sort(key=lambda u: (0 if "contact" in u.lower() else (1 if "mention" in u.lower() else 2)))
    return found_urls[:3]


def enrich_single_lead(lead: Dict[str, Any]) -> Dict[str, Any]:
    """Enrichit un lead avec l'email extrait, les métadonnées de contact et le canal d'outbound."""
    website = sanitize_url(lead.get("website"))
    emails: Set[str] = set()
    legal_info = {"siret": None, "siren": None, "dirigeant": None}

    if website:
        # 1. Scraping page d'accueil
        home_html = fetch_page_content(website)
        if home_html:
            emails.update(extract_emails_from_html(home_html))
            legal_info.update(extract_manager_and_siret(home_html))

            # 2. Si pas d'email direct ou pas de dirigeant, on explore les sous-pages stratégiques
            if len(emails) == 0 or not legal_info["dirigeant"]:
                subpages = find_subpage_links(website, home_html)
                for sub_url in subpages:
                    sub_html = fetch_page_content(sub_url)
                    if sub_html:
                        emails.update(extract_emails_from_html(sub_html))
                        sub_legal = extract_manager_and_siret(sub_html)
                        if not legal_info["dirigeant"] and sub_legal["dirigeant"]:
                            legal_info["dirigeant"] = sub_legal["dirigeant"]
                        if not legal_info["siret"] and sub_legal["siret"]:
                            legal_info["siret"] = sub_legal["siret"]

    # Traitement des emails trouvés
    sorted_emails = sorted(list(emails), key=lambda e: (0 if "contact@" in e or "info@" in e else 1))
    primary_email = sorted_emails[0] if sorted_emails else None

    # Détermination du canal optimal
    if primary_email:
        primary_channel = "EMAIL_COLD"
        outbound_status = "READY_TO_SEND"
    elif lead.get("phone"):
        primary_channel = "SMS_OR_CALL"
        outbound_status = "REQUIRES_PHONE_OUTREACH"
    else:
        primary_channel = "MANUAL_LOOKUP"
        outbound_status = "INCOMPLETE_CONTACT"

    lead["emails_found"] = sorted_emails
    lead["primary_email"] = primary_email
    lead["dirigeant"] = legal_info["dirigeant"]
    lead["siret"] = legal_info["siret"]
    lead["siren"] = legal_info["siren"]
    lead["primary_channel"] = primary_channel
    lead["outbound_status"] = outbound_status
    lead["enriched_at"] = datetime.utcnow().isoformat() + "Z"

    return lead


def enrich_leads(leads: List[Dict[str, Any]], max_workers: int = 6) -> List[Dict[str, Any]]:
    """Enrichit une liste de leads en parallèle avec ThreadPoolExecutor."""
    logger.info(f"Démarrage de l'enrichissement pour {len(leads)} leads (Threads: {max_workers})...")
    enriched: List[Dict[str, Any]] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_lead = {executor.submit(enrich_single_lead, lead): lead for lead in leads}
        for future in concurrent.futures.as_completed(future_to_lead):
            try:
                res = future.result()
                enriched.append(res)
                site_flag = "🌐 Site" if res.get("website") else "🚫 Pas de site"
                email_flag = f"📧 {res['primary_email']}" if res.get("primary_email") else "❌ Pas d'email"
                logger.info(f"[{len(enriched)}/{len(leads)}] {res['name']} ({site_flag}) -> {email_flag}")
            except Exception as e:
                logger.error(f"Erreur d'enrichissement sur un lead: {e}")

    return enriched


def main():
    parser = argparse.ArgumentParser(description="Enrichisseur d'emails et coordonnées de contact B2B")
    parser.add_argument("-i", "--input", type=str, default="leads_maps.json", help="Fichier JSON des leads bruts Maps")
    parser.add_argument("-o", "--output", type=str, default="leads_enriched.json", help="Fichier JSON de sortie enrichi")
    parser.add_argument("--workers", type=int, default=6, help="Nombre de requêtes parallèles")
    parser.add_argument("--export-csv", type=str, help="Export optionnel CSV")
    parser.add_argument("--sample", action="store_true", help="Enrichir un échantillon test")

    args = parser.parse_args()

    if args.sample or not os.path.exists(args.input):
        logger.info("Utilisation des données d'exemple pour démonstration...")
        from scraper_google_maps import generate_sample_leads
        raw_leads = generate_sample_leads(activity="Plombier", city="Lyon")
    else:
        with open(args.input, "r", encoding="utf-8") as f:
            raw_leads = json.load(f)

    enriched_leads = enrich_leads(raw_leads, max_workers=args.workers)

    # Sauvegarde JSON
    output_path = os.path.abspath(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_leads, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ {len(enriched_leads)} leads enrichis enregistrés dans : {output_path}")

    # Export CSV si demandé
    if args.export_csv:
        import csv
        fieldnames = [
            "name", "opportunity_score", "primary_channel", "primary_email",
            "phone", "city", "rating", "reviews_count", "website", "main_hook",
            "dirigeant", "siret"
        ]
        with open(args.export_csv, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in enriched_leads:
                writer.writerow(row)
        logger.info(f"Export CSV sauvegardé dans : {args.export_csv}")

    # Statistiques
    with_email = sum(1 for l in enriched_leads if l.get("primary_email"))
    with_phone = sum(1 for l in enriched_leads if l.get("phone"))
    high_urgency = sum(1 for l in enriched_leads if l.get("opportunity_score", 0) >= 30 and l.get("primary_email"))

    print("\n" + "=" * 60)
    print("📊 BILAN DE L'ENRICHISSEMENT DE CONTACT")
    print("=" * 60)
    print(f"Total leads traités                : {len(enriched_leads)}")
    print(f"Emails professionnels trouvés       : {with_email} ({int(with_email/len(enriched_leads)*100) if enriched_leads else 0}%)")
    print(f"Téléphones directs exploitables     : {with_phone}")
    print(f"Cibles prêtes à l'outbound (>= 30) : {high_urgency} prospects ultra-chauds")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
