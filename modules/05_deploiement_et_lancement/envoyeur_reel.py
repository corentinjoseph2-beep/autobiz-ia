#!/usr/bin/env python3
"""
envoyeur_reel.py — Moteur d'expédition réel des emails de prospection (Module 05)
AutoBiz IA — Déploiement Cloud & Lancement Réel

Fonctionnalités :
- Envoi réel ultra-sécurisé vers les prospects du Batch 1 (15 prospects ciblés).
- Support des canaux : SMTP (Gmail app password, OVH, Brevo, Mailjet) ou API Resend.
- Mode simulation et prévisualisation (--dry-run).
- Mode d'auto-test vers sa propre boîte mail (--test-email mon_email@gmail.com).
- Temporisation aléatoire anti-spam entre chaque envoi (45 à 90 secondes par défaut).
- Protection contre les doublons (idempotence via suivi_envois.json).
- Traçabilité et journalisation dans envois_batch_1.log.
"""

import os
import sys
import json
import time
import random
import logging
import argparse
import smtplib
from pathlib import Path
from email.message import EmailMessage
from typing import Dict, Any, List, Optional

import requests
from dotenv import load_dotenv

# Chemins de référence
MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent.parent
MODULE_04_DIR = PROJECT_ROOT / "modules" / "04_distribution_ventes"

# Chargement prioritaire du .env du module 05, puis module 04, puis racine
for env_candidate in [MODULE_DIR / ".env", MODULE_04_DIR / ".env", PROJECT_ROOT / ".env"]:
    if env_candidate.exists():
        load_dotenv(dotenv_path=env_candidate)

# Configuration du logging
LOG_FILE = MODULE_DIR / "envois_batch_1.log"
SUIVI_FILE = MODULE_DIR / "suivi_envois.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("EnvoyeurReel")

# Configuration Stripe et Support
STRIPE_BASE_URL = os.getenv(
    "STRIPE_PAYMENT_LINK_URL",
    "https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201"
)
FROM_EMAIL = os.getenv("FROM_EMAIL", "AutoBiz IA <contact@autobiz-ia.fr>")
SENDER_NAME = os.getenv("SENDER_NAME", "Corentin — AutoBiz IA")


def charger_prospects(batch_file: Path) -> List[Dict[str, Any]]:
    """Charge la liste des prospects depuis le fichier JSON."""
    if not batch_file.exists():
        logger.error(f"Fichier introuvable : {batch_file}")
        sys.exit(1)
    with open(batch_file, "r", encoding="utf-8") as f:
        prospects = json.load(f)
    return prospects


def charger_suivi() -> Dict[str, Any]:
    """Charge l'état d'avancement des envois précédents."""
    if SUIVI_FILE.exists():
        try:
            with open(SUIVI_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def sauvegarder_suivi(suivi: Dict[str, Any]):
    """Sauvegarde l'état d'avancement mis à jour."""
    with open(SUIVI_FILE, "w", encoding="utf-8") as f:
        json.dump(suivi, f, indent=2, ensure_ascii=False)


def construire_email_prospect(prospect: Dict[str, Any]) -> Dict[str, str]:
    """
    Construit l'objet et le corps de l'email Séquence 1 (J+0 Teaser Micro-audit)
    hautement personnalisé selon cold_email_sequences.md.
    """
    nom = prospect.get("business_name", "votre entreprise")
    ville = prospect.get("city", "votre ville")
    metier = prospect.get("metier", "artisan")
    faille = prospect.get("main_weakness", "votre fiche n'est pas optimisée sur Google Maps")
    client_ref = prospect.get("client_reference_id", f"LEAD_{prospect.get('index', 1)}")
    
    # Construction de l'URL Stripe avec tracking du prospect
    stripe_link = f"{STRIPE_BASE_URL}?client_reference_id={client_ref}"

    dirigeant_salutation = ""
    if prospect.get("dirigeant"):
        dirigeant_salutation = f" {prospect['dirigeant']}"

    subject = f"Fiche Google {nom} (remarque rapide)"

    # Corps Plain Text optimisé anti-spam (0 mot marketing blacklisté)
    plain_text = f"""Bonjour{dirigeant_salutation},

En regardant les fiches des {metier}s sur Google Maps à {ville}, je suis tombé sur votre établissement {nom}.

Un point précis a attiré mon attention : {faille}.

Voici le diagnostic rapide en 3 constats :
1. Sur smartphone, Google met en avant les 3 premiers résultats locaux. Votre configuration actuelle vous fait perdre entre 25% et 40% des appels au profit de vos confrères directs.
2. Vos avis récents ne bénéficient pas d'une réponse optimisée selon les critères algorithmiques de Google (qui favorisent les réponses avec mots-clés d'intervention).
3. 2 modifications simples dans vos paramètres de fiche permettraient de sécuriser votre position locale dès cette semaine.

J'ai compilé l'audit correctif complet de votre fiche (analyse concurrentielle locale à {ville}, plan d'action en 7 étapes et modèles de réponses prêts à copier-coller) :

👉 Débloquer votre audit complet et votre plan d'action (49 €) :
{stripe_link}

(Rapport généré immédiatement après règlement, garanti satisfait ou remboursé sous 14 jours si vous n'obtenez pas de résultat concret).

Bien cordialement,

{SENDER_NAME}
Observatoire de la Visibilité Locale
P.S. : Si vous ne souhaitez plus recevoir nos analyses locales, répondez simplement "Stop"."""

    # Version HTML sobre (ressemble à un courriel personnel saisi à la main)
    html = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 15px; line-height: 1.6; color: #1f2937;">
<p>Bonjour{dirigeant_salutation},</p>

<p>En regardant les fiches des {metier}s sur Google Maps à {ville}, je suis tombé sur votre établissement <strong>{nom}</strong>.</p>

<p>Un point précis a attiré mon attention : <em>{faille}</em>.</p>

<p>Voici le diagnostic rapide en 3 constats :</p>
<ol>
  <li>Sur smartphone, Google met en avant les 3 premiers résultats locaux. Votre configuration actuelle vous fait perdre entre 25% et 40% des appels au profit de vos confrères directs.</li>
  <li>Vos avis récents ne bénéficient pas d'une réponse optimisée selon les critères algorithmiques de Google (qui favorisent les réponses avec mots-clés d'intervention).</li>
  <li>2 modifications simples dans vos paramètres de fiche permettraient de sécuriser votre position locale dès cette semaine.</li>
</ol>

<p>J'ai compilé l'audit correctif complet de votre fiche (analyse concurrentielle locale à {ville}, plan d'action en 7 étapes et modèles de réponses prêts à copier-coller) :</p>

<p style="margin: 24px 0;">
  👉 <strong><a href="{stripe_link}" style="color: #2563eb; text-decoration: underline;">Débloquer votre audit complet et votre plan d'action (49 €)</a></strong>
</p>

<p style="font-size: 13px; color: #6b7280;"><em>(Rapport généré immédiatement après règlement, garanti satisfait ou remboursé sous 14 jours si vous n'obtenez pas de résultat concret).</em></p>

<p>Bien cordialement,</p>

<p><strong>{SENDER_NAME}</strong><br>
Observatoire de la Visibilité Locale</p>

<p style="font-size: 12px; color: #9ca3af; margin-top: 30px;">
P.S. : Si vous ne souhaitez plus recevoir nos analyses locales, répondez simplement "Stop".
</p>
</body>
</html>"""

    return {
        "subject": subject,
        "plain_text": plain_text,
        "html": html,
        "stripe_link": stripe_link,
    }


def envoyer_via_smtp(to_email: str, subject: str, plain_text: str, html: str) -> Dict[str, Any]:
    """Expédition sécurisée par serveur SMTP (Gmail App Password, Brevo, OVH)."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_host, smtp_user, smtp_password]):
        return {
            "success": False,
            "error": "Paramètres SMTP incomplets (SMTP_HOST, SMTP_USER, SMTP_PASSWORD manquants dans .env)",
        }

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg.set_content(plain_text)
        msg.add_alternative(html, subtype="html")

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

        return {"success": True, "method": "smtp", "detail": f"Envoyé avec succès à {to_email}"}
    except Exception as e:
        return {"success": False, "method": "smtp", "error": str(e)}


def envoyer_via_resend(to_email: str, subject: str, plain_text: str, html: str) -> Dict[str, Any]:
    """Expédition via l'API REST Resend."""
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        return {"success": False, "error": "RESEND_API_KEY manquante"}

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "text": plain_text,
        "html": html,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code in (200, 201):
            return {"success": True, "method": "resend", "id": resp.json().get("id")}
        return {"success": False, "method": "resend", "error": f"HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"success": False, "method": "resend", "error": str(e)}


def expedier_email(to_email: str, subject: str, plain_text: str, html: str) -> Dict[str, Any]:
    """Sélectionne automatiquement le canal d'envoi disponible (Resend puis SMTP)."""
    if os.getenv("RESEND_API_KEY") and not os.getenv("RESEND_API_KEY", "").startswith("votre_"):
        return envoyer_via_resend(to_email, subject, plain_text, html)
    return envoyer_via_smtp(to_email, subject, plain_text, html)


def compte_a_rebours(secondes: int):
    """Affiche un compte à rebours dynamique dans la console."""
    for s in range(secondes, 0, -1):
        sys.stdout.write(f"\r⏳ Temporisation anti-spam : prochain envoi dans {s:02d}s...")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 65 + "\r")
    sys.stdout.flush()


def executer_envois(
    batch_file: Path,
    mode: str,
    test_email: Optional[str] = None,
    delay_min: int = 45,
    delay_max: int = 90,
):
    """Exécute la boucle d'envoi selon le mode choisi."""
    prospects = charger_prospects(batch_file)
    suivi = charger_suivi()

    logger.info("=" * 70)
    logger.info("🚀 AutoBiz IA — Module 05 : Expéditeur Réel de Prospection")
    logger.info(f"   • Prospects chargés : {len(prospects)}")
    logger.info(f"   • Mode sélectionné  : {mode.upper()}")
    logger.info(f"   • Expéditeur (From) : {FROM_EMAIL}")
    logger.info(f"   • Lien Stripe Base  : {STRIPE_BASE_URL}")
    logger.info("=" * 70)

    # 1. Mode Test Unitaire vers son propre email
    if mode == "test" and test_email:
        logger.info(f"🧪 Envoi d'un email de test unique à : {test_email}")
        prospect_modele = prospects[0]
        email_data = construire_email_prospect(prospect_modele)

        print("\n--- [APERÇU OBJET] ---")
        print(email_data["subject"])
        print("\n--- [APERÇU CORPS (PLAIN TEXT)] ---")
        print(email_data["plain_text"])
        print("-" * 50)

        res = expedier_email(
            to_email=test_email,
            subject=f"[TEST] {email_data['subject']}",
            plain_text=email_data["plain_text"],
            html=email_data["html"],
        )

        if res.get("success"):
            logger.info(f"✅ Email de test envoyé avec succès via {res.get('method')} !")
        else:
            logger.error(f"❌ Échec du test : {res.get('error')}")
        return

    # 2. Mode Dry-Run (Prévisualisation sans envoi)
    if mode == "dry-run":
        logger.info("🔍 Mode DRY-RUN activé : affichage des 15 emails prêts à partir...")
        for i, prospect in enumerate(prospects, 1):
            email_data = construire_email_prospect(prospect)
            print(f"\n==================== PROSPECT #{i:02d} / {len(prospects):02d} ====================")
            print(f"🏢 Établissement  : {prospect['business_name']} ({prospect.get('city')})")
            print(f"📧 Destinataire   : {prospect['primary_email']}")
            print(f"⭐ Note / Avis    : {prospect.get('rating')}/5 ({prospect.get('reviews_count')} avis)")
            print(f"🔗 Réf Prospect   : {prospect.get('client_reference_id')}")
            print(f"✉️ Objet          : {email_data['subject']}")
            print(f"💳 Lien Stripe    : {email_data['stripe_link']}")
            print("----------------- Extrait Message -----------------")
            lignes = email_data["plain_text"].split("\n")
            print("\n".join(lignes[:9]) + "\n[... suite du message ...]")
        
        logger.info("\n✅ Simulation DRY-RUN terminée avec succès. Aucun email réel n'a été émis.")
        logger.info("Pour lancer les envois réels : python3 envoyeur_reel.py --live")
        return

    # 3. Mode Live (Envoi réel)
    if mode == "live":
        print("\n" + "⚠️ " * 15)
        print("ATTENTION : VOUS ÊTES SUR LE POINT DE DÉCLENCHER LES ENVOIS RÉELS AUX PROSPECTS.")
        print(f"Nombre de cibles : {len(prospects)}")
        print(f"Délai aléatoire anti-spam : entre {delay_min}s et {delay_max}s entre chaque email.")
        print("⚠️ " * 15 + "\n")

        confirmation = input("Tapez 'OUI' pour confirmer l'expédition réelle : ").strip()
        if confirmation != "OUI":
            logger.warning("Envoi annulé par l'opérateur.")
            return

        total_envoyes = 0
        total_deja_faits = 0
        total_erreurs = 0

        for i, prospect in enumerate(prospects, 1):
            client_ref = prospect["client_reference_id"]
            to_email = prospect["primary_email"]
            nom = prospect["business_name"]

            # Vérification si déjà envoyé
            if client_ref in suivi and suivi[client_ref].get("status") == "sent":
                logger.info(f"⏩ Prospect #{i:02d} ({nom} <{to_email}>) déjà contacté le {suivi[client_ref].get('sent_at')}. Ignoré.")
                total_deja_faits += 1
                continue

            email_data = construire_email_prospect(prospect)
            logger.info(f"📤 [{i}/{len(prospects)}] Expédition vers {nom} <{to_email}>...")

            res = expedier_email(
                to_email=to_email,
                subject=email_data["subject"],
                plain_text=email_data["plain_text"],
                html=email_data["html"],
            )

            horodatage = time.strftime("%Y-%m-%d %H:%M:%S")

            if res.get("success"):
                logger.info(f"✅ Envoyé avec succès ({res.get('method')}) à {to_email}")
                suivi[client_ref] = {
                    "business_name": nom,
                    "email": to_email,
                    "city": prospect.get("city"),
                    "status": "sent",
                    "sent_at": horodatage,
                    "method": res.get("method"),
                    "stripe_link": email_data["stripe_link"],
                }
                sauvegarder_suivi(suivi)
                total_envoyes += 1

                # Temporisation anti-spam si ce n'est pas le dernier prospect
                if i < len(prospects):
                    pause = random.randint(delay_min, delay_max)
                    compte_a_rebours(pause)
            else:
                logger.error(f"❌ Échec pour {nom} ({to_email}) : {res.get('error')}")
                suivi[client_ref] = {
                    "business_name": nom,
                    "email": to_email,
                    "city": prospect.get("city"),
                    "status": "failed",
                    "failed_at": horodatage,
                    "error": res.get("error"),
                }
                sauvegarder_suivi(suivi)
                total_erreurs += 1

        logger.info("\n" + "=" * 60)
        logger.info("🏁 BILAN DE LA CAMPAGNE BATCH 1 :")
        logger.info(f"   • Nouveaux emails envoyés : {total_envoyes}")
        logger.info(f"   • Déjà envoyés (ignorés)  : {total_deja_faits}")
        logger.info(f"   • Erreurs rencontrées     : {total_erreurs}")
        logger.info(f"   • Journalisation écrite   : {LOG_FILE}")
        logger.info(f"   • État de suivi mis à jour : {SUIVI_FILE}")
        logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoBiz IA — Expéditeur Réel Batch 1")
    parser.add_argument(
        "--batch",
        type=Path,
        default=MODULE_DIR / "prospects_batch_1.json",
        help="Chemin vers le fichier JSON des prospects",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prévisualise les emails et les liens Stripe sans aucun envoi réel",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Déclenche l'envoi réel aux prospects avec confirmation",
    )
    parser.add_argument(
        "--test-email",
        type=str,
        default=None,
        help="Envoie un email de test unique à l'adresse spécifiée",
    )
    parser.add_argument(
        "--delay-min",
        type=int,
        default=45,
        help="Délai anti-spam minimum en secondes entre chaque envoi (défaut: 45)",
    )
    parser.add_argument(
        "--delay-max",
        type=int,
        default=90,
        help="Délai anti-spam maximum en secondes entre chaque envoi (défaut: 90)",
    )

    args = parser.parse_args()

    if args.test_email:
        executer_envois(args.batch, mode="test", test_email=args.test_email)
    elif args.live:
        executer_envois(
            args.batch,
            mode="live",
            delay_min=args.delay_min,
            delay_max=args.delay_max,
        )
    else:
        # Par défaut : mode sécurisé dry-run
        executer_envois(args.batch, mode="dry-run")
