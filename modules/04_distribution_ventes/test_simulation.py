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
    print("🎉 TOUS LES TESTS SONT AU VERT ! Le pipeline est 100% prêt.")
    print("==================================================")

if __name__ == "__main__":
    test_pipeline()
