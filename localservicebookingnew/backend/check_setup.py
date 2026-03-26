#!/usr/bin/env python3
"""
Quick Setup Script for Local Service Booking
Checks prerequisites and provides setup instructions
"""

import sys
import subprocess
import os

def check_python():
    """Check if Python 3.8+ is installed"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
            return False
    except:
        print("❌ Python not found")
        return False

def check_mysql():
    """Check if MySQL is accessible"""
    try:
        result = subprocess.run(['mysql', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ MySQL - OK ({result.stdout.strip()})")
            return True
        else:
            print("❌ MySQL not accessible")
            return False
    except:
        print("❌ MySQL not found in PATH")
        return False

def check_pip_packages():
    """Check if required Python packages are installed"""
    required = ['flask', 'sqlalchemy', 'pymysql', 'bcrypt', 'python-dotenv']
    missing = []

    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - Missing")

    return len(missing) == 0, missing

def main():
    print("🔍 Checking prerequisites for Local Service Booking...\n")

    # Check Python
    python_ok = check_python()
    print()

    # Check MySQL
    mysql_ok = check_mysql()
    print()

    # Check packages
    packages_ok, missing = check_pip_packages()
    print()

    # Summary
    all_ok = python_ok and mysql_ok and packages_ok

    if all_ok:
        print("🎉 All prerequisites are met!")
        print("\n🚀 To start the application:")
        print("1. python setup_db.py    # Setup database")
        print("2. python run.py         # Start server")
        print("\n📊 Test: http://localhost:5000/api/health")
    else:
        print("⚠️  Some prerequisites are missing. Please install:")
        print()

        if not python_ok:
            print("🐍 Python 3.8+:")
            print("   Download: https://python.org/downloads/")
            print()

        if not mysql_ok:
            print("🗄️  MySQL Server:")
            print("   Download: https://dev.mysql.com/downloads/mysql/")
            print("   Or use XAMPP: https://www.apachefriends.org/")
            print()

        if missing:
            print("📦 Python packages:")
            print(f"   pip install {' '.join(missing)}")
            print()

        print("🔄 After installing, run this script again:")
        print("   python check_setup.py")

    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())