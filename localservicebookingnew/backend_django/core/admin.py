from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ServiceProvider, Booking, Feedback, OTP


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone', 'is_active')
    list_filter = ('user_type', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {'fields': ('userId', 'user_type', 'phone', 'address')}),
    )


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'location', 'price_per_hour', 'phone_number', 'is_available')
    list_filter = ('service_type', 'is_available')
    search_fields = ('name', 'location')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('bookingId', 'user', 'provider', 'date', 'status', 'payment_status')
    list_filter = ('status', 'payment_status')
    search_fields = ('bookingId', 'user__username', 'provider__name')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'rating', 'created_at')
    list_filter = ('rating',)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'purpose', 'otp_code', 'is_used', 'created_at')
    list_filter = ('purpose', 'is_used')
