import os
import sys
from django.db.backends.base.base import BaseDatabaseWrapper

print(f"BaseDatabaseWrapper version: {BaseDatabaseWrapper.__module__}")
print(f"get_database_version in BaseDatabaseWrapper dict: {'get_database_version' in BaseDatabaseWrapper.__dict__}")
if 'get_database_version' in BaseDatabaseWrapper.__dict__:
    attr = BaseDatabaseWrapper.__dict__['get_database_version']
    print(f"Attribute type: {type(attr)}")
    if isinstance(attr, property):
        print("IT IS A PROPERTY!")
    else:
        print("IT IS NOT A PROPERTY")

from mysql.connector.django.base import DatabaseWrapper as MySQLConnectorWrapper
print(f"\nMySQLConnectorWrapper: {MySQLConnectorWrapper}")
print(f"get_database_version in MySQLConnectorWrapper dict: {'get_database_version' in MySQLConnectorWrapper.__dict__}")
attr = MySQLConnectorWrapper.__dict__['get_database_version']
print(f"Attribute type: {type(attr)}")
