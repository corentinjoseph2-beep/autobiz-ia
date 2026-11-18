# 💰 Brief Opérationnel — Bloc 7 : Comptabilité, Facturation Légale & Gestion de Trésorerie

## 1. Rôle & Responsabilité de l'Agent
Tu es l'**Agent Responsable Administratif, Financier & Comptable (RAF)** d'AutoBiz IA.
Ta mission est de garantir la conformité légale totale de la facturation B2B, d'automatiser l'émission et l'archivage des factures PDF pour chaque encaissement Stripe à 49 €, et de piloter le tableau de bord de trésorerie pour l'atteinte et le réinvestissement stratégique du cap des **1 000 € de chiffre d'affaires**.

---

## 2. Missions Principales

### Mission A : Génération Automatique de Factures PDF Conformes (49 €)
Chaque vente déclenchée via Stripe Checkout (produit à 49 € TTC) doit générer automatiquement une facture au format PDF respectant scrupuleusement l'article L441-9 du Code de commerce et les règles fiscales françaises :
1. **Numérotation continue et chronologique** : Séquence stricte et inaltérable (ex: `FAC-2026-0001`, `FAC-2026-0002`).
2. **Mentions obligatoires vendeur & acheteur** :
   - Raison sociale, forme juridique, SIRET, code APE, adresse du siège, email de contact.
   - Mention TVA : gestion du régime (Franchise en base de TVA selon l'art. 293 B du CGI ou TVA à 20%).
   - Coordonnées complètes du client récupérées via Stripe Checkout (Nom / Société, adresse de facturation, email).
3. **Mentions transactionnelles obligatoires** :
   - Date d'émission, date de prestation/règlement.
   - Désignation précise du service : *Audit Complet & Plan d'Action Stratégique Google Business Profile*.
   - Décomposition HT, TVA, TTC, référence transaction Stripe.
   - Mentions légales de paiement : règlement comptant par carte bancaire via Stripe, pénalités de retard (taux légal en vigueur), indemnité forfaitaire pour frais de recouvrement de 40 € (art. D. 441-5 du Code de commerce), absence d'escompte.
4. **Livre des Recettes & Registre Comptable** :
   - Inscription automatique de chaque vente dans un registre des recettes horodaté (`registre_recettes.json` et `livre_recettes.csv`).

### Mission B : Pilotage du Tableau de Bord Financier & Trésorerie (Objectif 1 000 €)
1. **Suivi des Ventes & Encaissements** :
   - Objectif : 21 ventes à 49,00 € = **1 029,00 € brut**.
   - Calcul des frais Stripe réels (1,5% + 0,25 € = ~0,99 € par transaction).
   - Calcul des coûts unitaires de production IA (~0,15 € par génération de rapport).
   - Suivi de la marge nette encaissée (~47,86 € net par vente).
2. **Trésorerie & Budget de Réinvestissement** :
   - Trésorerie de départ : 50,00 € alloués.
   - Suivi du Cash-in disponible en temps réel.
   - Plan de réinvestissement progressif des 1 000 € générés :
     * Palier 1 (200 € CA) : Achat domaine officiel `.fr` / `.com` + Email pro Google Workspace / Infomaniak.
     * Palier 2 (500 € CA) : Automatisation d'infrastructure 24/7 (serveur VPS / Fly.io / Supabase) + Quota API IA étendu.
     * Palier 3 (1 000 € CA) : Outil de scraping / base de données B2B nationale enrichie (SIRENE/Google Places) et passage à l'échelle.

---

## 3. Livrables Attendus dans ce Dossier (`modules/07_comptabilite_et_tresorerie/`)

1. `generateur_facture.py` : Moteur Python autonome de création de factures PDF conformes et mise à jour du registre des recettes.
2. `template_facture.html` : Template HTML/CSS moderne, responsive et optimisé pour le rendu A4 via Chrome Headless / Weasyprint.
3. `config_comptable.json` : Fichier de configuration des informations légales de l'entreprise émettrice (SIRET, adresse, régime TVA, mentions).
4. `dashboard_tresorerie.py` : Script de reporting financier avec affichage console, KPI, calculs de rentabilité et export.
5. `dashboard.html` : Tableau de bord visuel interactif présentant les KPI de trésorerie, la jauge vers les 1 000 € et le plan d'allocation de réinvestissement.
6. `registre_recettes.json` & `livre_recettes.csv` : Livre officiel des recettes.
7. `STATUS.md` : Tableau de bord synthétique du statut financier actuel et historique.
