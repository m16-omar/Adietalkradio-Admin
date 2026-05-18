from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    LiveStreamViewSet, ShowViewSet,
    PodcastViewSet, NewsArticleViewSet, BannerViewSet,
    TeamMemberViewSet, PromotionSubmitView, PaymentInitializeView, 
    PaymentVerifyView, WebinarRegisterView, UserRegistrationView,
    ActiveWebinarEventView, PastWebinarEventsView, CustomLoginView,
    PasswordResetRequestView, PasswordResetConfirmView, BroadcastNotificationViewSet,
    ArchiveShowViewSet, DeleteAccountView, GoogleAuthView
)


router = DefaultRouter()
router.register(r'livestream', LiveStreamViewSet, basename='livestream')
router.register(r'shows/schedule', ShowViewSet, basename='shows')
router.register(r'podcasts/videos', PodcastViewSet, basename='podcasts')
router.register(r'news', NewsArticleViewSet, basename='api_news')
router.register(r'banners', BannerViewSet, basename='banners')
router.register(r'team', TeamMemberViewSet, basename='team')
router.register(r'notifications', BroadcastNotificationViewSet, basename='notifications')
router.register(r'archive-shows', ArchiveShowViewSet, basename='archive-shows')

urlpatterns = [
    # Auth
    path('auth/register/', UserRegistrationView.as_view(), name='auth_register'),
    path('auth/login/', CustomLoginView.as_view(), name='auth_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/google/', GoogleAuthView.as_view(), name='auth_google'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/delete-account/', DeleteAccountView.as_view(), name='auth_delete_account'),
    
    # Promotions & Payments
    path('promotions/submit/', PromotionSubmitView.as_view(), name='promotion_submit'),
    path('payments/initialize/', PaymentInitializeView.as_view(), name='payment_initialize'),
    path('payments/verify/', PaymentVerifyView.as_view(), name='payment_verify'),
    
    # Webinar
    path('webinars/register/', WebinarRegisterView.as_view(), name='webinar_register'),
    path('webinars/current/', ActiveWebinarEventView.as_view(), name='current_webinar'),
    path('webinars/past/', PastWebinarEventsView.as_view(), name='past_webinars'),
    
    # Router endpoints (News, Shows, Podcasts, Team, etc.)
    path('', include(router.urls)),
]
