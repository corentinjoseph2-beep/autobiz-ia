# 🔐 PROTOCOLE EXÉCUTIF : RENOUVELLEMENT DE LA CLÉ STRIPE & SYNCHRONISATION RENDER (2 CLICS)

> **Document officiel à destination de la Direction Générale et du CEO**  
> **Temps d'exécution estimé** : Moins de 2 minutes  
> **Niveau technique requis** : Aucun (Procédure guidée en 2 clics)

---

## 🧭 Résumé de Situation & Pourquoi ce Protocole

- **Incident neutralisé** : Une ancienne clé d'API restreinte (`rk_live_...dTcbQo`) a été détectée dans l'historique public GitHub (commit `2ccc66b1`).
- **Impact financier : STRICTEMENT 0,00 €** : Les robots de surveillance Stripe ont automatiquement révoqué et désactivé cette clé préventivement. Aucun virement, débit ou modification n'a été possible.
- **Continuité des paiements** : Le lien de paiement Stripe direct ([buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201](https://buy.stripe.com/5kQ5kDeuJ6BJ2js7YE8N201)) reste **100% opérationnel**. Les paiements des artisans continuent d'être encaissés sans interruption.
- **Objectif de ce protocole** : Fournir à notre serveur Cloud Render une toute nouvelle clé restreinte afin qu'il puisse traiter et livrer automatiquement les audits commandés par les clients.

---

## 🛡️ Règle d'Or de Sécurité : La Clé Restreinte (Moindre Privilège)

Nous utilisons impérativement une **Clé Restreinte (`rk_live_...`)** et **JAMAIS** la clé secrète principale (`sk_live_...`).

| Type de Clé | Droits accordés | Risque en cas de fuite | Statut OptiLocal |
| :--- | :--- | :--- | :---: |
| **Clé Secrète Principale** (`sk_live_...`) | Tous les droits (Virements, Solde, RIB, etc.) | 🔴 Élevé (Détournement possible) | ⛔ **STRICTEMENT PROSCRITE** |
| **Clé Restreinte** (`rk_live_...`) | Uniquement lecture des paiements et webhook | 🟢 Zéro risque (Aucun virement possible) | ✅ **OBLIGATOIRE** |

---

## ⚡ ÉTAPE 1 (CLIC 1) : Générer la Clé Restreinte sur Stripe (1 minute)

1. Ouvrez directement la page officielle des clés API Stripe :  
   👉 **[dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys)**  
   *(Assurez-vous que l'interrupteur en haut à droite est bien sur le mode **Production / Live** et non "Test")*.

2. Dans la section **Clés restreintes** (*Restricted keys*), cliquez sur :  
   👉 **+ Créer une clé restreinte** (*Create restricted key*).

3. Renseignez les paramètres suivants :
   - **Nom de la clé** : `OptiLocal - Render Webhook 2026`

4. Définissez les **Permissions exactes** requises par notre système :

   | Ressource Stripe | Niveau d'accès | Rôle technique pour OptiLocal |
   | :--- | :---: | :--- |
   | **Sessions Checkout** (*Checkout Sessions*) | **Lecture** (*Read*) | Lecture des commandes de 49 €, récupération du nom de l'artisan et de son email. |
   | **Paiements / Intentions** (*PaymentIntents*) | **Lecture** (*Read*) | Validation de la bonne exécution du règlement bancaire. |
   | **Charges** (*Charges*) | **Lecture** (*Read*) | Extraction des frais Stripe (~1,50 €) pour le Module 07 (Facture B2B légale). |
   | **Clients** (*Customers*) | **Lecture** (*Read*) | Consultation des données client transmises lors du paiement. |
   | **Points de terminaison Webhook** (*Webhook Endpoints*) | **Lecture** (*Read*) | Vérification du point d'écoute du serveur cloud. |
   | **Remboursements** (*Refunds*) | **Aucun** (*None*) | Gestion manuelle des remboursements "Garantie Sérénité" sur le Dashboard. |
   | **Toutes les autres ressources** (Virements, Soldes, Banques...) | **Aucun accès** (*None*) | 🛡️ **Verrouillage absolu** : Zéro opération bancaire permise. |

5. Faites défiler tout en bas de la page et cliquez sur **Créer la clé** (*Create key*).
6. **Copiez immédiatement la clé générée** (elle commence par `rk_live_...`).  
   *(⚠️ Stripe ne vous la montrera qu'une seule fois. Gardez-la dans votre presse-papier pour l'Étape 2).*

---

## ⚡ ÉTAPE 2 (CLIC 2) : Mettre à jour Render (30 secondes)

1. Ouvrez votre tableau de bord Render :  
   👉 **[dashboard.render.com](https://dashboard.render.com)**

2. Cliquez sur votre service Web :  
   👉 **`autobiz-ia-webhook`**

3. Dans le menu de gauche, cliquez sur **Environment** (Variables d'environnement).

4. Repérez ou renseignez les variables d'environnement nécessaires :  
   - **`STRIPE_SECRET_KEY`** (Clé d'API restreinte — Obligatoire pour la rotation) :  
     Cliquez dans le champ de valeur et collez votre nouvelle clé `rk_live_...`.  
     *(Si une variable `STRIPE_API_KEY` est également présente, appliquez la même modification)*.  
   - **`STRIPE_WEBHOOK_SECRET`** (Secret de signature du Webhook — Recommandé pour validation cryptographique) :  
     Pour que le serveur authentifie formellement chaque notification Stripe et passe l'indicateur `webhook_secret_set` à `true` :  
     1. Ouvrez **[dashboard.stripe.com/webhooks](https://dashboard.stripe.com/webhooks)**.  
     2. Cliquez sur votre point de terminaison (`https://autobiz-ia-webhook.onrender.com/webhook`).  
     3. Dans la section **Secret pour signer** (*Signing secret*), cliquez sur **Révéler** (*Reveal*).  
     4. Copiez la clé qui commence par `whsec_...` et collez-la dans la variable `STRIPE_WEBHOOK_SECRET` sur Render.  
     *(Si cette variable n'apparaît pas encore dans la liste Render, cliquez sur **Add Environment Variable** pour l'ajouter)*.  

5. Cliquez sur le bouton bleu en bas :  
   👉 **Save Changes** (Enregistrer les modifications).  

6. **C'est terminé !**  
   Render déclenche automatiquement le redéploiement à chaud du serveur en 30 secondes, sans interruption de service (*Zero-Downtime Deployment*).  

---

## ✅ ÉTAPE 3 : Contrôle de Fonctionnement Immédiat (10 secondes)

Pour vous assurer que le serveur a bien pris en compte votre nouvelle clé :

1. Cliquez sur le lien de diagnostic de votre serveur cloud :  
   👉 **[https://autobiz-ia-webhook.onrender.com/health](https://autobiz-ia-webhook.onrender.com/health)**

2. La page doit afficher instantanément ce statut certifié :
   ```json
   {
     "status": "healthy",
     "service": "OptiLocal Webhook Listener",
     "module": "04_distribution_ventes",
     "stripe_configured": true,
     "webhook_secret_set": true
   }
   ```

- ✅ `"stripe_configured": true` confirme que la nouvelle clé restreinte `rk_live_...` est active et valide.
- ✅ `"webhook_secret_set": true` confirme que la clé de signature `whsec_...` est configurée et sécurise les webhooks via validation cryptographique HMAC.  
  *(Note : Si vous observez temporairement `"webhook_secret_set": false`, le serveur traite tout de même les paiements en mode réceptif, mais il est vivement conseillé de renseigner `STRIPE_WEBHOOK_SECRET` selon la procédure de l'Étape 2 pour verrouiller la sécurité)*.

---

## 💻 ÉTAPE 4 (Optionnelle) : Mise à jour sur votre Ordinateur Local

Si vous effectuez des tests de développement sur votre poste personnel, mettez à jour votre fichier local `.env` (qui reste strictement sur votre machine et n'est jamais envoyé sur GitHub) :

- Fichier `modules/04_distribution_ventes/.env` :
  ```env
  STRIPE_SECRET_KEY=rk_live_VOTRE_NOUVELLE_CLE_ICI
  STRIPE_API_KEY=rk_live_VOTRE_NOUVELLE_CLE_ICI
  ```
- Fichier `modules/05_deploiement_et_lancement/.env` :
  ```env
  STRIPE_SECRET_KEY=rk_live_VOTRE_NOUVELLE_CLE_ICI
  STRIPE_API_KEY=rk_live_VOTRE_NOUVELLE_CLE_ICI
  ```

---

## ❓ FAQ & Sécurité Opérationnelle

### Que se passe-t-il si un artisan paie pendant que j'effectue le changement ?
**Aucune commande n'est perdue.** Stripe enregistre tous les paiements et conserve les événements webhook en mémoire tampon. En cas d'indisponibilité momentanée du serveur, Stripe réessaie automatiquement l'envoi toutes les heures pendant 72 heures. Dès que Render a redémarré avec la nouvelle clé, tous les événements en attente sont immédiatement délivrés et traités.

### Pourquoi le code sur GitHub n'a-t-il plus aucune clé réelle ?
Pour respecter les normes bancaires et de cybersécurité les plus strictes, tous les fichiers publics du dépôt (`.env.example`, `deploy_config.md`) n'utilisent désormais que des marqueurs fictifs `rk_live_votre_cle_ici`. Les vraies clés vivent exclusivement dans l'espace sécurisé de Render.

### Quelle est la différence entre STRIPE_SECRET_KEY et STRIPE_WEBHOOK_SECRET ?
- **`STRIPE_SECRET_KEY` (`rk_live_...`)** : C'est la clé d'authentification API qui permet à notre serveur d'interagir avec Stripe (lecture des sessions et vérification des paiements). C'est cette clé qui a fait l'objet d'une rotation suite à l'alerte.
- **`STRIPE_WEBHOOK_SECRET` (`whsec_...`)** : C'est le secret partagé permettant à notre serveur de certifier cryptographiquement qu'une notification de paiement reçue sur `/webhook` provient bien des serveurs Stripe officiels et n'a pas été usurpée par un tiers.

