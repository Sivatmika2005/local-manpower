import os
import sys

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_booking.settings')

import django
django.setup()

from django.db import connections
connection = connections['default']
print(f"Engine: {connection.settings_dict['ENGINE']}")
print(f"Actual connection class: {connection.__class__}")

import inspect
try:
    method = connection.get_database_version
    print(f"Actual connection signature: {inspect.signature(method)}")
except AttributeError:
    print("get_database_version NOT FOUND on connection")

try:
    print("Calling actual connection.get_database_version()...")
    print(connection.get_database_version())
    print("Calling actual connection.get_database_version(None)...")
    print(connection.get_database_version(None))
except Exception as e:
    print(f"Error calling get_database_version: {e}")
    import traceback
    traceback.print_exc()

# Also check features
print(f"Minimum database version: {connection.features.minimum_database_version}")
