import os
import django
import traceback
import sys
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_booking.settings')
try:
    django.setup()
    print("Running migrate...")
    call_command('migrate')
    print("Success!")
except Exception as e:
    print(f"Caught exception: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
