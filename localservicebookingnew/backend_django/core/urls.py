from django.urls import path
from . import views

urlpatterns = [
    # ── Health ────────────────────────────────────────────────────────────────
    path('api/health/', views.health_check),
    path('api/health', views.health_check),

    # ── Auth ──────────────────────────────────────────────────────────────────
    path('api/auth/register', views.api_register),
    path('api/auth/register/', views.api_register),
    path('api/register', views.api_register),
    path('api/auth/login', views.api_login),
    path('api/auth/login/', views.api_login),
    path('api/login', views.api_login),
    path('api/firebase-sync', views.api_firebase_sync),
    path('api/firebase-sync/', views.api_firebase_sync),

    # OTP
    path('api/auth/otp/send', views.api_send_otp),
    path('api/auth/otp/send/', views.api_send_otp),
    path('api/auth/otp/verify-login', views.api_verify_otp_login),
    path('api/auth/otp/verify-login/', views.api_verify_otp_login),
    path('api/auth/otp/verify-reset', views.api_verify_otp_reset),
    path('api/auth/otp/verify-reset/', views.api_verify_otp_reset),

    # ── Profile (edit) ────────────────────────────────────────────────────────
    path('api/profile/', views.api_my_profile),
    path('api/profile', views.api_my_profile),
    path('api/profile/upload-image/', views.api_upload_profile_image),
    path('api/profile/upload-image', views.api_upload_profile_image),

    # ── Providers ─────────────────────────────────────────────────────────────
    path('api/providers/', views.api_providers),
    path('api/providers', views.api_providers),
    path('api/providers/<str:provider_id>/status/', views.api_update_provider_status),
    path('api/providers/<str:provider_id>/status', views.api_update_provider_status),
    path('api/providers/<str:provider_id>/', views.api_provider_detail),
    path('api/providers/<str:provider_id>', views.api_provider_detail),

    # ── Bookings ──────────────────────────────────────────────────────────────
    path('api/bookings', views.api_bookings),
    path('api/bookings/', views.api_bookings),
    path('api/admin/bookings/', views.api_admin_all_bookings),
    path('api/admin/bookings', views.api_admin_all_bookings),
    path('api/admin/promote/', views.api_promote_admin),
    path('api/admin/promote', views.api_promote_admin),
    path('api/bookings/customer/<str:customer_id>', views.api_customer_bookings),
    path('api/bookings/customer/<str:customer_id>/', views.api_customer_bookings),
    path('api/bookings/provider/<str:provider_id>', views.api_provider_bookings),
    path('api/bookings/provider/<str:provider_id>/', views.api_provider_bookings),
    path('api/bookings/<str:booking_id>/status', views.api_update_booking_status),
    path('api/bookings/<str:booking_id>/status/', views.api_update_booking_status),

    # ── Feedback ──────────────────────────────────────────────────────────────
    path('api/feedback', views.api_feedback),
    path('api/feedback/', views.api_feedback),
    path('api/feedback/provider/<str:provider_id>', views.api_provider_feedback),
    path('api/feedback/provider/<str:provider_id>/', views.api_provider_feedback),

    path('api/payment/qr/', views.api_payment_qr),
    path('api/payment/qr', views.api_payment_qr),

    # ── Chatbot ───────────────────────────────────────────────────────────────
    path('api/chatbot/', views.api_chatbot),
    path('api/chatbot', views.api_chatbot),

    # ── Page routes ───────────────────────────────────────────────────────────
    path('', views.home_view, name='home'),
    path('home.html', views.home_view),
    path('about.html', views.about_view, name='about'),
    path('signup.html', views.signup_view, name='signup'),
    path('login.html', views.login_view, name='login'),
    path('forgotpass.html', views.forgotpass_view, name='forgotpass'),

    # Listing pages
    path('electrician_listing.html', views.electrician_listing_view, name='electrician_listing'),
    path('plumber_listing.html', views.plumber_listing_view, name='plumber_listing'),
    path('mechanic_listing.html', views.mechanic_listing_view, name='mechanic_listing'),

    # Provider public profile  /provider/<id>/
    path('provider/<int:provider_id>/', views.provider_profile_view, name='provider_profile'),

    # Book Now  /book/<id>/
    path('book/<int:provider_id>/', views.book_now_view, name='book_now'),

    # Booking form (also handles ?id= query param)
    path('booking.html', views.booking_view, name='booking'),

    # Payment & Feedback
    path('payment.html', views.payment_view, name='payment'),
    path('feedback.html', views.feedback_view, name='feedback'),

    # Dashboards & profile pages
    path('admin_dashboard.html', views.admin_dashboard_view, name='admin_dashboard'),
    path('provider_dashboard.html', views.provider_dashboard_view, name='provider_dashboard'),
    path('my-bookings.html', views.my_bookings_view, name='my_bookings'),
    path('my-profile.html', views.my_profile_view, name='my_profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),

    # Legacy alias — /provider-profile.html?id=X redirects to /provider/X/
    path('provider-profile.html', views.profile_view, name='profile'),

    # Social login complete — issues JWT and redirects to correct dashboard
    path('auth/social/complete/', views.social_login_redirect, name='social_login_complete'),
]
