#!/usr/bin/env python3
"""
Database Setup Script for Local Service Booking
This script creates the MySQL database and tables automatically.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

def setup_database():
    """Setup MySQL database and create tables"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        print("Please set DATABASE_URL=mysql+pymysql://username:password@localhost/local_service_booking")
        return False

    try:
        # Create engine
        engine = create_engine(database_url)

        # Test connection
        with engine.connect() as conn:
            print("✅ Connected to MySQL database")

            # Create database if it doesn't exist
            conn.execute(text("CREATE DATABASE IF NOT EXISTS local_service_booking"))
            print("✅ Database 'local_service_booking' created/verified")

        # Switch to the database
        db_url_with_db = database_url + '/local_service_booking'
        engine = create_engine(db_url_with_db)

        with engine.connect() as conn:
            # Create users table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    userId VARCHAR(20) UNIQUE NOT NULL,
                    fullName VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    dob DATE NOT NULL,
                    address VARCHAR(200) NOT NULL,
                    username VARCHAR(30) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    userType VARCHAR(20) NOT NULL DEFAULT 'customer',
                    status VARCHAR(20) DEFAULT 'active',
                    businessName VARCHAR(100),
                    serviceCategory VARCHAR(50),
                    experience VARCHAR(50),
                    description TEXT,
                    hourlyRate FLOAT,
                    rating FLOAT DEFAULT 0.0,
                    totalBookings INT DEFAULT 0,
                    registrationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                    lastLogin DATETIME,
                    INDEX idx_userId (userId),
                    INDEX idx_email (email),
                    INDEX idx_username (username),
                    INDEX idx_userType (userType),
                    INDEX idx_status (status)
                )
            """))

            # Create bookings table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bookingId VARCHAR(20) UNIQUE NOT NULL,
                    customerId VARCHAR(20) NOT NULL,
                    providerId VARCHAR(20),
                    serviceType VARCHAR(50),
                    serviceLocation VARCHAR(200),
                    preferredDate DATE,
                    preferredTime VARCHAR(20),
                    additionalNotes TEXT,
                    serviceAmount FLOAT,
                    serviceFee FLOAT,
                    status VARCHAR(20) DEFAULT 'pending_payment',
                    bookingDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_bookingId (bookingId),
                    INDEX idx_customerId (customerId),
                    INDEX idx_providerId (providerId),
                    INDEX idx_status (status)
                )
            """))

            print("✅ Tables created successfully")

            # Insert sample data
            try:
                conn.execute(text("""
                    INSERT IGNORE INTO users (userId, fullName, email, phone, dob, address, username, password, userType, businessName, serviceCategory, experience, hourlyRate, rating) VALUES
                    ('PROV10001', 'John Electrician', 'john@example.com', '1234567890', '1985-05-15', '123 Main St, City', 'john_electric', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8ZJcKvqUe', 'provider', 'John Electrical Services', 'electrician', '10 years', 50.00, 4.8),
                    ('PROV10002', 'Mike Plumber', 'mike@example.com', '1234567891', '1980-03-20', '456 Oak Ave, City', 'mike_plumber', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8ZJcKvqUe', 'provider', 'Mike Plumbing Co', 'plumber', '15 years', 60.00, 4.9),
                    ('PROV10003', 'Sarah Mechanic', 'sarah@example.com', '1234567892', '1990-08-10', '789 Pine Rd, City', 'sarah_mechanic', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8ZJcKvqUe', 'provider', 'Sarah Auto Repair', 'mechanic', '8 years', 45.00, 4.7)
                """))
                print("✅ Sample data inserted")
            except Exception as e:
                print(f"⚠️  Sample data insertion failed (may already exist): {e}")

        print("🎉 Database setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Run: python app.py")
        print("2. Test: http://localhost:5000/api/health")
        return True

    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Local Service Booking Database...")
    success = setup_database()
    sys.exit(0 if success else 1)