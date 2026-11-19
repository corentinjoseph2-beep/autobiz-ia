"""
Module d'envoi d'emails transactionnels avec pièce jointe (Rapport PDF).
Prend en charge :
1. SMTP standard (Brevo, Mailjet, Gmail, OVH, etc.)
2. API Resend (si configurée)
3. Mode Simulation / Fichiers locaux (si aucune clé n'est renseignée)
"""

import os
import smtplib
import mimetypes
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Dict, Any

import requests
from dotenv import load_dotenv

from email_templates import get_delivery_email

# Chargement des variables d'environnement
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


def send_delivery_email(
    to_email: str,
    customer_name: Optional[str] = None,
    business_name: Optional[str] = None,
    pdf_path: Optional[str] = None,
    score: int = 58,
    download_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Envoie l'email de livraison avec le rapport PDF en pièce jointe.
    Retourne un dictionnaire {'success': bool, 'method': str, 'detail': str}.
    """
    templates = get_delivery_email(
        customer_name=customer_name,
        business_name=business_name,
        score=score,
        download_url=download_url,
        support_email=os.getenv("SUPPORT_EMAIL", "contact@optilocal.fr"),
    )
    
    subject = templates["subject"]
    text_content = templates["text"]
    html_content = templates["html"]
    from_email = os.getenv("FROM_EMAIL", "OptiLocal <contact@optilocal.fr>")

    # 1. Vérification si Resend API est configurée
    resend_api_key = os.getenv("RESEND_API_KEY")
    if resend_api_key and not resend_api_key.startswith("votre_"):
        return _send_via_resend(
            api_key=resend_api_key,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            pdf_path=pdf_path,
        )

    # 2. Vérification si SMTP est configuré
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if smtp_host and smtp_user and smtp_password and not smtp_host.startswith("votre_"):
        return _send_via_smtp(
            smtp_host=smtp_host,
            smtp_port=int(os.getenv("SMTP_PORT", 587)),
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            pdf_path=pdf_path,
        )

    # 3. Mode Fallback / Simulation (Enregistrement local sans erreur)
    return _send_via_local_outbox(
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        pdf_path=pdf_path,
    )


def _send_via_smtp(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    from_email: str,
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str,
    pdf_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Envoi via serveur SMTP avec sécurité STARTTLS ou SSL."""
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(text_content)
        msg.add_alternative(html_content, subtype="html")

        # Pièce jointe PDF si existante
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            msg.add_attachment(
                pdf_data,
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(pdf_path),
            )

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

        return {
            "success": True,
            "method": "smtp",
            "detail": f"Email envoyé avec succès via SMTP à {to_email}",
        }
    except Exception as e:
        return {
            "success": False,
            "method": "smtp",
            "detail": f"Erreur lors de l'envoi SMTP : {str(e)}",
        }


def _send_via_resend(
    api_key: str,
    from_email: str,
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str,
    pdf_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Envoi via l'API REST de Resend (alternative ultra-rapide)."""
    import base64

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
        "text": text_content,
    }

    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            b64_pdf = base64.b64encode(f.read()).decode("utf-8")
        payload["attachments"] = [
            {
                "filename": os.path.basename(pdf_path),
                "content": b64_pdf,
            }
        ]

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code in (200, 201):
            return {
                "success": True,
                "method": "resend",
                "detail": f"Email envoyé via Resend (ID: {response.json().get('id')})",
            }
        return {
            "success": False,
            "method": "resend",
            "detail": f"Erreur Resend ({response.status_code}): {response.text}",
        }
    except Exception as e:
        return {
            "success": False,
            "method": "resend",
            "detail": f"Exception Resend : {str(e)}",
        }


def _send_via_local_outbox(
    from_email: str,
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str,
    pdf_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Mode local sans SMTP configuré : sauvegarde le message généré dans un dossier outbox/
    pour validation locale sans risque de blocage.
    """
    outbox_dir = Path(__file__).parent / "outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)

    timestamp = os.popen("date +%Y%m%d_%H%M%S").read().strip()
    html_file = outbox_dir / f"email_{timestamp}_{to_email.replace('@', '_at_')}.html"
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(f"<!-- To: {to_email} | From: {from_email} | Subject: {subject} -->\n")
        f.write(html_content)

    return {
        "success": True,
        "method": "local_outbox",
        "detail": f"[Mode Simulation Local] Email enregistré avec succès dans : {html_file.name}",
        "file_path": str(html_file),
    }
