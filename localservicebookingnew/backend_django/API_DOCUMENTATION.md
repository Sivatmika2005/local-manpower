# API Documentation – Local Service Booking

Base URL: `http://127.0.0.1:8000/api`

---

## Authentication

All authenticated endpoints require JWT token in header:
```
Authorization: Bearer <access_token>
```

---

## 1. Authentication Endpoints

### 1.1 Register

**POST** `/auth/register`

Register a new user (customer or provider).

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "userType": "customer",
  "phone": "9876543210",
  "address": "123 Main St",
  "first_name": "John",
  "last_name": "Doe",
  
  // Provider-specific (optional, only if userType=provider)
  "service_type": "electrician",
  "location": "Mumbai",
  "price_per_hour": 500,
  "provider_phone": "9876543210"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "user": {
      "userId": "john_doe",
      "username": "john_doe",
      "email": "john@example.com",
      "fullName": "John Doe",
      "userType": "customer",
      "phone": "9876543210"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

---

### 1.2 Login

**POST** `/auth/login`

Login with username/email + password.

**Request Body:**
```json
{
  "username": "john_doe",  // or "email": "john@example.com"
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": { /* user object */ },
    "tokens": { /* JWT tokens */ }
  }
}
```

---

### 1.3 Send OTP

**POST** `/auth/otp/send`

Send OTP for phone login or password reset.

**Request Body:**
```json
{
  "identifier": "9876543210",  // phone or email
  "purpose": "phone_login"     // or "email_reset"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "OTP sent to 9876543210"
}
```

---

### 1.4 Verify OTP (Phone Login)

**POST** `/auth/otp/verify-login`

Verify OTP and login via phone number.

**Request Body:**
```json
{
  "phone": "9876543210",
  "otp": "123456"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "OTP verified",
  "data": {
    "user": { /* user object */ },
    "tokens": { /* JWT tokens */ }
  }
}
```

---

### 1.5 Verify OTP (Password Reset)

**POST** `/auth/otp/verify-reset`

Verify OTP and reset password.

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "123456",
  "new_password": "newpass123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Password reset successful"
}
```

---

## 2. Provider Endpoints

### 2.1 List Providers

**GET** `/providers/`

Get all service providers (with optional category filter).

**Query Parameters:**
- `category` (optional): `electrician`, `plumber`, or `mechanic`

**Example:**
```
GET /api/providers/?category=electrician
```

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "userId": "arun_kumar",
      "fullName": "Arun Kumar",
      "specialization": "Electrician",
      "rating": 4.8,
      "location": "Chennai",
      "price": 450.0,
      "phone": "9876543210",
      "description": "Experienced electrician...",
      "isAvailable": true,
      "experience": 8,
      "responseTime": 25
    }
  ]
}
```

---

### 2.2 Get Provider Details

**GET** `/providers/<provider_id>/`

Get detailed info for a specific provider (accepts numeric ID or username).

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": "arun_kumar",
    "fullName": "Arun Kumar",
    "specialization": "Electrician",
    "rating": 4.8,
    "location": "Chennai",
    "price": 450.0,
    "phone": "9876543210",
    "description": "Experienced electrician...",
    "isAvailable": true,
    "feedback": [
      {
        "user": "john_doe",
        "rating": 5,
        "comment": "Excellent work!",
        "date": "2026-03-20"
      }
    ]
  }
}
```

---

### 2.3 Register as Provider

**POST** `/providers/`

Register current user as a service provider (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "John's Electrical Services",
  "service_type": "electrician",
  "location": "Mumbai",
  "price_per_hour": 600,
  "phone_number": "9876543210",
  "description": "Professional electrical services..."
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Provider registered",
  "data": { /* provider object */ }
}
```

---

## 3. Booking Endpoints

### 3.1 Create Booking

**POST** `/bookings/`

Create a new service booking.

**Request Body:**
```json
{
  "providerId": 1,           // or provider username
  "date": "2026-04-15",
  "time": "09:00 AM – 11:00 AM",
  "address": "123 Main St, Mumbai"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Booking created",
  "data": {
    "bookingId": "BK123456",
    "providerName": "Arun Kumar",
    "amount": 450.0,
    "providerId": 1
  }
}
```

---

### 3.2 Get User Bookings

**GET** `/bookings/`

Get all bookings for authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "bookings": [
    {
      "id": 1,
      "bookingId": "BK123456",
      "user": 1,
      "user_name": "john_doe",
      "provider": 1,
      "provider_name": "Arun Kumar",
      "provider_service": "electrician",
      "date": "2026-04-15",
      "time": "09:00 AM – 11:00 AM",
      "address": "123 Main St",
      "status": "Pending",
      "service_amount": "450.00",
      "payment_status": "Pending",
      "payment_method": null,
      "created_at": "2026-03-24T10:30:00Z"
    }
  ]
}
```

---

### 3.3 Get Customer Bookings

**GET** `/bookings/customer/<customer_id>/`

Get all bookings for a specific customer.

---

### 3.4 Get Provider Bookings

**GET** `/bookings/provider/<provider_id>/`

Get all bookings for a specific provider.

---

### 3.5 Update Booking Status

**PATCH** `/bookings/<booking_id>/status/`

Update booking status and/or payment method.

**Request Body:**
```json
{
  "status": "Completed",
  "payment_method": "online"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Booking updated"
}
```

---

## 4. Feedback Endpoints

### 4.1 Submit Feedback

**POST** `/feedback/`

Submit feedback for a provider.

**Request Body:**
```json
{
  "provider": 1,
  "rating": 5,
  "comment": "Excellent service! Very professional."
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Feedback submitted",
  "data": {
    "id": 1,
    "user": 1,
    "user_name": "john_doe",
    "provider": 1,
    "provider_name": "Arun Kumar",
    "rating": 5,
    "comment": "Excellent service!",
    "created_at": "2026-03-24T10:30:00Z"
  }
}
```

---

### 4.2 Get All Feedback

**GET** `/feedback/`

Get all feedback records.

---

### 4.3 Get Provider Feedback

**GET** `/feedback/provider/<provider_id>/`

Get all feedback for a specific provider.

**Response (200):**
```json
{
  "success": true,
  "avg_rating": 4.8,
  "data": [
    {
      "id": 1,
      "user_name": "john_doe",
      "rating": 5,
      "comment": "Excellent!",
      "created_at": "2026-03-24T10:30:00Z"
    }
  ]
}
```

---

## 5. Payment Endpoints

### 5.1 Get Payment QR Code

**GET** `/payment/qr/?bookingId=<booking_id>`

Generate UPI QR code for payment.

**Response (200):**
```json
{
  "success": true,
  "qr_code": "iVBORw0KGgoAAAANSUhEUgAA...",  // base64 PNG
  "upi_url": "upi://pay?pa=9876543210@ybl&pn=Arun+Kumar&am=450&cu=INR",
  "amount": 450.0,
  "provider_name": "Arun Kumar",
  "phone": "9876543210"
}
```

---

## Error Responses

All endpoints return consistent error format:

**400 Bad Request:**
```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "email": ["This field is required."]
  }
}
```

**401 Unauthorized:**
```json
{
  "success": false,
  "message": "Authentication required"
}
```

**404 Not Found:**
```json
{
  "success": false,
  "message": "Provider not found"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "message": "Server error"
}
```

---

## Rate Limiting

No rate limiting currently implemented. For production, consider:
- django-ratelimit
- nginx rate limiting
- API gateway (AWS API Gateway, Kong, etc.)

---

## Pagination

Not implemented. For large datasets, add DRF pagination:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
```

---

## Testing with cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123","userType":"customer"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Get providers
curl http://localhost:8000/api/providers/

# Create booking (with JWT)
curl -X POST http://localhost:8000/api/bookings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"providerId":1,"date":"2026-04-15","time":"09:00 AM","address":"Test St"}'
```

---

## Postman Collection

Import this JSON into Postman for easy testing:

```json
{
  "info": { "name": "Local Service Booking API" },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/auth/register",
            "body": {
              "mode": "raw",
              "raw": "{\"username\":\"test\",\"email\":\"test@test.com\",\"password\":\"test123\"}"
            }
          }
        }
      ]
    }
  ],
  "variable": [
    { "key": "base_url", "value": "http://localhost:8000/api" }
  ]
}
```

---

## WebSocket Support

Not currently implemented. For real-time features (notifications, live booking updates), consider:
- Django Channels
- Socket.IO
- Server-Sent Events (SSE)
