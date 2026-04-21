from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display as unfold_display
from .models import (
    LiveStream, Show, Podcast, NewsArticle, Banner,
    WebinarRegistration, TeamMember, Promotion, Transaction, WebinarEvent, Comment, Day,
    BroadcastNotification
)

@admin.register(Day)
class DayAdmin(ModelAdmin):
    list_display = ('name', 'code')

@admin.register(LiveStream)
class LiveStreamAdmin(ModelAdmin):
    list_display = ('stream_url', 'is_active', 'updated_at')

@admin.register(Show)
class ShowAdmin(ModelAdmin):
    list_display = ('title', 'presenter', 'display_days', 'start_time', 'end_time', 'is_active')
    list_filter = ('days', 'is_active')
    search_fields = ('title', 'presenter__name')
    filter_horizontal = ('days',)

    @unfold_display(description="Days")
    def display_days(self, obj):
        return ", ".join([day.code for day in obj.days.all()])

@admin.register(Podcast)
class PodcastAdmin(ModelAdmin):
    list_display = ('title', 'category', 'views', 'likes_count', 'published_date')
    search_fields = ('title', 'category')

@admin.register(NewsArticle)
class NewsArticleAdmin(ModelAdmin):
    list_display = ('title', 'category', 'author', 'published_date', 'views', 'likes_count')
    list_filter = ('category', 'published_date')
    search_fields = ('title', 'author', 'description')

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('user', 'article', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'article__title', 'content')
    actions = ['approve_comments', 'disapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)

@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ('name', 'role')
    search_fields = ('name', 'role')

@admin.register(Promotion)
class PromotionAdmin(ModelAdmin):
    list_display = ('full_name', 'company_name', 'promotion_type', 'is_paid', 'created_at')
    list_filter = ('promotion_type', 'is_paid', 'created_at')
    search_fields = ('full_name', 'email', 'artist_name', 'song_title', 'company_name')

    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'phone_number', 'is_paid')
        }),
        ('Promotion Type', {
            'fields': ('promotion_type', 'preferred_date', 'topic')
        }),
        ('Music Airplay Details', {
            'fields': ('artist_name', 'song_title', 'genre', 'song_link'),
            'classes': ('collapse',),
            'description': 'Applicable if Promotion Type is Music Airplay'
        }),
        ('Advertisement & Sponsorships Details', {
            'fields': ('company_name', 'budget_estimation', 'campaign_details'),
            'classes': ('collapse',),
            'description': 'Applicable if Promotion Type is Advertisement & Sponsorships'
        }),
    )

@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ('reference', 'promotion', 'gateway', 'amount', 'status', 'created_at')
    list_filter = ('gateway', 'status', 'created_at')
    search_fields = ('reference', 'promotion__full_name')

@admin.register(WebinarRegistration)
class WebinarRegistrationAdmin(ModelAdmin):
    list_display = ('name', 'email', 'organization', 'phone', 'registered_at')
    search_fields = ('name', 'email', 'organization')

@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ('title', 'is_active')
    list_filter = ('is_active',)

@admin.register(WebinarEvent)
class WebinarEventAdmin(ModelAdmin):
    list_display = ('title', 'date', 'time', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'date')

@admin.register(BroadcastNotification)
class BroadcastNotificationAdmin(ModelAdmin):
    list_display = ('title', 'notify_type', 'created_at')
    list_filter = ('notify_type', 'created_at')
    search_fields = ('title', 'body')

