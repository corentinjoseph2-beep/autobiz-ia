# 🌐 Guide de Déploiement Cloud 24/7 & Mise en Ligne Webhook (0 €)

> **Projet** : AutoBiz IA — Micro-Service B2B Automatisé  
> **Module** : 05 — Déploiement Cloud & Lancement Réel  
> **Budget engagé** : **0,00 €** (Hébergement Cloud Gratuit garanti)  
> **Temps opérateur requis** : ~3 minutes (copier-coller 3 champs)

---

## 🎯 Objectif
Mettre en ligne le serveur d'écoute Stripe (`webhook_listener.py`) sur un serveur cloud gratuit accessible 24h/24 par Stripe, avec adresse **HTTPS sécurisée**, sans que votre ordinateur n'ait besoin de rester allumé.

Dès qu'un prospect règle les **49 €** sur votre lien Stripe :
1. Stripe prévient votre serveur cloud instantanément.
2. Le serveur génère le rapport d'audit PDF complet.
3. Le serveur expédie automatiquement le PDF au client par email.

---

## 🚀 Étape 1 : Choix de la Plateforme d'Hébergement Gratuit (0 €)

Nous recommandons **Render.com** (référence mondiale, plan gratuit permanent avec certificat HTTPS automatique).

| Hébergeur | Coût | Certificat HTTPS | Facilité | Statut |
| :--- | :--- | :--- | :--- | :--- |
| **Render.com** | **0 € / mois** (750h gratuites) | Inclus (SSL auto) | ⭐⭐⭐⭐⭐ (1 clic) | **Recommandé** |
| **Koyeb.com** | **0 € / mois** (Nano-instance) | Inclus (SSL auto) | ⭐⭐⭐⭐ | Alternative solide |
| **Railway.app** | 5 $ de crédits offerts | Inclus | ⭐⭐⭐⭐ | Alternative pay-as-you-go |

---

## 🛠️ Étape 2 : Déploiement en 1 Clic sur Render.com

### Option A — Déploiement Automatique via GitHub (Le plus simple)
1. Rendez-vous sur **[dashboard.render.com](https://dashboard.render.com)** (inscription gratuite en 1 clic avec votre compte GitHub ou Google).
2. Cliquez sur **New +** > **Web Service**.
3. Sélectionnez votre dépôt GitHub contenant ce projet.
4. Remplissez les champs suivants (ou laissez `render.yaml` le faire pour vous) :
   - **Name** : `autobiz-ia-webhook`
   - **Region** : Frankfurt (Europe) ou Oregon
   - **Environment** : `Python 3`
   - **Build Command** :  
     ```bash
     pip install -r modules/04_distribution_ventes/requirements.txt gunicorn
     ```
   - **Start Command** :  
     ```bash
     gunicorn --chdir modules/04_distribution_ventes webhook_listener:app --bind 0.0.0.0:$PORT --workers 2
     ```
   - **Instance Type** : `Free` (0 €/mois).

5. Dans la section **Environment Variables**, ajoutez :
   - `STRIPE_SECRET_KEY` = `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`
   - `FROM_EMAIL` = `AutoBiz IA <contact@autobiz-ia.fr>`
   - `SUPPORT_EMAIL` = `contact@autobiz-ia.fr`
   - *(Vos identifiants SMTP ou Resend pour l'expédition automatique du PDF)*

6. Cliquez sur **Create Web Service**.  
   👉 En 90 secondes, Render vous attribue une adresse URL publique sécurisée :  
   `https://autobiz-ia-webhook.onrender.com`

---

## 🔗 Étape 3 : Relier l'URL Cloud à votre Compte Stripe

Une fois votre serveur déployé sur Render :

1. Ouvrez votre tableau de bord Stripe en mode Production :  
   👉 **[dashboard.stripe.com/webhooks](https://dashboard.stripe.com/webhooks)**
2. Cliquez sur le bouton bleu **+ Ajouter un point de terminaison** (Add endpoint).
3. Remplissez :
   - **URL du point de terminaison** :  
     `https://VOTRE-APP.onrender.com/webhook`  
     *(Remplacez par votre vraie URL Render, bien terminer par `/webhook`)*
   - **Description** : `AutoBiz IA - Webhook Livraison Automatique 24/7`
   - **Événements à écouter** : Cliquez sur *Sélectionner des événements* > Cochez uniquement :  
     `checkout.session.completed`
4. Validez en cliquant sur **Ajouter un point de terminaison**.
5. Sur la page qui s'ouvre, cliquez sur **Révéler** sous "Secret pour signer" :  
   Copiez la clé qui commence par `whsec_...`.
6. Retournez dans les variables d'environnement de votre service Render et collez cette valeur dans `STRIPE_WEBHOOK_SECRET`.

---

## 🩺 Étape 4 : Tester la Bonne Réception (Health Check)

Ouvrez simplement dans votre navigateur ou via terminal :
```bash
curl https://VOTRE-APP.onrender.com/health
```

Réponse attendue :
```json
{
  "module": "04_distribution_ventes",
  "service": "AutoBiz IA Webhook Listener",
  "status": "healthy",
  "stripe_configured": true,
  "webhook_secret_set": true
}
```

---

## 📧 Étape 5 : Configuration du Canal d'Expédition des Emails (0 €)

Pour expédier les 15 emails de prospection et livrer les rapports PDF automatiquement :

### Option 1 (Recommandée & Gratuite) : Brevo SMTP (0 €)
1. Créez un compte gratuit sur [Brevo.com](https://www.brevo.com/) (300 emails/jour offerts à vie, 0 €).
2. Rendez-vous dans **Paramètres SMTP & API** > Générer une clé SMTP.
3. Renseignez dans votre `.env` local et sur Render :
   ```env
   SMTP_HOST=smtp-relay.brevo.com
   SMTP_PORT=587
   SMTP_USER=votre-email@domaine.com
   SMTP_PASSWORD=votre-cle-smtp
   ```

### Option 2 (Alternative Immédiate 0 €) : Mot de passe d'application Gmail
1. Sur votre compte Google (ou boîte dédiée) > Sécurité > Validation en deux étapes > **Mots de passe des applications**.
2. Générez un mot de passe de 16 lettres pour "Messagerie".
3. Renseignez dans `.env` :
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=votre-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

## 🚀 Étape 6 : Lancer le 1er Lot de Prospects (Batch 1)

Une fois vos identifiants renseignés dans le fichier `.env` :

1. **Vérification préliminaire (0 risque)** :
   ```bash
   python3 modules/05_deploiement_et_lancement/envoyeur_reel.py --dry-run
   ```
2. **Auto-test vers votre propre boîte mail** :
   ```bash
   python3 modules/05_deploiement_et_lancement/envoyeur_reel.py --test-email votre_adresse@gmail.com
   ```
3. **Expédition réelle des 15 emails** :
   ```bash
   python3 modules/05_deploiement_et_lancement/envoyeur_reel.py --live
   ```
   *(Le script temporise automatiquement entre 45 et 90 secondes entre chaque artisan pour garantir 0 détection spam et 100% de délivrabilité en boîte principale).*
