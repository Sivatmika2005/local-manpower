from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, ServiceProvider, Booking, Feedback


# ── User ──────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    userType = serializers.CharField(source='user_type', required=False)
    fullName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'userId', 'username', 'email', 'password', 'userType',
                  'fullName', 'phone', 'address']
        extra_kwargs = {'password': {'write_only': True}}

    def get_fullName(self, obj):
        full = f"{obj.first_name} {obj.last_name}".strip()
        return full if full else obj.username

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    userType = serializers.CharField(source='user_type', default='customer')
    fullName = serializers.CharField(write_only=True, required=False, allow_blank=True)
    # Provider-specific
    service_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    location     = serializers.CharField(write_only=True, required=False, allow_blank=True)
    price_per_hour = serializers.DecimalField(
        write_only=True, required=False, allow_null=True,
        max_digits=10, decimal_places=2
    )
    provider_phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    upi_id         = serializers.CharField(write_only=True, required=False, allow_blank=True)
    description    = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'userType', 'fullName',
                  'phone', 'address', 'first_name', 'last_name',
                  'service_type', 'location', 'price_per_hour',
                  'provider_phone', 'upi_id', 'description']

    def to_internal_value(self, data):
        # Map frontend camelCase to backend snake_case
        new_data = data.copy()
        mapping = {
            'userType': 'user_type',
            'fullName': 'fullName',
            'serviceType': 'service_type',
            'pricePerHour': 'price_per_hour',
            'providerPhone': 'provider_phone',
            'upiId': 'upi_id'
        }
        for f, b in mapping.items():
            if f in data:
                new_data[b] = data[f]
        return super().to_internal_value(new_data)

    def validate(self, data):
        # For providers, enforce required fields: name, service, location, price, phone, upi, image
        if data.get('user_type') == 'provider':
            errors = {}
            if not data.get('service_type', '').strip():
                errors['service_type'] = 'Service type is required for providers.'
            if not data.get('location', '').strip():
                errors['location'] = 'Location/city is required for providers.'
            if not data.get('upi_id', '').strip():
                errors['upi_id'] = 'UPI ID is required for providers.'
            if not (data.get('price_per_hour') or 0):
                errors['price_per_hour'] = 'Price per hour is required for providers.'
            
            # Note: name and phone are also required but usually come from User model or specific provider fields
            if errors:
                raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        service_type   = validated_data.pop('service_type', '').strip()
        location       = validated_data.pop('location', '').strip()
        price_per_hour = validated_data.pop('price_per_hour', None)
        provider_phone = validated_data.pop('provider_phone', '').strip()
        upi_id         = validated_data.pop('upi_id', '').strip()
        description    = validated_data.pop('description', '').strip()
        full_name_raw  = validated_data.pop('fullName', '').strip()
        password       = validated_data.pop('password')

        # Derive first/last name from fullName if not explicitly set
        if full_name_raw and not validated_data.get('first_name'):
            parts = full_name_raw.split(' ', 1)
            validated_data['first_name'] = parts[0]
            validated_data['last_name']  = parts[1] if len(parts) > 1 else ''

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        print(f'[REGISTER] User saved: id={user.id} username={user.username} type={user.user_type}')

        if user.user_type == 'provider':
            full_name = f"{user.first_name} {user.last_name}".strip() or full_name_raw or user.username
            provider = ServiceProvider.objects.create(
                user=user,
                name=full_name,
                service_type=service_type.lower() if service_type else 'other',
                location=location or 'Local Area',
                price_per_hour=price_per_hour or 500,
                phone_number=provider_phone or user.phone or '',
                upi_id=upi_id,
                description=description,
                status=ServiceProvider.STATUS_AVAILABLE,
            )
            print(f"Provider saved: {provider.id}")
            print(f'[REGISTER] Provider details: name={provider.name!r} '
                  f'type={provider.service_type!r} upi={provider.upi_id!r} '
                  f'loc={provider.location!r} price={provider.price_per_hour}')
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField()

    def validate(self, data):
        identifier = data.get('username') or data.get('email')
        password = data.get('password')
        if not identifier:
            raise serializers.ValidationError('Username or email is required.')

        # Try username first, then email
        from django.db.models import Q
        user = User.objects.filter(Q(username=identifier) | Q(email=identifier)).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials.')
        data['user'] = user
        return data


# ── ServiceProvider ───────────────────────────────────────────────────────────

class ServiceProviderSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = ServiceProvider
        fields = ['id', 'name', 'service_type', 'location', 'price_per_hour',
                  'phone_number', 'description', 'is_available',
                  'avg_rating', 'review_count']

    def get_avg_rating(self, obj):
        return obj.average_rating()

    def get_review_count(self, obj):
        return obj.feedback_set.count()


# ── Booking ───────────────────────────────────────────────────────────────────

class BookingSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_service = serializers.CharField(source='provider.service_type', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'bookingId', 'user', 'user_name', 'provider', 'provider_name',
                  'provider_service', 'date', 'time', 'address', 'status',
                  'service_amount', 'payment_status', 'payment_method', 'created_at']
        read_only_fields = ['bookingId', 'service_amount', 'created_at']


# ── Feedback ──────────────────────────────────────────────────────────────────

class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_name', 'provider', 'provider_name',
                  'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']
