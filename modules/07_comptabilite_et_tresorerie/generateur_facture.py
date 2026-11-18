#!/usr/bin/env python3
"""
Moteur de Facturation Légale Automatique — AutoBiz IA (Module 07).
Génère une facture PDF A4 conforme aux obligations B2B françaises pour chaque vente Stripe (49 €)
et met à jour le Livre des Recettes (JSON + CSV) de manière séquentielle et inaltérable.
"""

import os
import sys
import json
import csv
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from jinja2 import Environment, FileSystemLoader

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
FACTURES_DIR = CURRENT_DIR / "factures_emises"
CONFIG_FILE = CURRENT_DIR / "config_comptable.json"
REGISTRE_JSON = CURRENT_DIR / "registre_recettes.json"
LIVRE_CSV = CURRENT_DIR / "livre_recettes.csv"

FACTURES_DIR.mkdir(parents=True, exist_ok=True)


def charger_config() -> dict:
    """Charge les paramètres d'émission et fiscaux."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Configuration introuvable: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder_config(config: dict) -> None:
    """Met à jour la configuration (notamment le pointeur de séquence)."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def charger_registre() -> list:
    """Charge l'historique complet des recettes enregistrées."""
    if not REGISTRE_JSON.exists():
        return []
    try:
        with open(REGISTRE_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def trouver_navigateur_chrome() -> Optional[str]:
    """Détecte l'exécutable Chrome/Chromium disponible sur le système."""
    chemins_possibles = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
    ]
    for chemin in chemins_possibles:
        if chemin and os.path.exists(chemin):
            return chemin
    return None


def convertir_html_en_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Convertit un fichier HTML en PDF via Chrome Headless avec mise en page A4 exacte."""
    chrome_bin = trouver_navigateur_chrome()
    if not chrome_bin:
        print(f"[!] Erreur: Navigateur Chrome introuvable pour {html_path.name}")
        return False

    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        str(html_path.resolve()),
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25)
        return res.returncode == 0 and pdf_path.exists()
    except Exception as e:
        print(f"[!] Erreur lors de la conversion PDF : {e}")
        return False


def obtenir_prochain_numero_facture(config: dict) -> Tuple[str, int]:
    """
    Garantit une numérotation continue et chronologique sans trou.
    Détermine le numéro séquentiel d'après le registre et la configuration.
    """
    registre = charger_registre()
    prefixe = config.get("sequence_facturation", {}).get("prefixe", "FAC-2026-")
    longueur = config.get("sequence_facturation", {}).get("longueur_chiffres", 4)
    prochain_num_cfg = config.get("sequence_facturation", {}).get("prochain_numero", 1)

    max_num_existant = 0
    for r in registre:
        num_str = r.get("numero_facture", "")
        if num_str.startswith(prefixe):
            try:
                val = int(num_str.replace(prefixe, ""))
                if val > max_num_existant:
                    max_num_existant = val
            except ValueError:
                pass

    prochain_seq = max(max_num_existant + 1, prochain_num_cfg)
    numero_facture = f"{prefixe}{str(prochain_seq).zfill(longueur)}"
    return numero_facture, prochain_seq


def initialiser_livre_recettes_si_necessaire() -> None:
    """Crée le header CSV du livre des recettes officiel s'il n'existe pas."""
    if not LIVRE_CSV.exists() or LIVRE_CSV.stat().st_size == 0:
        with open(LIVRE_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                "Date Encaissement",
                "Numéro Facture",
                "Nom Client / Raison Sociale",
                "Nature Prestation",
                "Montant HT (€)",
                "TVA (€)",
                "Montant TTC (€)",
                "Mode Règlement",
                "Réf. Transaction Stripe",
                "Frais Stripe Estimés (€)",
                "Net Encaissé (€)"
            ])


def enregistrer_dans_livre_recettes(recette: dict) -> None:
    """Ajoute une ligne comptable au livre des recettes CSV."""
    initialiser_livre_recettes_si_necessaire()
    with open(LIVRE_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            recette.get("date_paiement", ""),
            recette.get("numero_facture", ""),
            recette.get("client_nom", ""),
            recette.get("designation", ""),
            f"{recette.get('montant_ht', 0.0):.2f}".replace(".", ","),
            f"{recette.get('montant_tva', 0.0):.2f}".replace(".", ","),
            f"{recette.get('montant_ttc', 0.0):.2f}".replace(".", ","),
            recette.get("mode_reglement", "Carte Bancaire"),
            recette.get("reference_stripe", ""),
            f"{recette.get('frais_stripe', 0.0):.2f}".replace(".", ","),
            f"{recette.get('net_encaisse', 0.0):.2f}".replace(".", ",")
        ])


def generer_facture(
    donnees_vente: Dict[str, Any],
    chemin_pdf_cible: Optional[Path] = None,
    mettre_a_jour_registre: bool = True
) -> Dict[str, Any]:
    """
    Génère une facture conforme complète à partir des données de vente.
    Retourne un dictionnaire récapitulatif avec les chemins de fichiers générés.
    """
    config = charger_config()
    emetteur = config.get("emetteur", {})
    fiscalite = config.get("fiscalite", {})
    produit = config.get("produit", {})
    params_fin = config.get("parametres_financiers", {})

    numero_facture, prochain_seq = obtenir_prochain_numero_facture(config)

    maintenant = datetime.now()
    date_emission = donnees_vente.get("date_emission") or maintenant.strftime("%d/%m/%Y")
    date_paiement = donnees_vente.get("date_paiement") or maintenant.strftime("%d/%m/%Y à %H:%M")

    # Calculs financiers
    montant_ttc = float(donnees_vente.get("montant_ttc", produit.get("prix_unitaire_ttc", 49.00)))
    taux_tva = float(fiscalite.get("taux_tva_pourcent", 0.0))

    if taux_tva > 0:
        montant_ht = round(montant_ttc / (1.0 + (taux_tva / 100.0)), 2)
        montant_tva = round(montant_ttc - montant_ht, 2)
    else:
        montant_ht = montant_ttc
        montant_tva = 0.0

    # Calcul des frais Stripe réels / estimés
    frais_pct = float(params_fin.get("frais_stripe_pourcentage", 1.5)) / 100.0
    frais_fixe = float(params_fin.get("frais_stripe_fixe_eur", 0.25))
    frais_stripe = round(donnees_vente.get("frais_stripe") or (montant_ttc * frais_pct + frais_fixe), 2)
    cout_ia = float(params_fin.get("cout_ia_moyen_eur", 0.15))
    net_encaisse = round(montant_ttc - frais_stripe, 2)
    marge_nette = round(net_encaisse - cout_ia, 2)

    reference_stripe = donnees_vente.get("stripe_session_id") or donnees_vente.get("reference_stripe") or f"cs_live_{maintenant.strftime('%Y%m%d%H%M%S')}"

    client_info = {
        "nom_client": donnees_vente.get("client_nom") or donnees_vente.get("customer_name") or "Client Entreprise",
        "email": donnees_vente.get("client_email") or donnees_vente.get("customer_email") or "contact@client.fr",
        "adresse": donnees_vente.get("client_adresse", ""),
        "code_postal": donnees_vente.get("client_cp", ""),
        "ville": donnees_vente.get("client_ville", ""),
        "pays": donnees_vente.get("client_pays", "France"),
        "siret": donnees_vente.get("client_siret", ""),
        "telephone": donnees_vente.get("client_telephone", ""),
        "nom_etablissement": donnees_vente.get("nom_etablissement") or donnees_vente.get("business_name") or "",
    }

    # Préparation du contexte pour le template HTML
    context = {
        "numero_facture": numero_facture,
        "date_emission": date_emission,
        "date_paiement": date_paiement,
        "emetteur": emetteur,
        "client": client_info,
        "produit": produit,
        "fiscalite": fiscalite,
        "reference_stripe": reference_stripe,
        "montant_ht": montant_ht,
        "taux_tva": taux_tva,
        "montant_tva": montant_tva,
        "montant_ttc": montant_ttc,
    }

    # Rendu HTML avec Jinja2
    env = Environment(loader=FileSystemLoader(str(CURRENT_DIR)))
    template = env.get_template("template_facture.html")
    html_content = template.render(**context)

    # Sauvegarde du fichier HTML temporaire et du PDF final
    slug_facture = numero_facture.lower().replace("-", "_")
    html_path = FACTURES_DIR / f"facture_{slug_facture}.html"
    pdf_path = chemin_pdf_cible or (FACTURES_DIR / f"facture_{slug_facture}.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Conversion en PDF
    pdf_cree = convertir_html_en_pdf(html_path, pdf_path)
    if not pdf_cree:
        print(f"[!] Attention : la conversion PDF a échoué. Le fichier HTML est disponible : {html_path}")

    # Enregistrement comptable
    entree_recette = {
        "numero_facture": numero_facture,
        "date_paiement": date_paiement,
        "date_iso": maintenant.isoformat(),
        "client_nom": client_info["nom_client"],
        "client_email": client_info["email"],
        "client_etablissement": client_info["nom_etablissement"],
        "designation": produit.get("designation", "Audit Local SEO"),
        "montant_ht": montant_ht,
        "montant_tva": montant_tva,
        "montant_ttc": montant_ttc,
        "mode_reglement": "Carte Bancaire (Stripe)",
        "reference_stripe": reference_stripe,
        "frais_stripe": frais_stripe,
        "cout_ia": cout_ia,
        "net_encaisse": net_encaisse,
        "marge_nette": marge_nette,
        "fichier_pdf": str(pdf_path) if pdf_path.exists() else None,
        "fichier_html": str(html_path),
    }

    if mettre_a_jour_registre:
        registre = charger_registre()
        registre.append(entree_recette)
        with open(REGISTRE_JSON, "w", encoding="utf-8") as f:
            json.dump(registre, f, indent=2, ensure_ascii=False)

        enregistrer_dans_livre_recettes(entree_recette)

        # Mise à jour de la séquence
        config["sequence_facturation"]["prochain_numero"] = prochain_seq + 1
        sauvegarder_config(config)

    return {
        "success": True,
        "numero_facture": numero_facture,
        "pdf_path": str(pdf_path) if pdf_path.exists() else None,
        "html_path": str(html_path),
        "montant_ttc": montant_ttc,
        "net_encaisse": net_encaisse,
        "frais_stripe": frais_stripe,
        "marge_nette": marge_nette,
        "recette": entree_recette,
    }


def traiter_webhook_stripe_event(session_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fonction passerelle appelée directement lors d'un événement Stripe `checkout.session.completed`.
    Extrait les données client et produit pour émettre immédiatement la facture conforme.
    """
    customer_details = session_event.get("customer_details") or {}
    custom_fields = session_event.get("custom_fields") or []

    # Extraction du nom d'établissement ou custom_fields
    business_name = ""
    for field in custom_fields:
        if field.get("key") == "business_name":
            business_name = field.get("text", {}).get("value", "")

    # Montant payé (en centimes dans Stripe)
    amount_total = session_event.get("amount_total", 4900) / 100.0

    donnees_vente = {
        "client_nom": customer_details.get("name") or "Client Partenaire",
        "client_email": customer_details.get("email") or session_event.get("customer_email") or "client@pro.com",
        "client_adresse": customer_details.get("address", {}).get("line1", ""),
        "client_cp": customer_details.get("address", {}).get("postal_code", ""),
        "client_ville": customer_details.get("address", {}).get("city", ""),
        "client_pays": customer_details.get("address", {}).get("country", "FR"),
        "client_telephone": customer_details.get("phone", ""),
        "nom_etablissement": business_name,
        "montant_ttc": amount_total,
        "stripe_session_id": session_event.get("id", ""),
    }

    return generer_facture(donnees_vente)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Générateur de Factures PDF Conformes B2B (AutoBiz IA)")
    parser.add_argument("--client", default="Boulangerie du Moulin", help="Nom du client ou entreprise")
    parser.add_argument("--email", default="contact@boulangeriedumoulin.fr", help="Email du client")
    parser.add_argument("--etablissement", default="Boulangerie du Moulin (Paris 11e)", help="Établissement audité")
    parser.add_argument("--adresse", default="14 Rue de la Roquette", help="Adresse de facturation")
    parser.add_argument("--ville", default="Paris", help="Ville de facturation")
    parser.add_argument("--cp", default="75011", help="Code postal")
    parser.add_argument("--montant", type=float, default=49.00, help="Montant TTC en euros")
    parser.add_argument("--stripe-id", default=None, help="ID de transaction Stripe")
    parser.add_argument("--no-save", action="store_true", help="Ne pas enregistrer au registre")

    args = parser.parse_args()

    donnees = {
        "client_nom": args.client,
        "client_email": args.email,
        "nom_etablissement": args.etablissement,
        "client_adresse": args.adresse,
        "client_ville": args.ville,
        "client_cp": args.cp,
        "montant_ttc": args.montant,
        "stripe_session_id": args.stripe_id or f"cs_test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    }

    print("📄 Génération de la facture conforme...")
    resultat = generer_facture(donnees, mettre_a_jour_registre=not args.no_save)
    print(f"✅ Facture créée : {resultat['numero_facture']}")
    print(f"   PDF généré    : {resultat['pdf_path']}")
    print(f"   Net perçu     : {resultat['net_encaisse']} € (Frais Stripe: {resultat['frais_stripe']} €)")
