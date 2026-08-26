"""
Sends a single digest email with TWO sections: geopolitical/security
alerts and travel advisories, kept visually and logically separate since
they serve different purposes (situational awareness vs. travel risk).

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


def _format_items_table(items: list[dict]) -> str:
    rows = []
    for item in items:
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
    <table style="width:100%;border-collapse:collapse;">
        {''.join(rows)}
    </table>
    """


def _format_digest_html(geo_items: list[dict], travel_items: list[dict]) -> str:
    sections = []

    if geo_items:
        sections.append(f"""
        <h3 style="color:#1a1a1a;border-bottom:2px solid #1a5fb4;padding-bottom:6px;">
          🌍 Geopolitical &amp; Security Alerts ({len(geo_items)})
        </h3>
        {_format_items_table(geo_items)}
        """)

    if travel_items:
        sections.append(f"""
        <h3 style="color:#1a1a1a;border-bottom:2px solid #c64600;padding-bottom:6px;margin-top:28px;">
          ✈️ Travel Advisories ({len(travel_items)})
        </h3>
        {_format_items_table(travel_items)}
        """)

    total = len(geo_items) + len(travel_items)
    return f"""
    <html><body style="font-family:Arial,sans-serif;">
      <h2>Intel Monitor Digest</h2>
      <p style="color:#666;">{total} new item(s) &middot; {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
      {''.join(sections)}
    </body></html>
    """


def send_digest(email_config: dict, geo_items: list[dict], travel_items: list[dict] = None):
    travel_items = travel_items or []
    if not email_config.get("enabled") or (not geo_items and not travel_items):
        return

    total = len(geo_items) + len(travel_items)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{email_config.get('subject_prefix', '[Intel Monitor]')} {total} new item(s)"
    msg["From"] = email_config["sender_email"]
    msg["To"] = email_config["recipient_email"]

    msg.attach(MIMEText(_format_digest_html(geo_items, travel_items), "html"))

    with smtplib.SMTP(email_config["smtp_host"], email_config["smtp_port"]) as server:
        server.starttls()
        server.login(email_config["sender_email"], email_config["sender_app_password"])
        server.send_message(msg)

    print(f"  [x] Sent digest email: {len(geo_items)} geopolitical + {len(travel_items)} travel advisory item(s).")