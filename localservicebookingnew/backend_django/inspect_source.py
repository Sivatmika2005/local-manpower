import os
import sys

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_booking.settings')

import django
django.setup()

from django.db import connections
connection = connections['default']

import inspect
try:
    method = connection.get_database_version
    print(f"File: {inspect.getfile(method)}")
    print("--- SOURCE ---")
    print(inspect.getsource(method))
    print("--- END SOURCE ---")
except Exception as e:
    print(f"Error: {e}")

try:
    from django.db.backends.base.base import BaseDatabaseWrapper
    print(f"\nBaseDatabaseWrapper File: {inspect.getfile(BaseDatabaseWrapper.get_database_version)}")
    print("--- BASE SOURCE ---")
    print(inspect.getsource(BaseDatabaseWrapper.get_database_version))
    print("--- END BASE SOURCE ---")
except Exception as e:
    print(f"Error inspecting base: {e}")
