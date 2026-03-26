const API_URL = '/api';

const apiService = {
    // Auth
    async login(email, password) {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return await response.json();
    },

    async register(userData) {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        return await response.json();
    },

    // Bookings
    async createBooking(bookingData) {
        const response = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bookingData)
        });
        return await response.json();
    },

    async getCustomerBookings(customerId) {
        const response = await fetch(`${API_URL}/bookings/customer/${customerId}`);
        return await response.json();
    },

    async getProviderBookings(providerId) {
        const response = await fetch(`${API_URL}/bookings/provider/${providerId}`);
        return await response.json();
    },

    async updateBookingStatus(bookingId, status) {
        const response = await fetch(`${API_URL}/bookings/${bookingId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        return await response.json();
    },

    // Feedback
    async submitFeedback(feedbackData) {
        const response = await fetch(`${API_URL}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(feedbackData)
        });
        return await response.json();
    },

    async getProviderFeedback(providerId) {
        const response = await fetch(`${API_URL}/feedback/provider/${providerId}`);
        return await response.json();
    },

    // Users
    async getProviders() {
        const response = await fetch(`${API_URL}/users/providers`);
        return await response.json();
    },

    async getProvidersByCategory(category) {
        const response = await fetch(`${API_URL}/users/providers?category=${encodeURIComponent(category)}`);
        return await response.json();
    },

    async getProvider(providerId) {
        const response = await fetch(`${API_URL}/users/${providerId}`);
        return await response.json();
    }
};

window.apiService = apiService;
