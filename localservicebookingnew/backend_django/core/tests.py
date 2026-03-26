from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, ServiceProvider, Booking, Feedback, OTP, ChatbotBooking

User = get_user_model()


class AuthenticationTests(APITestCase):
    """Test authentication endpoints."""

    def test_register_customer(self):
        """Test customer registration."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'userType': 'customer',
            'phone': '9876543210',
        }
        response = self.client.post('/api/auth/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])

    def test_register_provider(self):
        """Test provider registration with service details."""
        data = {
            'username': 'provider1',
            'email': 'provider@example.com',
            'password': 'provpass123',
            'userType': 'provider',
            'serviceType': 'electrician',
            'location': 'Mumbai',
            'pricePerHour': 500,
            'upiId': 'test@upi',
            'fullName': 'Test Provider'
        }
        response = self.client.post('/api/auth/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check provider was created
        self.assertTrue(ServiceProvider.objects.filter(user__username='provider1').exists())

    def test_login_success(self):
        """Test successful login."""
        user = User.objects.create_user(username='testuser', password='testpass123')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post('/api/auth/login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])

    def test_login_invalid_credentials(self):
        """Test login with wrong password."""
        User.objects.create_user(username='testuser', password='testpass123')
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post('/api/auth/login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])


class OTPTests(APITestCase):
    """Test OTP functionality."""

    def test_send_otp_phone(self):
        """Test sending OTP for phone login."""
        data = {'identifier': '9876543210', 'purpose': 'phone_login'}
        response = self.client.post('/api/auth/otp/send', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Check OTP was created
        self.assertTrue(OTP.objects.filter(identifier='9876543210').exists())

    def test_verify_otp_login(self):
        """Test OTP verification for phone login."""
        # Create OTP
        otp = OTP.objects.create(
            identifier='9876543210',
            otp_code='123456',
            purpose=OTP.PURPOSE_PHONE,
        )
        data = {'phone': '9876543210', 'otp': '123456'}
        response = self.client.post('/api/auth/otp/verify-login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Check user was created
        self.assertTrue(User.objects.filter(phone='9876543210').exists())


class ProviderTests(APITestCase):
    """Test provider endpoints."""

    def setUp(self):
        """Create sample providers."""
        user = User.objects.create_user(username='provider1', password='pass123', user_type='provider')
        ServiceProvider.objects.create(
            user=user,
            name='Test Provider',
            service_type='electrician',
            location='Mumbai',
            price_per_hour=500,
            phone_number='9876543210',
            upi_id='test@upi',
        )

    def test_list_providers(self):
        """Test listing all providers."""
        response = self.client.get('/api/providers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreater(len(response.data['data']), 0)

    def test_filter_providers_by_category(self):
        """Test filtering providers by service type."""
        response = self.client.get('/api/providers/?category=electrician')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for provider in response.data['data']:
            self.assertEqual(provider['specialization'].lower(), 'electrician')

    def test_get_provider_detail(self):
        """Test getting provider details."""
        provider = ServiceProvider.objects.first()
        response = self.client.get(f'/api/providers/{provider.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['fullName'], 'Test Provider')


class BookingTests(APITestCase):
    """Test booking endpoints."""

    def setUp(self):
        """Create test user and provider."""
        self.user = User.objects.create_user(username='customer1', password='pass123')
        provider_user = User.objects.create_user(username='provider1', password='pass123', user_type='provider')
        self.provider = ServiceProvider.objects.create(
            user=provider_user,
            name='Test Provider',
            service_type='electrician',
            location='Mumbai',
            price_per_hour=500,
            upi_id='test@upi',
        )

    def test_create_booking(self):
        """Test creating a booking."""
        data = {
            'providerId': self.provider.id,
            'date': '2026-04-15',
            'time': '09:00 AM – 11:00 AM',
            'address': '123 Test St',
        }
        response = self.client.post('/api/bookings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('bookingId', response.data['data'])

    def test_get_user_bookings(self):
        """Test getting bookings for authenticated user."""
        # Create booking
        Booking.objects.create(
            user=self.user,
            provider=self.provider,
            bookingId='BK123456',
            date='2026-04-15',
            time='09:00 AM',
            address='Test St',
            service_amount=500,
        )
        # Login
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['bookings']), 1)


class FeedbackTests(APITestCase):
    """Test feedback endpoints."""

    def setUp(self):
        """Create test data."""
        self.user = User.objects.create_user(username='customer1', password='pass123')
        provider_user = User.objects.create_user(username='provider1', password='pass123', user_type='provider')
        self.provider = ServiceProvider.objects.create(
            user=provider_user,
            name='Test Provider',
            service_type='electrician',
            location='Mumbai',
            price_per_hour=500,
            upi_id='test@upi',
        )

    def test_submit_feedback(self):
        """Test submitting feedback."""
        data = {
            'provider': self.provider.id,
            'rating': 5,
            'comment': 'Excellent service!',
        }
        response = self.client.post('/api/feedback/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_get_provider_feedback(self):
        """Test getting feedback for a provider."""
        Feedback.objects.create(
            user=self.user,
            provider=self.provider,
            rating=5,
            comment='Great!',
        )
        # Auth usually required for feedback detail but let's check
        response = self.client.get(f'/api/feedback/provider/{self.provider.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertIn('avg_rating', response.data)


class ModelTests(TestCase):
    """Test model methods."""

    def test_user_save_generates_userId(self):
        """Test User model auto-generates userId."""
        user = User.objects.create_user(username='testuser', password='pass123')
        self.assertEqual(user.userId, 'testuser')

    def test_provider_average_rating(self):
        """Test ServiceProvider average_rating method."""
        user = User.objects.create_user(username='provider1', password='pass123')
        provider = ServiceProvider.objects.create(
            user=user,
            name='Test',
            service_type='electrician',
            location='Mumbai',
            price_per_hour=500,
            upi_id='test@upi',
        )
        customer = User.objects.create_user(username='customer1', password='pass123')
        Feedback.objects.create(user=customer, provider=provider, rating=5)
        Feedback.objects.create(user=customer, provider=provider, rating=3)
        self.assertEqual(provider.average_rating(), 4.0)

    def test_otp_expiry(self):
        """Test OTP expiry check."""
        import datetime
        from django.utils import timezone
        otp = OTP.objects.create(
            identifier='test@test.com',
            otp_code='123456',
            purpose=OTP.PURPOSE_EMAIL,
        )
        # Fresh OTP should not be expired
        self.assertFalse(otp.is_expired())
        # Manually set old timestamp
        otp.created_at = timezone.now() - datetime.timedelta(minutes=15)
        otp.save()
        self.assertTrue(otp.is_expired())


class ChatbotTests(APITestCase):
    """Test chatbot state machine and booking."""

    def test_chatbot_intent_detection(self):
        """Test that keywords trigger the correct service."""
        # Electrician
        response = self.client.post('/api/chatbot', {'message': 'my fan is broken'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Electrician', response.data['reply'])
        self.assertEqual(response.data['state'], 'COLLECTING_NAME')

    def test_chatbot_booking_flow(self):
        """Test full step-by-step booking flow."""
        # 1. Start with intent
        self.client.post('/api/chatbot', {'message': 'plumber for leak'}, format='json')
        
        # 2. Provide name
        response = self.client.post('/api/chatbot', {'message': 'John Doe'}, format='json')
        self.assertEqual(response.data['state'], 'COLLECTING_PHONE')
        
        # 3. Provide phone
        response = self.client.post('/api/chatbot', {'message': '9876543210'}, format='json')
        self.assertEqual(response.data['state'], 'COLLECTING_ADDRESS')
        
        # 4. Provide address and finalize
        response = self.client.post('/api/chatbot', {'message': '123 Chatbot Lane'}, format='json')
        self.assertEqual(response.data['state'], 'INITIAL')
        self.assertIn('received', response.data['reply'].lower())
        
        # Check if record exists
        self.assertTrue(ChatbotBooking.objects.filter(name='John Doe', service_type='Plumber').exists())

    def test_chatbot_faq(self):
        """Test FAQ responses."""
        response = self.client.post('/api/chatbot', {'message': 'what are your working hours?'}, format='json')
        self.assertIn('9 AM to 8 PM', response.data['reply'])
