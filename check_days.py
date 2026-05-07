import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adietalkradio_admin.settings')
django.setup()

from radio.models import Day

for day in Day.objects.all():
    print(f"Day: {day.name}, Code: {day.code}")
