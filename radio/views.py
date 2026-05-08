from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.views import APIView
from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import (
    LiveStream, Show, Podcast, NewsArticle, Banner,
    WebinarRegistration, TeamMember, Promotion, Transaction, Comment, WebinarEvent,
    PasswordResetOTP, BroadcastNotification, ArchiveShow
)
from .serializers import (
    LiveStreamSerializer, ShowSerializer, PodcastSerializer, 
    NewsArticleSerializer, BannerSerializer, WebinarRegistrationSerializer, 
    TeamMemberSerializer, PromotionSerializer, TransactionSerializer, 
    WebinarEventSerializer, CommentSerializer, BroadcastNotificationSerializer,
    ArchiveShowSerializer
)
import threading
from django.core.mail import send_mail, EmailMultiAlternatives
import stripe
import requests
import uuid
import random
import datetime
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import Http404

def send_background_promotion_emails(user_data, admin_data):
    """
    Sends both user and admin emails in a single background thread 
    to ensure the main response isn't delayed.
    """
    try:
        # 1. Send User Confirmation
        msg_user = EmailMultiAlternatives(
            user_data['subject'], 
            user_data['text'], 
            user_data['from'], 
            [user_data['to']]
        )
        msg_user.attach_alternative(user_data['html'], "text/html")
        msg_user.send()

        # 2. Send Admin Notification
        msg_admin = EmailMultiAlternatives(
            admin_data['subject'], 
            admin_data['text'], 
            admin_data['from'], 
            [admin_data['to']]
        )
        msg_admin.attach_alternative(admin_data['html'], "text/html")
        msg_admin.send()
        
    except Exception as e:
        print(f"[Background Email Error] Failed to send: {e}")

def send_background_webinar_emails(user_data, admin_data):
    """
    Sends both user and admin emails for webinar registration in a background thread.
    """
    try:
        # 1. Send User Confirmation
        msg_user = EmailMultiAlternatives(
            user_data['subject'], 
            user_data['text'], 
            user_data['from'], 
            [user_data['to']]
        )
        msg_user.attach_alternative(user_data['html'], "text/html")
        msg_user.send()

        # 2. Send Admin Notification
        msg_admin = EmailMultiAlternatives(
            admin_data['subject'], 
            admin_data['text'], 
            admin_data['from'], 
            [admin_data['to']]
        )
        # msg_admin.attach_alternative(admin_data['html'], "text/html") # Optional for admin
        msg_admin.send()
        
    except Exception as e:
        print(f"[Background Webinar Email Error] Failed to send: {e}")

# --- Authentication Views ---

class ActiveWebinarEventView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        active_event = WebinarEvent.objects.filter(is_active=True).first()
        if active_event:
            return Response({
                "id": active_event.id,
                "title": active_event.title,
                "description": active_event.description,
                "flyer_url": request.build_absolute_uri(active_event.flyer_image.url) if active_event.flyer_image else None,
                "speaker_name": active_event.speaker_name,
                "speaker_role": active_event.speaker_role,
                "speaker_image_url": request.build_absolute_uri(active_event.speaker_image.url) if active_event.speaker_image else None,
                "date": active_event.date,
                "time": active_event.time,
                "platform": active_event.platform,
                "passcode": active_event.passcode,
                "is_active": active_event.is_active
            }, status=status.HTTP_200_OK)
        return Response({"error": "No active webinar found"}, status=status.HTTP_404_NOT_FOUND)

class PastWebinarEventsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        past_events = WebinarEvent.objects.filter(is_active=False).order_by('-created_at')
        serializer = WebinarEventSerializer(past_events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        full_name = request.data.get('full_name')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({"error": "Email and Password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=email).exists():
            return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=email, email=email, password=password)
        first_name = full_name.split(' ')[0] if full_name else ""
        last_name = ' '.join(full_name.split(' ')[1:]) if full_name and len(full_name.split(' ')) > 1 else ""
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "User registered successfully",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": full_name or ""
            }
        }, status=status.HTTP_201_CREATED)

class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # In Django we saved the username as email
        user = authenticate(username=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": f"{user.first_name} {user.last_name}".strip()
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Placeholder for Google Identity integration
        id_token = request.data.get('id_token')
        return Response({"message": "Google Login Successful (Placeholder)", "id_token": id_token})

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if user:
            # Generate 6-digit OTP
            otp_code = str(random.randint(100000, 999999))
            # Set expiration to 10 minutes from now
            expires_at = timezone.now() + datetime.timedelta(minutes=10)
            
            # Save OTP
            PasswordResetOTP.objects.create(
                user=user,
                otp=otp_code,
                expires_at=expires_at
            )
            
            # Send email
            send_mail(
                subject="Your AdieTalk Password Reset Code",
                message=f"Your password reset code is: {otp_code}\n\nThis code expires in 10 minutes.\n\nPlease enter this code in the AdieTalk Radio app to reset your password.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=f"""
                    <div style="font-family: sans-serif; padding: 20px; color: #333;">
                        <h2 style="color: #C0392B;">AdieTalk Radio</h2>
                        <p>Use the code below to reset your password in the app:</p>
                        <div style="background: #f0f0f0; padding: 20px; font-size: 24px; font-weight: bold; border-left: 5px solid #C0392B;">
                            {otp_code}
                        </div>
                        <p>This code expires in 10 minutes.</p>
                        <p>Stay tuned,<br>AdieTalk Radio Team</p>
                    </div>
                """,
                fail_silently=False
            )

        # Always return 200 to prevent email enumeration
        return Response(
            {"message": "If an account with that email exists, an OTP has been sent."},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp_code, new_password]):
            return Response(
                {"error": "email, otp, and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        # Find valid OTP
        otp_entry = PasswordResetOTP.objects.filter(
            user=user, 
            otp=otp_code, 
            is_used=False
        ).last()

        if otp_entry and otp_entry.is_valid():
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            otp_entry.is_used = True
            otp_entry.save()
            
            return Response({"message": "Password successfully reset"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

class TeamMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TeamMember.objects.all().order_by('name')
    serializer_class = TeamMemberSerializer
    pagination_class = None
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

class LiveStreamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LiveStream.objects.filter(is_active=True).order_by('-updated_at')
    serializer_class = LiveStreamSerializer
    pagination_class = None
    authentication_classes = []
    permission_classes = [permissions.AllowAny]



class ShowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Show.objects.filter(is_active=True).order_by('start_time')
    serializer_class = ShowSerializer
    pagination_class = None
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        day = self.request.query_params.get('day_of_week')
        if day:
            # Filter by the code in the related Day model
            queryset = queryset.filter(days__code=day.upper())
        return queryset.distinct()

class PodcastViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Podcast.objects.all().order_by('-published_date')
    serializer_class = PodcastSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Podcast.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        podcast = self.get_object()
        user = request.user
        if podcast.liked_by.filter(id=user.id).exists():
            podcast.liked_by.remove(user)
            return Response({'status': 'unliked', 'likes_count': podcast.likes_count, 'is_liked': False})
        else:
            podcast.liked_by.add(user)
            return Response({'status': 'liked', 'likes_count': podcast.likes_count, 'is_liked': True})


class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.all().order_by('-published_date')
    serializer_class = NewsArticleSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        NewsArticle.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        article = self.get_object()
        user = request.user
        if article.liked_by.filter(id=user.id).exists():
            article.liked_by.remove(user)
            return Response({'status': 'unliked', 'likes_count': article.likes_count, 'is_liked': False})
        else:
            article.liked_by.add(user)
            return Response({'status': 'liked', 'likes_count': article.likes_count, 'is_liked': True})

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        article = self.get_object()
        if request.method == 'POST':
            content = request.data.get('content')
            if not content:
                return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
            comment = Comment.objects.create(
                article=article,
                user=request.user,
                content=content
            )
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        comments = article.comments.filter(is_approved=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAdminUser])
    def delete_comment(self, request, pk=None):
        comment_id = request.data.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id, article_id=pk)
        comment.delete()
        return Response({'status': 'comment deleted'}, status=status.HTTP_204_NO_CONTENT)

class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.filter(is_active=True).order_by('-id')
    serializer_class = BannerSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

class BroadcastNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BroadcastNotification.objects.all().order_by('-created_at')
    serializer_class = BroadcastNotificationSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
class ArchiveShowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArchiveShow.objects.all().order_by('-date_aired')
    serializer_class = ArchiveShowSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

# --- Promotions & Payments ---

class PromotionSubmitView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        promo_type = request.data.get('type')
        # Support both flat structure (new) and nested 'data' structure (old)
        payload = request.data.get('data', request.data)
        
        if not promo_type:
            return Response({"error": "Promotion 'type' is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            promotion = Promotion.objects.create(
                promotion_type=promo_type,
                # Music Airplay Specific
                artist_name=payload.get('artist_name'),
                song_title=payload.get('song_title'),
                genre=payload.get('genre'),
                song_link=payload.get('song_link'),
                
                # Advertisement Specific
                company_name=payload.get('company_name'),
                advertisement_type=payload.get('advertisement_type'),
                budget_estimation=payload.get('budget_estimation'),
                campaign_details=payload.get('campaign_details'),
                
                # Interview Specific
                topic=payload.get('topic'),
                bio=payload.get('bio'),
                social_media=payload.get('social_media'),
                
                # Common/Shared Fields
                full_name=payload.get('full_name') or payload.get('contact_person'), # contact_person fallback
                email=payload.get('email'),
                phone_number=payload.get('phone_number'),
                preferred_date=payload.get('preferred_date') if payload.get('preferred_date') else None,
                additional_info=payload.get('additional_info')
            )
            # Emails are sent automatically via the post_save signal in signals.py

            return Response({"id": promotion.id, "message": "Promotion submitted successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PaymentInitializeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        promo_id = request.data.get('promo_id')
        gateway = request.data.get('gateway')
        
        promotion = get_object_or_404(Promotion, id=promo_id)
        
        # Prices: Music Airplay: $50, Interview: $150
        amount = 50.00 if promotion.promotion_type == 'music_airplay' else 150.00
        reference = str(uuid.uuid4())
        
        # Create Transaction record
        Transaction.objects.create(
            promotion=promotion,
            gateway=gateway,
            amount=amount,
            reference=reference
        )
        
        if gateway == 'paystack':
            # Dummy Paystack initialization logic
            checkout_url = f"https://checkout.paystack.com/{reference}"
        elif gateway == 'stripe':
            # Dummy Stripe initialization logic
            checkout_url = f"https://checkout.stripe.com/pay/{reference}"
        elif gateway == 'paypal':
            # Dummy PayPal initialization logic
            checkout_url = f"https://www.paypal.com/checkoutnow?token={reference}"
        else:
            return Response({"error": "Unsupported gateway"}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            "checkout_url": checkout_url,
            "transaction_reference": reference
        })

class PaymentVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        reference = request.data.get('transaction_reference')
        transaction = get_object_or_404(Transaction, reference=reference)
        
        # In a real app, verify with the gateway here.
        transaction.status = 'verified'
        transaction.save()
        
        promotion = transaction.promotion
        promotion.is_paid = True
        promotion.save()
        
        return Response({"status": "success", "message": "Payment verified"})

# --- Webinar Registration ---

EVENT_DATE = "Saturday, February 22, 2026"
EVENT_TIME = "11AM (EST) & 5PM (WAT)"
EVENT_LINK = "https://us02web.zoom.us/j/86074316637?pwd=UVJqSzd6c21xZEhFcHdDaHlmMndBZz09"
MEETING_ID = "813 0543 1064"
PASSCODE   = "392742"

class WebinarRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        webinar_id = request.data.get('webinar')
        email = request.data.get('email')
        
        if WebinarRegistration.objects.filter(email=email, webinar_id=webinar_id).exists():
            return Response({'error': 'You have already registered for this webinar.'}, status=status.HTTP_409_CONFLICT)

        serializer = WebinarRegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        registration = serializer.save()

        # Get the webinar event details for confirmation
        target_webinar = registration.webinar or WebinarEvent.objects.filter(is_active=True).first()
        if target_webinar:
            event_title = target_webinar.title
            event_date  = target_webinar.date or "TBA"
            event_time  = target_webinar.time or "TBA"
            event_link  = target_webinar.link or "https://zoom.us"
            meeting_id  = target_webinar.meeting_id or "—"
            passcode    = target_webinar.passcode or "—"
        else:
            event_title = "Upcoming Webinar"
            event_date  = "Check website for dates"
            event_time  = "TBA"
            event_link  = "https://adietalkradio.com/webinars"
            meeting_id  = "813 0543 1064"
            passcode    = "392742"

        # Prepare email data (Using simplified from address for better reliability)
        from_email = settings.EMAIL_HOST_USER 
        
        user_email_data = {
            'subject': f"You're Registered! — {event_title}",
            'to': registration.email,
            'from': from_email,
            'text': (
                f"Hi {registration.name},\n\n"
                f"You're registered!\n\n"
                f"Date: {event_date}\n"
                f"Time: {event_time}\n"
                f"Link: {event_link}\n"
                f"Meeting ID: {meeting_id}\n"
                f"Passcode: {passcode}\n\n"
                "See you there!\n— The Adietalk Team"
            ),
            'html': f"""
                <div style="font-family: sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #c0392b;">🎉 You're Registered!</h2>
                    <p>Hi <strong>{registration.name}</strong>,</p>
                    <p>You have successfully registered for our upcoming webinar.</p>
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 5px 0;"><b>Event:</b> {event_title}</p>
                        <p style="margin: 5px 0;"><b>Date:</b> {event_date}</p>
                        <p style="margin: 5px 0;"><b>Time:</b> {event_time}</p>
                        <p style="margin: 5px 0;"><b>Meeting ID:</b> {meeting_id}</p>
                        <p style="margin: 5px 0;"><b>Passcode:</b> {passcode}</p>
                    </div>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{event_link}" style="background:#c0392b; color:white; padding:15px 30px; border-radius:8px; text-decoration:none; font-weight: bold; display: inline-block;">Join Webinar Now</a>
                    </div>
                    <p style="color: #666; font-size: 14px;">If the button above doesn't work, copy and paste this link into your browser:<br>{event_link}</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                    <p>See you there! <br>— The Adietalk Team</p>
                </div>
            """
        }

        admin_email_data = {
            'subject': f"New Webinar Registration: {registration.name}",
            'to': settings.EMAIL_HOST_USER,
            'from': from_email,
            'text': (
                f"A new user has registered for the webinar. Here are their details:\n\n"
                f"Name: {registration.name}\n"
                f"Email: {registration.email}\n"
                f"Phone: {registration.phone}\n"
                f"Organization: {registration.organization}\n"
                f"Interest: {registration.interested}\n"
                f"Webinar: {event_title}\n"
            )
        }

        # Send emails in background
        threading.Thread(
            target=send_background_webinar_emails,
            args=(user_email_data, admin_email_data)
        ).start()

        return Response({'message': 'Registration successful!'}, status=status.HTTP_201_CREATED)

# Helper function to fix get_object_or_404
def get_object_or_404(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise Http404("No matching object found")
def landing_page(request):
    return render(request, 'radio/landing.html')
