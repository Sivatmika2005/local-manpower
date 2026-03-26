# Local Service Booking - Python Backend Setup

## Prerequisites

1. **Python 3.8+** - Download from https://python.org
2. **MySQL Server** - Download from https://dev.mysql.com/downloads/mysql/
3. **Git** (optional) - For version control

## Installation Steps

### 1. Install Python Dependencies

```bash
cd "c:\Users\Admin\Downloads\local serice booking (2) (1)\local serice booking\backend"
pip install -r requirements.txt
```

### 2. Setup MySQL Database

**Option A: Using MySQL Command Line**
```sql
-- Create database
CREATE DATABASE local_service_booking;

-- Create user (optional)
CREATE USER 'lsb_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON local_service_booking.* TO 'lsb_user'@'localhost';
FLUSH PRIVILEGES;
```

**Option B: Using MySQL Workbench**
1. Open MySQL Workbench
2. Connect to your MySQL server
3. Create new schema named `local_service_booking`

### 3. Configure Environment Variables

Update the `.env` file with your MySQL credentials:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost/local_service_booking
```

Replace:
- `username` with your MySQL username (usually 'root')
- `password` with your MySQL password

### 4. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 5. Test the Setup

Open browser and visit: `http://localhost:5000/api/health`

You should see:
```json
{
  "success": true,
  "message": "Server is running",
  "timestamp": "2026-03-17T..."
}
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login

### Providers
- `GET /api/providers?category=electrician` - Get providers by category
- `GET /api/users/{userId}` - Get user details

### Bookings
- `POST /api/bookings` - Create new booking
- `GET /api/bookings` - Get user bookings

## Troubleshooting

### MySQL Connection Issues
1. Make sure MySQL service is running
2. Check username/password in `.env`
3. Verify database exists: `local_service_booking`

### Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Python Import Errors
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## Database Schema

The application automatically creates these tables:
- `users` - User accounts (customers and providers)
- `bookings` - Service bookings

## Development

For development with auto-reload:
```bash
pip install flask[dev]
flask --app app.py run --debug
```
   sudo systemctl start mongod
   ```

5. **Run the server**
   ```bash
   # Development mode
   npm run dev
   
   # Production mode
   npm start
   ```

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/auth/register` | Register new user | Public |
| POST | `/api/auth/login` | Login user | Public |
| POST | `/api/auth/admin-login` | Admin login | Public |
| GET | `/api/auth/me` | Get current user | Private |

### Users

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/users` | Get all users | Public |
| GET | `/api/users/:userId` | Get user by ID | Public |
| PUT | `/api/users/:userId` | Update user | Private |
| DELETE | `/api/users/:userId` | Delete user | Private |
| GET | `/api/users/stats/overview` | Get user statistics | Private |

### Providers

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/providers` | Get all providers | Public |
| GET | `/api/providers/new` | Get new providers (last 60 min) | Public |
| GET | `/api/providers/categories` | Get service categories | Public |
| GET | `/api/providers/:providerId` | Get provider by ID | Public |
| PUT | `/api/providers/:providerId/rating` | Update provider rating | Private |
| PUT | `/api/providers/:providerId/availability` | Update provider availability | Private |
| GET | `/api/providers/stats/overview` | Get provider statistics | Private |

## 🔧 Database Schema

### User Model

```javascript
{
  userId: String,           // Unique user ID (CUST0001, PROV0001)
  fullName: String,         // Full name
  email: String,           // Email (unique)
  phone: String,           // Phone number
  dob: Date,               // Date of birth
  address: String,         // Address
  username: String,        // Username (unique)
  password: String,        // Hashed password
  userType: String,        // 'customer' or 'provider'
  status: String,          // 'active', 'inactive', 'suspended'
  registrationDate: Date,  // Registration date
  lastLogin: Date,         // Last login date
  profileImage: String,    // Profile image URL
  
  // Provider specific fields
  businessName: String,    // Business name
  serviceCategory: String, // Service category
  experience: String,      // Experience description
  description: String,     // Provider description
  availability: String,    // 'available', 'busy', 'offline'
  rating: Number,          // Rating (0-5)
  totalBookings: Number    // Total bookings count
}
```

## 📝 API Usage Examples

### Register a New User

```javascript
POST /api/auth/register
Content-Type: application/json

{
  "fullName": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "dob": "1990-01-01",
  "address": "123 Main St, City, State",
  "username": "johndoe123",
  "password": "password123",
  "userType": "customer"
}
```

### Login User

```javascript
POST /api/auth/login
Content-Type: application/json

{
  "username": "johndoe123",
  "password": "password123"
}
```

### Get Providers

```javascript
GET /api/providers?page=1&limit=10&category=Plumbing&sortBy=rating&sortOrder=desc
```

## 🔒 Security Features

- **Password Hashing**: Uses bcryptjs with salt rounds
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive validation for all inputs
- **CORS Protection**: Configurable CORS settings
- **Error Handling**: Secure error responses without sensitive data

## 🧪 Testing

The server includes a health check endpoint:

```bash
GET http://localhost:5000/api/health
```

Response:
```json
{
  "success": true,
  "message": "Server is running",
  "timestamp": "2023-10-01T12:00:00.000Z"
}
```

## 📦 Deployment

### Development
```bash
npm run dev
```

### Production
```bash
npm start
```

### Environment Variables
- `NODE_ENV`: Set to 'production' for production mode
- `PORT`: Server port (default: 5000)
- `MONGODB_URI`: MongoDB connection string
- `JWT_SECRET`: Secret key for JWT tokens
- `JWT_EXPIRE`: Token expiration time
- `FRONTEND_URL`: Frontend application URL for CORS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For any issues or questions, please contact the development team.
