import os
import sys
import traceback

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_booking.settings')

import django
django.setup()

from django.db import connections

def patch_wrapper(wrapper_class):
    original = wrapper_class.get_database_version
    def patched(self, *args, **kwargs):
        print(f"DEBUG: get_database_version called on {self.__class__} with args={args}, kwargs={kwargs}")
        try:
            return original(self, *args, **kwargs)
        except TypeError as e:
            print(f"DEBUG: TypeError in original: {e}")
            # Try calling without args if it fails
            return original(self)
    wrapper_class.get_database_version = patched
    print(f"Patched {wrapper_class}")

# Patch all loaded backends
for conn in connections.all():
    patch_wrapper(conn.__class__)

from django.core.management import call_command
try:
    print("Running migrate with monkeypatch...")
    call_command('migrate', interactive=False)
except Exception:
    print("\n--- TRACEBACK ---")
    traceback.print_exc()
    print("--- END TRACEBACK ---")
