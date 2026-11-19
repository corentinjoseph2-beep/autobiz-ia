# 🚀 Statut du Module 05 : Déploiement Cloud & Lancement Réel

- **État général** : 🟡 **En attente de rotation de clé Stripe sur Render** / 🟢 **Infrastructure Cloud & Expéditeur Prêts**
- **Date de mise à jour** : 19/11/2026 (Assainissement fuite de clé Stripe & Guide de renouvellement express)
- **Responsable** : Agent Bloc 5 (Ingénieur DevOps & Déploiement Cloud)
- **Budget engagé** : **0,00 € / 50,00 €** (Stratégie 100% Gratuite préservant la réserve intacte)

---

## 📦 1. Composants Techniques Réalisés

| Composant | Fichier | Description | Statut |
| :--- | :--- | :--- | :--- |
| **Guide Déploiement 24/7** | `deploy_config.md` | Guide pas à pas de mise en ligne cloud gratuite (Render/Koyeb) — Assaini (clés remplacées par des placeholders). | ✅ Assaini |
| **Infrastructure as Code** | `render.yaml` | Blueprint de déploiement automatisé en 1 clic pour Render.com. | ✅ Terminé |
| **Conteneurisation Cloud** | `Dockerfile` | Image conteneur de production Python 3.11 avec Gunicorn multi-workers. | ✅ Terminé |
| **Fichier Processus** | `Procfile` | Déclaration de commande de démarrage pour PaaS (Render, Railway, Fly). | ✅ Terminé |
| **Fichier Variables** | `.env.example` | Template de configuration assaini pour le webhook Stripe et le canal d'envoi. | ✅ Assaini |
| **Protocole Renouvellement Clés** | `PROTOCOLE_RENOUVELLEMENT_STRIPE.md` | Procédure express en 2 clics pour renouveler la clé Stripe et mettre à jour Render. | ✅ Disponible & Documenté |
| **Expéditeur Réel** | `envoyeur_reel.py` | Script d'envoi sécurisé avec temporisation anti-spam (45-90s) et tracking. | ✅ Terminé & Testé |
| **Base Prospects Batch 1** | `prospects_batch_1.json` | 15 prospects qualifiés (Bordeaux & Lyon) avec emails vérifiés et failles. | ✅ Terminé |
| **Historique & Journalisation**| `envois_batch_1.log` | Traçabilité intégrale de chaque tentative et envoi. | ✅ Opérationnel |

---

## 👥 2. Tableau de Bord — Prospects du Batch 1 (15 Artisans Qualifiés)

Lien Stripe officiel injecté dans chaque email :  
`https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201?client_reference_id={Réf}`

| # | Entreprise | Ville | Métier | Email Cible | Note & Avis | Faille Google Maps Repérée | Réf Tracking Stripe | Statut |
| :-: | :--- | :--- | :--- | :--- | :--- | :-: | :--- | :--- | :--- |
| 1 | **Bicycl'eau Plombier** | Bordeaux | Plombier | `contact@bicycleau.fr` | 4.9 (35) | Optimisation attributs & mots-clés d'intervention | `BATCH1_LEAD_01_BICYCLEAUPLO` | 🟡 Prêt à l'envoi |
| 2 | **Napoléon Plomberie** | Bordeaux | Plombier Chauffagiste | `contact@napoleon-plomberie.com` | 4.9 (138) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_02_NAPOLONPLOMB` | 🟡 Prêt à l'envoi |
| 3 | **Cafonso Serrurier** | Bordeaux | Serrurier | `caciano.afonso028@gmail.com` | 5.0 (23) | Volume d'avis sous le seuil critique Top 3 | `BATCH1_LEAD_03_CAFONSOSERRU` | 🟡 Prêt à l'envoi |
| 4 | **MGB Serrurier** | Bordeaux | Serrurier | `mgb33000@gmail.com` | 5.0 (689) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_04_MGBSERRURIER` | 🟡 Prêt à l'envoi |
| 5 | **Clés Stop Dépanne** | Bordeaux | Serrurier | `clesstop.contact@gmail.com` | 4.9 (253) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_05_CLSSTOPDPANN` | 🟡 Prêt à l'envoi |
| 6 | **B&L Plomberie** | Bordeaux | Plombier | `louis.barlemont@gmail.com` | 5.0 (27) | Volume d'avis sous le seuil critique Top 3 | `BATCH1_LEAD_06_BLPLOMBERIEB` | 🟡 Prêt à l'envoi |
| 7 | **Serrurerie Bacci** | Bordeaux | Serrurier | `contact@serrurerie-bacci.com` | 5.0 (512) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_07_SERRURERIEBA` | 🟡 Prêt à l'envoi |
| 8 | **SERLOCK** | Bordeaux | Serrurier | `contact@serlock.fr` | 5.0 (22) | Volume d'avis sous le seuil critique Top 3 | `BATCH1_LEAD_08_SERLOCK` | 🟡 Prêt à l'envoi |
| 9 | **Serrurerie Bordelaise** | Bordeaux | Serrurier | `contact@serrurerie-bordelaise.com` | 4.8 (161) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_09_SERRURERIEBO` | 🟡 Prêt à l'envoi |
| 10 | **Abeille Services** | Bordeaux | Serrurier | `contact@abeille-depannage.com` | 4.9 (443) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_10_ABEILLESERVI` | 🟡 Prêt à l'envoi |
| 11 | **JT 33 Serrurier** | Bordeaux | Serrurier | `torresj33@outlook.fr` | 4.9 (411) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_11_JT33SERRURIE` | 🟡 Prêt à l'envoi |
| 12 | **PENA - Fermetures** | Bordeaux | Serrurier | `info@pena-serrurerie.com` | 4.7 (164) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_12_PENAFERMETUR` | 🟡 Prêt à l'envoi |
| 13 | **Selfcity Bordeaux** | Bordeaux | Plombier Chauffagiste | `contact@selfcity.fr` | 4.8 (129) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_13_SELFCITYBORD` | 🟡 Prêt à l'envoi |
| 14 | **BL Plomberie** | Lyon | Plombier | `contact@blplomberie.fr` | 4.1 (31) | Volume d'avis sous le seuil critique Top 3 | `BATCH1_LEAD_14_BLPLOMBERIE` | 🟡 Prêt à l'envoi |
| 15 | **MK Plomberie** | Lyon | Plombier | `contact@mk-plomberie.com` | 4.9 (105) | Réponses sémantiques aux avis récents incomplètes | `BATCH1_LEAD_15_MKPLOMBERIEP` | 🟡 Prêt à l'envoi |

---

## ⚡ 3. Commandes d'Exécution

```bash
# 1. Tester et prévisualiser sans envoyer (Mode Sécurisé 0 risque)
python3 modules/05_deploiement_et_lancement/envoyeur_reel.py --dry-run

# 2. S'envoyer un email de test pour validation visuelle dans sa boîte de réception
python3 modules/05_deploiement_et_lancement/envoyeur_reel.py --test-email mon_email@gmail.com

# 3. Déclencher les envois réels avec temporisation anti-spam (45 à 90s)
python3 modules/05_deploiement_et_lancement/envoyeur_reel.py --live
```

---

## 📊 4. Objectifs & Métriques de Conversion visés

- **Volume envoyé** : 15 emails ciblés.
- **Taux de délivrabilité visé** : 100% (0 rebond dur, 0 signalement spam).
- **Taux d'ouverture attendu** : > 50% (grâce à l'objet court et la personnalisation par ville).
- **Objectif de conversion** : 1 à 2 ventes sur ce premier lot (**49 € à 98 € de CA initial**).
- **Rentabilité** : Dépenses = 0 € -> Marge nette = 100%.

---

## 🛡️ 5. Registre des Incidents de Sécurité & Post-Mortem (19/11/2026)

### 📌 Incident INC-2026-11-19-STRIPE-01
- **Description** : Détection publique d'une clé API restreinte Stripe en clair (`rk_live_...dTcbQo`) dans les fichiers modèles de configuration (`modules/05_deploiement_et_lancement/.env.example` et `deploy_config.md`) via le commit initial `2ccc66b1`.
- **Canal de détection** : Notification automatique de sécurité émise par Stripe vers l'adresse administrative (`vumavuma148@gmail.com`).
- **Mesure de confinement immédiate Stripe** : Killswitch automatique appliqué par Stripe — la clé a été immédiatement désactivée et révoquée côté serveurs Stripe.
- **Bilan d'impact & Analyse médico-légale** :
  - **Pertes financières** : **0,00 €** (aucun détournement de fonds, aucun mouvement frauduleux).
  - **Données sensibles** : Aucune exfiltration constatée (la clé restreinte ne donnait pas accès aux données bancaires brutes).
  - **Disponibilité opérationnelle** : Le lien de paiement Stripe direct 49 € est 100% actif. Le webhook Render requiert l'injection de la nouvelle clé pour exécuter des requêtes Stripe authentifiées.
- **Mesures d'assainissement appliquées** :
  1. **Purge du code source** : Remplacement systématique de la clé exposée par le placeholder sécurisé `rk_live_votre_cle_ici`.
  2. **Rédaction du protocole de renouvellement** : Fichier `PROTOCOLE_RENOUVELLEMENT_STRIPE.md` créé pour guider la Direction Générale (génération d'une nouvelle clé restreinte + mise à jour Render en 2 clics).
  3. **Mise à jour documentaire** : Actualisation des statuts opérationnels des modules 04 et 05.
  4. **Synchronisation Git** : Commit ciblé et push sécurisé vers la branche `main` sur GitHub.
- **Procédure de reprise de service (RTO < 2 min)** :
  1. Se connecter sur [dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys).
  2. Cliquer sur **Créer une clé restreinte** (Permissions : Charges `Write`, Checkout Sessions `Write`, Webhook Endpoints `Read`).
  3. Coller la nouvelle clé dans l'onglet **Environment** du service Webhook sur Render.com (`STRIPE_SECRET_KEY`).
  4. Redémarrage automatique du service Render pris en compte.
