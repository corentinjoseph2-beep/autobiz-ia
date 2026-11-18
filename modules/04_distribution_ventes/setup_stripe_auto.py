#!/usr/bin/env python3
"""
Script d'automatisation de la configuration Stripe pour AutoBiz IA (Module 04).
Crée le produit à 49 €, le tarif, et génère le lien de paiement Stripe Checkout avec
les champs personnalisés requis.
"""

import sys
import os
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(CURRENT_DIR))

import stripe

def configure_stripe(api_key: str):
    stripe.api_key = api_key.strip()

    print("🔌 Connexion à l'API Stripe...")
    try:
        account = stripe.Account.retrieve()
        account_id = getattr(account, "id", "Inconnu")
        biz = getattr(account, "business_profile", None)
        biz_name = getattr(biz, "name", None) if biz else None
        email = getattr(account, "email", None)
        display_name = biz_name or email or account_id
        print(f"✅ Connecté au compte Stripe : {display_name} (ID: {account_id})")
    except Exception as e:
        print(f"❌ Erreur d'authentification Stripe : {e}")
        sys.exit(1)

    print("\n📦 1. Création ou récupération du produit 'Audit Stratégique Google Business'...")
    product = None
    try:
        # Recherche si le produit existe déjà pour éviter les doublons
        existing_products = stripe.Product.list(limit=10, active=True)
        for p in existing_products.data:
            if "Audit" in p.name:
                product = p
                print(f"ℹ️ Produit existant réutilisé : {product.name} (ID: {product.id})")
                break
        
        if not product:
            product = stripe.Product.create(
                name="Audit Complet Google Business Profile & Référencement Local",
                description="Diagnostic stratégique complet, analyse de visibilité locale, benchmark concurrentiel et plan d'action correctif sous 7 jours.",
                tax_code="txcd_20030000",
                metadata={
                    "project": "AutoBiz IA",
                    "module": "04_distribution_ventes",
                    "service": "audit_local_seo",
                },
            )
            print(f"✅ Produit créé : {product.name} (ID: {product.id})")
    except Exception as e:
        print(f"❌ Erreur gestion produit : {e}")
        sys.exit(1)

    print("\n💶 2. Configuration du tarif à 49,00 EUR...")
    price = None
    try:
        prices = stripe.Price.list(product=product.id, active=True, limit=5)
        for pr in prices.data:
            if pr.unit_amount == 4900 and pr.currency == "eur":
                price = pr
                print(f"ℹ️ Tarif existant réutilisé : 49,00 € TTC (ID: {price.id})")
                break

        if not price:
            price = stripe.Price.create(
                product=product.id,
                unit_amount=4900,  # 49,00 € en centimes
                currency="eur",
                metadata={
                    "project": "AutoBiz IA",
                    "tier": "standard",
                },
            )
            print(f"✅ Tarif configuré : 49,00 € TTC (ID: {price.id})")
    except Exception as e:
        print(f"❌ Erreur création tarif : {e}")
        sys.exit(1)

    print("\n🔗 3. Génération du Stripe Payment Link (Lien de paiement hébergé)...")
    try:
        # Recherche d'un lien existant actif
        payment_link = None
        existing_links = stripe.PaymentLink.list(limit=10, active=True)
        for pl in existing_links.data:
            for item in getattr(pl, "line_items", {}).get("data", []):
                if item.get("price", {}).get("id") == price.id:
                    payment_link = pl
                    print(f"ℹ️ Lien de paiement existant réutilisé : {payment_link.url}")
                    break
            if payment_link:
                break

        if not payment_link:
            payment_link = stripe.PaymentLink.create(
                line_items=[
                    {
                        "price": price.id,
                        "quantity": 1,
                    }
                ],
                custom_fields=[
                    {
                        "key": "business_name",
                        "label": {
                            "type": "custom",
                            "custom": "Nom de l'établissement ou lien Google Maps",
                        },
                        "type": "text",
                        "optional": False,
                    }
                ],
                after_completion={
                    "type": "hosted_confirmation",
                    "hosted_confirmation": {
                        "custom_message": "Merci pour votre commande ! Votre audit personnalisé est en cours de génération et vous sera livré par email d'ici 1 minute.",
                    },
                },
                billing_address_collection="auto",
                phone_number_collection={"enabled": True},
                managed_payments={"enabled": False},
                metadata={
                    "project": "AutoBiz IA",
                    "product": "audit_gbp",
                },
            )
            print(f"🎉 NOUVEAU LIEN DE PAIEMENT CRÉÉ AVEC SUCCÈS !")

        print(f"\n=======================================================")
        print(f"👉 LIEN DE PAIEMENT OFFICIEL (À transmettre aux prospects) :")
        print(f"   {payment_link.url}")
        print(f"=======================================================")
    except Exception as e:
        print(f"❌ Erreur création Payment Link : {e}")
        sys.exit(1)

    # 4. Sauvegarde dans le fichier .env
    env_file = CURRENT_DIR / ".env"
    env_content = f"""# ==============================================================================
# Configuration AutoBiz IA — Module 04 : Paiement & Livraison Automatique
# ==============================================================================
STRIPE_SECRET_KEY={stripe.api_key}
STRIPE_PRODUCT_ID={product.id}
STRIPE_PRICE_ID={price.id}
STRIPE_PAYMENT_LINK_URL={payment_link.url}

# Secret de signature Webhook (pour écouter checkout.session.completed)
STRIPE_WEBHOOK_SECRET=

# Configuration Email Expéditeur & Support
FROM_EMAIL=AutoBiz IA <contact@autobiz-ia.fr>
SUPPORT_EMAIL=contact@autobiz-ia.fr

# Serveur local
PORT=5000
HOST=0.0.0.0
DEBUG=true
"""
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    print(f"\n💾 Variables d'environnement sauvegardées dans : {env_file}")

    return {
        "product_id": product.id,
        "price_id": price.id,
        "payment_link_url": payment_link.url,
    }

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else os.getenv("STRIPE_SECRET_KEY")
    if not key:
        print("Usage: python3 setup_stripe_auto.py <STRIPE_SECRET_KEY>")
        sys.exit(1)
    configure_stripe(key)
