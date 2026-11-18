# 💳 Guide de Configuration Stripe Checkout & Payment Link (5 minutes)

Ce guide permet à tout opérateur (même débutant technique) de mettre en place le système d'encaissement de **49 €** en moins de 5 minutes, sans coder ni créer de site web.

---

## ⚡ En résumé
* **Outil** : Stripe Payment Link (page de paiement sécurisée et hébergée à 100% par Stripe).
* **Frais** : 0 € d'abonnement. 1,4% + 0,25 € par vente (prélevé uniquement en cas de vente réussie).
* **Objectif** : Vendre un audit à 49 €, collecter l'email de l'acheteur ainsi que le nom de sa fiche Google, et notifier notre script de livraison instantanée.

---

## Étape 1 : Créer le compte Stripe (si pas encore fait)
1. Rendez-vous sur [dashboard.stripe.com/register](https://dashboard.stripe.com/register).
2. Renseignez votre adresse email, nom et mot de passe.
3. Activez votre compte en renseignant les informations de votre entreprise ou micro-entreprise (IBAN pour recevoir les virements).
4. *Astuce* : Vous pouvez tester tout le système en **Mode Test** (interrupteur en haut à droite du tableau de bord Stripe) avant de basculer en mode réel.

---

## Étape 2 : Créer le Produit (Audit Visibilité Locale)
1. Dans le menu de gauche, allez dans **Catalogue de produits** (ou *Produits*) -> cliquez sur **+ Ajouter un produit**.
2. Remplissez les champs suivants :
   * **Nom** : `Audit Complet Google Business Profile & Référencement Local`
   * **Description** : `Rapport d'audit stratégique complet, analyse de visibilité locale, benchmark concurrentiel et plan d'action correctif sous 7 jours.`
   * **Image** (optionnel mais recommandé) : Un aperçu de couverture de rapport ou mockup d'audit PDF.
   * **Tarification** :
     * Modèle de tarification : **Tarification standard**
     * Prix : **49,00 €**
     * Facturation : **Paiement unique** (One-time)
3. Cliquez sur **Enregistrer le produit** (en haut à droite).

---

## Étape 3 : Générer le Lien de Paiement (Payment Link)
1. Sur la fiche du produit créé, cliquez sur **Créer un lien de paiement** (ou allez dans *Paiements* -> *Liens de paiement* -> *Nouveau*).
2. Dans les options de gauche :
   * **Options supplémentaires** :
     * Cochez **"Collecter les adresses de facturation"** (recommandé pour les clients B2B).
     * Cochez **"Demander un numéro de téléphone"** (facultatif mais utile pour du suivi commercial).
   * **Champs personnalisés (Indispensable pour automatiser l'audit !)** :
     * Cliquez sur **Ajouter un champ personnalisé**.
     * Type : **Texte**.
     * Libellé : `Nom de votre établissement ou lien Google Maps`.
     * Clé (optionnelle) : `business_name`.
     * Cochez la case **Obligatoire**.
     * *(Ainsi, le client saisit exactement le nom de son commerce au moment de payer).*
   * **Confirmation après paiement** :
     * Choisissez **"Afficher la page de confirmation"** avec un message personnalisé :
       > *"Merci pour votre commande ! Votre audit personnalisé est en cours de génération et vient de vous être envoyé par email. Vérifiez votre boîte de réception d'ici 1 minute."*
3. Cliquez sur **Créer le lien** en haut à droite.
4. **Félicitations** : Vous obtenez une URL du type `https://buy.stripe.com/test_...` prête à être partagée dans vos emails de prospection.

---

## Étape 4 : Personnalisation dynamique du lien (Optionnel mais puissant)
Pour maximiser la conversion lors de l'envoi d'emails de prospection, vous pouvez pré-remplir l'email et un identifiant :
```
https://buy.stripe.com/votre_identifiant?prefilled_email=client@restaurant.fr&client_reference_id=PROSPECT_123
```
* `prefilled_email` : Pré-remplit l'email du prospect pour lui éviter de le retaper.
* `client_reference_id` : Permet de réconcilier le paiement avec la fiche prospect prospectée.

---

## Étape 5 : Configurer le Webhook pour la livraison automatique

Le webhook informe notre script `webhook_listener.py` dès qu'un paiement de 49 € est validé.

### Option A — En local (Tests avec Stripe CLI)
1. Téléchargez la Stripe CLI :
   * macOS : `brew install stripe/stripe-cli/stripe`
2. Connectez la CLI à votre compte :
   ```bash
   stripe login
   ```
3. Lancez l'écoute et le renvoi vers notre script local (port 5000) :
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```
4. La CLI affichera votre secret de signature webhook : `whsec_xxxxxxxxxxxxxxxxxxxx`.
5. Copiez ce code dans votre fichier `.env` :
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxx
   ```

### Option B — En production (Hébergement en ligne gratuit / cloud)
1. Allez dans le **Dashboard Stripe** -> **Développeurs** -> **Webhooks** -> **Ajouter un endpoint**.
2. **URL de l'endpoint** : `https://votre-domaine-ou-serveur.com/webhook` (ex: Render.com, Fly.io, Railway, VPS, ou tunnel ngrok).
3. **Événements à écouter** :
   * Cochez uniquement : `checkout.session.completed`
4. Cliquez sur **Ajouter un point de terminaison**.
5. Révélez le **Secret de signature** (`whsec_...`) et ajoutez-le à vos variables d'environnement.

---

## Étape 6 : Récupérer vos clés API Stripe
1. Dans le Dashboard Stripe, allez dans **Développeurs** -> **Clés d'API**.
2. Copiez la **Clé secrète** (`sk_test_...` pour les tests ou `sk_live_...` en production).
3. Renseignez-la dans le fichier `.env` :
   ```env
   STRIPE_SECRET_KEY=sk_test_...
   ```

Votre système d'encaissement est opérationnel à 100% !
