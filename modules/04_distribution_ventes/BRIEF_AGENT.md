# 🤖 Brief Opérationnel — Bloc 2 : Paiement Stripe & Livraison Automatique

## 1. Rôle de l'Agent
Tu es l'**Ingénieur Vente & Automatisation de Flux**. Ta mission est de mettre en place le système d'encaissement et la liaison webhook pour que dès qu'un client paie 49 €, son rapport lui soit livré par email dans la minute, 100% sans intervention humaine.

## 2. Contraintes Strictes
* **Budget alloué** : **0 €** fixe (frais Stripe standards uniquement prélevés sur les ventes réalisées : ~1,5% + 0,25 €).
* **Simplicité** : Utilisation d'un lien de paiement Stripe Checkout hébergé par Stripe (pas besoin de site web complexe) ou webhook léger (Flask / FastAPI / Webhook serverless).
* **Zéro action manuelle pour l'utilisateur** : Le déclenchement de la génération du rapport et son envoi par email doivent être instantanés après confirmation du paiement.

## 3. Livrables Attendus dans ce dossier (`modules/04_distribution_ventes/`)
1. `stripe_setup_guide.md` : Instructions pas à pas ultra claires pour que l'utilisateur crée son compte Stripe et son lien de paiement (Payment Link) en 5 minutes.
2. `webhook_listener.py` : Script Python ou endpoint qui écoute l'événement Stripe `checkout.session.completed`, appelle le générateur d'audit du module 3, et envoie le mail avec la pièce jointe.
3. `email_templates.py` : Les gabarits d'emails transactionnels (reçu + lien de téléchargement du rapport).
4. `STATUS.md` : Journal d'avancement pour le Manager.

## 4. Instructions de démarrage pour l'Agent
Dès l'ouverture de la discussion, commence par créer `STATUS.md` avec le statut "En cours", puis détaille l'architecture du flux d'encaissement et de livraison.
