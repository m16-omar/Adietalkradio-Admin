from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class LiveStream(models.Model):
    """
    Singleton model to store the live streaming URL.
    """
    stream_url = models.URLField(max_length=500, help_text="Direct link to the audio stream (.mp3, .aac, etc.)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.stream_url

    class Meta:
        verbose_name = "Live Stream"
        verbose_name_plural = "Live Stream"

class TeamMember(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='team/')
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.role}"

class Day(models.Model):
    name = models.CharField(max_length=10, unique=True)
    code = models.CharField(max_length=3, unique=True) # MON, TUE, etc.

    class Meta:
        ordering = ['id'] # Maintain order: Mon, Tue, etc.

    def __str__(self):
        return self.name

class Show(models.Model):
    title = models.CharField(max_length=200)
    show_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    presenter = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, related_name='shows')
    image = models.ImageField(upload_to='shows/', blank=True, null=True)
    days = models.ManyToManyField(Day, related_name='shows')
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        days_str = ", ".join([day.code for day in self.days.all()])
        return f"{self.title} ({days_str} {self.start_time} - {self.end_time})"

    @property
    def show_name(self):
        return self.title

    @property
    def host_name(self):
        return self.presenter.name if self.presenter else "Unknown Host"

    @property
    def host_image_url(self):
        return self.presenter.image.url if self.presenter and self.presenter.image else ""

class Podcast(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    youtube_video_id = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, default='General')
    thumbnail_url = models.URLField(blank=True, null=True)
    audio_file = models.FileField(upload_to='podcasts/', blank=True, null=True, help_text="Upload MP3 file")
    audio_url = models.URLField(blank=True, null=True, help_text="Or provide external audio URL")
    image = models.ImageField(upload_to='podcasts/covers/', blank=True, null=True)
    published_date = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_podcasts', blank=True)
    
    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        return self.liked_by.count()

class NewsArticle(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    content = models.TextField()
    category = models.CharField(max_length=100, default='News')
    category_color = models.CharField(max_length=20, default='#FF0000') # Hex color
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    author = models.CharField(max_length=150, blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_articles', blank=True)
    
    def __str__(self):
        return self.title
    
    @property
    def likes_count(self):
        return self.liked_by.count()

    class Meta:
        verbose_name_plural = "News Articles"

class Comment(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"

    class Meta:
        ordering = ['-created_at']

class Promotion(models.Model):
    TYPE_CHOICES = [
        ('music_airplay', 'Music Airplay'),
        ('interview_booking', 'Interview Booking'),
        ('advertisement', 'Advertisement & Sponsorships'),
    ]
    
    promotion_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    
    # Music Airplay Specific
    artist_name = models.CharField(max_length=150, blank=True, null=True)
    song_title = models.CharField(max_length=150, blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    song_link = models.URLField(blank=True, null=True)
    
    # Advertisement Specific
    company_name = models.CharField(max_length=200, blank=True, null=True)
    advertisement_type = models.CharField(max_length=100, blank=True, null=True)
    budget_estimation = models.CharField(max_length=100, blank=True, null=True)
    campaign_details = models.TextField(blank=True, null=True)
    
    # Interview Specific
    topic = models.TextField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    social_media = models.TextField(blank=True, null=True)
    
    # Common/Shared Fields
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    preferred_date = models.DateField(blank=True, null=True) # Changed to DateField for YYYY-MM-DD
    additional_info = models.TextField(blank=True, null=True) # Shared by Music & Interview
    
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.promotion_type} - {self.full_name}"

class Transaction(models.Model):
    GATEWAY_CHOICES = [
        ('paystack', 'Paystack'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]
    
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='transactions')
    gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=150, unique=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gateway} - {self.reference} - {self.status}"

class WebinarRegistration(models.Model):
    webinar       = models.ForeignKey('WebinarEvent', on_delete=models.CASCADE, related_name='registrations', null=True, blank=True)
    name          = models.CharField(max_length=255)
    email         = models.EmailField()
    organization  = models.CharField(max_length=255)
    phone         = models.CharField(max_length=50)
    interested    = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'webinar')

    def __str__(self):
        return f"{self.name} registered for {self.webinar.title if self.webinar else 'General'}"

class Banner(models.Model):
    title = models.CharField(max_length=150, help_text="For internal reference")
    image = models.ImageField(upload_to='banners/')
    target_url = models.URLField(blank=True, null=True, help_text="Link to open when banner is clicked")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class WebinarEvent(models.Model):
    title = models.CharField(max_length=255, default="Adietalk Webinar")
    description = models.TextField(blank=True, null=True)
    date = models.CharField(max_length=150, help_text="e.g., Saturday, February 22, 2026")
    time = models.CharField(max_length=150, help_text="e.g., 11AM (EST) & 5PM (WAT)")
    platform = models.CharField(max_length=100, default="Zoom")
    link = models.URLField(max_length=500)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)
    passcode = models.CharField(max_length=100, blank=True, null=True)
    flyer_image = models.ImageField(upload_to='webinars/', blank=True, null=True)
    speaker_name = models.CharField(max_length=255, blank=True, null=True, default="Prof. Adie Jumbo")
    speaker_role = models.CharField(max_length=255, blank=True, null=True)
    speaker_image = models.ImageField(upload_to='webinars/speakers/', blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Only one webinar should be active at a time")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}"

    class Meta:
        verbose_name = "Webinar Event"
        verbose_name_plural = "Webinar Events"
        
    def save(self, *args, **kwargs):
        if self.is_active:
            # disable other active events to ensure only one is active at a time
            queryset = WebinarEvent.objects.filter(is_active=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            queryset.update(is_active=False)
        super().save(*args, **kwargs)

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"OTP for {self.user.username}"

class BroadcastNotification(models.Model):
    title = models.CharField(max_length=250)
    body = models.TextField()
    notify_type = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 'news', 'podcast', 'show'")
    image_url = models.URLField(max_length=500, blank=True, null=True)
    content_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID of the related object (News, Podcast, etc.)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notify_type}] {self.title}"

class ArchiveShow(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date_aired = models.DateField()
    audio_file = models.FileField(upload_to='archive_shows/audio/', blank=True, null=True, help_text="Upload MP3 file of the previous show")
    audio_url = models.URLField(blank=True, null=True, help_text="Or provide external audio URL")
    image = models.ImageField(upload_to='archive_shows/covers/', blank=True, null=True)
    presenter = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='archived_shows')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.date_aired})"

    class Meta:
        verbose_name = "Archived Show"
        verbose_name_plural = "Archived Shows"
        ordering = ['-date_aired']

class PlatformAnalytics(models.Model):
    PLATFORM_CHOICES = [
        ('web', 'Web'),
        ('android', 'Android'),
        ('ios', 'iOS'),
    ]
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True)
    views = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_platform_display()} - {self.views} views"

    class Meta:
        verbose_name = "Platform Analytics"
        verbose_name_plural = "Platform Analytics"
