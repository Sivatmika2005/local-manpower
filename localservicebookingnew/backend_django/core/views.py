"""
views.py – Complete backend for Local Service Booking App
"""
import random
import string
import io
import base64
import datetime

from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

import qrcode

from .models import User, ServiceProvider, Booking, Feedback, OTP, ChatbotBooking
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ServiceProviderSerializer, BookingSerializer, FeedbackSerializer,
)

DEFAULT_PHONE = getattr(settings, 'DEFAULT_PROVIDER_PHONE', '9360522919')

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_otp():
    return ''.join(random.choices(string.digits, k=6))


def _jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}


def _user_payload(user):
    full = f"{user.first_name} {user.last_name}".strip() or user.username
    provider = ServiceProvider.objects.filter(user=user).first()
    # Resolve profile image: prefer uploaded file, fall back to URL
    if user.profile_image:
        pic = user.profile_image.url
    else:
        pic = user.profile_picture or ''
    payload = {
        'userId': user.userId or user.username,
        'username': user.username,
        'email': user.email,
        'fullName': full,
        'userType': user.user_type,
        'phone': user.phone,
        'profile_picture': pic,
    }
    if provider:
        payload['providerId'] = provider.id
        payload['serviceType'] = provider.service_type
        payload['location'] = provider.location
        payload['price'] = float(provider.price_per_hour)
    return payload


# Removed _seed_sample_providers


def _provider_dict(p):
    """Serialize a ServiceProvider to a consistent dict for ALL API responses."""
    # Resolve profile image — same source used everywhere
    profile_img = ''
    if p.user:
        if p.user.profile_image:
            profile_img = p.user.profile_image.url
        elif p.user.profile_picture:
            profile_img = p.user.profile_picture

    status_val = getattr(p, 'status', None) or (
        ServiceProvider.STATUS_AVAILABLE if p.is_available else ServiceProvider.STATUS_UNAVAILABLE
    )
    return {
        'id': p.id,
        'userId': p.user.username if p.user else f'p{p.id}',
        'fullName': p.name,
        'specialization': p.service_type.capitalize(),
        'serviceType': p.service_type,
        'rating': p.average_rating(),
        'location': p.location,
        'price': float(p.price_per_hour),
        'phone': p.phone_number or DEFAULT_PHONE,
        'upi_id': p.upi_id or '',
        'description': p.description or '',
        'isAvailable': status_val == ServiceProvider.STATUS_AVAILABLE,
        'status': status_val,
        'experience': 5,
        'responseTime': 30,
        'profileImage': profile_img,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'success': True, 'message': 'Server is running',
                     'timestamp': datetime.datetime.now().isoformat()})


# ─────────────────────────────────────────────────────────────────────────────
# Auth – Register
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """
    Handles both JSON and multipart/form-data (for profile image upload at registration).
    """
    # Support multipart form data (file upload) as well as JSON
    data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

    serializer = RegisterSerializer(data=data)
    if not serializer.is_valid():
        print(f'[REGISTER] Validation errors: {serializer.errors}')
        return Response({'success': False, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    # Handle profile image upload if provided
    image_file = request.FILES.get('profile_image')
    if image_file:
        user.profile_image = image_file
        user.save(update_fields=['profile_image'])
        user.profile_picture = user.profile_image.url
        user.save(update_fields=['profile_picture'])
        # Also attach to provider record
        provider = ServiceProvider.objects.filter(user=user).first()
        if provider:
            print(f'[REGISTER] Profile image saved for provider id={provider.id}')

    tokens = _jwt_for_user(user)
    return Response({
        'success': True,
        'message': 'Registration successful',
        'data': {'user': _user_payload(user), 'tokens': tokens},
    }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────────────────────────────────────
# Auth – Login
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = _jwt_for_user(user)
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {'user': _user_payload(user), 'tokens': tokens},
        })
    return Response({'success': False, 'message': 'Invalid credentials',
                     'errors': serializer.errors},
                    status=status.HTTP_401_UNAUTHORIZED)


# ─────────────────────────────────────────────────────────────────────────────
# Auth – Firebase Sync
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_firebase_sync(request):
    d = request.data
    uid = d.get('userId')
    email = d.get('email')
    phone = d.get('phone')
    user_type = d.get('userType', 'customer')
    full_name = d.get('fullName', 'Firebase User')
    
    if not uid and not email and not phone:
        return Response({'success': False, 'message': 'Missing identifiers'}, status=400)
    
    user = None
    if email:
        user = User.objects.filter(email=email).first()
    if not user and phone:
        user = User.objects.filter(phone=phone).first()
    if not user and uid:
        user = User.objects.filter(username=uid).first()
        
    if not user:
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        user = User.objects.create(
            username=uid if uid else (email.split('@')[0] if email else f"user_{random.randint(1000,9999)}"),
            email=email or '',
            phone=phone or '',
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            userId=uid
        )
        user.set_unusable_password()
        user.save()
        
    # Provider setup
    if user.user_type == 'provider':
        ServiceProvider.objects.get_or_create(
            user=user,
            defaults={
                'name': full_name,
                'service_type': 'other',
                'location': 'Unknown',
                'price_per_hour': 500,
            }
        )
        
    tokens = _jwt_for_user(user)
    return Response({
        'success': True,
        'message': 'Firebase synced',
        'data': {'user': _user_payload(user), 'tokens': tokens}
    })


# ─────────────────────────────────────────────────────────────────────────────
# Auth – OTP: Send
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_send_otp(request):
    identifier = request.data.get('identifier', '').strip()
    purpose = request.data.get('purpose', OTP.PURPOSE_PHONE)
    
    if not identifier:
        return Response({'success': False, 'message': 'identifier is required'}, status=400)
        
    # User requested: "when the user enters the registered emailid"
    if purpose == OTP.PURPOSE_EMAIL:
        if not User.objects.filter(email=identifier).exists():
            return Response({'success': False, 'message': 'No account found with this email address.'}, status=404)

    otp_code = _make_otp()
    OTP.objects.create(identifier=identifier, otp_code=otp_code, purpose=purpose)
    if purpose == OTP.PURPOSE_EMAIL:
        try:
            send_mail(
                subject='Your Password Reset OTP',
                message=f'Your OTP is: {otp_code}  (valid for 10 minutes)',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com'),
                recipient_list=[identifier],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[OTP EMAIL FAILED] To: {identifier}  OTP: {otp_code} | Error: {e}')
    else:
        print(f'[OTP SMS] To: {identifier}  OTP: {otp_code}')
        
    return Response({
        'success': True, 
        'message': f'OTP sent to {identifier}',
        'dev_otp': otp_code  # Always send this back to trigger the frontend popup!
    })


# ─────────────────────────────────────────────────────────────────────────────
# Auth – OTP: Verify login
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_verify_otp_login(request):
    phone = request.data.get('phone', '').strip()
    otp_code = request.data.get('otp', '').strip()
    if not phone or not otp_code:
        return Response({'success': False, 'message': 'phone and otp are required'}, status=400)
    record = OTP.objects.filter(
        identifier=phone, otp_code=otp_code,
        purpose=OTP.PURPOSE_PHONE, is_used=False
    ).order_by('-created_at').first()
    if not record or record.is_expired():
        return Response({'success': False, 'message': 'Invalid or expired OTP'}, status=400)
    record.is_used = True
    record.save()
    user = User.objects.filter(phone=phone).first()
    if not user:
        uname = f'user_{phone[-4:]}'
        user = User.objects.create(username=uname, phone=phone, user_type='customer')
        user.set_unusable_password()
        user.save()
    tokens = _jwt_for_user(user)
    return Response({'success': True, 'message': 'OTP verified',
                     'data': {'user': _user_payload(user), 'tokens': tokens}})


# ─────────────────────────────────────────────────────────────────────────────
# Auth – OTP: Reset password
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_verify_otp_reset(request):
    email = request.data.get('email', '').strip()
    otp_code = request.data.get('otp', '').strip()
    new_password = request.data.get('new_password', '').strip()
    if not email or not otp_code or not new_password:
        return Response({'success': False, 'message': 'email, otp and new_password required'}, status=400)
    record = OTP.objects.filter(
        identifier=email, otp_code=otp_code,
        purpose=OTP.PURPOSE_EMAIL, is_used=False
    ).order_by('-created_at').first()
    if not record or record.is_expired():
        return Response({'success': False, 'message': 'Invalid or expired OTP'}, status=400)
    user = User.objects.filter(email=email).first()
    if not user:
        return Response({'success': False, 'message': 'No account with that email'}, status=404)
    user.set_password(new_password)
    user.save()
    record.is_used = True
    record.save()
    return Response({'success': True, 'message': 'Password reset successful'})


# ─────────────────────────────────────────────────────────────────────────────
# Profile – Get & Edit (API)
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([AllowAny])
def api_my_profile(request):
    """GET/PUT /api/profile/ — get or update the logged-in user's profile."""
    user = request.user if request.user.is_authenticated else None
    if not user:
        return Response({'success': False, 'message': 'Authentication required'}, status=401)

    if request.method == 'GET':
        payload = _user_payload(user)
        provider = ServiceProvider.objects.filter(user=user).first()
        if provider:
            payload['providerProfile'] = _provider_dict(provider)
        return Response({'success': True, 'data': payload})

    # PUT / PATCH – update profile
    d = request.data
    if d.get('first_name') is not None:
        user.first_name = d['first_name']
    if d.get('last_name') is not None:
        user.last_name = d['last_name']
    if d.get('email'):
        user.email = d['email']
    if d.get('phone') is not None:
        user.phone = d['phone']
    if d.get('address') is not None:
        user.address = d['address']
    if d.get('profile_picture') is not None:
        user.profile_picture = d['profile_picture']
    if d.get('password'):
        user.set_password(d['password'])
    user.save()

    # Update provider profile if applicable
    provider = ServiceProvider.objects.filter(user=user).first()
    if provider:
        if d.get('location'):
            provider.location = d['location']
        if d.get('price_per_hour'):
            provider.price_per_hour = d['price_per_hour']
        if d.get('phone_number') is not None:
            provider.phone_number = d['phone_number']
        if d.get('description') is not None:
            provider.description = d['description']
        if d.get('service_type'):
            provider.service_type = d['service_type'].lower()
        if d.get('upi_id') is not None:
            provider.upi_id = d['upi_id']
        provider.save()
        print(f"Provider updated: {provider.id}")

    return Response({'success': True, 'message': 'Profile updated',
                     'data': _user_payload(user)})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_upload_profile_image(request):
    """POST /api/profile/upload-image/ — upload profile image file."""
    user = request.user if request.user.is_authenticated else None
    if not user:
        return Response({'success': False, 'message': 'Authentication required'}, status=401)

    image_file = request.FILES.get('profile_image')
    if not image_file:
        return Response({'success': False, 'message': 'No image file provided'}, status=400)

    # Save via ImageField and also sync the URL field so frontend gets it
    user.profile_image = image_file
    user.save()
    # Sync URL field so _user_payload returns the correct URL
    user.profile_picture = user.profile_image.url
    user.save(update_fields=['profile_picture'])

    return Response({
        'success': True,
        'message': 'Profile image uploaded',
        'profile_picture': user.profile_image.url,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Providers API
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_providers(request):
    if request.method == 'GET':
        category = request.query_params.get('category', '').lower()
        qs = ServiceProvider.objects.select_related('user').all()
        if category:
            qs = qs.filter(service_type=category)
        return Response({'success': True, 'data': [_provider_dict(p) for p in qs]})

    # POST – register a new provider
    if not request.user.is_authenticated:
        return Response({'success': False, 'message': 'Authentication required'}, status=401)
    d = request.data
    user = request.user
    user.user_type = 'provider'
    user.save()
    provider, created = ServiceProvider.objects.update_or_create(
        user=user,
        defaults={
            'name': d.get('name', user.username),
            'service_type': (d.get('service_type') or 'other').lower(),
            'location': d.get('location', '') or 'Local Area',
            'price_per_hour': d.get('price_per_hour', 500) or 500,
            'phone_number': d.get('phone_number', ''),
            'upi_id': d.get('upi_id', ''),
            'description': d.get('description', ''),
            'status': ServiceProvider.STATUS_AVAILABLE,
        },
    )
    print(f"Provider saved: {provider.id}")
    print(f'[PROVIDER] {"Created" if created else "Updated"}: id={provider.id} name={provider.name} upi={provider.upi_id}')
    return Response({'success': True, 'message': 'Provider registered',
                     'data': _provider_dict(provider)}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_provider_detail(request, provider_id):
    provider = None
    if str(provider_id).isdigit():
        provider = ServiceProvider.objects.filter(id=int(provider_id)).first()
    if not provider:
        provider = ServiceProvider.objects.filter(user__username=provider_id).first()
    if not provider:
        return Response({'success': False, 'message': 'Provider not found'}, status=404)

    feedbacks = Feedback.objects.filter(provider=provider).select_related('user')
    fb_data = [
        {'user': f.user.username, 'rating': f.rating,
         'comment': f.comment, 'date': f.created_at.strftime('%Y-%m-%d')}
        for f in feedbacks
    ]
    data = _provider_dict(provider)
    data['feedback'] = fb_data
    return Response({'success': True, 'data': data})


@api_view(['PATCH', 'POST'])
@permission_classes([AllowAny])
def api_update_provider_status(request, provider_id):
    """PATCH /api/providers/<id>/status/ — update provider availability status."""
    provider = None
    if str(provider_id).isdigit():
        provider = ServiceProvider.objects.filter(id=int(provider_id)).first()
    if not provider:
        provider = ServiceProvider.objects.filter(user__username=provider_id).first()
    if not provider:
        return Response({'success': False, 'message': 'Provider not found'}, status=404)

    new_status = request.data.get('status', '').lower()
    valid = [ServiceProvider.STATUS_AVAILABLE, ServiceProvider.STATUS_BUSY, ServiceProvider.STATUS_UNAVAILABLE]
    if new_status not in valid:
        return Response({'success': False, 'message': f'Invalid status. Use: {valid}'}, status=400)

    provider.status = new_status
    provider.is_available = (new_status == ServiceProvider.STATUS_AVAILABLE)
    provider.save(update_fields=['status', 'is_available'])
    print(f'[STATUS] Provider {provider.id} ({provider.name}) → {new_status}')
    return Response({'success': True, 'message': f'Status updated to {new_status}', 'status': new_status})


# ─────────────────────────────────────────────────────────────────────────────
# Bookings API
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_bookings(request):
    if request.method == 'POST':
        d = request.data
        pid = d.get('providerId') or d.get('provider_id')
        provider = None
        if pid:
            if str(pid).isdigit():
                provider = ServiceProvider.objects.filter(id=int(pid)).first()
            if not provider:
                provider = ServiceProvider.objects.filter(user__username=pid).first()
        if not provider:
            return Response({'success': False, 'message': 'Provider not found'}, status=404)

        if request.user.is_authenticated:
            user = request.user
        else:
            user, _ = User.objects.get_or_create(
                username='guest',
                defaults={'user_type': 'customer', 'email': 'guest@local.com'},
            )

        booking_id = f"BK{random.randint(100000, 999999)}"
        booking = Booking.objects.create(
            bookingId=booking_id,
            user=user,
            provider=provider,
            date=d.get('date') or d.get('bookingDate'),
            time=d.get('time') or d.get('bookingTime', ''),
            address=d.get('address') or d.get('location', ''),
            service_amount=provider.price_per_hour,
            status=Booking.STATUS_PENDING,
            payment_status='Pending',
        )
        return Response({
            'success': True,
            'message': 'Booking created',
            'data': {
                'bookingId': booking.bookingId,
                'providerName': provider.name,
                'amount': float(provider.price_per_hour),
                'providerId': provider.id,
            },
        }, status=status.HTTP_201_CREATED)

    # GET
    if request.user.is_authenticated:
        if getattr(request.user, 'user_type', None) == 'admin' or request.user.is_superuser:
            bookings = Booking.objects.all().select_related('provider', 'user').order_by('-id')[:50]
        else:
            bookings = Booking.objects.filter(user=request.user).select_related('provider')
        return Response({'success': True, 'bookings': BookingSerializer(bookings, many=True).data})
    return Response({'success': False, 'message': 'Not authenticated'}, status=401)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_admin_all_bookings(request):
    """Dedicated endpoint for admin dashboard – returns all bookings.
    Accepts ?username=<admin_username> as a lightweight identity check."""
    username = request.query_params.get('username', '')
    # Allow if already authenticated as admin/superuser
    is_admin = (
        (request.user.is_authenticated and (
            getattr(request.user, 'user_type', None) == 'admin' or request.user.is_superuser
        ))
        or
        (username and User.objects.filter(username=username, user_type='admin').exists())
        or
        (username and User.objects.filter(username=username, is_superuser=True).exists())
    )
    if not is_admin:
        return Response({'success': False, 'message': 'Admin access required'}, status=403)

    bookings = Booking.objects.all().select_related('provider', 'user').order_by('-id')[:100]
    return Response({'success': True, 'bookings': BookingSerializer(bookings, many=True).data})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_promote_admin(request):
    """POST /api/admin/promote/ — switch a user's type to admin"""
    admin_username = request.query_params.get('username') or request.data.get('admin_username')
    # Simple check for admin auth based on existing patterns
    is_admin = (
        (request.user.is_authenticated and (
            getattr(request.user, 'user_type', None) == 'admin' or request.user.is_superuser
        ))
        or
        (admin_username and User.objects.filter(username=admin_username, user_type='admin').exists())
        or
        (admin_username and User.objects.filter(username=admin_username, is_superuser=True).exists())
    )
    if not is_admin:
        return Response({'success': False, 'message': 'Admin access required'}, status=403)
        
    target_username = request.data.get('username')
    action = request.data.get('action', 'promote')
    if not target_username:
        return Response({'success': False, 'message': 'Target username required'}, status=400)
        
    if action == 'demote' and target_username == admin_username:
        return Response({'success': False, 'message': 'You cannot demote yourself'}, status=400)
        
    user = User.objects.filter(username=target_username).first()
    if not user:
        return Response({'success': False, 'message': 'User not found'}, status=404)
        
    if action == 'demote':
        is_provider = ServiceProvider.objects.filter(user=user).exists()
        user.user_type = 'provider' if is_provider else 'customer'
        user.is_staff = False
        user.is_superuser = False
        user.save(update_fields=['user_type', 'is_staff', 'is_superuser'])
        return Response({'success': True, 'message': f'{target_username} is no longer an Admin.'})
        
    user.user_type = 'admin'
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=['user_type', 'is_staff', 'is_superuser'])
    return Response({'success': True, 'message': f'{target_username} is now an admin!'})


@api_view(['GET'])
@permission_classes([AllowAny])
def api_customer_bookings(request, customer_id):
    bookings = Booking.objects.filter(
        Q(user__username=customer_id) | Q(user__userId=customer_id)
    ).select_related('provider')
    return Response({'success': True, 'bookings': BookingSerializer(bookings, many=True).data})


@api_view(['GET'])
@permission_classes([AllowAny])
def api_provider_bookings(request, provider_id):
    bookings = Booking.objects.filter(
        Q(provider__user__username=provider_id) |
        Q(provider__id=int(provider_id) if str(provider_id).isdigit() else 0)
    ).select_related('user', 'provider')
    return Response({'success': True, 'bookings': BookingSerializer(bookings, many=True).data})


@api_view(['PATCH'])
@permission_classes([AllowAny])
def api_update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, bookingId=booking_id)
    new_status = request.data.get('status')
    payment_method = request.data.get('payment_method')
    if new_status:
        booking.status = new_status
    if payment_method:
        booking.payment_method = payment_method
        booking.payment_status = 'Paid'
    booking.save()
    return Response({'success': True, 'message': 'Booking updated'})


# ─────────────────────────────────────────────────────────────────────────────
# Feedback API
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_feedback(request):
    if request.method == 'POST':
        d = request.data.copy()
        if request.user.is_authenticated:
            user = request.user
        else:
            user, _ = User.objects.get_or_create(
                username='guest',
                defaults={'user_type': 'customer', 'email': 'guest@local.com'},
            )

        provider_id = d.get('provider') or d.get('providerId')
        provider = None
        if provider_id:
            if str(provider_id).isdigit():
                provider = ServiceProvider.objects.filter(id=int(provider_id)).first()
            if not provider:
                provider = ServiceProvider.objects.filter(user__username=provider_id).first()

        if not provider:
            booking_id = d.get('bookingId')
            if booking_id:
                booking = Booking.objects.filter(bookingId=booking_id).select_related('provider').first()
                if booking:
                    provider = booking.provider

        if not provider:
            return Response({'success': False, 'message': 'Provider not found'}, status=404)

        fb = Feedback.objects.create(
            user=user, provider=provider,
            rating=int(d.get('rating', 5)),
            comment=d.get('comment', d.get('feedback', '')),
        )
        return Response({'success': True, 'message': 'Feedback submitted',
                         'data': FeedbackSerializer(fb).data})

    feedbacks = Feedback.objects.all().select_related('user', 'provider')
    return Response({'success': True, 'data': FeedbackSerializer(feedbacks, many=True).data})


@api_view(['GET'])
@permission_classes([AllowAny])
def api_provider_feedback(request, provider_id):
    provider = None
    if str(provider_id).isdigit():
        provider = ServiceProvider.objects.filter(id=int(provider_id)).first()
    if not provider:
        provider = ServiceProvider.objects.filter(user__username=provider_id).first()
    if not provider:
        return Response({'success': False, 'message': 'Provider not found'}, status=404)
    feedbacks = Feedback.objects.filter(provider=provider).select_related('user')
    return Response({'success': True, 'avg_rating': provider.average_rating(),
                     'data': FeedbackSerializer(feedbacks, many=True).data})


# ─────────────────────────────────────────────────────────────────────────────
# Chatbot API
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_chatbot(request):
    """
    State-based chatbot logic.
    States: INITIAL, COLLECTING_NAME, COLLECTING_PHONE, COLLECTING_SERVICE, COLLECTING_ADDRESS
    """
    message = request.data.get('message', '').lower().strip()
    session_state = request.session.get('chatbot_state', 'INITIAL')

    # Handle clear chat/reset
    if 'clear chat' in message:
        request.session['chatbot_state'] = 'INITIAL'
        for key in ['chatbot_temp_name', 'chatbot_temp_phone', 'chatbot_temp_service']:
            if key in request.session: del request.session[key]
        return Response({'success': True, 'reply': 'Chat state reset.', 'state': 'INITIAL'})
    
    # ── FAQ Support ──────────────────
    faq_map = {
        'working hours': "We are available from 9 AM to 8 PM, Monday to Saturday.",
        'hours': "We are available from 9 AM to 8 PM, Monday to Saturday.",
        'cost': "Service costs vary. Electricians start at ₹450/hr, Plumbers at ₹350/hr, and Mechanics at ₹550/hr.",
        'price': "Service costs vary. Electricians start at ₹450/hr, Plumbers at ₹350/hr, and Mechanics at ₹550/hr.",
        'areas': "We currently cover Chennai, Bangalore, Mumbai, Delhi, Hyderabad, and Pune.",
        'location': "We currently cover Chennai, Bangalore, Mumbai, Delhi, Hyderabad, and Pune.",
    }
    
    for key, val in faq_map.items():
        if key in message:
            return Response({
                'success': True,
                'reply': val,
                'state': session_state
            })

    # ── State Machine ────────────────
    if session_state == 'INITIAL':
        # Intent Detection
        if any(kw in message for kw in ['fan', 'light', 'electrician', 'wiring']):
            request.session['chatbot_state'] = 'COLLECTING_NAME'
            request.session['chatbot_temp_service'] = 'Electrician'
            return Response({
                'success': True,
                'reply': "I can help with that! Let's get you an Electrician. First, what is your name?",
                'state': 'COLLECTING_NAME'
            })
        elif any(kw in message for kw in ['pipe', 'leak', 'water', 'plumber', 'tap']):
            request.session['chatbot_state'] = 'COLLECTING_NAME'
            request.session['chatbot_temp_service'] = 'Plumber'
            return Response({
                'success': True,
                'reply': "Sure, a Plumber can fix that. What is your name?",
                'state': 'COLLECTING_NAME'
            })
        elif any(kw in message for kw in ['bike', 'car', 'repair', 'mechanic', 'engine']):
            request.session['chatbot_state'] = 'COLLECTING_NAME'
            request.session['chatbot_temp_service'] = 'Mechanic'
            return Response({
                'success': True,
                'reply': "Our Mechanics are ready. Please tell me your name to start the booking.",
                'state': 'COLLECTING_NAME'
            })
        elif 'book' in message or 'service' in message:
            return Response({
                'success': True,
                'reply': "What service do you need? (Electrician, Plumber, or Mechanic)",
                'quick_replies': ['Electrician', 'Plumber', 'Mechanic'],
                'state': 'INITIAL'
            })
        else:
            return Response({
                'success': True,
                'reply': "Hi! I can help you find services like Electrician, Plumber, or Mechanic. What do you need?",
                'quick_replies': ['Electrician', 'Plumber', 'Mechanic'],
                'state': 'INITIAL'
            })

    elif session_state == 'COLLECTING_NAME':
        request.session['chatbot_temp_name'] = message.title()
        request.session['chatbot_state'] = 'COLLECTING_PHONE'
        return Response({
            'success': True,
            'reply': f"Thanks, {message.title()}. What is your phone number?",
            'state': 'COLLECTING_PHONE'
        })

    elif session_state == 'COLLECTING_PHONE':
        # Simple validation
        if not any(c.isdigit() for c in message) or len(message) < 10:
             return Response({
                'success': True,
                'reply': "Please provide a valid 10-digit phone number.",
                'state': 'COLLECTING_PHONE'
            })
        request.session['chatbot_temp_phone'] = message
        request.session['chatbot_state'] = 'COLLECTING_ADDRESS'
        return Response({
            'success': True,
            'reply': "Almost done! Where should we send the professional? (Please provide your address)",
            'state': 'COLLECTING_ADDRESS'
        })

    elif session_state == 'COLLECTING_ADDRESS':
        # Finalize booking
        name = request.session.get('chatbot_temp_name')
        phone = request.session.get('chatbot_temp_phone')
        service = request.session.get('chatbot_temp_service')
        address = message.title()
        
        ChatbotBooking.objects.create(
            name=name, phone=phone, service_type=service, address=address
        )
        
        # Reset session
        request.session['chatbot_state'] = 'INITIAL'
        for key in ['chatbot_temp_name', 'chatbot_temp_phone', 'chatbot_temp_service']:
            if key in request.session: del request.session[key]
            
        return Response({
            'success': True,
            'reply': f"Excellent! Your booking request for an {service} has been received. Our team will call you at {phone} shortly. Do you need anything else?",
            'quick_replies': ['Working Hours', 'Service Cost', 'Clear Chat'],
            'state': 'INITIAL'
        })

    return Response({'success': False, 'message': 'Unknown state'})


# ─────────────────────────────────────────────────────────────────────────────
# Payment – QR Code
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def api_payment_qr(request):
    booking_id = request.query_params.get('bookingId')
    booking = get_object_or_404(Booking, bookingId=booking_id)
    provider = booking.provider
    amount = float(booking.service_amount)

    # Use provider's UPI ID if set, otherwise fall back to phone@ybl
    if provider.upi_id:
        upi_pa = provider.upi_id
    else:
        phone = provider.phone_number if provider.phone_number else DEFAULT_PHONE
        upi_pa = f"{phone}@ybl"

    upi_url = f"upi://pay?pa={upi_pa}&pn={provider.name}&am={amount}&cu=INR"

    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return Response({
        'success': True,
        'qr_code': qr_b64,
        'upi_url': upi_url,
        'upi_id': upi_pa,
        'amount': amount,
        'provider_name': provider.name,
        'phone': provider.phone_number or DEFAULT_PHONE,
        'date': booking.date,
        'time': booking.time,
        'address': booking.address,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Template (SSR) views
# ─────────────────────────────────────────────────────────────────────────────

def home_view(request):
    return render(request, 'core/home.html')


def signup_view(request):
    return render(request, 'core/signup.html')


def login_view(request):
    return render(request, 'core/login.html')


def forgotpass_view(request):
    return render(request, 'core/forgotpass.html')


def electrician_listing_view(request):
    return render(request, 'core/electrician_listing.html')


def plumber_listing_view(request):
    return render(request, 'core/plumber_listing.html')


def mechanic_listing_view(request):
    return render(request, 'core/mechanic_listing.html')


def provider_profile_view(request, provider_id):
    """Public provider profile page — /provider/<id>/"""
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    feedbacks = Feedback.objects.filter(provider=provider).select_related('user')
    return render(request, 'core/provider-profile.html', {
        'provider': provider,
        'feedbacks': feedbacks,
        'default_phone': DEFAULT_PHONE,
    })


def book_now_view(request, provider_id):
    """/book/<provider_id>/ — renders booking form for a specific provider."""
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    return render(request, 'core/booking.html', {'provider': provider})


def booking_view(request):
    """Generic /booking.html — reads ?id= from query string."""
    provider_id = request.GET.get('id')
    provider = None
    if provider_id and str(provider_id).isdigit():
        provider = ServiceProvider.objects.filter(id=int(provider_id)).first()
    return render(request, 'core/booking.html', {'provider': provider})


def payment_view(request):
    booking_id = request.GET.get('bookingId')
    booking = None
    qr_b64 = None
    upi_url = None

    if booking_id:
        booking = Booking.objects.filter(bookingId=booking_id).select_related('provider').first()

    if booking:
        provider = booking.provider
        amount = float(booking.service_amount)
        if provider.upi_id:
            upi_pa = provider.upi_id
        else:
            phone = provider.phone_number if provider.phone_number else DEFAULT_PHONE
            upi_pa = f"{phone}@ybl"
        upi_url = f"upi://pay?pa={upi_pa}&pn={provider.name}&am={amount}&cu=INR"
        qr = qrcode.QRCode(version=1, box_size=8, border=4)
        qr.add_data(upi_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return render(request, 'core/payment.html', {
        'booking': booking,
        'qr_code': qr_b64,
        'upi_url': upi_url,
    })


def feedback_view(request):
    booking_id = request.GET.get('bookingId')
    provider_id = request.GET.get('providerId')
    booking = None
    provider = None

    if booking_id:
        booking = Booking.objects.filter(bookingId=booking_id).select_related('provider', 'user').first()
        if booking:
            provider = booking.provider

    if not provider and provider_id:
        if str(provider_id).isdigit():
            provider = ServiceProvider.objects.filter(id=int(provider_id)).first()
        if not provider:
            provider = ServiceProvider.objects.filter(user__username=provider_id).first()

    return render(request, 'core/feedback.html', {'booking': booking, 'provider': provider})


def admin_dashboard_view(request):
    return render(request, 'core/admin_dashboard.html')


def provider_dashboard_view(request):
    return render(request, 'core/provider_dashboard.html')


def my_bookings_view(request):
    return render(request, 'core/my-bookings.html')


def my_profile_view(request):
    return render(request, 'core/my-profile.html')


def edit_profile_view(request):
    return render(request, 'core/my-profile.html')


def about_view(request):
    return render(request, 'core/about.html')


# ─────────────────────────────────────────────────────────────────────────────
# Legacy aliases (keep old URLs working)
# ─────────────────────────────────────────────────────────────────────────────

def profile_view(request):
    """Old /provider-profile.html — redirect to my-profile for logged-in providers,
    or show public profile if ?id= is given."""
    provider_id = request.GET.get('id')
    if provider_id and str(provider_id).isdigit():
        return redirect(f'/provider/{provider_id}/')
    return render(request, 'core/my-profile.html')


def social_login_redirect(request):
    """
    Called after allauth Google login succeeds (LOGIN_REDIRECT_URL).
    Issues a JWT for the Django session user and passes it to the frontend via JS.
    """
    user = request.user
    if not user.is_authenticated:
        return redirect('/login.html')

    tokens = _jwt_for_user(user)
    payload = _user_payload(user)

    # Ensure provider record exists if user_type is provider
    if user.user_type == 'provider':
        ServiceProvider.objects.get_or_create(
            user=user,
            defaults={
                'name': payload['fullName'],
                'service_type': 'other',
                'location': 'Unknown',
                'price_per_hour': 500,
            }
        )

    import json
    user_json = json.dumps(payload)
    tokens_json = json.dumps(tokens)

    # Render a tiny redirect page that stores the session in localStorage then redirects
    html = f"""<!DOCTYPE html>
<html><head><title>Logging in...</title></head>
<body>
<script>
  localStorage.setItem('authToken', {json.dumps(tokens['access'])});
  localStorage.setItem('currentUser', {json.dumps(user_json)});
  var userType = {json.dumps(payload.get('userType','customer'))};
  if (userType === 'provider') {{
    window.location.href = '/provider_dashboard.html';
  }} else if (userType === 'admin') {{
    window.location.href = '/admin_dashboard.html';
  }} else {{
    window.location.href = '/';
  }}
</script>
<p>Redirecting...</p>
</body></html>"""
    from django.http import HttpResponse
    return HttpResponse(html)
