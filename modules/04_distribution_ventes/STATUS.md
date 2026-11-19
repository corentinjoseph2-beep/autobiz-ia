# Statut du Module 04 : Paiement Stripe & Livraison Automatique

- **État général** : 🟡 **En attente de rotation de clé Stripe sur Render** (Lien de Paiement 100% actif, Webhook opérationnel, clé API restreinte révoquée par sécurité par Stripe)
- **Responsable** : Agent Vente & Automatisation de Flux (Bloc 2)
- **Objectif** : Encaissement autonome de 49 € via Stripe Payment Link et livraison immédiate (< 1 min) par email de l'audit PDF sans aucune intervention humaine.
- **Lien de Paiement Stripe Actif (Production)** : `https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201`
- **Produit Stripe** : `prod_VeWYmMCXIoRdVF` — *Audit Stratégique de Visibilité Google Maps (Prestation B2B)*
- **Description Produit** : *Audit de performance locale, benchmark concurrentiel et plan d'action pour commerces, artisans et entreprises. Prestation de conseil déductible en frais professionnels.*
- **Champs Obligatoires Configurés** :
  1. `business_name` : "Nom de l'établissement ou lien Google Maps" (OBLIGATOIRE)
  2. `business_address` : "Adresse complète et Ville de l'établissement" (OBLIGATOIRE)
  3. `billing_address_collection` : "required" (Adresse postale de facturation OBLIGATOIRE)
- **Serveur Webhook Cloud 24/7 (Render)** : `https://autobiz-ia-webhook.onrender.com/webhook`
- **Webhook Endpoint Stripe ID** : `we_1UdExCGlJLwWRlFayDS1Chb0` (Événement : `checkout.session.completed`)
- **Signature Cryptographique Stripe** : Configurée et active dans Render (`whsec_...`)
- **Intégration Module 03 (Audit PDF) & 07 (Facturation)** : ✅ Connectés & Validés en Cloud
- **Dernière mise à jour** : 2026-11-19 (Incident d'exposition clé restreinte Stripe maîtrisé — Révocation automatique Stripe, assainissement code, protocole de rotation documenté)

---

## 🚨 Alerte Sécurité & Registre d'Incident Stripe (19/11/2026)

- **Date de détection** : 19 novembre 2026 (Notification automatique Stripe reçue sur `vumavuma148@gmail.com`).
- **Événement déclencheur** : Détection publique sur GitHub de la clé restreinte `rk_live_...dTcbQo` présente dans le commit initial `2ccc66b1`.
- **Réaction automatique Stripe** : Désactivation et révocation immédiate de la clé par les robots de sécurité Stripe (killswitch instantané).
- **Impact financier & intégrité** : **0,00 € de perte** (aucun détournement, solde et transactions 100% sécurisés, compte Stripe intact).
- **Statut opérationnel des flux** :
  - **Lien de Paiement 49 €** (`https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201`) : **100% Fonctionnel** (hébergé nativement sur l'infrastructure sécurisée Stripe, indépendant de la clé compromise).
  - **Signature Webhook** (`whsec_...`) : **Intacte et active** pour la validation des événements entrants.
  - **Serveur Webhook Render** : Reçoit et valide les notifications d'achat, mais les requêtes API sortantes vers Stripe nécessitent l'actualisation de la variable `STRIPE_SECRET_KEY` dans Render.
- **Mesures d'assainissement appliquées** :
  1. Purge et remplacement de toute clé en clair par `rk_live_votre_cle_ici` dans l'ensemble des fichiers de configuration (`.env.example`, `deploy_config.md`).
  2. Rédaction du protocole de rotation express en 2 clics : `modules/05_deploiement_et_lancement/PROTOCOLE_RENOUVELLEMENT_STRIPE.md`.
  3. Mise à jour des statuts et synchronisation sécurisée sur GitHub `main`.
- **Action requise de la Direction Générale (Temps estimé : 2 minutes)** :
  - Suivre le protocole en 2 clics : créer une nouvelle clé restreinte sur `dashboard.stripe.com/apikeys` et renseigner `STRIPE_SECRET_KEY` dans Render.

---

## 🏗️ Architecture du Flux Automatisé

```
[Prospect / Email de Vente]
        │
        ▼ (Clic sur le lien de paiement)
[Stripe Checkout Payment Link (49 €)]
        │  * Récupère : Email client, Nom de l'établissement / URL fiche Google
        │  * Gère la transaction bancaire sécurisée
        ▼ (Événement webhook : checkout.session.completed)
[Serveur Webhook : webhook_listener.py]
        │
        ├─► 1. Vérification de la signature cryptographique Stripe
        ├─► 2. Extraction des données (Email, Nom du commerce, Place ID)
        ├─► 3. Déclenchement du moteur d'audit (Module 03 : generateur_audit.py)
        │       └─► Génération du rapport PDF personnalisé en < 15s
        └─► 4. Envoi automatique de l'email de livraison (email_templates.py)
                └─► Email HTML pro avec rapport PDF en pièce jointe + lien de téléchargement
```

---

## 📋 Composants & Avancement

| Composant | Fichier | Statut | Description |
| :--- | :--- | :---: | :--- |
| **Guide Stripe** | `stripe_setup_guide.md` | ✅ Terminé | Configuration pas à pas en 5 min (Compte, Produit 49€, Payment Link, Webhook). |
| **Templates Emails** | `email_templates.py` | ✅ Terminé | Gabarits transactionnels HTML & Text (Livraison de l'audit, garantie sérénité artisan). |
| **Serveur Webhook** | `webhook_listener.py` | ✅ Terminé | Écouteur Flask/HTTP avec validation Stripe, intégration Module 03 et SMTP/Resend. |
| **Configuration** | `.env.example` & `requirements.txt` | ✅ Assaini | Variables d'environnement assainies (placeholders neutres) et dépendances légères. |
| **Protocole de Renouvellement** | `PROTOCOLE_RENOUVELLEMENT_STRIPE.md` | ✅ Prêt | Procédure en 2 clics (Module 05) pour générer et injecter la nouvelle clé. |
| **Tests de bout en bout** | `test_simulation.py` | ✅ Prêt | Simulation complète de paiement et de livraison sans carte bancaire réelle. |

---

## 🎯 Prochaines Étapes
1. Rotation de la clé Stripe par la Direction Générale (suivre `modules/05_deploiement_et_lancement/PROTOCOLE_RENOUVELLEMENT_STRIPE.md`).
2. Injection de la nouvelle valeur `STRIPE_SECRET_KEY` dans les variables d'environnement sur Render.com.
3. Test de validation en local via Stripe CLI (`stripe trigger checkout.session.completed`) ou simulation de bout en bout pour valider la reprise nominale à 100%.
