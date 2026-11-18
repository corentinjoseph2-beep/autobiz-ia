#!/usr/bin/env python3
"""
generateur_audit.py — Moteur d'Audit & Générateur de Rapports PDF Haute Fidélité
Module 03 : Moteur d'Audit IA

Génère en moins de 15 secondes un rapport d'audit PDF à haute valeur perçue (qualité agence)
pour les fiches Google Business Profile, avec adaptation sectorielle automatique
(BTP/Artisanat vs Commerces de bouche vs Santé/Beauté) et mode batch pour traitement en masse.

Lien Stripe de paiement officiel :
    https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201

Utilisation :
    python3 generateur_audit.py                                 # Audit de test par défaut
    python3 generateur_audit.py --input fiche.json              # Unitaire depuis JSON
    python3 generateur_audit.py --batch prospects.json          # En masse depuis une liste JSON
    python3 generateur_audit.py --batch ./dossier_prospects/    # En masse depuis un dossier de JSONs
    python3 generateur_audit.py --help
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

CURRENT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = CURRENT_DIR / "template_rapport.html"

# Lien Stripe officiel validé
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201"

# Import du moteur d'adaptation sectorielle
try:
    from moteur_sectoriel import adapter_donnees_secteur, detecter_secteur
except ImportError:
    # Fallback si importé depuis un autre répertoire
    sys.path.append(str(CURRENT_DIR))
    from moteur_sectoriel import adapter_donnees_secteur, detecter_secteur


# Données de secours / test par défaut
SAMPLE_DATA = {
    "business_name": "Plomberie & Chauffage Martin Frères",
    "address": "12 Rue de la République, 92100 Boulogne-Billancourt",
    "category": "Plombier chauffagiste / Rénovation sanitaire",
    "rating": 4.1,
    "review_count": 28,
    "response_rate": 14,
}


def _get_metric_color(score: int) -> str:
    """Retourne la couleur hexadécimale associée à un score."""
    if score >= 75:
        return "#16a34a"  # Vert
    elif score >= 50:
        return "#d97706"  # Orange
    return "#dc2626"      # Rouge


def enrichir_donnees(data: dict) -> dict:
    """
    Enrichit les données :
    1. Adaptation sectorielle sémantique (BTP, Food, Santé/Beauté, Services).
    2. Calculs graphiques (SVG gauge math, offsets, labels de statut).
    3. Codes couleurs dynamiques.
    """
    # 1. Adaptation sectorielle
    res = adapter_donnees_secteur(data)
    
    # 2. Référence d'audit & date
    now = datetime.datetime.now()
    res.setdefault("audit_ref", f"AUD-{now.strftime('%Y%m')}-{abs(hash(res.get('business_name', '')) % 9000) + 1000}")
    res.setdefault("audit_date", now.strftime("%d/%m/%Y"))
    res.setdefault("stripe_url", STRIPE_CHECKOUT_URL)
    
    score = int(res.get("overall_score", 50))
    # SVG gauge math : circonférence = 2 * pi * 45 ≈ 283
    dashoffset = round(283 * (1 - (score / 100.0)), 1)
    res["score_dashoffset"] = dashoffset
    
    if score >= 75:
        res["score_color"] = "#16a34a"
        res["score_bg"] = "#f0fdf4"
        res["score_border"] = "#bbf7d0"
        res["score_status_label"] = "Profil Optimisé"
    elif score >= 50:
        res["score_color"] = "#d97706"
        res["score_bg"] = "#fffbeb"
        res["score_border"] = "#fde68a"
        res["score_status_label"] = "Optimisation Nécessaire"
    else:
        res["score_color"] = "#dc2626"
        res["score_bg"] = "#fef2f2"
        res["score_border"] = "#fecaca"
        res["score_status_label"] = "Visibilité Vulnérable"
        
    # Couleurs des sous-métriques
    for metric_name in ["completeness", "reputation", "activity", "seo"]:
        key_val = f"metric_{metric_name}"
        score_val = int(res.get(key_val, 50))
        res[f"{key_val}_color"] = _get_metric_color(score_val)
        
    return res


def rendre_html(template_path: Path, data: dict) -> str:
    """Remplace les balises de template {{ cle }} par les valeurs fournies."""
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    for key, val in data.items():
        placeholder = f"{{{{ {key} }}}}"
        placeholder_no_space = f"{{{{{key}}}}}"
        str_val = str(val)
        html = html.replace(placeholder, str_val).replace(placeholder_no_space, str_val)
        
    return html


def trouver_navigateur_chrome() -> Optional[str]:
    """Cherche un binaire Chromium / Google Chrome disponible."""
    chemins_possibles = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("chrome")
    ]
    for chemin in chemins_possibles:
        if chemin and os.path.exists(chemin):
            return chemin
    return None


def convertir_html_en_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Convertit un fichier HTML en PDF via Chrome Headless avec mise en page A4 exacte."""
    chrome_bin = trouver_navigateur_chrome()
    if not chrome_bin:
        print(f"[!] Navigateur Chrome/Chromium introuvable pour {html_path.name}")
        return False

    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        str(html_path.resolve())
    ]
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25)
        return res.returncode == 0 and pdf_path.exists()
    except Exception as e:
        print(f"[!] Erreur de conversion PDF : {e}")
        return False


def generer_audit(data: dict, output_pdf_path: Optional[Path] = None, output_dir: Optional[Path] = None) -> Tuple[Path, Optional[Path]]:
    """
    Fonction principale de génération d'audit unitaire.
    Prend un dictionnaire de données et retourne (chemin_html, chemin_pdf).
    """
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template introuvable à {TEMPLATE_PATH}")

    data_enrichie = enrichir_donnees(data)
    
    target_dir = Path(output_dir) if output_dir else CURRENT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    
    slug_name = "".join(c if c.isalnum() else "_" for c in data.get("business_name", "audit")).lower()
    html_output = target_dir / f"rapport_{slug_name}.html"
    
    if output_pdf_path is None:
        pdf_output = target_dir / f"rapport_{slug_name}.pdf"
    else:
        pdf_output = Path(output_pdf_path)

    # 1. Rendu HTML
    contenu_html = rendre_html(TEMPLATE_PATH, data_enrichie)
    with open(html_output, "w", encoding="utf-8") as f:
        f.write(contenu_html)

    # 2. Conversion PDF
    succes_pdf = convertir_html_en_pdf(html_output, pdf_output)
    if not succes_pdf:
        pdf_output = None

    return html_output, pdf_output


def generer_en_masse(sources: List[Dict[str, Any]], output_dir: Path) -> Dict[str, Any]:
    """
    Génère les audits en masse pour une liste de fiches.
    Garantit l'isolation des erreurs : si une fiche échoue, les autres continuent.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    start_time = datetime.datetime.now()
    
    reussis = 0
    echoues = 0
    rapports_crees = []

    print(f"\n🚀 Lancement du traitement en masse : {len(sources)} fiches à traiter...")
    print(f"📁 Dossier de destination : {output_dir}\n" + "-" * 60)

    for i, item in enumerate(sources, 1):
        b_name = item.get("business_name", f"Prospect_{i}")
        cat = item.get("category", "Non spécifié")
        secteur = detecter_secteur(cat, b_name)
        
        item_start = datetime.datetime.now()
        try:
            html_p, pdf_p = generer_audit(item, output_dir=output_dir)
            item_elapsed = (datetime.datetime.now() - item_start).total_seconds()
            
            if pdf_p and pdf_p.exists():
                reussis += 1
                rapports_crees.append({"name": b_name, "sector": secteur, "pdf": str(pdf_p), "time": item_elapsed})
                print(f"[{i:02d}/{len(sources):02d}] ✅ {b_name[:32]:<32} | {secteur:<20} | ⏱️ {item_elapsed:.1f}s")
            else:
                reussis += 1
                rapports_crees.append({"name": b_name, "sector": secteur, "html": str(html_p), "time": item_elapsed})
                print(f"[{i:02d}/{len(sources):02d}] ⚠️ {b_name[:32]:<32} | HTML seul | ⏱️ {item_elapsed:.1f}s")
        except Exception as e:
            echoues += 1
            print(f"[{i:02d}/{len(sources):02d}] ❌ {b_name[:32]:<32} | ERREUR : {e}")

    total_time = (datetime.datetime.now() - start_time).total_seconds()
    avg_time = (total_time / len(sources)) if sources else 0.0

    print("-" * 60)
    print(f"🏁 Fin du traitement en masse :")
    print(f"   • Total fiches traitées : {len(sources)}")
    print(f"   • Succès               : {reussis}")
    print(f"   • Échecs               : {echoues}")
    print(f"   • Temps total          : {total_time:.2f} s")
    print(f"   • Temps moyen / audit  : {avg_time:.2f} s / rapport")
    print("-" * 60 + "\n")

    return {
        "total": len(sources),
        "success": reussis,
        "failed": echoues,
        "total_time": total_time,
        "avg_time": avg_time,
        "reports": rapports_crees
    }


def charger_sources_batch(batch_arg: str) -> List[Dict[str, Any]]:
    """Charge des fiches depuis un fichier JSON (liste ou objet unique) ou un dossier."""
    p = Path(batch_arg)
    if not p.exists():
        raise FileNotFoundError(f"Source batch introuvable : {batch_arg}")

    sources = []
    if p.is_dir():
        fichiers_json = sorted(list(p.glob("*.json")))
        for f in fichiers_json:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    contenu = json.load(fp)
                    if isinstance(contenu, list):
                        sources.extend(contenu)
                    elif isinstance(contenu, dict):
                        sources.append(contenu)
            except Exception as e:
                print(f"[!] Erreur de lecture pour {f.name} : {e}")
    else:
        with open(p, "r", encoding="utf-8") as fp:
            contenu = json.load(fp)
            if isinstance(contenu, list):
                sources = contenu
            elif isinstance(contenu, dict):
                sources = [contenu]

    return sources


def main():
    parser = argparse.ArgumentParser(
        description="Générateur de rapport d'audit de visibilité locale (Unitaire ou En masse)"
    )
    parser.add_argument("--input", "-i", type=str, help="Fichier JSON d'entrée pour un audit unitaire")
    parser.add_argument("--batch", "-b", type=str, help="Fichier JSON (liste) ou dossier contenant plusieurs fiches JSON")
    parser.add_argument("--output", "-o", type=str, help="Fichier PDF de sortie désiré (en mode unitaire)")
    parser.add_argument("--outdir", "-d", type=str, default=str(CURRENT_DIR / "sorties_audits"), help="Dossier de sortie des rapports")
    args = parser.parse_args()

    # Mode 1 : Traitement en masse (--batch)
    if args.batch:
        sources = charger_sources_batch(args.batch)
        out_dir = Path(args.outdir)
        generer_en_masse(sources, out_dir)
        return

    # Mode 2 : Traitement unitaire (--input ou par défaut)
    start_time = datetime.datetime.now()
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"📥 Données chargées depuis : {args.input}")
    else:
        print("ℹ️ Aucun fichier d'entrée spécifié : utilisation du jeu de données BTP de test.")
        data = SAMPLE_DATA

    secteur = detecter_secteur(data.get("category", ""), data.get("business_name", ""))
    print(f"🔍 Secteur d'activité détecté automatiquement : {secteur.upper()}")

    out_pdf = Path(args.output) if args.output else None
    out_dir = Path(args.outdir) if args.outdir and not args.output else None
    
    html_res, pdf_res = generer_audit(data, output_pdf_path=out_pdf, output_dir=out_dir)

    elapsed = (datetime.datetime.now() - start_time).total_seconds()
    print(f"✅ HTML généré : {html_res}")
    if pdf_res:
        print(f"✅ PDF généré  : {pdf_res}")
    print(f"⏱️ Temps d'exécution : {elapsed:.2f} secondes (Objectif < 15s : {'OK' if elapsed < 15 else 'DEPASSE'})")


if __name__ == "__main__":
    main()
