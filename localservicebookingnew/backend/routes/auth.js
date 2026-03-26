const express = require('express');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const router = express.Router();

// Generate JWT Token
const generateToken = (userId) => {
    return jwt.sign({ userId }, process.env.JWT_SECRET, {
        expiresIn: process.env.JWT_EXPIRE || '7d'
    });
};

// @route   POST /api/auth/register
// @desc    Register a new user
// @access  Public
router.post('/register', async (req, res) => {
    try {
        const {
            fullName,
            email,
            phone,
            dob,
            address,
            username,
            password,
            userType,
            businessName,
            serviceCategory,
            experience,
            description,
            hourlyRate
        } = req.body;

        // Validation
        if (!fullName || !email || !phone || !dob || !address || !username || !password) {
            return res.status(400).json({
                success: false,
                message: 'Please provide all required fields'
            });
        }

        // Check if user already exists
        const existingUser = await User.findOne({
            $or: [{ email }, { username }]
        });

        if (existingUser) {
            return res.status(400).json({
                success: false,
                message: existingUser.email === email ? 'Email already exists' : 'Username already exists'
            });
        }

        // Generate userId
        const userId = User.generateUserId(userType === 'provider' ? 'PROV' : 'CUST');

        // Create user object
        const userData = {
            userId,
            fullName,
            email,
            phone,
            dob,
            address,
            username,
            password,
            userType: userType || 'customer'
        };

        // Add provider-specific fields if userType is provider
        if (userType === 'provider') {
            userData.businessName = businessName || fullName;
            userData.serviceCategory = serviceCategory || 'General';
            userData.experience = experience || '';
            userData.description = description || '';
            userData.hourlyRate = hourlyRate || 0;
        }

        // Create new user
        const user = new User(userData);
        await user.save();

        // Generate token
        const token = generateToken(user._id);

        res.status(201).json({
            success: true,
            message: 'User registered successfully',
            data: {
                user: user.getProfile(),
                token
            }
        });

    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({
            success: false,
            message: 'Registration failed',
            error: error.message
        });
    }
});

// @route   POST /api/auth/login
// @desc    Login user
// @access  Public
router.post('/login', async (req, res) => {
    try {
        const { username, password } = req.body;

        // Validation
        if (!username || !password) {
            return res.status(400).json({
                success: false,
                message: 'Please provide username and password'
            });
        }

        // Find user by username or email
        const user = await User.findOne({
            $or: [{ username }, { email: username }]
        });

        if (!user) {
            return res.status(401).json({
                success: false,
                message: 'Invalid credentials'
            });
        }

        // Check if user is active
        if (user.status !== 'active') {
            return res.status(401).json({
                success: false,
                message: 'Account is not active'
            });
        }

        // Check password
        const isPasswordValid = await user.comparePassword(password);

        if (!isPasswordValid) {
            return res.status(401).json({
                success: false,
                message: 'Invalid credentials'
            });
        }

        // Update last login
        await user.updateLastLogin();

        // Generate token
        const token = generateToken(user._id);

        res.status(200).json({
            success: true,
            message: 'Login successful',
            data: {
                user: user.getProfile(),
                token
            }
        });

    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({
            success: false,
            message: 'Login failed',
            error: error.message
        });
    }
});

// @route   POST /api/auth/admin-login
// @desc    Admin login
// @access  Public
router.post('/admin-login', async (req, res) => {
    try {
        const { username, password } = req.body;

        // Check hardcoded admin credentials
        if (username === 'admin' && password === 'admin123') {
            const adminUser = {
                userId: 'ADMIN001',
                fullName: 'Administrator',
                username: 'admin',
                userType: 'admin',
                status: 'active'
            };

            const token = generateToken('admin');

            res.status(200).json({
                success: true,
                message: 'Admin login successful',
                data: {
                    user: adminUser,
                    token
                }
            });
        } else {
            res.status(401).json({
                success: false,
                message: 'Invalid admin credentials'
            });
        }

    } catch (error) {
        console.error('Admin login error:', error);
        res.status(500).json({
            success: false,
            message: 'Admin login failed',
            error: error.message
        });
    }
});

// @route   GET /api/auth/me
// @desc    Get current user
// @access  Private
router.get('/me', async (req, res) => {
    try {
        // This would require middleware to verify JWT token
        // For now, we'll implement a basic version
        const token = req.header('Authorization')?.replace('Bearer ', '');

        if (!token) {
            return res.status(401).json({
                success: false,
                message: 'No token provided'
            });
        }

        try {
            const decoded = jwt.verify(token, process.env.JWT_SECRET);
            
            // Handle admin user
            if (decoded.userId === 'admin') {
                const adminUser = {
                    userId: 'ADMIN001',
                    fullName: 'Administrator',
                    username: 'admin',
                    userType: 'admin',
                    status: 'active'
                };
                return res.status(200).json({
                    success: true,
                    data: { user: adminUser }
                });
            }

            // Find regular user
            const user = await User.findById(decoded.userId);
            
            if (!user) {
                return res.status(401).json({
                    success: false,
                    message: 'User not found'
                });
            }

            res.status(200).json({
                success: true,
                data: { user: user.getProfile() }
            });

        } catch (jwtError) {
            return res.status(401).json({
                success: false,
                message: 'Invalid token'
            });
        }

    } catch (error) {
        console.error('Get user error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get user',
            error: error.message
        });
    }
});

module.exports = router;
