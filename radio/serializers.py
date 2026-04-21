from rest_framework import serializers
from .models import (
    LiveStream, Show, Podcast, NewsArticle, Banner,
    WebinarRegistration, TeamMember, Promotion, Transaction, WebinarEvent, Comment, Day,
    BroadcastNotification
)

class WebinarEventSerializer(serializers.ModelSerializer):
    flyer_url = serializers.SerializerMethodField()

    class Meta:
        model = WebinarEvent
        fields = [
            'id', 'title', 'description', 'date', 'time', 'platform', 
            'link', 'meeting_id', 'passcode', 'flyer_image', 'flyer_url', 
            'is_active', 'created_at'
        ]

    def get_flyer_url(self, obj):
        if obj.flyer_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.flyer_image.url)
            return obj.flyer_image.url
        return ""

class LiveStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStream
        fields = '__all__'

class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = ['id', 'name', 'code']

class TeamMemberSerializer(serializers.ModelSerializer):
    social_media = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'role', 'bio', 'image', 'image_url', 'social_media']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return ""

    def get_social_media(self, obj):
        return {
            "twitter": obj.twitter_url,
            "instagram": obj.instagram_url,
            "linkedin": obj.linkedin_url
        }

class ShowSerializer(serializers.ModelSerializer):
    presenter = TeamMemberSerializer(read_only=True)
    day_of_week_display = serializers.SerializerMethodField()
    days = DaySerializer(many=True, read_only=True)

    class Meta:
        model = Show
        fields = [
            'id', 'show_name', 'show_type', 'host_name', 
            'start_time', 'end_time', 'image', 'host_image_url',
            'days', 'day_of_week_display', 'is_active', 'presenter'
        ]

    def get_day_of_week_display(self, obj):
        return ", ".join([day.name for day in obj.days.all()])

class PodcastSerializer(serializers.ModelSerializer):
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Podcast
        fields = [
            'id', 'youtube_video_id', 'title', 'description', 'category', 
            'thumbnail_url', 'audio_file', 'audio_url', 'image', 'image_url',
            'published_date', 'views', 'likes_count', 'is_liked'
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return ""

    def get_is_liked(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            return obj.liked_by.filter(id=user.id).exists()
        return False

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'content', 'created_at']

    def get_user_name(self, obj):
        if obj.user.first_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.username

class NewsArticleSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'description', 'content', 'image', 'image_url', 
            'category', 'category_color', 'published_date', 
            'views', 'likes_count', 'is_liked', 'comments'
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return ""

    def get_is_liked(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            return obj.liked_by.filter(id=user.id).exists()
        return False

    def get_comments(self, obj):
        approved_comments = obj.comments.filter(is_approved=True)
        return CommentSerializer(approved_comments, many=True).data

class PromotionSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    type = serializers.CharField(source='promotion_type')

    class Meta:
        model = Promotion
        fields = ['type', 'data']

    def get_data(self, obj):
        if obj.promotion_type == 'music_airplay':
            return {
                "artist_name": obj.artist_name,
                "song_title": obj.song_title,
                "genre": obj.genre,
                "song_link": obj.song_link,
                "email": obj.email,
                "phone_number": obj.phone_number,
                "preferred_date": obj.preferred_date,
                "additional_info": obj.additional_info
            }
        elif obj.promotion_type == 'advertisement':
            return {
                "company_name": obj.company_name,
                "advertisement_type": obj.advertisement_type,
                "budget_estimation": obj.budget_estimation,
                "campaign_details": obj.campaign_details,
                "full_name": obj.full_name,
                "email": obj.email,
                "phone_number": obj.phone_number,
                "preferred_date": obj.preferred_date,
            }
        elif obj.promotion_type == 'interview_booking':
            return {
                "full_name": obj.full_name,
                "email": obj.email,
                "phone_number": obj.phone_number,
                "preferred_date": obj.preferred_date,
                "topic": obj.topic,
                "bio": obj.bio,
                "social_media": obj.social_media,
                "additional_info": obj.additional_info
            }
        else:
            return {
                "full_name": obj.full_name,
                "email": obj.email,
                "phone_number": obj.phone_number,
                "preferred_date": obj.preferred_date,
            }

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class WebinarRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WebinarRegistration
        fields = ['name', 'email', 'organization', 'phone', 'interested']

class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'image_url', 'target_url', 'is_active']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return ""

class BroadcastNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastNotification
        fields = ['id', 'title', 'body', 'notify_type', 'created_at']

