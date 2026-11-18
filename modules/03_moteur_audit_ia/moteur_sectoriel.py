"""
moteur_sectoriel.py — Intelligence Sémantique & Adaptation Sectorielle
Module 03 : Moteur d'Audit IA

Ce module analyse les métadonnées d'une fiche Google Business Profile et adapte :
- Le secteur d'activité (BTP/Artisanat, Commerces de bouche, Santé/Beauté, Services).
- Le vocabulaire métier et les métriques de manque à gagner (chantiers vs couverts vs consultations).
- Les 3 failles critiques spécifiques au secteur.
- Le plan d'action en 7 étapes d'action concrètes adapté au métier.
- Les scripts de réponses aux avis calibrés pour la réputation du domaine.
"""

import re
import unicodedata
from typing import Dict, Any

def _normaliser_texte(texte: str) -> str:
    """Retire les accents et passe en minuscules pour comparaison robuste."""
    if not texte:
        return ""
    nfkd = unicodedata.normalize('NFKD', texte.lower())
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

# Mots-clés de classification sectorielle
MOTS_CLES_SECTEURS = {
    "btp_artisanat": [
        "plomb", "electr", "macon", "couvr", "menuis", "peint", "serrur", "renov",
        "batiment", "btp", "chauffag", "clim", "garage", "mecanic", "carrosserie",
        "auto", "depann", "artisan", "isolation", "toiture", "terrassement", "paysag",
        "ramon", "vitr", "serrure", "metall", "charpent", "carrel", "facad", "travaux"
    ],
    "restauration_bouche": [
        "restau", "pizz", "brasser", "bistr", "boulang", "patiss", "traiteur",
        "bouch", "cave", "vin", "bar", "cafe", "crep", "snack", "burger", "sushi",
        "food", "chocolat", "fromag", "epicerie", "rotiss", "glac", "brunch"
    ],
    "sante_beaute": [
        "dent", "docteur", "medecin", "kine", "osteo", "optic", "pharmac", "coiff",
        "beaut", "esthet", "ongle", "barbi", "spa", "massage", "soin", "pedicur",
        "podolog", "infirm", "laser", "bien-etre", "psycho", "dermatol", "ophtalm"
    ]
}


def detecter_secteur(category: str = "", business_name: str = "") -> str:
    """
    Identifie automatiquement le secteur d'activité à partir de la catégorie
    Google Maps et du nom de l'établissement (insensible aux accents et à la casse).
    """
    texte = _normaliser_texte(f"{category} {business_name}")
    
    # 1. Test BTP / Artisanat
    for mot in MOTS_CLES_SECTEURS["btp_artisanat"]:
        if mot in texte:
            return "btp_artisanat"
            
    # 2. Test Commerces de bouche / Restauration
    for mot in MOTS_CLES_SECTEURS["restauration_bouche"]:
        if mot in texte:
            return "restauration_bouche"
            
    # 3. Test Santé / Beauté
    for mot in MOTS_CLES_SECTEURS["sante_beaute"]:
        if mot in texte:
            return "sante_beaute"
            
    # 4. Fallback générique : Services & Commerces locaux
    return "service_pro"


def extraire_ville(address: str) -> str:
    """Extrait la commune ou la ville d'une adresse française standard."""
    if not address:
        return "votre secteur"
    # Recherche code postal 5 chiffres suivi de la ville
    match = re.search(r'\b\d{5}\s+([A-Za-zÀ-ÿ\- ]+)', address)
    if match:
        return match.group(1).strip()
    # Fallback : dernier élément séparé par une virgule
    parties = address.split(",")
    if len(parties) > 1:
        return parties[-1].strip()
    return "votre localité"


def adapter_donnees_secteur(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrichit et adapte toutes les données de l'audit pour le secteur détecté.
    Garantit qu'aucun champ nécessaire au template ne reste vide.
    """
    data = dict(raw_data)
    name = data.get("business_name", "Votre Établissement")
    cat = data.get("category", "Commerce / Service local")
    addr = data.get("address", "")
    ville = extraire_ville(addr)
    
    rating = float(data.get("rating", 4.1))
    review_count = int(data.get("review_count", 25))
    response_rate = int(data.get("response_rate", 20))
    secteur = detecter_secteur(cat, name)
    data["secteur_detecte"] = secteur

    # Calcul ou inférence de notes de base si non fournies
    if "overall_score" not in data:
        base_score = int(min(95, max(30, (rating / 5.0) * 50 + min(review_count, 50) * 0.4 + (response_rate / 100.0) * 25)))
        data["overall_score"] = base_score
        
    data.setdefault("metric_completeness", 55)
    data.setdefault("metric_reputation", int(min(90, max(25, rating * 16))))
    data.setdefault("metric_activity", 30 if response_rate < 30 else 55)
    data.setdefault("metric_seo", 52)
    data.setdefault("activity_status", "Faible activité récente" if response_rate < 40 else "Actif")
    data.setdefault("local_rank", "Position #6 à #9 (Hors du Top 3 Maps)")

    # =========================================================================
    # 1. BTP & ARTISANAT (Plombier, Électricien, Maçon, Garage, Chauffagiste...)
    # =========================================================================
    if secteur == "btp_artisanat":
        data.setdefault(
            "estimated_revenue_loss",
            f"Votre fiche actuelle perd environ 4 à 8 demandes de devis et chantiers qualifiés chaque mois au profit des confrères artisans de {ville}. Sur un panier moyen de chantier de 850 € à 3 500 €, le manque à gagner est estimé à 3 400 € — 6 800 € de chiffre d'affaires mensuel."
        )
        data.setdefault("flaw_1_severity", "Priorité Critique 🔴")
        data.setdefault("flaw_1_title", f"{100 - response_rate}% des avis laissés sans réponse officielle")
        data.setdefault("flaw_1_desc", f"Les avis mentionnant des délais ou des questions techniques sont restés sans prise de parole publique. Dans l'artisanat, 84% des particuliers consultent les réponses du chef d'entreprise avant de signer un devis.")
        data.setdefault("flaw_1_impact", "L'algorithme de proximité Google Maps déclasse les profils artisans inactifs sous la 5ème position locale.")

        data.setdefault("flaw_2_severity", "Priorité Majeure 🟠")
        data.setdefault("flaw_2_title", "Rayon d'intervention géographique & catalogue prestations non renseignés")
        data.setdefault("flaw_2_desc", "La liste précise des prestations (dépannage d'urgence, installation, mise aux normes, entretien) et les communes couvertes ne sont pas déclarées dans l'outil de gestion de profil.")
        data.setdefault("flaw_2_impact", f"Votre fiche n'apparaît pas lors des recherches mobiles d'urgence géolocalisées à {ville} et aux alentours.")

        data.setdefault("flaw_3_severity", "Priorité Modérée 🟡")
        data.setdefault("flaw_3_title", "Absence de galerie photos 'Chantiers & Réalisations avant/après'")
        data.setdefault("flaw_3_desc", "Moins de 5 photos récentes. Les particuliers ont besoin de preuves visuelles de chantiers terminés, d'outillage professionnel et de véhicules logotés pour être rassurés.")
        data.setdefault("flaw_3_impact", "Taux de conversion appel téléphonique inférieur de 45% par rapport aux artisans de la zone disposant d'un portfolio visuel actif.")

        data.setdefault("step_1_title", "Activer la zone desservie (Service Area) et les communes limitrophes")
        data.setdefault("step_1_desc", f"Déclarer explicitement {ville} et les 10 communes voisines pour capter les requêtes d'artisans dans un rayon de 15 km.")

        data.setdefault("step_2_title", "Configurer les 8 prestations majeures avec mention 'Devis gratuit'")
        data.setdefault("step_2_desc", "Renseigner dépannage, rénovation, entretien, remplacement avec descriptions mot-clés et délais d'intervention moyens.")

        data.setdefault("step_3_title", "Rédiger la description avec garanties professionnelles (Décennale, Assurances)")
        data.setdefault("step_3_desc", "Mettre en avant les certifications (RGE, Qualibat, assurance décennale), la réactivité et les années de savoir-faire.")

        data.setdefault("step_4_title", "Intégrer le QR Code d'avis sur les devis, factures et camionnettes")
        data.setdefault("step_4_desc", "Systématiser la demande d'avis à la fin de chaque chantier réussi pour générer 3 à 6 avis 5 étoiles réguliers par mois.")

        data.setdefault("step_5_title", "Désamorcer les litiges et avis d'attente avec le script artisanat")
        data.setdefault("step_5_desc", "Répondre avec professionnalisme aux avis critiques en rappelant les contraintes d'approvisionnement ou d'urgence météo.")

        data.setdefault("step_6_title", "Ajouter 6 photos de chantiers réels géolocalisées par mois")
        data.setdefault("step_6_desc", "Prendre en photo les réalisations finies directement depuis le smartphone avec localisation activée.")

        data.setdefault("step_7_title", "Publier 1 Google Post bimensuel sur les disponibilités d'intervention")
        data.setdefault("step_7_desc", "Annoncer les créneaux ouverts pour les devis de saison (chauffage avant l'hiver, toiture, isolation, révision).")

        data.setdefault("review_template_negative", (
            f"« Bonjour [Nom du client],\n\n"
            f"Nous prenons note de votre avis et regrettons que votre expérience avec {name} n'ait pas été pleinement satisfaisante.\n\n"
            f"La qualité de nos réalisations et le respect de nos engagements sont au cœur de nos exigences d'artisans. "
            f"Afin de faire le point ensemble sur votre chantier et de trouver une solution rapide, je vous invite à joindre directement "
            f"notre responsable au 01 XX XX XX XX ou par email à contact@{name.lower().replace(' ', '')}.fr.\n\n"
            f"— La Direction de {name} »"
        ))
        data.setdefault("review_template_neutral", (
            f"« Bonjour [Nom du client],\n\n"
            f"Merci pour votre confiance lors de notre intervention à {ville}.\n\n"
            f"Nous sommes fiers du travail accompli et restons constamment à l'écoute pour améliorer notre réactivité et notre service. "
            f"N'hésitez pas à nous recommander à vos proches pour leurs futurs projets !\n\n"
            f"— L'équipe de {name} »"
        ))
        data.setdefault("review_template_positive", (
            f"« Bonjour [Nom du client],\n\n"
            f"Un grand merci pour votre confiance et ce retour chaleureux ! ⭐⭐⭐⭐⭐\n\n"
            f"C'est un véritable plaisir pour notre équipe d'avoir mené à bien vos travaux à {ville}. Savoir que vous êtes pleinement satisfait "
            f"de la propreté du chantier et de la qualité de pose est la plus belle des récompenses pour nos artisans.\n\n"
            f"Restant à votre entière disposition pour vos futurs projets,\n"
            f"— {name} »"
        ))
        data.setdefault("keyword_example", f"travaux et dépannage à {ville}")

    # =========================================================================
    # 2. COMMERCES DE BOUCHE & RESTAURATION (Restaurant, Pizzeria, Boulangerie)
    # =========================================================================
    elif secteur == "restauration_bouche":
        data.setdefault(
            "estimated_revenue_loss",
            f"Votre établissement perd environ 60 à 95 couverts et réservations chaque mois au profit des adresses concurrentes de {ville}. Avec un ticket moyen de 28 € à 42 € par personne, le manque à gagner direct est évalué à 2 100 € — 3 800 € de chiffre d'affaires mensuel."
        )
        data.setdefault("flaw_1_severity", "Priorité Critique 🔴")
        data.setdefault("flaw_1_title", f"{100 - response_rate}% des avis clients sans réponse")
        data.setdefault("flaw_1_desc", "Les commentaires portant sur le service ou l'attente en salle n'ont pas reçu de réponse. 89% des clients indécis lisent les réponses de la direction avant de réserver une table.")
        data.setdefault("flaw_1_impact", "Pénalité sur l'attractivité immédiate et rétrogradation dans les suggestions 'Où manger à proximité'.")

        data.setdefault("flaw_2_severity", "Priorité Majeure 🟠")
        data.setdefault("flaw_2_title", "Menu, carte des prix & spécialités du chef non intégrés")
        data.setdefault("flaw_2_desc", "L'onglet 'Menu' officiel de Google est vide ou renvoie vers un lien externe non mobile. Les clients mobiles veulent voir les formules midi, les prix et les options végétariennes en 1 clic.")
        data.setdefault("flaw_2_impact", f"Perte de visibilité sur les recherches ciblées comme 'menu du jour', 'terrasse {ville}' ou 'plat maison'.")

        data.setdefault("flaw_3_severity", "Priorité Modérée 🟡")
        data.setdefault("flaw_3_title", "Galerie photo dominée par des clichés clients de qualité inégale")
        data.setdefault("flaw_3_desc", "Absence de photos professionnelles valorisant les assiettes signature, la fraîcheur des ingrédients, la salle et l'accueil en terrasse.")
        data.setdefault("flaw_3_impact", "Baisse de 38% du taux de clics vers l'itinéraire GPS et l'appel direct.")

        data.setdefault("step_1_title", "Activer l'onglet 'Menu' officiel de Google avec les tarifs du moment")
        data.setdefault("step_1_desc", "Saisir les entrées, plats, desserts phares et formules midi avec descriptifs gourmands et prix nets.")

        data.setdefault("step_2_title", "Configurer les attributs clés (Terrasse, À emporter, Réservation, Options végé)")
        data.setdefault("step_2_desc", "Cocher l'ensemble des attributs de restauration recherchés par les consommateurs sur smartphone.")

        data.setdefault("step_3_title", "Mettre en avant le 'Fait maison' et la provenance des produits dans la description")
        data.setdefault("step_3_desc", f"Raconter l'histoire de la maison, l'ambiance chaleureuse et la localisation idéale au cœur de {ville}.")

        data.setdefault("step_4_title", "Placer un chevalet QR Code Google sur les tables et au moment de l'addition")
        data.setdefault("step_4_desc", "Inviter chaleureusement les convives ravis à partager leur expérience pour engranger 8 à 15 avis 5 étoiles par semaine.")

        data.setdefault("step_5_title", "Répondre avec élégance et bienveillance à l'ensemble des avis sous 24h")
        data.setdefault("step_5_desc", "Utiliser le script restauration pour désamorcer les déceptions d'attente lors des soirs de forte affluence.")

        data.setdefault("step_6_title", "Publier chaque semaine une photo HD du plat du jour ou de la suggestion du chef")
        data.setdefault("step_6_desc", "Stimuler l'appétit des actifs de la zone avant midi avec un visuel attractif et l'horaire de service.")

        data.setdefault("step_7_title", "Mettre à jour les horaires spéciaux (Jours fériés, ouvertures d'été)")
        data.setdefault("step_7_desc", "Éviter les avis 1 étoile évitables causés par des clients trouvant porte close un jour férié non renseigné.")

        data.setdefault("review_template_negative", (
            f"« Bonjour [Prénom du client],\n\n"
            f"Nous vous remercions d'avoir pris le temps de nous écrire. Nous sommes sincèrement désolés que votre repas chez {name} n'ait pas comblé vos attentes.\n\n"
            f"Notre équipe met un point d'honneur à régaler ses convives avec des produits frais et un service attentionné. "
            f"Lors des fortes affluences, des imprévus peuvent survenir et nous en sommes désolés. Nous serions ravis d'échanger avec vous par email à direction@{name.lower().replace(' ', '')}.fr pour vous réinviter à découvrir notre vraie cuisine.\n\n"
            f"— L'équipe de {name} »"
        ))
        data.setdefault("review_template_neutral", (
            f"« Bonjour [Prénom du client],\n\n"
            f"Merci pour votre visite chez {name} à {ville} et pour votre retour !\n\n"
            f"Nous sommes heureux que vous ayez apprécié l'ambiance et la cuisine, mais nous notons vos remarques pour progresser encore. "
            f"Au plaisir de vous surprendre lors de votre prochaine venue avec nos nouvelles suggestions de saison !\n\n"
            f"— {name} »"
        ))
        data.setdefault("review_template_positive", (
            f"« Bonjour [Prénom du client],\n\n"
            f"Toute l'équipe vous remercie infiniment pour ce magnifique commentaire et cette note 5 étoiles ! ⭐⭐⭐⭐⭐\n\n"
            f"Savoir que vous vous êtes régalé avec nos plats et que vous avez passé un agréable moment à {ville} est notre plus belle fierté. "
            f"Nous travaillons chaque jour des produits frais et passionnés pour vous offrir cette expérience.\n\n"
            f"Au plaisir de vous régaler très bientôt !\n"
            f"— L'équipe de {name} »"
        ))
        data.setdefault("keyword_example", f"cuisine maison et restaurant à {ville}")

    # =========================================================================
    # 3. SANTÉ, SOINS & BEAUTÉ (Dentiste, Kiné, Coiffure, Institut, Optique...)
    # =========================================================================
    elif secteur == "sante_beaute":
        data.setdefault(
            "estimated_revenue_loss",
            f"Votre établissement perd environ 14 à 24 nouveaux rendez-vous et consultations chaque mois au profit des confrères de {ville}. Sur un panier moyen de soin de 45 € à 130 €, le manque à gagner direct est estimé à 1 800 € — 3 100 € de chiffre d'affaires mensuel."
        )
        data.setdefault("flaw_1_severity", "Priorité Critique 🔴")
        data.setdefault("flaw_1_title", f"{100 - response_rate}% des avis patients/clients sans réponse d'écoute")
        data.setdefault("flaw_1_desc", "Dans le domaine de la santé et du soin corporel, la réassurance et l'empathie sont fondamentales. L'absence de réponse publique aux doutes ou remarques fait fuir 78% des nouveaux prospects vers d'autres cabinets.")
        data.setdefault("flaw_1_impact", "Dégradation de l'indice de confiance algorithmique et perte de position dans le Top 3 Maps.")

        data.setdefault("flaw_2_severity", "Priorité Majeure 🟠")
        data.setdefault("flaw_2_title", "Bouton de réservation directe & catalogue des soins non paramétrés")
        data.setdefault("flaw_2_desc", "Aucun lien de réservation en ligne (Doctolib, Planity, ou agenda direct) n'est connecté à la fiche. Les soins spécifiques et rituels ne sont pas détaillés avec leur durée et leurs bienfaits.")
        data.setdefault("flaw_2_impact", f"Perte de l'ensemble des rendez-vous pris le soir ou le week-end en dehors des heures d'ouverture du secrétariat.")

        data.setdefault("flaw_3_severity", "Priorité Modérée 🟡")
        data.setdefault("flaw_3_title", "Visuels froids ou absents ne reflétant pas l'atmosphère du lieu")
        data.setdefault("flaw_3_desc", "Aucune photo lumineuse du cabinet/salon, de l'espace d'attente apaisant et de l'équipe souriante pour dissiper l'appréhension des patients.")
        data.setdefault("flaw_3_impact", "Baisse de 42% du taux de clics par rapport aux profils valorisant un cadre rassurant et propre.")

        data.setdefault("step_1_title", "Connecter le lien de prise de rendez-vous en ligne immédiat")
        data.setdefault("step_1_desc", "Permettre la réservation 24h/24 en 1 clic pour capter les demandes impulsives en soirée.")

        data.setdefault("step_2_title", "Lister l'ensemble des 10 prestations clés avec durées indicatives")
        data.setdefault("step_2_desc", f"Détailler les actes et soins spécialisés les plus recherchés à {ville} avec clarté et bienveillance.")

        data.setdefault("step_3_title", "Optimiser la description axée sur le confort, l'écoute et l'hygiène")
        data.setdefault("step_3_desc", "Souligner l'approche personnalisée, les qualifications professionnelles et la facilité d'accès (parking, transports).")

        data.setdefault("step_4_title", "Installer une carte de réassurance et QR Code discret à l'accueil")
        data.setdefault("step_4_desc", "Proposer aux patients/clients comblés de laisser un mot d'encouragement au moment de leur départ.")

        data.setdefault("step_5_title", "Appliquer le protocole de réponse diplomatique à 100% des avis sous 48h")
        data.setdefault("step_5_desc", "Désamorcer les remarques sur les délais d'attente avec humanité en expliquant la gestion des soins d'urgence.")

        data.setdefault("step_6_title", "Publier 8 photos lumineuses mettant en valeur la propreté et la sérénité des lieux")
        data.setdefault("step_6_desc", "Montrer l'espace de soin propre, le matériel de pointe et un accueil chaleureux.")

        data.setdefault("step_7_title", "Partager 1 conseil santé/beauté par mois via Google Post")
        data.setdefault("step_7_desc", "Informer sur la prévention saisonnière, les nouveautés de soins ou les consignes pratiques.")

        data.setdefault("review_template_negative", (
            f"« Bonjour [Nom du patient/client],\n\n"
            f"Nous vous remercions pour votre retour. Nous regrettons sincèrement que votre expérience chez {name} n'ait pas été à la hauteur de vos espérances.\n\n"
            f"L'écoute, la douceur et l'hygiène sont les piliers absolus de notre pratique. Lors des journées chargées ou de prises en charge complexes, des décalages peuvent parfois survenir. "
            f"Nous serions très heureux d'échanger directement avec vous par téléphone au 01 XX XX XX XX pour entendre vos remarques et rétablir votre pleine confiance.\n\n"
            f"— L'équipe de {name} »"
        ))
        data.setdefault("review_template_neutral", (
            f"« Bonjour [Nom du patient/client],\n\n"
            f"Merci d'avoir pris le temps de donner votre avis suite à votre passage chez {name} à {ville}.\n\n"
            f"Votre satisfaction nous tient à cœur et nous prenons note de vos remarques pour perfectionner l'accueil et le confort de notre espace. "
            f"Au plaisir de vous accompagner lors de votre prochain rendez-vous !\n\n"
            f"— {name} »"
        ))
        data.setdefault("review_template_positive", (
            f"« Bonjour [Nom du patient/client],\n\n"
            f"Un grand merci pour vos encouragements et pour cette excellente note ! ⭐⭐⭐⭐⭐\n\n"
            f"Savoir que vous vous êtes senti en totale confiance et satisfait de la qualité de nos soins à {ville} est une merveilleuse récompense pour toute notre équipe. "
            f"Nous mettons tout notre cœur pour que chaque rendez-vous soit un moment de sérénité.\n\n"
            f"Prenez bien soin de vous et à très bientôt !\n"
            f"— Toute l'équipe de {name} »"
        ))
        data.setdefault("keyword_example", f"soins et rendez-vous à {ville}")

    # =========================================================================
    # 4. SERVICES PRO & COMMERCES GÉNÉRAUX (Auto-école, Agence, Pressing...)
    # =========================================================================
    else:
        data.setdefault(
            "estimated_revenue_loss",
            f"Votre établissement perd environ 8 à 15 prospects qualifiés chaque mois au profit de vos concurrents directs de {ville}, représentant une perte estimée à 1 500 € — 3 500 € de chiffre d'affaires mensuel."
        )
        data.setdefault("flaw_1_severity", "Priorité Critique 🔴")
        data.setdefault("flaw_1_title", f"{100 - response_rate}% des avis clients sans réponse")
        data.setdefault("flaw_1_desc", "Les avis clients sont laissés sans suivi officiel, ce qui freine la réassurance des prospects comparant plusieurs prestataires locaux.")
        data.setdefault("flaw_1_impact", "Perte de réputation locale et baisse de classement dans le moteur de recherche Google Maps.")

        data.setdefault("flaw_2_severity", "Priorité Majeure 🟠")
        data.setdefault("flaw_2_title", "Services et prestations détaillées absents")
        data.setdefault("flaw_2_desc", "Les prestations principales ne sont pas listées avec leurs caractéristiques et tarifs indicatifs.")
        data.setdefault("flaw_2_impact", "Déclassement lors des recherches vocales et mobiles géolocalisées.")

        data.setdefault("flaw_3_severity", "Priorité Modérée 🟡")
        data.setdefault("flaw_3_title", "Manque de signaux d'activité et de fraîcheur")
        data.setdefault("flaw_3_desc", "Aucun Google Post récent ni mise à jour des photos de façade et d'équipe.")
        data.setdefault("flaw_3_impact", "Google privilégie les profils locaux mettant à jour leurs données au moins une fois par mois.")

        data.setdefault("step_1_title", "Compléter les catégories métiers primaires et secondaires")
        data.setdefault("step_1_desc", "Associer 3 à 5 catégories précises pour couvrir l'ensemble du périmètre d'activité.")

        data.setdefault("step_2_title", "Publier la liste complète des prestations proposées")
        data.setdefault("step_2_desc", f"Décrire chaque service avec précision et intégrer la localité {ville}.")

        data.setdefault("step_3_title", "Optimiser la description d'établissement avec vos points forts")
        data.setdefault("step_3_desc", "Exploiter les 750 caractères pour présenter l'expertise, les garanties et l'accès.")

        data.setdefault("step_4_title", "Mettre en place un protocole de collecte d'avis clients")
        data.setdefault("step_4_desc", "Solliciter les clients satisfaits par SMS, QR Code ou email post-prestation.")

        data.setdefault("step_5_title", "Répondre systématiquement aux avis sous 48h")
        data.setdefault("step_5_desc", "Désamorcer les critiques avec courtoisie et remercier chaleureusement les avis 5 étoiles.")

        data.setdefault("step_6_title", "Ajouter 5 photos authentiques de vos locaux et de votre équipe")
        data.setdefault("step_6_desc", "Humaniser votre entreprise et rassurer immédiatement les visiteurs.")

        data.setdefault("step_7_title", "Publier une actualité Google Post par quinzaine")
        data.setdefault("step_7_desc", "Informer les clients des nouveautés, offres saisonnières ou horaires modifiés.")

        data.setdefault("review_template_negative", (
            f"« Bonjour [Nom du client],\n\n"
            f"Nous prenons note de votre retour et regrettons que notre service n'ait pas été à la hauteur de vos attentes.\n\n"
            f"La satisfaction de nos clients est notre priorité. Afin de comprendre ce qui s'est passé et trouver une solution, "
            f"je vous invite à me joindre directement au 01 XX XX XX XX ou par email à direction@{name.lower().replace(' ', '')}.fr.\n\n"
            f"— La Direction de {name} »"
        ))
        data.setdefault("review_template_neutral", (
            f"« Bonjour [Nom du client],\n\n"
            f"Merci pour votre confiance chez {name} à {ville}.\n\n"
            f"Nous prenons note de vos remarques pour perfectionner continuellement notre service. Au plaisir de vous revoir !\n\n"
            f"— {name} »"
        ))
        data.setdefault("review_template_positive", (
            f"« Bonjour [Nom du client],\n\n"
            f"Merci beaucoup pour votre recommandation et votre note 5 étoiles ! ⭐⭐⭐⭐⭐\n\n"
            f"Toute l'équipe est ravie d'avoir pu répondre à vos attentes à {ville}. Votre fidélité et votre confiance sont notre meilleure motivation.\n\n"
            f"Au plaisir de vous accompagner à nouveau,\n"
            f"— {name} »"
        ))
        data.setdefault("keyword_example", f"prestations et services à {ville}")

    # Données de concurrence synthétisées si non fournies
    data.setdefault("competitor_1_name", f"Leader Concurrent {ville}")
    data.setdefault("competitor_1_rating", 4.8)
    data.setdefault("competitor_1_reviews", max(85, review_count * 2))
    data.setdefault("competitor_2_name", f"Second Concurrent {ville}")
    data.setdefault("competitor_2_rating", 4.6)
    data.setdefault("competitor_2_reviews", max(55, int(review_count * 1.5)))
    data.setdefault("competitor_avg_rating", 4.7)
    data.setdefault("competitor_avg_reviews", max(70, int(review_count * 1.7)))

    return data
