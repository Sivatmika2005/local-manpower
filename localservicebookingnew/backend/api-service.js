// API Service for Local Service Booking App
// This file should be included in your frontend HTML files

class ApiService {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';
        this.token = localStorage.getItem('authToken');
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        localStorage.setItem('authToken', token);
    }

    // Get authentication token
    getToken() {
        return this.token || localStorage.getItem('authToken');
    }

    // Clear authentication token
    clearToken() {
        this.token = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
    }

    // Make API request
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add authorization header if token exists
        if (this.getToken()) {
            config.headers.Authorization = `Bearer ${this.getToken()}`;
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication endpoints
    async register(userData) {
        const response = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });

        if (response.success) {
            this.setToken(response.token);
            localStorage.setItem('currentUser', JSON.stringify(response.user));
        }

        return response;
    }

    async login(username, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (response.success) {
            this.setToken(response.token);
            localStorage.setItem('currentUser', JSON.stringify(response.user));
        }

        return response;
    }

    async getCurrentUser() {
        try {
            const response = await this.request('/auth/me');
            return response;
        } catch (error) {
            // Token might be expired, clear it
            this.clearToken();
            throw error;
        }
    }

    // User endpoints
    async getUsers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/users?${queryString}`);
    }

    async getUser(userId) {
        return await this.request(`/users/${userId}`);
    }

    async updateUser(userId, userData) {
        return await this.request(`/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    async deleteUser(userId) {
        return await this.request(`/users/${userId}`, {
            method: 'DELETE'
        });
    }

    async getUserStats() {
        return await this.request('/users/stats/overview');
    }

    // Booking endpoints
    async getBookings() {
        return await this.request('/bookings');
    }

    async createBooking(bookingData) {
        return await this.request('/bookings', {
            method: 'POST',
            body: JSON.stringify(bookingData)
        });
    }

    async getProviderBookings(providerId) {
        return await this.request(`/providers/${providerId}/bookings`);
    }

    // Provider endpoints
    async getProviders(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/providers?${queryString}`);
    }

    // Utility methods
    async healthCheck() {
        return await this.request('/health');
    }

    isLoggedIn() {
        return !!this.getToken();
    }

    getCurrentUserFromStorage() {
        const user = localStorage.getItem('currentUser');
        return user ? JSON.parse(user) : null;
    }

    logout() {
        this.clearToken();
        window.location.href = 'local serice booking/login.html';
    }
}

// Create global API service instance
const apiService = new ApiService();

// Make it available globally
window.apiService = apiService;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApiService;
}
