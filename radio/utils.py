from .models import Show, Podcast, NewsArticle, WebinarRegistration, TeamMember, PlatformAnalytics
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
        
    max_val = max(data) if data and max(data) > 0 else 10
    
    chart_stats = []
    for lbl, dt in zip(labels, data):
        height = int((dt / max_val) * 100) if max_val > 0 else 0
        if height < 5: height = 5 # Ensure minimum visible height
        chart_stats.append({
            'label': lbl,
            'data': dt,
            'height': height
        })

    # Real Monthly Registration Stats for the last 7 months
    monthly_labels = []
    monthly_data = []
    
    for i in range(6, -1, -1):
        # Calculate the month and year
        month_target = now.month - i
        year_target = now.year
        if month_target <= 0:
            month_target += 12
            year_target -= 1
            
        count = WebinarRegistration.objects.filter(
            registered_at__year=year_target,
            registered_at__month=month_target
        ).count()
        
        # Get month abbreviation (e.g., "Jan", "Feb")
        import calendar
        monthly_labels.append(calendar.month_abbr[month_target])
        monthly_data.append(count)
        
    monthly_max_val = max(monthly_data) if monthly_data and max(monthly_data) > 0 else 10
    
    monthly_chart_stats = []
    for lbl, dt in zip(monthly_labels, monthly_data):
        height = int((dt / monthly_max_val) * 100) if monthly_max_val > 0 else 0
        if height < 5: height = 5
        monthly_chart_stats.append({
            'label': lbl,
            'data': dt,
            'height': height
        })

    import json
    
    context.update({
        "chart_labels": json.dumps(labels),
        "chart_data": json.dumps(data),
        "chart_stats": chart_stats,
        "max_chart_value": max_val,
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_data),
        "monthly_chart_stats": monthly_chart_stats,
        "monthly_max_chart_value": monthly_max_val,
    })

    # Platform Analytics
    web_views = 0
    android_views = 0
    ios_views = 0

    try:
        web_obj = PlatformAnalytics.objects.filter(platform='web').first()
        if web_obj: web_views = web_obj.views
        
        android_obj = PlatformAnalytics.objects.filter(platform='android').first()
        if android_obj: android_views = android_obj.views
        
        ios_obj = PlatformAnalytics.objects.filter(platform='ios').first()
        if ios_obj: ios_views = ios_obj.views
    except Exception:
        pass
        
    total_platform_views = web_views + android_views + ios_views
    if total_platform_views == 0:
        total_platform_views = 1 # Avoid division by zero
        
    context.update({
        "web_views": web_views,
        "android_views": android_views,
        "ios_views": ios_views,
        "web_percent": int((web_views / total_platform_views) * 100),
        "android_percent": int((android_views / total_platform_views) * 100),
        "ios_percent": int((ios_views / total_platform_views) * 100),
    })

    return context
