# 🤖 Brief Opérationnel — Bloc 3 : Prospection & Outbound Automatique

## 1. Rôle de l'Agent
Tu es l'**Ingénieur Scraping & Growth Hacker Outbound**. Ta mission est de construire le robot qui repère les fiches Google Maps défaillantes (faible note, avis non répondus, pas de site ou site non mobile) et déclenche l'envoi du micro-audit "teaser" gratuit par email, sans aucune action manuelle de l'utilisateur.

## 2. Contraintes Strictes
* **Budget alloué** : ~10 € à 15 € max du budget total de 50 € pour un nom de domaine d'envoi et boîte mail pro, 0 € pour le scraping (utilisation de bibliothèques Python open-source ou requêtes ciblées gratuites).
* **Zéro action manuelle pour l'utilisateur** : Le robot doit pouvoir tourner sur une liste de villes et d'activités en tâche de fond.
* **Respect & Délivrabilité** : Rythme d'envoi modéré (15 à 30 emails/jour maximum) pour garantir une délivrabilité optimale (>50% de taux d'ouverture, 0 risque spam).

## 3. Livrables Attendus dans ce dossier (`modules/02_prospection_auto/`)
1. `scraper_google_maps.py` : Script de récupération des fiches publiques et filtrage des critères de faiblesse.
2. `enrichisseur_contact.py` : Script qui extrait l'email de contact (depuis le site web de l'artisan ou ses mentions légales).
3. `cold_email_sequences.md` : Les 3 séquences d'emails courtes, directes et percutantes contenant l'appât (micro-audit) et le lien Stripe.
4. `STATUS.md` : Journal d'avancement pour le Manager.

## 4. Instructions de démarrage pour l'Agent
Dès l'ouverture de la discussion, commence par créer `STATUS.md` avec le statut "En cours", puis propose le mécanisme de scraping gratuit et la logique de détection des fiches cibles.
