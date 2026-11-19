"""
Templates d'emails transactionnels pour la livraison automatique d'audit B2B.
Offre une version HTML responsive moderne et une version texte brut optimisée
pour la délivrabilité et les filtres anti-spam.
"""

from typing import Dict, Optional, List


def get_delivery_email(
    customer_name: Optional[str] = None,
    business_name: Optional[str] = None,
    score: Optional[int] = 58,
    critical_flaws_count: int = 3,
    download_url: Optional[str] = None,
    support_email: str = "contact@optilocal.fr",
) -> Dict[str, str]:
    """
    Génère le sujet, la version HTML et la version texte brut de l'email
    de livraison du rapport d'audit après paiement de 49 €.
    """
    safe_customer = customer_name.strip() if customer_name else "Madame, Monsieur"
    safe_business = business_name.strip() if business_name else "votre établissement"
    
    subject = f"🚀 Votre Audit Stratégique Google Business [{safe_business}] est prêt !"

    # Version Texte Brut (Deliverability First)
    text_content = f"""Bonjour {safe_customer},

Nous vous confirmons la bonne réception de votre commande pour l'Audit Stratégique de :
>> {safe_business}

Votre rapport d'audit complet est généré et disponible :
- Pièce jointe : vous trouverez le fichier PDF complet de 4 pages joint à cet email.
{f"- Lien de téléchargement direct sécurisé : {download_url}" if download_url else ""}

RÉSUMÉ DU DIAGNOSTIC INITIAL :
--------------------------------------------------
* Score d'optimisation global estimé : {score}/100
* Failles critiques détectées : {critical_flaws_count} points d'attention prioritaires
* Plan d'action : 7 étapes concrètes prêtes à déployer

CE QUE VOUS DEVEZ FAIRE MAINTENANT :
1. Ouvrez le rapport PDF en pièce jointe.
2. Consultez la section "Plan d'action prioritaire sous 30 jours".
3. Utilisez les modèles de réponses pré-rédigés pour vos avis clients.

--------------------------------------------------
GARANTIE SÉRÉNITÉ ARTISAN :
Si cet audit ne vous apporte pas entière satisfaction, répondez simplement 'REMBOURSEMENT' à cet email. Vous êtes recrédité sous 2h sans aucune justification.
--------------------------------------------------

Une question ou besoin d'éclaircissements sur un point du rapport ?
Répondez simplement directement à cet email ou contactez-nous à {support_email}.

Merci pour votre confiance,

L'équipe OptiLocal
Observatoire du Référencement Local
https://optilocal.fr
"""

    # Version HTML Responsive Haute Valeur Perçue
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Votre Audit Stratégique</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #f4f6f8;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      -webkit-font-smoothing: antialiased;
    }}
    .wrapper {{
      width: 100%;
      table-layout: fixed;
      background-color: #f4f6f8;
      padding: 30px 10px;
    }}
    .main-card {{
      max-width: 600px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 15px rgba(0,0,0,0.06);
      border: 1px solid #e2e8f0;
    }}
    .header {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      padding: 36px 30px;
      text-align: center;
      color: #ffffff;
    }}
    .header h1 {{
      margin: 0;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .header p {{
      margin: 8px 0 0;
      font-size: 14px;
      color: #94a3b8;
    }}
    .content {{
      padding: 32px 30px;
    }}
    .badge {{
      display: inline-block;
      background-color: #ecfdf5;
      color: #059669;
      font-weight: 600;
      font-size: 12px;
      padding: 4px 12px;
      border-radius: 9999px;
      margin-bottom: 16px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .greeting {{
      font-size: 16px;
      line-height: 1.6;
      margin-bottom: 20px;
    }}
    .highlight-box {{
      background-color: #f8fafc;
      border-left: 4px solid #3b82f6;
      border-radius: 4px;
      padding: 18px 20px;
      margin: 24px 0;
    }}
    .score-banner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 8px;
      padding: 16px 20px;
      margin: 20px 0;
    }}
    .score-number {{
      font-size: 28px;
      font-weight: 800;
      color: #1d4ed8;
    }}
    .cta-container {{
      text-align: center;
      margin: 30px 0 24px;
    }}
    .btn {{
      display: inline-block;
      background-color: #2563eb;
      color: #ffffff !important;
      text-decoration: none;
      font-weight: 600;
      font-size: 15px;
      padding: 14px 28px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(37,99,235,0.25);
    }}
    .steps-list {{
      margin: 20px 0;
      padding-left: 20px;
      line-height: 1.7;
      color: #334155;
    }}
    .footer {{
      background-color: #f8fafc;
      padding: 24px 30px;
      border-top: 1px solid #e2e8f0;
      text-align: center;
      font-size: 12px;
      color: #64748b;
      line-height: 1.5;
    }}
    .footer a {{
      color: #2563eb;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="main-card">
      <div class="header">
        <h1>OptiLocal — Observatoire du Référencement Local</h1>
        <p>Rapport d'audit de visibilité locale généré avec succès</p>
      </div>
      <div class="content">
        <span class="badge">Commande confirmée (49,00 €)</span>
        
        <p class="greeting">
          Bonjour <strong>{safe_customer}</strong>,<br><br>
          Nous avons le plaisir de vous transmettre votre rapport stratégique personnalisé pour <strong>{safe_business}</strong>.
        </p>

        <div class="score-banner">
          <div>
            <div style="font-size: 12px; color: #475569; text-transform: uppercase; font-weight: 600;">Score d'audit initial</div>
            <div style="font-size: 14px; color: #1e293b; margin-top: 2px;">Potentiel d'acquisition inexploité</div>
          </div>
          <div class="score-number">{score}<span style="font-size: 16px; color: #64748b;">/100</span></div>
        </div>

        <div class="highlight-box">
          <p style="margin: 0; font-size: 14px; line-height: 1.5;">
            📎 <strong>Le rapport complet PDF de 4 pages est directement rattaché en pièce jointe</strong> à ce message. Vous pouvez également y accéder directement ci-dessous.
          </p>
        </div>

        {f'''<div class="cta-container">
          <a href="{download_url}" class="btn" target="_blank">📥 Télécharger mon rapport d'audit PDF</a>
        </div>''' if download_url else ''}

        <div style="background-color: #f0fdf4; border: 1px solid #86efac; border-left: 4px solid #16a34a; border-radius: 8px; padding: 18px 20px; margin: 24px 0;">
          <p style="margin: 0 0 6px; font-weight: 700; color: #15803d; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">
            🛡️ Garantie Sérénité Artisan
          </p>
          <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #166534;">
            Si cet audit ne vous apporte pas entière satisfaction, répondez simplement <strong>&laquo;&nbsp;REMBOURSEMENT&nbsp;&raquo;</strong> à cet email. Vous êtes recrédité sous 2h sans aucune justification.
          </p>
        </div>

        <p style="font-size: 14px; font-weight: 600; margin-top: 24px; margin-bottom: 8px;">
          🚀 Vos 3 actions prioritaires pour cette semaine :
        </p>
        <ol class="steps-list" style="font-size: 14px;">
          <li><strong>Corriger les {critical_flaws_count} failles majeures</strong> identifiées dans la section 2 du rapport.</li>
          <li><strong>Copier-coller les modèles de réponses</strong> pré-rédigés pour vos avis clients stratégiques.</li>
          <li><strong>Appliquer le plan d'action en 7 étapes</strong> pour dépasser vos 3 concurrents directs identifiés.</li>
        </ol>

        <p style="font-size: 13px; color: #64748b; line-height: 1.5; margin-top: 28px;">
          Une question ou un accompagnement spécifique ? Répondez simplement directement à ce courriel, un consultant de notre équipe vous répondra sous 24h ouvrées.
        </p>
      </div>

      <div class="footer">
        <p style="margin: 0 0 6px;">
          OptiLocal — Observatoire du Référencement Local • Diagnostic & Performance Locale
        </p>
        <p style="margin: 0;">
          Paiement sécurisé par Stripe • Reçu disponible sur votre espace bancaire • <a href="mailto:{support_email}">{support_email}</a>
        </p>
      </div>
    </div>
  </div>
</body>
</html>
"""
    return {
        "subject": subject,
        "text": text_content,
        "html": html_content,
    }
