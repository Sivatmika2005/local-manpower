// Universal Session Manager for Local Service Booking App
// This script manages user sessions across all pages

class SessionManager {
    constructor() {
        this.currentUser = null;
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        console.log('SessionManager initializing...');
        // Load user session on page load
        this.loadUserSession();
        
        // Update UI based on session
        this.updateUI();
        
        // Set up session monitoring
        this.setupSessionMonitoring();
        
        // Add additional check after a short delay for slow-loading navbars
        setTimeout(() => this.updateNavigation(), 500);
    }

    loadUserSession() {
        try {
            const userStr = localStorage.getItem('currentUser');
            if (userStr) {
                this.currentUser = JSON.parse(userStr);
                
                // Ensure userId exists
                if (!this.currentUser.userId && this.currentUser.username) {
                    this.currentUser.userId = this.currentUser.username;
                }
                
                // Ensure fullName exists
                if (!this.currentUser.fullName && this.currentUser.username) {
                    this.currentUser.fullName = this.currentUser.username;
                }
                
                console.log('Session loaded:', this.currentUser);
            }
        } catch (error) {
            console.error('Error loading session:', error);
            this.clearSession();
        }
    }

    getCurrentUser() {
        return this.currentUser;
    }

    isLoggedIn() {
        // Multiple checks to ensure accurate login state
        if (!this.currentUser) {
            // Try to load from localStorage as fallback
            this.loadUserSession();
        }
        
        const isLogged = !!(this.currentUser && this.currentUser.userId);
        
        console.log('isLoggedIn check:', {
            hasCurrentUser: !!this.currentUser,
            hasUserId: !!(this.currentUser && this.currentUser.userId),
            result: isLogged
        });
        
        return isLogged;
    }

    updateUserSession(userData) {
        this.currentUser = userData;
        localStorage.setItem('currentUser', JSON.stringify(userData));
        this.updateUI();
    }

    clearSession() {
        this.currentUser = null;
        localStorage.removeItem('currentUser');
        localStorage.removeItem('authToken');
        this.updateUI();
    }

    logout() {
        console.log('Logging out user:', this.currentUser?.fullName);
        this.clearSession();
        window.location.href = 'login.html';
    }

    updateUI() {
        // Update profile displays
        this.updateProfileDisplays();
        
        // Update navigation
        this.updateNavigation();
        
        // Show/hide login-required content
        this.updateContentVisibility();
    }

    updateProfileDisplays() {
        // Update all profile name elements
        const profileElements = document.querySelectorAll('[id*="profileName"], [id*="userName"], [class*="user-name"]');
        profileElements.forEach(element => {
            if (this.currentUser && this.currentUser.fullName) {
                element.textContent = this.currentUser.fullName;
            }
        });

        // Update header profile specifically
        const headerProfileName = document.getElementById('headerProfileName');
        if (headerProfileName && this.currentUser) {
            headerProfileName.textContent = this.currentUser.fullName;
        }

        // Update profile name in home2.html
        const profileName = document.getElementById('profileName');
        if (profileName && this.currentUser) {
            profileName.textContent = this.currentUser.fullName;
        }
    }

    updateNavigation() {
        // Find navigation areas and update based on login status
        const navElements = document.querySelectorAll('nav, .nav, .navigation');
        
        navElements.forEach(nav => {
            if (this.isLoggedIn()) {
                // User is logged in - show profile/logout
                this.addProfileToNav(nav);
            } else {
                // User is not logged in - show login link
                this.addLoginToNav(nav);
            }
        });
    }

    addProfileToNav(navElement) {
        // Remove existing login/signup buttons
        const existingLoginBtn = navElement.querySelector('.btn') || navElement.querySelector('a[href*="login"]');
        if (existingLoginBtn && !existingLoginBtn.closest('.user-profile')) {
            existingLoginBtn.remove();
        }

        // Check if profile already exists
        if (navElement.querySelector('.user-profile')) {
            // Update name if it exists but might be wrong
            const nameEl = navElement.querySelector('#navProfileName');
            if (nameEl) nameEl.textContent = this.currentUser.fullName;
            return;
        }

        // Create profile dropdown
        const profileDiv = document.createElement('div');
        profileDiv.className = 'user-profile';
        profileDiv.innerHTML = `
            <div class="profile-dropdown">
                <button class="profile-btn" onclick="sessionManager.toggleDropdown()">
                    <img src="https://picsum.photos/seed/${this.currentUser.username}/40/40.jpg" alt="Profile" class="profile-img">
                    <span id="navProfileName">${this.currentUser.fullName || 'User'}</span>
                    <i class="fas fa-chevron-down"></i>
                </button>
                <div class="dropdown-menu" id="profileDropdown">
                    <div class="dropdown-header">
                        <div class="user-info">
                            <strong>${this.currentUser.fullName}</strong>
                            <span class="user-email">${this.currentUser.email || this.currentUser.username}</span>
                        </div>
                    </div>
                    <div class="dropdown-divider"></div>
                    <a href="my-profile.html" class="dropdown-item">
                        <i class="fas fa-user"></i> My Profile
                    </a>
                    <a href="my-bookings.html" class="dropdown-item">
                        <i class="fas fa-calendar-alt"></i> My Bookings
                    </a>
                    <div class="dropdown-divider"></div>
                    <a href="#" class="dropdown-item" onclick="sessionManager.logout()" style="color: #e74c3c;">
                        <i class="fas fa-sign-out-alt"></i> Logout
                    </a>
                </div>
            </div>
        `;

        // Add styles if not already added
        if (!document.getElementById('session-manager-styles')) {
            const style = document.createElement('style');
            style.id = 'session-manager-styles';
            style.textContent = `
                header {
                    z-index: 10000 !important;
                }

                .user-profile {
                    position: relative;
                    display: flex;
                    align-items: center;
                }
                
                .profile-btn {
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-size: 14px;
                    transition: all 0.3s ease;
                    height: 40px;
                }
                
                .profile-btn:hover {
                    background: rgba(255, 255, 255, 0.2);
                    border-color: rgba(255, 255, 255, 0.3);
                }
                
                .profile-img {
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    border: 1.5px solid rgba(255, 255, 255, 0.5);
                    object-fit: cover;
                }
                
                /* Ensure nav links are centered with the profile */
                nav, .navigation, .nav {
                    display: flex !important;
                    align-items: center !important;
                    flex-wrap: nowrap !important;
                    gap: 15px;
                }
                
                nav a, .navigation a, .nav a {
                    display: flex;
                    align-items: center;
                    height: 40px;
                    text-decoration: none !important;
                    color: white !important;
                    transition: opacity 0.3s;
                }

                nav a:hover, .navigation a:hover, .nav a:hover {
                    opacity: 0.8;
                }
                
                .login-link.btn {
                    background: #2c3e50;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    padding: 0 20px;
                    border-radius: 20px;
                    font-weight: 600;
                }
                
                .dropdown-header {
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px 8px 0 0;
                }
                
                .user-info {
                    display: flex;
                    flex-direction: column;
                }
                
                .user-info strong {
                    font-size: 14px;
                    color: #2c3e50;
                }
                
                .user-email {
                    font-size: 11px;
                    color: #6c757d;
                }
                
                .dropdown-menu {
                    position: absolute;
                    top: calc(100% + 10px);
                    right: 0;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    min-width: 220px;
                    display: none;
                    z-index: 10001;
                    border: 1px solid rgba(0,0,0,0.05);
                    overflow: hidden;
                }
                
                .dropdown-menu.show {
                    display: block;
                    animation: profileFadeIn 0.2s ease-out;
                }
                
                @keyframes profileFadeIn {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .dropdown-item {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 12px 20px;
                    color: #444 !important;
                    text-decoration: none !important;
                    transition: all 0.2s ease;
                    font-size: 14px;
                }
                
                .dropdown-item:hover {
                    background: #f0f2f5;
                    color: #2c3e50 !important;
                    padding-left: 24px;
                }
                
                .dropdown-item i {
                    width: 18px;
                    color: #2c3e50;
                    font-size: 16px;
                }
                
                .dropdown-divider {
                    height: 1px;
                    background: #eee;
                    margin: 0;
                }
                
                header .user-profile .dropdown-item {
                    color: #444 !important;
                }
            `;
            document.head.appendChild(style);
        }

        // Replace or append to navigation
        const existingLinks = navElement.querySelectorAll('a');
        if (existingLinks.length > 0) {
            // Insert before the last link if possible, or append
            navElement.appendChild(profileDiv);
        } else {
            navElement.appendChild(profileDiv);
        }
    }

    addLoginToNav(navElement) {
        // Remove existing profile dropdown if it exists
        const existingProfile = navElement.querySelector('.user-profile');
        if (existingProfile) {
            existingProfile.remove();
        }

        // Find any existing login link
        let loginLink = navElement.querySelector('.login-link') || navElement.querySelector('a[href*="login"]');
        
        if (!loginLink) {
            // Create login link if missing
            loginLink = document.createElement('a');
            loginLink.className = 'login-link btn';
            loginLink.textContent = 'Login';
            navElement.appendChild(loginLink);
        }

        // Force standardized properties
        loginLink.href = 'login.html';
        loginLink.style.display = 'flex';
        loginLink.style.alignItems = 'center';
        loginLink.style.zIndex = '10005';
        
        // Ensure it's not hidden
        loginLink.style.visibility = 'visible';
        loginLink.style.opacity = '1';
        loginLink.style.pointerEvents = 'auto';
    }

    updateContentVisibility() {
        // Show/hide content based on login status
        const loginRequiredElements = document.querySelectorAll('.login-required');
        const loggedInElements = document.querySelectorAll('.logged-in-only');
        const loggedOutElements = document.querySelectorAll('.logged-out-only');

        if (this.isLoggedIn()) {
            // Show logged-in content
            loggedInElements.forEach(el => el.style.display = 'block');
            loggedOutElements.forEach(el => el.style.display = 'none');
            
            // Enable login-required features
            loginRequiredElements.forEach(el => {
                el.style.pointerEvents = 'auto';
                el.style.opacity = '1';
            });
        } else {
            // Show logged-out content
            loggedInElements.forEach(el => el.style.display = 'none');
            loggedOutElements.forEach(el => el.style.display = 'block');
            
            // Disable login-required features
            loginRequiredElements.forEach(el => {
                el.style.pointerEvents = 'none';
                el.style.opacity = '0.5';
            });
        }
    }

    toggleDropdown() {
        const dropdown = document.getElementById('profileDropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function closeDropdown(e) {
                if (!e.target.closest('.profile-dropdown')) {
                    dropdown.classList.remove('show');
                    document.removeEventListener('click', closeDropdown);
                }
            });
        }
    }

    setupSessionMonitoring() {
        // Monitor storage changes (for multi-tab support)
        window.addEventListener('storage', (e) => {
            if (e.key === 'currentUser') {
                this.loadUserSession();
                this.updateUI();
            }
        });

        // Check session validity periodically
        setInterval(() => {
            if (this.isLoggedIn()) {
                // Could add server-side session validation here
                console.log('Session active for:', this.currentUser.fullName);
            }
        }, 60000); // Check every minute
    }

    // Redirect to login if not authenticated
    requireAuth() {
        if (!this.isLoggedIn()) {
            console.log('Authentication required, redirecting to login');
            window.location.href = 'login.html';
            return false;
        }
        return true;
    }

    // Get user type for routing
    getUserType() {
        return this.currentUser?.userType || 'customer';
    }

    // Check if user is admin
    isAdmin() {
        return this.getUserType() === 'admin';
    }

    // Check if user is provider
    isProvider() {
        return this.getUserType() === 'provider';
    }

    // Check if user is customer
    isCustomer() {
        return this.getUserType() === 'customer';
    }
}

// Initialize session manager
const sessionManager = new SessionManager();

// Debug function to check session state
window.checkSession = function() {
    console.log('=== Session Debug Info ===');
    console.log('Session Manager exists:', !!window.sessionManager);
    console.log('Session Manager isLoggedIn type:', typeof window.sessionManager?.isLoggedIn);
    console.log('Current user from session manager:', window.sessionManager?.getCurrentUser());
    
    // Direct localStorage check
    const localStorageUser = localStorage.getItem('currentUser');
    console.log('LocalStorage has user:', !!localStorageUser);
    if (localStorageUser) {
        try {
            const parsed = JSON.parse(localStorageUser);
            console.log('Parsed user:', parsed);
            console.log('Has userId:', !!parsed.userId);
            console.log('Has fullName:', !!parsed.fullName);
        } catch (e) {
            console.error('Error parsing localStorage user:', e);
        }
    }
    console.log('========================');
};

// Auto-check session on load
setTimeout(() => {
    if (window.checkSession) {
        window.checkSession();
    }
}, 1000);

// Make it globally available
window.sessionManager = sessionManager;

// Auto-logout function for protected pages
function protectPage() {
    sessionManager.requireAuth();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SessionManager;
}
