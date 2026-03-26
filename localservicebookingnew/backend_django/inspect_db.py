import os
import sys

# Add the project directory to sys.path
sys.path.append(r'c:\Users\23csed10\Downloads\local-service-booking-master\local-service-booking-master\backend_django')

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_booking.settings')

import django
django.setup()

from django.db import connections
connection = connections['default']

print(f"Engine: {connection.settings_dict['ENGINE']}")
print(f"Wrapper class: {connection.__class__}")
print(f"Wrapper file: {sys.modules[connection.__class__.__module__].__file__}")

try:
    method = connection.get_database_version
    print(f"get_database_version exists: {method}")
    import inspect
    print(f"Signature: {inspect.signature(method)}")
except AttributeError:
    print("get_database_version DOES NOT EXIST")
except Exception as e:
    print(f"Error accessing get_database_version: {e}")

try:
    print("Calling get_database_version()...")
    v = connection.get_database_version()
    print(f"Result: {v}")
except TypeError as e:
    print(f"TypeError on call (): {e}")

try:
    print("Calling get_database_version(None)...")
    v = connection.get_database_version(None)
    print(f"Result: {v}")
except TypeError as e:
    print(f"TypeError on call (None): {e}")
