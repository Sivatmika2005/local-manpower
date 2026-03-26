# Backend Setup Guide

This guide will help you set up the complete backend system for your Local Service Booking application.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
npm install
```

### 2. Start MongoDB

Make sure MongoDB is running on your system:

**Windows:**
```bash
net start MongoDB
```

**macOS/Linux:**
```bash
sudo systemctl start mongod
```

### 3. Start the Backend Server

```bash
# Development mode (with auto-restart)
npm run dev

# Production mode
npm start
```

The server will start on `http://localhost:5000`

### 4. Test the Backend

Open your browser and visit:
```
http://localhost:5000/api/health
```

You should see:
```json
{
  "success": true,
  "message": "Server is running",
  "timestamp": "2023-10-01T12:00:00.000Z"
}
```

## 📋 Complete Setup Instructions

### Prerequisites

1. **Node.js** (v14 or higher)
2. **MongoDB** (v4.0 or higher)
3. **Git** (optional)

### Step 1: Install Node.js Dependencies

```bash
cd backend
npm install express mongoose bcryptjs jsonwebtoken cors dotenv validator
npm install --save-dev nodemon
```

### Step 2: Configure Environment Variables

Edit the `.env` file in the `backend` folder:

```env
# Server Configuration
PORT=5000
NODE_ENV=development

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/local-service-booking

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRE=7d

# CORS Configuration
FRONTEND_URL=http://localhost:3000
```

### Step 3: Start MongoDB Service

**Option 1: Local MongoDB Installation**
- Download and install MongoDB from [mongodb.com](https://www.mongodb.com/try/download/community)
- Start the MongoDB service

**Option 2: MongoDB Atlas (Cloud)**
- Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Create a free cluster
- Get your connection string
- Update `MONGODB_URI` in `.env` file

### Step 4: Run the Backend Server

```bash
# Development mode (recommended for development)
npm run dev

# Production mode
npm start
```

### Step 5: Update Frontend to Use Backend

Your frontend is already configured to use the backend! The API service is included in:
- `backend/api-service.js` - Frontend API service
- Login page updated to use backend
- Signup page updated to use backend

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/admin-login` - Admin login
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/users` - Get all users
- `GET /api/users/:userId` - Get user by ID
- `PUT /api/users/:userId` - Update user
- `DELETE /api/users/:userId` - Delete user

### Providers
- `GET /api/providers` - Get all providers
- `GET /api/providers/new` - Get new providers (last 60 min)
- `GET /api/providers/categories` - Get service categories
- `GET /api/providers/:providerId` - Get provider by ID

## 🧪 Testing the Backend

### Test Registration

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "dob": "1990-01-01",
    "address": "123 Main St, City, State",
    "username": "johndoe123",
    "password": "password123",
    "userType": "customer"
  }'
```

### Test Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe123",
    "password": "password123"
  }'
```

### Test Get Users

```bash
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🗄️ Database Schema

### Users Collection

```javascript
{
  "_id": ObjectId,
  "userId": "CUST1001",
  "fullName": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "dob": "1990-01-01T00:00:00.000Z",
  "address": "123 Main St, City, State",
  "username": "johndoe123",
  "password": "hashed_password",
  "userType": "customer",
  "status": "active",
  "registrationDate": "2023-10-01T12:00:00.000Z",
  "lastLogin": "2023-10-01T12:30:00.000Z",
  "businessName": "John's Services", // providers only
  "serviceCategory": "Plumbing", // providers only
  "experience": "5 years", // providers only
  "description": "Professional plumbing services", // providers only
  "availability": "available", // providers only
  "rating": 4.5, // providers only
  "totalBookings": 25, // providers only
  "createdAt": "2023-10-01T12:00:00.000Z",
  "updatedAt": "2023-10-01T12:00:00.000Z"
}
```

## 🔒 Security Features

- **Password Hashing**: All passwords are hashed using bcryptjs
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: All inputs are validated before processing
- **CORS Protection**: Configurable CORS settings
- **Error Handling**: Secure error responses

## 🚨 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Make sure MongoDB is running
   - Check the `MONGODB_URI` in `.env` file
   - Verify MongoDB is accessible

2. **Port Already in Use**
   - Change the `PORT` in `.env` file
   - Kill the process using the port: `netstat -ano | findstr :5000`

3. **JWT Token Issues**
   - Check `JWT_SECRET` in `.env` file
   - Make sure token is included in Authorization header

4. **CORS Issues**
   - Update `FRONTEND_URL` in `.env` file
   - Make sure frontend URL is correct

### Debug Mode

Enable debug logging by setting:
```env
NODE_ENV=development
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:5000/api/health
```

### Database Stats

```javascript
// Connect to MongoDB shell
mongo local-service-booking

// Check collections
show collections

// Count users
db.users.countDocuments()

// Count providers
db.users.countDocuments({userType: "provider"})
```

## 🚀 Deployment

### Development
```bash
npm run dev
```

### Production
```bash
# Set production environment
export NODE_ENV=production

# Start server
npm start
```

### Using PM2 (Process Manager)

```bash
# Install PM2
npm install -g pm2

# Start server with PM2
pm2 start server.js --name "service-booking-backend"

# View logs
pm2 logs service-booking-backend

# Restart server
pm2 restart service-booking-backend
```

## 📞 Support

If you encounter any issues:

1. Check the console logs for error messages
2. Verify MongoDB is running and accessible
3. Check all environment variables are set correctly
4. Make sure the frontend is pointing to the correct backend URL

The backend is now ready to handle all user and provider data for your Local Service Booking application!
