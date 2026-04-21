import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adietalkradio_admin.settings')
django.setup()

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

print('=== SIMULATING REAL PROMOTION SUBMISSION ===')

# Simulate what happens when a user submits a form
promo_type = 'advertisement'
first_name = 'John'
recipient_email = settings.EMAIL_HOST_USER  # Send to ourselves as test
admin_email = settings.MARKETING_ADMIN_EMAIL

subject = "Your Advertisement & Sponsorship Request - AdieTalk Radio"
html_message = f"""
    <div style="font-family: sans-serif; padding: 20px; color: #333; max-width:600px;">
        <h2 style="color: #C0392B;">Let's Grow Your Brand!</h2>
        <p>Hi {first_name},</p>
        <p>Thank you for reaching out regarding advertisement and sponsorships on AdieTalk Radio.</p>
        <p>Our marketing team has received your campaign details and will be in touch within 24-48 hours.</p>
        <p>— The AdieTalk Radio Team</p>
    </div>
"""

admin_subject = f"NEW PROMOTION REQUEST: Advertisement"
admin_message = """
    <h2>New Advertisement Request</h2>
    <p><b>Name:</b> John Doe</p>
    <p><b>Email:</b> johndoe@test.com</p>
    <p><b>Phone:</b> +234 800 000 0000</p>
    <hr/>
    <p><b>Company:</b> Test Company Ltd</p>
    <p><b>Campaign Details:</b> Product launch campaign for Q2 2026</p>
"""

# Test 1: User email
print(f'\n[1] Sending user confirmation to: {recipient_email}')
try:
    msg = EmailMultiAlternatives(subject, 'Hi John, we received your request.', settings.EMAIL_HOST_USER, [recipient_email])
    msg.attach_alternative(html_message, 'text/html')
    msg.send()
    print('   SUCCESS - User email sent!')
except Exception as e:
    print(f'   FAILED - {type(e).__name__}: {e}')

# Test 2: Admin email
print(f'\n[2] Sending admin alert to: {admin_email}')
try:
    msg2 = EmailMultiAlternatives(admin_subject, 'New advertisement request from John Doe.', settings.EMAIL_HOST_USER, [admin_email])
    msg2.attach_alternative(admin_message, 'text/html')
    msg2.send()
    print('   SUCCESS - Admin email sent!')
except Exception as e:
    print(f'   FAILED - {type(e).__name__}: {e}')

print('\n=== DONE ===')
