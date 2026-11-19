#!/usr/bin/env python3
"""
Serveur Webhook de Distribution & Vente — OptiLocal (Module 04).
Écoute l'événement Stripe `checkout.session.completed`, déclenche la génération
automatique de l'audit PDF (Module 03), et expédie le rapport par email au client.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify
import stripe
from dotenv import load_dotenv

# Ajout du dossier courant au sys.path pour les imports locaux
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from email_sender import send_delivery_email

# Chargement de la configuration
env_file = CURRENT_DIR / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(CURRENT_DIR / "webhook_events.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("WebhookListener")

# Initialisation Flask
app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


def get_audit_generator_function():
    """
    Tente de charger dynamiquement le générateur d'audit officiel du Module 03 via importlib.
    Retourne la fonction callable ou None.
    """
    try:
        import importlib.util
        module_path = PROJECT_ROOT / "modules" / "03_moteur_audit_ia" / "generateur_audit.py"
        if module_path.exists():
            spec = importlib.util.spec_from_file_location("generateur_audit", str(module_path))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "generer_audit"):
                    return getattr(mod, "generer_audit")
                if hasattr(mod, "generer_audit_pdf"):
                    return getattr(mod, "generer_audit_pdf")
    except Exception as e:
        logger.warning(f"Impossible de charger le module 03 : {e}")

    return None


def get_invoice_generator_function():
    """
    Tente de charger dynamiquement le générateur de factures officielles du Module 07 via importlib.
    Retourne la fonction callable ou None.
    """
    try:
        import importlib.util
        module_path = PROJECT_ROOT / "modules" / "07_comptabilite_et_tresorerie" / "generateur_facture.py"
        if module_path.exists():
            spec = importlib.util.spec_from_file_location("generateur_facture", str(module_path))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "traiter_webhook_stripe_event"):
                    return getattr(mod, "traiter_webhook_stripe_event")
    except Exception as e:
        logger.warning(f"Impossible de charger le module 07 (Facturation) : {e}")

    return None


def generate_fallback_pdf(business_name: str, client_email: str, score: int = 48) -> str:
    """
    Générateur autonome sécurisé : produit un rapport complet et dense de 4 pages
    via le moteur autonome ReportLab. Élimine définitivement le risque de page blanche sur Render.
    """
    try:
        from generateur_audit import generate_autonomous_pdf
    except ImportError:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / "modules" / "03_moteur_audit_ia"))
        from generateur_audit import generate_autonomous_pdf

    audits_dir = CURRENT_DIR / "generated_audits"
    audits_dir.mkdir(parents=True, exist_ok=True)
    
    safe_slug = "".join(c if c.isalnum() else "_" for c in (business_name or "etablissement")).strip("_")[:50] or "etablissement"
    pdf_filename = f"Audit_Visibilite_{safe_slug}.pdf"
    pdf_path = audits_dir / pdf_filename

    logger.info(f"Génération du rapport autonome ReportLab pour '{business_name}'...")
    res_path = generate_autonomous_pdf(
        business_name=business_name or "Votre Établissement",
        client_email=client_email or "",
        audit_data=None,
        score=score,
        output_path=str(pdf_path),
    )
    logger.info(f"Rapport d'audit autonome généré avec succès : {res_path}")
    return str(res_path)


def process_paid_session(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Traite la session de paiement réussie :
    1. Extrait les coordonnées du client et de son entreprise.
    2. Génère le rapport d'audit (Module 03 ou Fallback).
    3. Envoie l'email avec la pièce jointe.
    """
    customer_details = session.get("customer_details") or {}
    customer_email = customer_details.get("email") or session.get("customer_email")
    customer_name = customer_details.get("name") or "Client"
    
    # Extraction du nom d'établissement et de l'adresse depuis les custom_fields du Payment Link
    business_name = None
    business_address = None
    custom_fields = session.get("custom_fields") or []
    for field in custom_fields:
        key = field.get("key")
        val = field.get("text", {}).get("value")
        if key in ("business_name", "nom_etablissement", "etablissement"):
            business_name = val
        elif key in ("business_address", "adresse_etablissement", "adresse", "address"):
            business_address = val
        elif field.get("type") == "text" and not business_name:
            business_name = val

    # Extraction de l'adresse de facturation si présente
    if not business_address and customer_details.get("address"):
        addr = customer_details.get("address")
        parts = [addr.get("line1"), addr.get("postal_code"), addr.get("city")]
        business_address = ", ".join(p for p in parts if p)

    # Fallback si absent des custom_fields : vérifie les métadonnées ou le nom du client
    metadata = session.get("metadata") or {}
    if not business_name:
        business_name = metadata.get("business_name") or metadata.get("etablissement")
    if not business_name:
        business_name = f"Établissement de {customer_name}"

    amount_total = session.get("amount_total", 4900) / 100.0
    currency = (session.get("currency") or "eur").upper()
    client_ref = session.get("client_reference_id") or "DIRECT"

    logger.info("=" * 60)
    logger.info("💰 NOUVELLE VENTE CONFIRMÉE !")
    logger.info(f"   • Montant      : {amount_total:.2f} {currency}")
    logger.info(f"   • Client       : {customer_name} <{customer_email}>")
    logger.info(f"   • Entreprise   : {business_name}")
    logger.info(f"   • Adresse      : {business_address or 'Non spécifiée'}")
    logger.info(f"   • Réf prospect : {client_ref}")
    logger.info("=" * 60)

    if not customer_email:
        err = "Impossible de livrer : aucun email client trouvé dans la session Stripe."
        logger.error(err)
        return {"status": "error", "message": err}

    # 1. Génération du Rapport d'Audit
    audit_fn = get_audit_generator_function()
    pdf_path = None
    score = 58  # Valeur standard ou calculée

    if audit_fn:
        try:
            logger.info("Appel du générateur d'audit officiel (Module 03)...")
            audit_result = audit_fn({
                "business_name": business_name,
                "address": business_address or "",
                "email": customer_email,
                "client_reference_id": client_ref,
            })
            if isinstance(audit_result, (tuple, list)):
                # Module 03 retourne (html_path, pdf_path)
                pdf_candidate = audit_result[1] if len(audit_result) > 1 else audit_result[0]
            else:
                pdf_candidate = audit_result
            
            if pdf_candidate:
                pdf_path = str(pdf_candidate)
                logger.info(f"✅ Rapport PDF produit par le Module 03 : {pdf_path}")
        except Exception as e:
            logger.error(f"Erreur du générateur d'audit Module 03 : {e}. Bascule sur le fallback.")
    
    if not pdf_path or not os.path.exists(pdf_path):
        logger.info("Utilisation du moteur de secours pour générer le PDF...")
        pdf_path = generate_fallback_pdf(business_name, customer_email, score=score)

    # 2. Envoi automatique du courriel de livraison
    logger.info(f"Expédition du courriel de livraison à {customer_email}...")
    email_result = send_delivery_email(
        to_email=customer_email,
        customer_name=customer_name,
        business_name=business_name,
        pdf_path=pdf_path,
        score=score,
    )
    logger.info(f"Résultat envoi email : {email_result.get('detail')}")

    # 3. Émission automatique de la Facture Légale B2B & Registre Recettes (Module 07)
    invoice_fn = get_invoice_generator_function()
    invoice_result = None
    if invoice_fn:
        try:
            logger.info("Émission de la facture conforme via le Module 07 (Comptabilité)...")
            invoice_result = invoice_fn(session)
            logger.info(f"✅ Facture émise : {invoice_result.get('numero_facture')} (PDF: {invoice_result.get('pdf_path')})")
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la facture : {e}")

    return {
        "status": "success",
        "customer_email": customer_email,
        "business_name": business_name,
        "pdf_path": pdf_path,
        "email_delivery": email_result,
        "invoice": invoice_result,
    }


@app.route("/health", methods=["GET"])
def health_check():
    """Vérification de l'état du serveur pour monitoring ou ping."""
    return jsonify({
        "status": "healthy",
        "service": "OptiLocal Webhook Listener",
        "module": "04_distribution_ventes",
        "stripe_configured": bool(stripe.api_key and not stripe.api_key.startswith("sk_test_votre")),
        "webhook_secret_set": bool(WEBHOOK_SECRET and not WEBHOOK_SECRET.startswith("whsec_votre")),
    }), 200


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """Endpoint principal de réception des webhooks Stripe."""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    event = None

    # Vérification cryptographique si le secret est configuré
    if WEBHOOK_SECRET and not WEBHOOK_SECRET.startswith("whsec_votre"):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Payload Stripe invalide : {e}")
            return jsonify({"error": "Invalid payload"}), 400
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Signature Stripe invalide : {e}")
            return jsonify({"error": "Invalid signature"}), 400
    else:
        # Mode développement / simulation sans validation de signature stricte
        try:
            event = json.loads(payload.decode("utf-8"))
        except Exception as e:
            logger.error(f"Impossible de parser le JSON en mode dev : {e}")
            return jsonify({"error": "Invalid JSON"}), 400

    event_type = event.get("type")
    logger.info(f"Événement Stripe reçu : {event_type}")

    if event_type == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        result = process_paid_session(session)
        return jsonify(result), 200

    # Autres événements Stripe acquittés silencieusement
    return jsonify({"status": "ignored", "type": event_type}), 200


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OptiLocal Webhook Listener")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 5000)))
    parser.add_argument("--simulate", action="store_true", help="Simule un achat immédiatement sans lancer le serveur")
    args = parser.parse_args()

    if args.simulate:
        logger.info("🧪 Lancement d'une simulation locale d'achat Stripe...")
        dummy_session = {
            "id": "cs_test_mock_123456",
            "amount_total": 4900,
            "currency": "eur",
            "customer_details": {
                "email": "dr.martin.dentiste@gmail.com",
                "name": "Dr. Jean Martin",
            },
            "custom_fields": [
                {
                    "key": "business_name",
                    "type": "text",
                    "text": {"value": "Cabinet Dentaire Dr Martin"},
                }
            ],
            "client_reference_id": "PROSPECT_PARIS_042",
        }
        res = process_paid_session(dummy_session)
        print("\nRésultat de la simulation :")
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    port = args.port
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(f"🚀 Serveur Webhook prêt et en écoute sur http://{host}:{port}/webhook")
    app.run(host=host, port=port, debug=False)
