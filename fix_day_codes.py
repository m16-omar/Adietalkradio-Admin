#!/usr/bin/env python3
"""
Fix production Day model codes.
Run this on the production server:
  python3 fix_day_codes.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adietalkradio_admin.settings')
django.setup()

from radio.models import Day

day_codes = {
    'Monday':    'MON',
    'Tuesday':   'TUE',
    'Wednesday': 'WED',
    'Thursday':  'THU',
    'Friday':    'FRI',
    'Saturday':  'SAT',
    'Sunday':    'SUN',
}

print("Current Day records:")
for day in Day.objects.all().order_by('id'):
    print(f"  id={day.id}  name={day.name!r}  code={day.code!r}")

print("\nFixing codes...")
for day in Day.objects.all():
    correct_code = day_codes.get(day.name)
    if correct_code and day.code != correct_code:
        print(f"  Updating '{day.name}': '{day.code}' -> '{correct_code}'")
        day.code = correct_code
        day.save()
    elif correct_code:
        print(f"  '{day.name}' already correct: '{day.code}'")
    else:
        print(f"  WARNING: Unknown day name '{day.name}'")

print("\nFinal Day records:")
for day in Day.objects.all().order_by('id'):
    print(f"  id={day.id}  name={day.name!r}  code={day.code!r}")
print("\nDone.")
