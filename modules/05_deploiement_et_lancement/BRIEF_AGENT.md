# 🤖 Brief Opérationnel — Bloc 5 : Déploiement Cloud & Lancement Réel

## 1. Rôle de l'Agent
Tu es l'**Ingénieur DevOps & Responsable Déploiement Production**. Ta mission est de sortir le projet de l'environnement local pour le déployer en ligne (24h/24 sans dépendre de l'ordinateur de l'utilisateur) et de brancher le canal d'expédition des emails réels de prospection.

## 2. Objectifs Précis
1. **Hébergement Webhook 24/7 (0 €)** : Déployer le serveur de réception Stripe (FastAPI/Flask) sur un hébergeur gratuit avec HTTPS (Render / Railway / Fly.io / Vercel Serverless) pour écouter les vrais paiements 24h/24.
2. **Configuration du canal d'envoi d'emails réels** :
   - Soit canal gratuit (Resend / Brevo / SMTP Gmail avec mot de passe d'application).
   - Soit domaine pro dédié (OVH / Hostinger ~10 € sur le budget de 50 €).
3. **Lancement du premier lot d'envois (Batch 1)** :
   - Expédition sécurisée des 15 premiers emails ultra-personnalisés avec teaser et lien Stripe.
   - Surveillance de la délivrabilité (0 rebond, 0 spam).

## 3. Livrables Attendus dans ce dossier (`modules/05_deploiement_et_lancement/`)
- `deploy_config.md` : Guide pas à pas de mise en ligne cloud gratuite en 1 clic.
- `envoyeur_reel.py` : Script d'envoi réel avec temporisation aléatoire (anti-spam) entre chaque envoi (ex: 45 à 90 secondes).
- `STATUS.md` : Tableau de bord de suivi des envois et des réponses.
