from .models import Show, Podcast, NewsArticle, WebinarRegistration, TeamMember
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

def dashboard_callback(request, context):
    """
    Callback for django-unfold to inject data into the admin dashboard.
    """
    # General Stat Counts
    context.update({
        "total_shows": Show.objects.count(),
        "total_podcasts": Podcast.objects.count(),
        "total_news": NewsArticle.objects.count(),
        "total_registrations": WebinarRegistration.objects.count(),
        "total_team": TeamMember.objects.count(),
    })

    # Weekly Registration Stats (for a chart)
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    
    # Example data for a chart (Labels and Values)
    # In a real app, you'd aggregate data by day
    context.update({
        "chart_labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "chart_data": [12, 19, 3, 5, 2, 3, 10], # Placeholder static data for now
    })

    return context
