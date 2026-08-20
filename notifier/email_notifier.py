"""
Sends a single digest email listing all newly matched items from this run.
Uses Gmail SMTP with an App Password by default (works with any SMTP host
though -- Outlook, your own mail server, etc.).

Gmail App Password setup (~1 minute), since Gmail blocks plain passwords:
1. Enable 2FA on your Google account if not already on.
2. Go to https://myaccount.google.com/apppasswords
3. Generate a password for "Mail" -> paste into config.json as sender_app_password.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def _format_digest_html(matched_items: list[dict]) -> str:
    rows = []
    for item in matched_items:
        rows.append(f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee;">
            <a href="{item['url']}" style="color:#1a5fb4;text-decoration:none;font-weight:600;">
              {item['title']}
            </a><br>
            <span style="color:#666;font-size:12px;">
              {item['source']} &middot; matched: {', '.join(item['matched_keywords'])}
              {f" &middot; {item['published_at']}" if item.get('published_at') else ''}
            </span>
          </td>
        </tr>
        """)
    return f"""
    <html><body style="font-family:Arial,sans-serif;">
      <h2>Intel Monitor Digest</h2>
      <p style="color:#666;">{len(matched_items)} new relevant item(s) &middot; {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
      <table style="width:100%;border-collapse:collapse;">
        {''.join(rows)}
      </table>
    </body></html>
    """


def send_digest(email_config: dict, matched_items: list[dict]):
    if not email_config.get("enabled") or not matched_items:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{email_config.get('subject_prefix', '[Intel Monitor]')} {len(matched_items)} new item(s)"
    msg["From"] = email_config["sender_email"]
    msg["To"] = email_config["recipient_email"]

    msg.attach(MIMEText(_format_digest_html(matched_items), "html"))

    with smtplib.SMTP(email_config["smtp_host"], email_config["smtp_port"]) as server:
        server.starttls()
        server.login(email_config["sender_email"], email_config["sender_app_password"])
        server.send_message(msg)

    print(f"  [x] Sent digest email with {len(matched_items)} item(s).")
