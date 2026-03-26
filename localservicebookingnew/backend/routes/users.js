const express = require('express');
const User = require('../models/User');
const router = express.Router();

// @route   GET /api/users
// @desc    Get all users (with pagination and filtering)
// @access  Public (for now - should be private in production)
router.get('/', async (req, res) => {
    try {
        const { page = 1, limit = 10, userType, status, search } = req.query;

        // Build query
        const query = {};
        
        if (userType) query.userType = userType;
        if (status) query.status = status;
        if (search) {
            query.$or = [
                { fullName: { $regex: search, $options: 'i' } },
                { username: { $regex: search, $options: 'i' } },
                { email: { $regex: search, $options: 'i' } }
            ];
        }

        const users = await User.find(query)
            .select('-password')
            .sort({ registrationDate: -1 })
            .limit(limit * 1)
            .skip((page - 1) * limit);

        const total = await User.countDocuments(query);

        res.status(200).json({
            success: true,
            data: {
                users,
                pagination: {
                    page: parseInt(page),
                    limit: parseInt(limit),
                    total,
                    pages: Math.ceil(total / limit)
                }
            }
        });

    } catch (error) {
        console.error('Get users error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get users',
            error: error.message
        });
    }
});

// @route   GET /api/users/:userId
// @desc    Get user by ID
// @access  Public (for now - should be private in production)
router.get('/:userId', async (req, res) => {
    try {
        const { userId } = req.params;

        const user = await User.findOne({ userId }).select('-password');

        if (!user) {
            return res.status(404).json({
                success: false,
                message: 'User not found'
            });
        }

        res.status(200).json({
            success: true,
            data: { user }
        });

    } catch (error) {
        console.error('Get user error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get user',
            error: error.message
        });
    }
});

// @route   PUT /api/users/:userId
// @desc    Update user profile
// @access  Private (would need authentication middleware)
router.put('/:userId', async (req, res) => {
    try {
        const { userId } = req.params;
        const updates = req.body;

        // Remove sensitive fields that shouldn't be updated directly
        delete updates.password;
        delete updates.userId;
        delete updates.registrationDate;

        const user = await User.findOneAndUpdate(
            { userId },
            updates,
            { new: true, runValidators: true }
        ).select('-password');

        if (!user) {
            return res.status(404).json({
                success: false,
                message: 'User not found'
            });
        }

        res.status(200).json({
            success: true,
            message: 'User updated successfully',
            data: { user }
        });

    } catch (error) {
        console.error('Update user error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to update user',
            error: error.message
        });
    }
});

// @route   DELETE /api/users/:userId
// @desc    Delete user
// @access  Private (would need authentication middleware)
router.delete('/:userId', async (req, res) => {
    try {
        const { userId } = req.params;

        const user = await User.findOneAndDelete({ userId });

        if (!user) {
            return res.status(404).json({
                success: false,
                message: 'User not found'
            });
        }

        res.status(200).json({
            success: true,
            message: 'User deleted successfully'
        });

    } catch (error) {
        console.error('Delete user error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to delete user',
            error: error.message
        });
    }
});

// @route   GET /api/users/stats
// @desc    Get user statistics
// @access  Private (would need authentication middleware)
router.get('/stats/overview', async (req, res) => {
    try {
        const totalUsers = await User.countDocuments();
        const totalCustomers = await User.countDocuments({ userType: 'customer' });
        const totalProviders = await User.countDocuments({ userType: 'provider' });
        const activeUsers = await User.countDocuments({ status: 'active' });
        const newUsersThisMonth = await User.countDocuments({
            registrationDate: {
                $gte: new Date(new Date().getFullYear(), new Date().getMonth(), 1)
            }
        });

        res.status(200).json({
            success: true,
            data: {
                totalUsers,
                totalCustomers,
                totalProviders,
                activeUsers,
                newUsersThisMonth
            }
        });

    } catch (error) {
        console.error('Get stats error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get statistics',
            error: error.message
        });
    }
});

module.exports = router;
