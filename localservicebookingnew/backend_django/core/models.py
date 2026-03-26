from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime


class User(AbstractUser):
    userId = models.CharField(max_length=50, unique=True, null=True, blank=True)
    user_type = models.CharField(max_length=20, default='customer')  # customer | provider | admin
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_picture = models.URLField(max_length=500, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.userId:
            self.userId = self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class OTP(models.Model):
    """Stores temporary OTPs for phone login and email password-reset."""
    PURPOSE_PHONE = 'phone_login'
    PURPOSE_EMAIL = 'email_reset'
    PURPOSE_CHOICES = [
        (PURPOSE_PHONE, 'Phone Login'),
        (PURPOSE_EMAIL, 'Email Reset'),
    ]

    identifier = models.CharField(max_length=255)   # phone number or email
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        from django.conf import settings
        expiry = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        return timezone.now() > self.created_at + datetime.timedelta(minutes=expiry)

    def __str__(self):
        return f"OTP({self.identifier}, {self.purpose})"


class ServiceProvider(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_BUSY = 'busy'
    STATUS_UNAVAILABLE = 'unavailable'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_BUSY, 'Busy'),
        (STATUS_UNAVAILABLE, 'Not Available'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50)   # electrician | plumber | mechanic
    location = models.CharField(max_length=100)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    upi_id = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE
    )

    def average_rating(self):
        from django.db.models import Avg
        result = self.feedback_set.aggregate(avg=Avg('rating'))['avg']
        return round(float(result), 1) if result else 0.0

    def __str__(self):
        return f"{self.name} ({self.service_type})"


class Booking(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_CONFIRMED = 'Confirmed'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    bookingId = models.CharField(max_length=50, unique=True, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.CharField(max_length=50)
    address = models.TextField()
    status = models.CharField(max_length=20, default=STATUS_PENDING)
    service_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, default='Pending')
    payment_method = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.bookingId} – {self.user.username}"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} for {self.provider.name}"


class ChatbotBooking(models.Model):
    """Specific table for chatbot leads as requested by user."""
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    service_type = models.CharField(max_length=50)
    address = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chatbot Lead: {self.name} ({self.service_type})"
