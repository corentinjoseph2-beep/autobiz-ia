#!/usr/bin/env python3
"""
Script de test & simulation pour le Module 04 (Paiement Stripe & Livraison).
Valide que le flux complet (réception paiement -> extraction -> audit PDF -> email) fonctionne sans erreur.
"""

import sys
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from webhook_listener import process_paid_session
from email_templates import get_delivery_email

def test_pipeline():
    print("==================================================")
    print("🧪 TEST 1 : Rendu du gabarit d'email transactionnel")
    print("==================================================")
    email_data = get_delivery_email(
        customer_name="Dr. Sophie Bernard",
        business_name="Cabinet Dentaire Opéra",
        score=62,
        critical_flaws_count=3,
        download_url="https://autobiz-ia.fr/download/mock-token-xyz",
    )
    assert email_data["subject"] == "🚀 Votre Audit Stratégique Google Business [Cabinet Dentaire Opéra] est prêt !"
    assert "Cabinet Dentaire Opéra" in email_data["html"]
    assert "Cabinet Dentaire Opéra" in email_data["text"]
    assert "62" in email_data["html"]
    print("✅ Gabarits validés avec succès (HTML & Texte).")

    print("\n==================================================")
    print("🧪 TEST 2 : Simulation d'un événement Stripe Checkout")
    print("==================================================")
    mock_session = {
        "id": "cs_test_auto_987654321",
        "object": "checkout.session",
        "amount_total": 4900,
        "currency": "eur",
        "payment_status": "paid",
        "customer_details": {
            "email": "contact@cabinet-opera.fr",
            "name": "Dr. Sophie Bernard",
        },
        "custom_fields": [
            {
                "key": "business_name",
                "type": "text",
                "text": {"value": "Cabinet Dentaire Opéra"},
            },
            {
                "key": "business_address",
                "type": "text",
                "text": {"value": "12 Place de l'Opéra, 75009 Paris"},
            }
        ],
        "client_reference_id": "PROSPECT_DENTISTES_014",
    }

    result = process_paid_session(mock_session)
    print(f"Statut : {result.get('status')}")
    print(f"Client : {result.get('customer_email')}")
    print(f"Entreprise : {result.get('business_name')}")
    print(f"PDF généré : {result.get('pdf_path')}")
    print(f"Livraison Email : {result.get('email_delivery', {}).get('detail')}")

    assert result["status"] == "success"
    assert Path(result["pdf_path"]).exists()
    assert result["email_delivery"]["success"] is True

    print("\n==================================================")
    print("🧪 TEST 3 : Validation de l'endpoint /webhook Flask avec Stripe-Signature")
    print("==================================================")
    import time, hmac, hashlib
    from unittest.mock import patch
    from webhook_listener import app
    import webhook_listener

    test_client = app.test_client()
    dummy_secret = "whsec_test_secret_for_tests_123"
    webhook_payload = json.dumps({
        "id": "evt_test_webhook_123",
        "type": "checkout.session.completed",
        "data": {
            "object": mock_session
        }
    }).encode("utf-8")
    ts = int(time.time())
    sig = hmac.new(dummy_secret.encode(), f"{ts}.".encode() + webhook_payload, hashlib.sha256).hexdigest()
    sig_header = f"t={ts},v1={sig}"

    with patch.object(webhook_listener, "WEBHOOK_SECRET", dummy_secret):
        resp = test_client.post(
            "/webhook",
            data=webhook_payload,
            headers={"Stripe-Signature": sig_header, "Content-Type": "application/json"}
        )
        assert resp.status_code == 200, f"Attendu 200, reçu {resp.status_code}: {resp.data}"
        resp_data = resp.get_json()
        assert resp_data.get("status") == "success"
        print(f"✅ Webhook validé avec succès (HTTP 200, statut: {resp_data.get('status')})")

    print("\n==================================================")
    print("🎉 TOUS LES TESTS SONT AU VERT ! Le pipeline est 100% prêt.")
    print("==================================================")

if __name__ == "__main__":
    test_pipeline()
