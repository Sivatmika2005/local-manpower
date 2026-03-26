from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import bcrypt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root@localhost/local_service_booking')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String(20), unique=True, index=True)
    fullName = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    dob = Column(Date)
    address = Column(String(200))
    username = Column(String(30), unique=True, index=True)
    password = Column(String(255))
    userType = Column(String(20))  # 'customer' or 'provider'
    status = Column(String(20), default='active')

    # Provider specific fields
    businessName = Column(String(100))
    serviceCategory = Column(String(50))
    experience = Column(String(50))
    description = Column(Text)
    hourlyRate = Column(Float)
    rating = Column(Float, default=0.0)
    totalBookings = Column(Integer, default=0)

    registrationDate = Column(DateTime, default=datetime.utcnow)
    lastLogin = Column(DateTime)

    @staticmethod
    def generate_user_id(user_type):
        prefix = 'PROV' if user_type == 'provider' else 'CUST'
        import random
        number = str(random.randint(10000, 99999))
        return f"{prefix}{number}"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    bookingId = Column(String(20), unique=True, index=True)
    customerId = Column(String(20))
    providerId = Column(String(20))
    serviceType = Column(String(50))
    serviceLocation = Column(String(200))
    preferredDate = Column(Date)
    preferredTime = Column(String(20))
    additionalNotes = Column(Text)
    serviceAmount = Column(Float)
    serviceFee = Column(Float)
    status = Column(String(20), default='pending_payment')
    bookingDate = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Helper Functions
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_booking_id():
    return f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Server is running',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Validation
        required_fields = ['fullName', 'email', 'phone', 'dob', 'address', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400

        db = get_db()

        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == data['email']) | (User.username == data['username'])
        ).first()

        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email or username already exists'
            }), 400

        # Generate user ID
        user_id = User.generate_user_id(data.get('userType', 'customer'))

        # Create user
        user = User(
            userId=user_id,
            fullName=data['fullName'],
            email=data['email'],
            phone=data['phone'],
            dob=datetime.strptime(data['dob'], '%Y-%m-%d').date(),
            address=data['address'],
            username=data['username'],
            password=hash_password(data['password']),
            userType=data.get('userType', 'customer')
        )

        # Add provider fields if user is provider
        if data.get('userType') == 'provider':
            user.businessName = data.get('businessName', data['fullName'])
            user.serviceCategory = data.get('serviceCategory', 'General')
            user.experience = data.get('experience', '')
            user.description = data.get('description', '')
            user.hourlyRate = float(data.get('hourlyRate', 0))

        db.add(user)
        db.commit()
        db.refresh(user)

        # Generate token
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': {
                    'userId': user.userId,
                    'fullName': user.fullName,
                    'email': user.email,
                    'userType': user.userType,
                    'businessName': user.businessName,
                    'serviceCategory': user.serviceCategory,
                    'hourlyRate': user.hourlyRate
                },
                'token': access_token
            }
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400

        db = get_db()
        user = db.query(User).filter(User.username == username).first()

        if not user or not check_password(password, user.password):
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401

        # Update last login
        user.lastLogin = datetime.utcnow()
        db.commit()

        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': {
                    'userId': user.userId,
                    'fullName': user.fullName,
                    'email': user.email,
                    'userType': user.userType,
                    'businessName': user.businessName,
                    'serviceCategory': user.serviceCategory,
                    'hourlyRate': user.hourlyRate
                },
                'token': access_token
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error': str(e)
        }), 500

@app.route('/api/providers', methods=['GET'])
def get_providers():
    try:
        category = request.args.get('category')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        db = get_db()
        query = db.query(User).filter(User.userType == 'provider', User.status == 'active')

        if category:
            query = query.filter(User.serviceCategory == category)

        total = query.count()
        providers = query.offset((page - 1) * limit).limit(limit).all()

        provider_list = []
        for provider in providers:
            provider_list.append({
                'userId': provider.userId,
                'fullName': provider.fullName,
                'businessName': provider.businessName,
                'serviceCategory': provider.serviceCategory,
                'experience': provider.experience,
                'hourlyRate': provider.hourlyRate,
                'rating': provider.rating,
                'address': provider.address,
                'phone': provider.phone,
                'description': provider.description
            })

        return jsonify({
            'success': True,
            'data': {
                'providers': provider_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get providers',
            'error': str(e)
        }), 500

@app.route('/api/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        db = get_db()
        user = db.query(User).filter(User.userId == user_id).first()

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'user': {
                    'userId': user.userId,
                    'fullName': user.fullName,
                    'businessName': user.businessName,
                    'serviceCategory': user.serviceCategory,
                    'experience': user.experience,
                    'hourlyRate': user.hourlyRate,
                    'rating': user.rating,
                    'address': user.address,
                    'phone': user.phone,
                    'description': user.description
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get user',
            'error': str(e)
        }), 500

@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        # Get customer info
        db = get_db()
        customer = db.query(User).filter(User.id == int(current_user_id)).first()

        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404

        booking = Booking(
            bookingId=generate_booking_id(),
            customerId=customer.userId,
            providerId=data.get('providerId'),
            serviceType=data.get('serviceType', 'General Service'),
            serviceLocation=data.get('serviceLocation'),
            preferredDate=datetime.strptime(data['preferredDate'], '%Y-%m-%d').date(),
            preferredTime=data.get('preferredTime'),
            additionalNotes=data.get('additionalNotes', ''),
            serviceAmount=float(data.get('serviceAmount', 0)),
            serviceFee=float(data.get('serviceFee', 0)),
            status='pending_payment'
        )

        db.add(booking)
        db.commit()

        return jsonify({
            'success': True,
            'message': 'Booking created successfully',
            'data': {
                'booking': {
                    'bookingId': booking.bookingId,
                    'status': booking.status,
                    'serviceAmount': booking.serviceAmount
                }
            }
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to create booking',
            'error': str(e)
        }), 500

@app.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    try:
        current_user_id = get_jwt_identity()
        db = get_db()

        user = db.query(User).filter(User.id == int(current_user_id)).first()
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        if user.userType == 'provider':
            bookings = db.query(Booking).filter(Booking.providerId == user.userId).all()
        else:
            bookings = db.query(Booking).filter(Booking.customerId == user.userId).all()

        booking_list = []
        for booking in bookings:
            booking_list.append({
                'bookingId': booking.bookingId,
                'customerId': booking.customerId,
                'providerId': booking.providerId,
                'serviceType': booking.serviceType,
                'serviceLocation': booking.serviceLocation,
                'preferredDate': booking.preferredDate.isoformat(),
                'preferredTime': booking.preferredTime,
                'serviceAmount': booking.serviceAmount,
                'status': booking.status,
                'bookingDate': booking.bookingDate.isoformat()
            })

        return jsonify({
            'success': True,
            'data': {
                'bookings': booking_list
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get bookings',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))