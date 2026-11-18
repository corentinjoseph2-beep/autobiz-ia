#!/usr/bin/env python3
"""
Tableau de Bord Financier & Pilotage de Trésorerie — AutoBiz IA (Module 07).
Calcule les KPI financiers en temps réel, suit la progression vers l'objectif
des 1 000 € de chiffre d'affaires, et gère le plan d'allocation de réinvestissement.
Génère l'affichage console, le rapport Markdown STATUS.md et le dashboard web interactif HTML.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
CONFIG_FILE = CURRENT_DIR / "config_comptable.json"
REGISTRE_JSON = CURRENT_DIR / "registre_recettes.json"
DEPENSES_JSON = CURRENT_DIR / "depenses_engagees.json"
STATUS_MD = CURRENT_DIR / "STATUS.md"
TABLEAU_DE_BORD_MD = CURRENT_DIR / "tableau_de_bord_1000eur.md"
DASHBOARD_HTML = CURRENT_DIR / "dashboard.html"


def charger_donnees() -> Dict[str, Any]:
    """Charge la configuration, le registre des recettes et le registre des dépenses."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Configuration introuvable: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    recettes = []
    if REGISTRE_JSON.exists():
        try:
            with open(REGISTRE_JSON, "r", encoding="utf-8") as f:
                recettes = json.load(f)
        except Exception:
            recettes = []

    depenses = []
    if DEPENSES_JSON.exists():
        try:
            with open(DEPENSES_JSON, "r", encoding="utf-8") as f:
                depenses = json.load(f)
        except Exception:
            depenses = []

    return {"config": config, "recettes": recettes, "depenses": depenses}


def calculer_kpis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule tous les indicateurs clés de performance financière."""
    config = data["config"]
    recettes = data["recettes"]
    depenses = data["depenses"]

    params_fin = config.get("parametres_financiers", {})
    objectif_ca = float(params_fin.get("objectif_ca_eur", 1000.00))
    budget_initial = float(params_fin.get("budget_initial_eur", 50.00))
    prix_unitaire = float(config.get("produit", {}).get("prix_unitaire_ttc", 49.00))
    ventes_cibles = int(params_fin.get("ventes_cibles", 21))

    nombre_ventes = len(recettes)
    ca_brut = sum(float(r.get("montant_ttc", 0.0)) for r in recettes)
    frais_stripe_total = sum(float(r.get("frais_stripe", 0.0)) for r in recettes)
    couts_ia_total = sum(float(r.get("cout_ia", 0.0)) for r in recettes)
    net_encaisse_total = sum(float(r.get("net_encaisse", 0.0)) for r in recettes)
    marge_nette_totale = sum(float(r.get("marge_nette", 0.0)) for r in recettes)

    total_depenses = sum(float(d.get("montant_eur", 0.0)) for d in depenses)
    tresorerie_active = round(budget_initial + net_encaisse_total - total_depenses, 2)

    progression_pct = min(100.0, round((ca_brut / objectif_ca) * 100.0, 1)) if objectif_ca > 0 else 0.0
    ventes_restantes = max(0, ventes_cibles - nombre_ventes)
    ca_manquant = max(0.0, round(objectif_ca - ca_brut, 2))

    # Évaluation des paliers de réinvestissement
    paliers = config.get("paliers_reinvestissement", [])
    paliers_evalues = []
    total_reinvesti_prevu = 0.0

    for p in paliers:
        seuil = float(p.get("palier_ca_eur", 0.0))
        atteint = ca_brut >= seuil
        allocation = float(p.get("allocation_estimee_eur", 0.0))
        if atteint:
            total_reinvesti_prevu += allocation
        paliers_evalues.append({
            "seuil_ca": seuil,
            "titre": p.get("titre"),
            "description": p.get("description"),
            "allocation": allocation,
            "atteint": atteint,
            "pct_progression": min(100.0, round((ca_brut / seuil) * 100.0, 1)) if seuil > 0 else 100.0
        })

    return {
        "nombre_ventes": nombre_ventes,
        "ventes_cibles": ventes_cibles,
        "ventes_restantes": ventes_restantes,
        "prix_unitaire": prix_unitaire,
        "ca_brut": round(ca_brut, 2),
        "objectif_ca": objectif_ca,
        "ca_manquant": ca_manquant,
        "progression_pct": progression_pct,
        "frais_stripe_total": round(frais_stripe_total, 2),
        "couts_ia_total": round(couts_ia_total, 2),
        "net_encaisse_total": round(net_encaisse_total, 2),
        "marge_nette_totale": round(marge_nette_totale, 2),
        "marge_nette_pct": round((marge_nette_totale / ca_brut * 100.0), 1) if ca_brut > 0 else 0.0,
        "budget_initial": budget_initial,
        "total_depenses": round(total_depenses, 2),
        "tresorerie_active": tresorerie_active,
        "paliers_reinvestissement": paliers_evalues,
        "total_reinvesti_prevu": round(total_reinvesti_prevu, 2),
        "recettes": recettes,
        "depenses": depenses,
    }


def generer_markdown_status(kpi: Dict[str, Any]) -> str:
    """Génère le contenu du STATUS.md avec les données financières en direct."""
    maintenant_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    barre_largeur = 25
    pleins = int((kpi["progression_pct"] / 100.0) * barre_largeur)
    barre = "█" * pleins + "░" * (barre_largeur - pleins)

    md = f"""# 📊 Tableau de Bord Financier & Trésorerie — Bloc 7
*Dernière mise à jour automatique : {maintenant_str}*

---

## 🎯 1. Cap des 1 000 € de Chiffre d'Affaires
| Indicateur Clé | Valeur Actuelle | Objectif Cible | Statut / Reste à faire |
| :--- | :--- | :--- | :--- |
| **Ventes d'audits (49 €)** | **{kpi['nombre_ventes']}** | {kpi['ventes_cibles']} ventes | **{kpi['ventes_restantes']} ventes restantes** |
| **Chiffre d'Affaires Brut** | **{kpi['ca_brut']:.2f} €** | {kpi['objectif_ca']:.2f} € | **{kpi['ca_manquant']:.2f} € à encaisser** |
| **Taux d'Atteinte du Cap** | **{kpi['progression_pct']:.1f}%** | 100% | `[{barre}]` |
| **Marge Nette Encaissée** | **{kpi['marge_nette_totale']:.2f} €** | ~980.00 € | Marge opérationnelle : **{kpi['marge_nette_pct']:.1f}%** |

---

## 💳 2. Détail Économique & Trésorerie
* **Budget initial de départ sécurisé** : `{kpi['budget_initial']:.2f} €`
* **Chiffre d'affaires brut perçu** : `{kpi['ca_brut']:.2f} €`
* **Frais bancaires Stripe (1,5% + 0,25 €)** : `- {kpi['frais_stripe_total']:.2f} €`
* **Coûts informatiques API IA (Gemini/OpenAI)** : `- {kpi['couts_ia_total']:.2f} €`
* **Dépenses réelles engagées** : `- {kpi['total_depenses']:.2f} €`
* 🟢 **Trésorerie Actuelle Disponible (Cash-in net)** : **`{kpi['tresorerie_active']:.2f} €`**

---

## 🚀 3. Feuille de Route du Réinvestissement des 1 000 €
Chaque euro gagné est sanctuarisé pour financer l'accélération d'AutoBiz IA :

| Palier CA | Action Stratégique | Budget Alloué | Statut |
| :--- | :--- | :--- | :--- |
"""
    for p in kpi["paliers_reinvestissement"]:
        statut_badge = "✅ **DÉBLOQUÉ**" if p["atteint"] else f"⏳ En attente ({p['pct_progression']}%)"
        md += f"| **{p['seuil_ca']:.0f} €** | {p['titre']}<br>*{p['description']}* | ~{p['allocation']:.0f} € | {statut_badge} |\n"

    md += """
---

## 🧾 4. Dernières Factures B2B Émises
| N° Facture | Date | Client | Établissement | Montant TTC | Frais Stripe | Net | Statut |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    if kpi["recettes"]:
        for r in reversed(kpi["recettes"][-5:]):
            md += f"| `{r.get('numero_facture')}` | {r.get('date_paiement')} | {r.get('client_nom')} | {r.get('client_etablissement', '-')} | **{r.get('montant_ttc', 0.0):.2f} €** | {r.get('frais_stripe', 0.0):.2f} € | {r.get('net_encaisse', 0.0):.2f} € | ✅ Payée |\n"
    else:
        md += "| *(Aucune facture émise pour le moment)* | - | - | - | - | - | - | - |\n"

    md += """
---
*Pour générer une nouvelle facture ou consulter le dashboard interactif :*
* CLI Facturation : `python3 modules/07_comptabilite_et_tresorerie/generateur_facture.py`
* Dashboard Web : `open modules/07_comptabilite_et_tresorerie/dashboard.html`
"""
    return md


def generer_dashboard_html(kpi: Dict[str, Any]) -> str:
    """Génère l'interface web complète et interactive du tableau de bord de trésorerie."""
    maintenant_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    
    recettes_rows = ""
    for r in reversed(kpi["recettes"]):
        recettes_rows += f"""
        <tr class="hover:bg-slate-800/50 transition-colors border-b border-slate-800">
            <td class="py-3 px-4 font-mono text-blue-400 font-semibold">{r.get('numero_facture')}</td>
            <td class="py-3 px-4 text-slate-300 text-sm">{r.get('date_paiement')}</td>
            <td class="py-3 px-4 font-medium text-white">{r.get('client_nom')}</td>
            <td class="py-3 px-4 text-slate-400 text-sm">{r.get('client_etablissement', '-')}</td>
            <td class="py-3 px-4 font-bold text-white text-right">{r.get('montant_ttc', 0.0):.2f} €</td>
            <td class="py-3 px-4 text-rose-400 text-right text-sm">-{r.get('frais_stripe', 0.0):.2f} €</td>
            <td class="py-3 px-4 font-bold text-emerald-400 text-right">+{r.get('net_encaisse', 0.0):.2f} €</td>
            <td class="py-3 px-4 text-center">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Payée
                </span>
            </td>
        </tr>
        """

    paliers_html = ""
    for p in kpi["paliers_reinvestissement"]:
        border_col = "border-emerald-500 bg-emerald-950/20" if p["atteint"] else "border-slate-800 bg-slate-900/60"
        badge = """<span class="px-2.5 py-1 text-xs font-bold rounded-md bg-emerald-500 text-slate-950">✓ DÉBLOQUÉ</span>""" if p["atteint"] else f"""<span class="px-2.5 py-1 text-xs font-semibold rounded-md bg-slate-800 text-slate-400">Progression : {p['pct_progression']}%</span>"""
        
        paliers_html += f"""
        <div class="p-5 rounded-xl border {border_col} transition-all">
            <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-blue-400 uppercase tracking-wider">Objectif : {p['seuil_ca']:.0f} € de CA</span>
                {badge}
            </div>
            <h4 class="text-lg font-bold text-white mb-1">{p['titre']}</h4>
            <p class="text-sm text-slate-400 mb-3">{p['description']}</p>
            <div class="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
                <span>Budget réinvestissement :</span>
                <span class="font-bold text-emerald-400 text-sm">~{p['allocation']:.0f} €</span>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="fr" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tableau de Bord Trésorerie & Facturation — AutoBiz IA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        brand: {{
                            50: '#eff6ff',
                            500: '#3b82f6',
                            600: '#2563eb',
                            700: '#1d4ed8',
                        }}
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans antialiased pb-16">

    <!-- NAVIGATION HEADER -->
    <header class="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center font-black text-xl shadow-lg shadow-blue-500/20">
                    ⚡
                </div>
                <div>
                    <h1 class="text-lg font-bold text-white">AutoBiz IA — Module 07</h1>
                    <p class="text-xs text-slate-400">Comptabilité, Facturation & Trésorerie</p>
                </div>
            </div>
            <div class="flex items-center gap-4 text-xs text-slate-400">
                <span class="flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    Système Opérationnel
                </span>
                <span class="hidden sm:inline text-slate-600">|</span>
                <span class="hidden sm:inline">Actualisé le {maintenant_str}</span>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-8">

        <!-- HERO : JAUGE DES 1 000 € -->
        <section class="bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 p-6 sm:p-8 rounded-2xl border border-slate-800 shadow-xl">
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-6">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 mb-3">
                        🎯 OBJECTIF PHASE 1 : 1 000 € DE CHIFFRE D'AFFAIRES
                    </div>
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                        {kpi['ca_brut']:.2f} € <span class="text-slate-500 font-medium text-2xl">/ {kpi['objectif_ca']:.2f} €</span>
                    </h2>
                    <p class="text-slate-400 text-sm mt-1">
                        <strong>{kpi['nombre_ventes']}</strong> ventes d'audits réalisées sur {kpi['ventes_cibles']} visées. Plus que <strong>{kpi['ventes_restantes']} ventes</strong> pour boucler le cap.
                    </p>
                </div>
                <div class="text-right">
                    <div class="text-4xl sm:text-5xl font-black text-blue-400">
                        {kpi['progression_pct']:.1f}%
                    </div>
                    <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mt-1">
                        Taux d'accomplissement
                    </div>
                </div>
            </div>

            <!-- BARRE DE PROGRESSION -->
            <div class="w-full bg-slate-800/80 rounded-full h-4 p-1 overflow-hidden border border-slate-700/50">
                <div class="bg-gradient-to-r from-blue-600 via-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-700 shadow-sm" style="width: {kpi['progression_pct']}%;"></div>
            </div>
        </section>

        <!-- KPI CARDS -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <!-- CARTE 1 -->
            <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 shadow">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Trésorerie Disponible</p>
                <div class="flex items-baseline gap-2">
                    <span class="text-3xl font-extrabold text-emerald-400">{kpi['tresorerie_active']:.2f} €</span>
                </div>
                <p class="text-xs text-slate-400 mt-2">Cash-in disponible (Budget 50 € inclus)</p>
            </div>

            <!-- CARTE 2 -->
            <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 shadow">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Marge Nette Encaissée</p>
                <div class="flex items-baseline gap-2">
                    <span class="text-3xl font-extrabold text-white">{kpi['marge_nette_totale']:.2f} €</span>
                    <span class="text-xs font-bold text-emerald-400">({kpi['marge_nette_pct']:.1f}%)</span>
                </div>
                <p class="text-xs text-slate-400 mt-2">Après frais Stripe & coûts serveurs</p>
            </div>

            <!-- CARTE 3 -->
            <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 shadow">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Frais Stripe Déduits</p>
                <div class="flex items-baseline gap-2">
                    <span class="text-3xl font-extrabold text-rose-400">-{kpi['frais_stripe_total']:.2f} €</span>
                </div>
                <p class="text-xs text-slate-400 mt-2">1,5% + 0,25 € par encaissement</p>
            </div>

            <!-- CARTE 4 -->
            <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 shadow">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Coûts de Calcul IA</p>
                <div class="flex items-baseline gap-2">
                    <span class="text-3xl font-extrabold text-amber-400">-{kpi['couts_ia_total']:.2f} €</span>
                </div>
                <p class="text-xs text-slate-400 mt-2">~0,15 € par génération de rapport</p>
            </div>
        </section>

        <!-- FEUILLE DE ROUTE RÉINVESTISSEMENT -->
        <section class="space-y-4">
            <div class="flex items-center justify-between">
                <div>
                    <h3 class="text-xl font-bold text-white">🚀 Plan de Réinvestissement des 1 000 €</h3>
                    <p class="text-sm text-slate-400">Allocation stratégique 100% autofinancée par les ventes</p>
                </div>
                <span class="text-xs font-bold px-3 py-1 bg-slate-800 text-slate-300 rounded-full">
                    Total Réinvesti Prévu : {kpi['total_reinvesti_prevu']:.0f} €
                </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                {paliers_html}
            </div>
        </section>

        <!-- REGISTRE DES VENTES & FACTURES -->
        <section class="bg-slate-900/60 rounded-xl border border-slate-800 overflow-hidden shadow">
            <div class="p-5 border-b border-slate-800 flex items-center justify-between">
                <div>
                    <h3 class="text-lg font-bold text-white">🧾 Journal des Ventes & Factures Emises</h3>
                    <p class="text-xs text-slate-400">Livre officiel des recettes synchronisé</p>
                </div>
                <span class="text-xs font-mono bg-slate-800 text-blue-400 px-3 py-1 rounded-md border border-slate-700">
                    {kpi['nombre_ventes']} enregistrements
                </span>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-slate-800 bg-slate-950/40 text-xs font-bold uppercase tracking-wider text-slate-400">
                            <th class="py-3 px-4">N° Facture</th>
                            <th class="py-3 px-4">Date</th>
                            <th class="py-3 px-4">Client</th>
                            <th class="py-3 px-4">Établissement</th>
                            <th class="py-3 px-4 text-right">Montant TTC</th>
                            <th class="py-3 px-4 text-right">Frais Stripe</th>
                            <th class="py-3 px-4 text-right">Net</th>
                            <th class="py-3 px-4 text-center">Statut</th>
                        </tr>
                    </thead>
                    <tbody>
                        {recettes_rows if recettes_rows else '<tr><td colspan="8" class="text-center py-8 text-slate-500">Aucune vente enregistrée pour le moment.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </section>

    </main>

</body>
</html>
"""
    return html


def synchroniser_dashboard(afficher_console: bool = True) -> Dict[str, Any]:
    """Calcule les KPI, génère STATUS.md et dashboard.html."""
    data = charger_donnees()
    kpi = calculer_kpis(data)

    # Écriture de STATUS.md et tableau_de_bord_1000eur.md
    md_content = generer_markdown_status(kpi)
    with open(STATUS_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(TABLEAU_DE_BORD_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Écriture de dashboard.html
    html_content = generer_dashboard_html(kpi)
    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    if afficher_console:
        print("\n" + "=" * 65)
        print("⚡ AUTOBIZ IA — TABLEAU DE BORD DE TRÉSORERIE & COMPTABILITÉ")
        print("=" * 65)
        print(f"🎯 Objectif Cap 1 000 €   : {kpi['ca_brut']:.2f} € / {kpi['objectif_ca']:.2f} € ({kpi['progression_pct']:.1f}%)")
        print(f"📦 Ventes Réalisées      : {kpi['nombre_ventes']} / {kpi['ventes_cibles']} ({kpi['ventes_restantes']} restantes)")
        print(f"💰 Chiffre d'Affaires Brut: {kpi['ca_brut']:.2f} €")
        print(f"💳 Frais Stripe Déduits  : -{kpi['frais_stripe_total']:.2f} €")
        print(f"🤖 Coûts Techniques IA   : -{kpi['couts_ia_total']:.2f} €")
        print(f"🟢 Marge Nette Totale    : {kpi['marge_nette_totale']:.2f} € ({kpi['marge_nette_pct']:.1f}%)")
        print(f"🏦 Trésorerie Active     : {kpi['tresorerie_active']:.2f} € (Budget 50 € inclus)")
        print("-" * 65)
        print("🚀 Paliers de Réinvestissement :")
        for p in kpi["paliers_reinvestissement"]:
            etat = "✅ DÉBLOQUÉ" if p["atteint"] else f"⏳ {p['pct_progression']}%"
            print(f"  • {p['seuil_ca']:.0f} € : {p['titre']} [{etat}] (~{p['allocation']:.0f} €)")
        print("=" * 65)
        print(f"📄 Markdown générés: {STATUS_MD.name} & {TABLEAU_DE_BORD_MD.name}")
        print(f"🌐 Dashboard Web   : {DASHBOARD_HTML.name}\n")

    return kpi


def ajouter_depense(montant: float, motif: str, categorie: str = "infrastructure") -> None:
    """Enregistre une dépense engagée pour la déduire de la trésorerie active."""
    depenses = []
    if DEPENSES_JSON.exists():
        try:
            with open(DEPENSES_JSON, "r", encoding="utf-8") as f:
                depenses = json.load(f)
        except Exception:
            depenses = []

    depense = {
        "id": f"dep_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "date": datetime.now().strftime("%d/%m/%Y"),
        "montant_eur": float(montant),
        "motif": motif,
        "categorie": categorie
    }
    depenses.append(depense)
    with open(DEPENSES_JSON, "w", encoding="utf-8") as f:
        json.dump(depenses, f, indent=2, ensure_ascii=False)
    print(f"✅ Dépense enregistrée : {motif} ({montant:.2f} €)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pilotage Financier & Tableau de Bord Trésorerie")
    parser.add_argument("--depense", type=float, default=None, help="Montant d'une dépense à enregistrer")
    parser.add_argument("--motif", type=str, default="Frais opérationnel", help="Motif de la dépense")
    parser.add_argument("--silencieux", action="store_true", help="Ne pas afficher la console")

    args = parser.parse_args()

    if args.depense is not None:
        ajouter_depense(args.depense, args.motif)

    synchroniser_dashboard(afficher_console=not args.silencieux)
