import os
import sys
import traceback

# Add the project directory to sys.path
sys.path.append(r'c:\Users\23csed10\Downloads\local-service-booking-master\local-service-booking-master\backend_django')

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_booking.settings')

try:
    import django
    django.setup()
    from django.core.management import call_command
    print("Running migrate...")
    call_command('migrate', interactive=False)
except Exception:
    print("\n--- FULL TRACEBACK ---")
    traceback.print_exc()
    print("--- END TRACEBACK ---\n")
    sys.exit(1)
