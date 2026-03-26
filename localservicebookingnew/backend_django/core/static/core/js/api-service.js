/**
 * api-service.js – Frontend API client
 * Matches Django backend routes exactly.
 */
if (typeof window.API_URL === 'undefined') {
    window.API_URL = '/api';
}
const API_URL = window.API_URL;

const apiService = {

    // ── Helpers ──────────────────────────────────────────────────────────────

    getHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem('authToken');
        if (token) headers['Authorization'] = `Bearer ${token}`;
        return headers;
    },

    _saveSession(data) {
        if (data && data.tokens) {
            localStorage.setItem('authToken', data.tokens.access);
        }
        if (data && data.user) {
            localStorage.setItem('currentUser', JSON.stringify(data.user));
        }
    },

    getCurrentUserFromStorage() {
        try {
            return JSON.parse(localStorage.getItem('currentUser') || 'null');
        } catch { return null; }
    },

    // ── Auth ─────────────────────────────────────────────────────────────────

    async register(userData) {
        // If userData has a profileImageFile, use multipart upload
        if (userData.profileImageFile) {
            return this.registerWithImage(userData);
        }

        // Normalize signup form fields to backend expected fields
        const nameParts = (userData.fullName || '').trim().split(' ');
        const payload = {
            username:   userData.username,
            email:      userData.email,
            password:   userData.password,
            userType:   userData.userType || 'customer',
            phone:      userData.phone || '',
            address:    userData.address || '',
            first_name: nameParts[0] || '',
            last_name:  nameParts.slice(1).join(' ') || '',
            fullName:   userData.fullName || '',
        };
        if ((userData.userType || 'customer') === 'provider') {
            payload.service_type   = userData.serviceCategory || userData.service_type || '';
            // Use dedicated location field, fall back to businessAddress
            payload.location       = userData.location || userData.businessAddress || '';
            payload.price_per_hour = userData.hourlyRate || userData.price_per_hour || 500;
            payload.provider_phone = userData.businessPhone || userData.phone || '';
            payload.upi_id         = userData.upiId || userData.upi_id || '';
            payload.description    = userData.businessDescription || userData.description || '';
        }
        const res = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (data.success) this._saveSession(data.data);
        return data;
    },

    async registerWithImage(userData) {
        // Multipart form submission — supports profile image file upload
        const nameParts = (userData.fullName || '').trim().split(' ');
        const form = new FormData();
        form.append('username',   userData.username);
        form.append('email',      userData.email);
        form.append('password',   userData.password);
        form.append('userType',   userData.userType || 'customer');
        form.append('phone',      userData.phone || '');
        form.append('address',    userData.address || '');
        form.append('first_name', nameParts[0] || '');
        form.append('last_name',  nameParts.slice(1).join(' ') || '');
        form.append('fullName',   userData.fullName || '');
        if ((userData.userType || 'customer') === 'provider') {
            form.append('service_type',   userData.serviceCategory || userData.service_type || '');
            form.append('location',       userData.location || userData.businessAddress || '');
            form.append('price_per_hour', userData.hourlyRate || userData.price_per_hour || 500);
            form.append('provider_phone', userData.businessPhone || userData.phone || '');
            form.append('upi_id',         userData.upiId || userData.upi_id || '');
            form.append('description',    userData.businessDescription || '');
        }
        if (userData.profileImageFile) {
            form.append('profile_image', userData.profileImageFile);
        }
        // No Content-Type header — browser sets multipart boundary automatically
        const token = localStorage.getItem('authToken');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const res = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers,
            body: form,
        });
        const data = await res.json();
        if (data.success) this._saveSession(data.data);
        return data;
    },

    async firebaseSync(userData) {
        const res = await fetch(`${API_URL}/firebase-sync/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData),
        });
        const data = await res.json();
        if (data.success) this._saveSession(data.data);
        return data;
    },

    async login(identifier, password) {
        const body = identifier.includes('@')
            ? { email: identifier, password }
            : { username: identifier, password };
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        if (data.success) this._saveSession(data.data);
        return data;
    },

    // Alias used by login.html
    async adminLogin(username, password) {
        return this.login(username, password);
    },

    async sendOTP(identifier, purpose = 'phone_login') {
        const res = await fetch(`${API_URL}/auth/otp/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier, purpose }),
        });
        return res.json();
    },

    async verifyOTPLogin(phone, otp) {
        const res = await fetch(`${API_URL}/auth/otp/verify-login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, otp }),
        });
        const data = await res.json();
        if (data.success) this._saveSession(data.data);
        return data;
    },

    async sendPasswordResetOTP(email) {
        return this.sendOTP(email, 'email_reset');
    },

    async resetPassword(email, otp, new_password) {
        const res = await fetch(`${API_URL}/auth/otp/verify-reset`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp, new_password }),
        });
        return res.json();
    },

    // ── Profile ───────────────────────────────────────────────────────────────

    async getMyProfile() {
        const res = await fetch(`${API_URL}/profile/`, { headers: this.getHeaders() });
        return res.json();
    },

    async updateMyProfile(data) {
        const res = await fetch(`${API_URL}/profile/`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });
        const result = await res.json();
        if (result.success && result.data) {
            // Refresh stored user data
            const current = this.getCurrentUserFromStorage() || {};
            localStorage.setItem('currentUser', JSON.stringify({ ...current, ...result.data }));
        }
        return result;
    },

    // ── Providers ─────────────────────────────────────────────────────────────

    async getProviders() {
        const res = await fetch(`${API_URL}/providers/`, { headers: this.getHeaders() });
        return res.json();
    },

    async getProvidersByCategory(category) {
        const res = await fetch(
            `${API_URL}/providers/?category=${encodeURIComponent(category.toLowerCase())}`,
            { headers: this.getHeaders() }
        );
        return res.json();
    },

    async getProvider(providerId) {
        const res = await fetch(`${API_URL}/providers/${providerId}/`, { headers: this.getHeaders() });
        return res.json();
    },

    async updateProviderStatus(providerId, newStatus) {
        const res = await fetch(`${API_URL}/providers/${providerId}/status/`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify({ status: newStatus }),
        });
        return res.json();
    },

    // ── Bookings ──────────────────────────────────────────────────────────────

    async createBooking(bookingData) {
        const res = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(bookingData),
        });
        return res.json();
    },

    async getCustomerBookings(customerId) {
        const res = await fetch(`${API_URL}/bookings/customer/${customerId}`, {
            headers: this.getHeaders(),
        });
        return res.json();
    },

    async getProviderBookings(providerId) {
        const res = await fetch(`${API_URL}/bookings/provider/${providerId}`, {
            headers: this.getHeaders(),
        });
        return res.json();
    },

    async updateBookingStatus(bookingId, statusValue, paymentMethod) {
        const body = { status: statusValue };
        if (paymentMethod) body.payment_method = paymentMethod;
        const res = await fetch(`${API_URL}/bookings/${bookingId}/status`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify(body),
        });
        return res.json();
    },

    // ── Feedback ──────────────────────────────────────────────────────────────

    async submitFeedback(feedbackData) {
        const res = await fetch(`${API_URL}/feedback`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(feedbackData),
        });
        return res.json();
    },

    async getProviderFeedback(providerId) {
        const res = await fetch(`${API_URL}/feedback/provider/${providerId}`, {
            headers: this.getHeaders(),
        });
        return res.json();
    },

    // ── Payment QR ────────────────────────────────────────────────────────────

    async getPaymentQR(bookingId) {
        const res = await fetch(`${API_URL}/payment/qr/?bookingId=${bookingId}`, {
            headers: this.getHeaders(),
        });
        return res.json();
    },
};

window.apiService = apiService;
