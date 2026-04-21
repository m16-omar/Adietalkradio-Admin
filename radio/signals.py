import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import (
    NewsArticle, Podcast, Show, TeamMember, WebinarEvent,
    Banner, BroadcastNotification, Promotion
)


def create_system_notification(title, body, notify_type, image_url=None, content_id=None):
    BroadcastNotification.objects.create(
        title=title,
        body=body,
        notify_type=notify_type,
        image_url=image_url,
        content_id=content_id
    )


# ─────────────────────────────────────────────────────────
# Promotion: Send confirmation + marketing alert emails
# ─────────────────────────────────────────────────────────

def _send_promotion_emails(instance):
    """Sends user confirmation & admin alert in a background thread."""
    try:
        sender     = settings.EMAIL_HOST_USER
        admin_to   = getattr(settings, 'MARKETING_ADMIN_EMAIL', 'marketing@adietalkradio.com')
        user_to    = instance.email
        first_name = (instance.full_name or 'there').split()[0]
        promo_type = instance.promotion_type

        # ── 1. Build user-facing subject & HTML ──────────
        logo_url = "https://res.cloudinary.com/dd8pvzw7m/image/upload/v1775569421/adietalk_email_logo.png"

        email_header = f"""
        <div style="background-color:#f9f9f9;padding:40px 10px;font-family:Arial,sans-serif;">
          <div style="max-width:600px;margin:auto;background-color:#ffffff;border:1px solid #e5e5e5;border-radius:4px;overflow:hidden;">
            <div style="background-color:#f4f4f4;padding:20px 30px;border-bottom:1px solid #e5e5e5;">
              <img src="{logo_url}" alt="AdieTalk Radio" style="max-height:50px;">
            </div>
            <div style="padding:40px 30px;color:#333;line-height:1.6;font-size:15px;">
        """

        email_footer = """
              <p style="margin-top:40px;">Thank you,<br>AdieTalk Radio Team</p>
            </div>
            <div style="padding:20px 30px 40px 30px;text-align:center;background-color:#ffffff;">
              <p style="font-size:12px;margin-bottom:15px;">
                <a href="https://adietalkradio.com" style="color:#0055cc;text-decoration:none;">Visit Our Website</a> | 
                <a href="mailto:marketing@adietalk.com" style="color:#0055cc;text-decoration:none;">Get Support</a>
              </p>
              <p style="color:#333;font-size:13px;font-weight:bold;margin:5px 0;">Copyright &copy; AdieTalk Radio, All rights reserved.</p>
              <p style="color:#888;font-size:12px;margin:5px 0;">358 North Avenue New Rochelle, NY 10801 United State | +1-800-655-0733</p>
            </div>
          </div>
        </div>
        """

        if promo_type == 'music_airplay':
            subject = "Your Music Airplay Submission – AdieTalk Radio"
            user_html = email_header + f"""
              <p>Thank you for contacting us. Your music airplay submission for <b>{instance.song_title or 'your track'}</b> by <b>{instance.artist_name or 'the artist'}</b> has been received and is being reviewed by our curation staff.</p>
              <p>Please note that email responses may take up to 24 to 48 business hours. Our team is available Monday through Friday, 9am-5pm.</p>
              <p>To add additional comments regarding this request, please reply to this email.</p>
            """ + email_footer

        elif promo_type == 'interview_booking':
            subject = "Your Interview Booking Request – AdieTalk Radio"
            user_html = email_header + f"""
              <p>Thank you for contacting us. Your interview booking request has been received and is being reviewed by our programming staff.</p>
              <p>Please note that email responses may take up to 24 to 48 business hours. Our team is available Monday through Friday, 9am-5pm.</p>
              <p>To add additional comments regarding this request, please reply to this email.</p>
            """ + email_footer

        elif promo_type == 'advertisement':
            subject = "Your Advertisement & Sponsorship Request – AdieTalk Radio"
            user_html = email_header + f"""
              <p>Thank you for contacting us. Your advertisement and sponsorship request has been received and is being reviewed by our marketing staff.</p>
              <p>Please note that email responses may take up to 24 to 48 business hours. Our team is available Monday through Friday, 9am-5pm.</p>
              <p>To add additional comments regarding this request, please reply to this email.</p>
            """ + email_footer

        else:
            subject = "Your Submission – AdieTalk Radio"
            user_html = email_header + f"""
              <p>Thank you for contacting us. Your request has been received and is being reviewed by our support staff.</p>
              <p>Please note that email responses may take up to 24 to 48 business hours. Our team is available Monday through Friday, 9am-5pm.</p>
              <p>To add additional comments regarding this request, please reply to this email.</p>
            """ + email_footer
        # ── 2. Send user confirmation ─────────────────────
        msg_user = EmailMultiAlternatives(
            subject=subject,
            body=f"Hi {first_name}, we received your request. Please view this email in an HTML-capable client for full details.\n\n— AdieTalk Radio Team",
            from_email=sender,
            to=[user_to],
        )
        msg_user.attach_alternative(user_html, "text/html")
        msg_user.send()

        # ── 3. Build admin alert ──────────────────────────
        admin_subject = f"🔔 NEW {promo_type.replace('_', ' ').upper()} REQUEST"
        details = ""
        if instance.artist_name:  details += f"<li><b>Artist:</b> {instance.artist_name}</li>"
        if instance.song_title:   details += f"<li><b>Song:</b> {instance.song_title}</li>"
        if instance.genre:        details += f"<li><b>Genre:</b> {instance.genre}</li>"
        if instance.company_name: details += f"<li><b>Company:</b> {instance.company_name}</li>"
        if instance.advertisement_type: details += f"<li><b>Ad Type:</b> {instance.advertisement_type}</li>"
        if instance.budget_estimation:  details += f"<li><b>Budget:</b> {instance.budget_estimation}</li>"
        if instance.topic:        details += f"<li><b>Topic:</b> {instance.topic}</li>"
        if instance.preferred_date: details += f"<li><b>Preferred Date:</b> {instance.preferred_date}</li>"

        extra = instance.campaign_details or instance.bio or instance.additional_info or "—"

        admin_html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;color:#333;">
          <h2 style="color:#C0392B;">New {promo_type.replace('_',' ').title()} Request</h2>
          <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:6px;border:1px solid #ddd;"><b>Name</b></td><td style="padding:6px;border:1px solid #ddd;">{instance.full_name}</td></tr>
            <tr><td style="padding:6px;border:1px solid #ddd;"><b>Email</b></td><td style="padding:6px;border:1px solid #ddd;">{instance.email}</td></tr>
            <tr><td style="padding:6px;border:1px solid #ddd;"><b>Phone</b></td><td style="padding:6px;border:1px solid #ddd;">{instance.phone_number or '—'}</td></tr>
          </table>
          {"<ul style='margin-top:12px;'>" + details + "</ul>" if details else ""}
          <p><b>Additional Details:</b><br>{extra}</p>
          <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
          <p style="color:#888;font-size:13px;">Manage this request in the <a href="http://127.0.0.1:8000/admin/">AdieTalk Admin Panel</a></p>
        </div>"""

        # ── 4. Send admin notification ────────────────────
        msg_admin = EmailMultiAlternatives(
            subject=admin_subject,
            body=f"New {promo_type} request from {instance.full_name} ({instance.email}). Check the admin panel for details.",
            from_email=sender,
            to=[admin_to],
        )
        msg_admin.attach_alternative(admin_html, "text/html")
        msg_admin.send()

        print(f"[Promotion Emails] ✅ Sent to user ({user_to}) and admin ({admin_to})")

    except Exception as e:
        print(f"[Promotion Email ERROR] ❌ {type(e).__name__}: {e}")


@receiver(post_save, sender=Promotion)
def on_promotion_created(sender, instance, created, **kwargs):
    """Fire emails in a background thread every time a new Promotion is saved."""
    if created:
        threading.Thread(target=_send_promotion_emails, args=(instance,), daemon=True).start()


# ─────────────────────────────────────────────────────────
# Existing model signals (unchanged)
# ─────────────────────────────────────────────────────────

@receiver(post_save, sender=NewsArticle)
def notify_new_article(sender, instance, created, **kwargs):
    if created:
        image_url = instance.image.url if instance.image else None
        create_system_notification(
            '📰 New Article Published!', instance.title, 'news',
            image_url=image_url, content_id=str(instance.id)
        )


@receiver(post_save, sender=Podcast)
def notify_new_podcast(sender, instance, created, **kwargs):
    if created:
        image_url = instance.image.url if instance.image else instance.thumbnail_url
        create_system_notification(
            '🎙️ New Podcast Uploaded!', instance.title, 'podcast',
            image_url=image_url, content_id=str(instance.id)
        )


@receiver(post_save, sender=Show)
def notify_new_show(sender, instance, created, **kwargs):
    if created and instance.is_active:
        image_url = instance.image.url if instance.image else None
        create_system_notification(
            '📻 New Radio Show Added!', instance.title, 'show',
            image_url=image_url, content_id=str(instance.id)
        )


@receiver(post_save, sender=WebinarEvent)
def notify_new_webinar(sender, instance, created, **kwargs):
    if created and instance.is_active:
        image_url = instance.flyer_image.url if instance.flyer_image else None
        create_system_notification(
            '🎓 New upcoming Webinar!', instance.title, 'webinar',
            image_url=image_url, content_id=str(instance.id)
        )


@receiver(post_save, sender=TeamMember)
def notify_new_team_member(sender, instance, created, **kwargs):
    if created:
        image_url = instance.image.url if instance.image else None
        create_system_notification(
            '👋 New Team Member!',
            f"Welcome {instance.name} to the Adietalk Radio team",
            'team', image_url=image_url, content_id=str(instance.id)
        )


@receiver(post_save, sender=Banner)
def notify_new_banner(sender, instance, created, **kwargs):
    if created and instance.is_active:
        image_url = instance.image.url if instance.image else None
        create_system_notification(
            '📣 Check out our latest update!', instance.title, 'banner',
            image_url=image_url, content_id=str(instance.id)
        )
