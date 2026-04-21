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

    # Real Daily Registration Stats for the last 7 days
    now = timezone.now()
    labels = []
    data = []
    
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        count = WebinarRegistration.objects.filter(
            registered_at__year=day.year,
            registered_at__month=day.month,
            registered_at__day=day.day
        ).count()
        labels.append(day.strftime("%a"))
        data.append(count)
        
    context.update({
        "chart_labels": labels,
        "chart_data": data,
    })

    return context
