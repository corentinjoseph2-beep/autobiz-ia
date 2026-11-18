# ✉️ Séquences Cold Email B2B — Fiches Google Maps

Ce document regroupe les templates d'accroche par email pour convertir les artisans et commerçants locaux ayant des failles sur leur fiche Google Maps.

---

## 🎯 Stratégie Psychologique & Principes Directeurs

1. **Rupture de schéma (Pattern Interrupt)** : Les artisans reçoivent chaque semaine des dizaines d'emails génériques d'agences disant *"Bonjour, nous créons des sites web, voulez-vous un devis ?"*. Ces emails sont ignorés ou jetés aux spams en 2 secondes.
2. **Hyper-personnalisation chirurgicale** : On mentionne immédiatement leur note exacte (`{{note}}/5`), leur nombre d'avis (`{{nombre_avis}}`), leur ville (`{{ville}}`) et la faille spécifique repérée par notre scraper.
3. **Appât gratuit immédiat (Micro-Audit Teaser)** : Au lieu de promettre un appel téléphonique de vente de 30 minutes, on leur offre 3 constats techniques instantanés dans l'email.
4. **Offre irrésistible sans friction** : Un lien Stripe Checkout direct à **49 €** (garantie "Satisfait ou remboursé sous 14 jours"). Moins cher qu'une heure de main d'œuvre, rentabilisé dès le premier client sauvé.
5. **Délivrabilité maximale (Taux d'ouverture visé > 55%)** : Format texte brut (Plain Text), zéro image lourde, zéro pièce jointe au premier contact, aucun mot déclencheur de filtre spam (*urgent, promo, offre exceptionnelle, 100% gratuit*).

---

## 📌 Variables Dynamiques Disponibles

| Variable | Description | Exemple |
| :--- | :--- | :--- |
| `{{nom_etablissement}}` | Nom commercial de l'établissement | *Tolstoi Serrurier* |
| `{{dirigeant}}` | Nom du gérant (si extrait des mentions) | *M. Dupont* (ou vide) |
| `{{ville}}` | Ville de l'activité | *Villeurbanne* |
| `{{metier}}` | Métier / secteur d'activité | *Serrurier* / *Plombier* |
| `{{note}}` | Note Google actuelle | *3.8* ou *4.2* |
| `{{nombre_avis}}` | Nombre total d'avis | *11* |
| `{{faille_principale}}` | Phrase générée par le scraper | *aucun site web n'est relié à votre fiche* |
| `{{lien_stripe}}` | Lien de paiement unique Stripe Checkout | `https://buy.stripe.com/audit49-ref123` |

---

## 📬 Séquence 1 : J+0 — L'Alerte Bienveillante & Le Micro-Audit (L'Appât)

* **Moment d'envoi** : Mardi ou Jeudi entre 07h15 et 08h30 (heures de consultation avant le premier chantier).
* **Objet 1 (Recommandé)** : `Fiche Google {{nom_etablissement}} (remarque rapide)`
* **Objet 2 (Alternative A/B)** : `{{ville}} : un détail sur vos avis Google`

### Corps de l'email :

```text
Bonjour{{ ' ' + dirigeant if dirigeant else '' }},

En regardant les fiches des {{metier}}s sur Google Maps à {{ville}}, je suis tombé sur votre établissement {{nom_etablissement}}.

Un point précis a attiré mon attention : {{faille_principale}}.

Voici le diagnostic rapide en 3 constats :
1. Sur smartphone, Google met en avant les 3 premiers résultats locaux. Votre configuration actuelle vous fait perdre entre 25% et 40% des appels au profit de vos confrères directs.
2. Vos avis récents ne bénéficient pas d'une réponse optimisée selon les critères algorithmiques de Google (qui favorisent les réponses avec mots-clés d'intervention).
3. 2 modifications simples dans vos paramètres de fiche permettraient de sécuriser votre position locale dès cette semaine.

J'ai compilé l'audit correctif complet de votre fiche (analyse concurrentielle locale à {{ville}}, plan d'action en 7 étapes et modèles de réponses prêts à copier-coller) :

👉 Débloquer votre audit complet et votre plan d'action (49 €) :
{{lien_stripe}}

(Rapport généré immédiatement après règlement, garanti satisfait ou remboursé sous 14 jours si vous n'obtenez pas de résultat concret).

Bien cordialement,

Corentin — AutoBiz IA
Observatoire de la Visibilité Locale
P.S. : Si vous ne souhaitez plus recevoir nos analyses locales, répondez simplement "Stop".
```

---

## 📬 Séquence 2 : J+3 — Le Test du Smartphone (La Concurrence)

* **Moment d'envoi** : 3 jours après l'Email 1, à 12h15 (pause déjeuner).
* **Objet** : `Re: Fiche Google {{nom_etablissement}} (remarque rapide)` *(Conserve le fil de discussion pour doubler le taux d'ouverture)*.

### Corps de l'email :

```text
Bonjour{{ ' ' + dirigeant if dirigeant else '' }},

Je fais suite à mon message de mardi concernant votre visibilité à {{ville}}.

Faites ce test rapide depuis votre téléphone : tapez simplement "{{metier}} {{ville}}" sur Google.

Regardez les 3 premiers artisans qui s'affichent sur la carte. Ils ne sont pas forcément meilleurs sur le terrain, mais ils cumulent 3 critères techniques que votre fiche n'a pas encore validés.

Le résultat ? Chaque semaine, des particuliers qui ont besoin d'un dépannage ou d'un devis appellent ces 3 fiches en priorité.

Pour 49 € (l'équivalent de 20 minutes d'intervention), vous avez entre les mains le diagnostic exact pour surclasser ces concurrents et verrouiller vos positions :

👉 Télécharger votre audit complet :
{{lien_stripe}}

Bonne fin de semaine à vous sur vos chantiers.

Corentin
AutoBiz IA
```

---

## 📬 Séquence 3 : J+7 — La Clôture Courtoise (Le Break-up Email)

* **Moment d'envoi** : 7 jours après le premier envoi, à 18h45 (fin de journée).
* **Objet** : `Dernier message / {{nom_etablissement}}`

### Corps de l'email :

```text
Bonjour{{ ' ' + dirigeant if dirigeant else '' }},

Je me permets ce dernier mot et je ne vous relancerai plus ensuite.

Si votre carnet de rendez-vous à {{ville}} est déjà complet pour les 6 prochains mois sans avoir besoin de nouveaux appels, c'est une excellente nouvelle, ne changez rien.

En revanche, si vous constatez des périodes creuses ou que vous souhaitez que votre fiche Google devienne une source régulière d'appels entrants qualifiés, votre rapport d'audit reste disponible ici :

👉 Accéder à votre audit complet (49 €) :
{{lien_stripe}}

Je vous souhaite une excellente continuation dans votre activité.

Bien cordialement,

Corentin
AutoBiz IA
```

---

## 🛡️ Règles Strictes de Délivrabilité & Anti-Spam

1. **Volume d'envoi quotidien** :
   - Semaine 1 : 10 à 15 emails / jour
   - Semaine 2 : 20 à 25 emails / jour
   - Rythme de croisière : **30 emails / jour maximum par boîte mail**.
   - Espacement aléatoire entre chaque envoi : 4 à 8 minutes (jamais d'envoi en rafale).

2. **Configuration DNS obligatoire pour le nom de domaine dédié** :
   - **SPF** : `v=spf1 include:_spf.google.com ~all` (ou adapté selon le SMTP)
   - **DKIM** : Clé 2048 bits configurée et active
   - **DMARC** : `v=DMARC1; p=quarantine; rua=mailto:dmarc@votre-domaine.fr`
   - **Domaine d'envoi distinct** : Toujours utiliser un domaine secondaire dédié (ex: `autobiz-audit.fr` ou `avis-artisan.fr`) pour préserver la réputation de tout domaine principal.

3. **Conformité Légale B2B & RGPD (France)** :
   - En France, l'article L. 34-5 du Code des postes et des communications électroniques autorise la prospection B2B par email sans consentement préalable **dès lors que le message est en rapport direct avec la profession de la personne contactée** (ce qui est 100% le cas ici : optimisation de sa fiche professionnelle publique).
   - Obligation d'indiquer l'identité de l'expéditeur et de proposer un moyen simple et sans frais de s'opposer à la réception de nouveaux messages (la mention "P.S. : Répondez Stop" est parfaitement conforme).
