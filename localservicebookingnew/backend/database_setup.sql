-- Local Service Booking Database Setup
-- Run this script in MySQL to create the database and tables

-- Create database
CREATE DATABASE IF NOT EXISTS local_service_booking;
USE local_service_booking;

-- Create users table
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

    -- Provider specific fields
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
);

-- Create bookings table
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
);

-- Insert sample data (optional)
INSERT INTO users (userId, fullName, email, phone, dob, address, username, password, userType, businessName, serviceCategory, experience, hourlyRate, rating) VALUES
('PROV10001', 'John Electrician', 'john@example.com', '1234567890', '1985-05-15', '123 Main St, City', 'john_electric', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8ZJcKvqUe', 'provider', 'John Electrical Services', 'electrician', '10 years', 50.00, 4.8),
('PROV10002', 'Mike Plumber', 'mike@example.com', '1234567891', '1980-03-20', '456 Oak Ave, City', 'mike_plumber', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8ZJcKvqUe', 'provider', 'Mike Plumbing Co', 'plumber', '15 years', 60.00, 4.9),
('PROV10003', 'Sarah Mechanic', 'sarah@example.com', '1234567892', '1990-08-10', '789 Pine Rd, City', 'sarah_mechanic', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8ZJcKvqUe', 'provider', 'Sarah Auto Repair', 'mechanic', '8 years', 45.00, 4.7);

-- Note: The password hash above is for 'password123'
-- In production, use proper password hashing

SELECT 'Database setup completed successfully!' as message;