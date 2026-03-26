const express = require('express');
const User = require('../models/User');
const router = express.Router();

// @route   GET /api/providers
// @desc    Get all providers with filtering and sorting
// @access  Public
router.get('/', async (req, res) => {
    try {
        const { 
            page = 1, 
            limit = 10, 
            category, 
            availability, 
            sortBy = 'registrationDate',
            sortOrder = 'desc',
            search 
        } = req.query;

        // Build query for providers only
        const query = { userType: 'provider', status: 'active' };
        
        if (category) query.serviceCategory = category;
        if (availability) query.availability = availability;
        if (search) {
            query.$or = [
                { businessName: { $regex: search, $options: 'i' } },
                { fullName: { $regex: search, $options: 'i' } },
                { serviceCategory: { $regex: search, $options: 'i' } },
                { description: { $regex: search, $options: 'i' } }
            ];
        }

        // Build sort object
        const sort = {};
        sort[sortBy] = sortOrder === 'desc' ? -1 : 1;

        const providers = await User.find(query)
            .select('-password')
            .sort(sort)
            .limit(limit * 1)
            .skip((page - 1) * limit);

        const total = await User.countDocuments(query);

        res.status(200).json({
            success: true,
            data: {
                providers,
                pagination: {
                    page: parseInt(page),
                    limit: parseInt(limit),
                    total,
                    pages: Math.ceil(total / limit)
                }
            }
        });

    } catch (error) {
        console.error('Get providers error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get providers',
            error: error.message
        });
    }
});

// @route   GET /api/providers/new
// @desc    Get recently registered providers (last 60 minutes)
// @access  Public
router.get('/new', async (req, res) => {
    try {
        const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
        
        const newProviders = await User.find({
            userType: 'provider',
            status: 'active',
            registrationDate: { $gte: oneHourAgo }
        })
        .select('-password')
        .sort({ registrationDate: -1 });

        res.status(200).json({
            success: true,
            data: {
                providers: newProviders,
                count: newProviders.length
            }
        });

    } catch (error) {
        console.error('Get new providers error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get new providers',
            error: error.message
        });
    }
});

// @route   GET /api/providers/categories
// @desc    Get all service categories
// @access  Public
router.get('/categories', async (req, res) => {
    try {
        const categories = await User.distinct('serviceCategory', {
            userType: 'provider',
            status: 'active',
            serviceCategory: { $ne: null, $ne: '' }
        });

        res.status(200).json({
            success: true,
            data: { categories }
        });

    } catch (error) {
        console.error('Get categories error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get categories',
            error: error.message
        });
    }
});

// @route   GET /api/providers/:providerId
// @desc    Get provider by ID
// @access  Public
router.get('/:providerId', async (req, res) => {
    try {
        const { providerId } = req.params;

        const provider = await User.findOne({ 
            userId: providerId, 
            userType: 'provider' 
        }).select('-password');

        if (!provider) {
            return res.status(404).json({
                success: false,
                message: 'Provider not found'
            });
        }

        res.status(200).json({
            success: true,
            data: { provider }
        });

    } catch (error) {
        console.error('Get provider error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get provider',
            error: error.message
        });
    }
});

// @route   PUT /api/providers/:providerId/rating
// @desc    Update provider rating
// @access  Private (would need authentication middleware)
router.put('/:providerId/rating', async (req, res) => {
    try {
        const { providerId } = req.params;
        const { rating } = req.body;

        if (!rating || rating < 0 || rating > 5) {
            return res.status(400).json({
                success: false,
                message: 'Rating must be between 0 and 5'
            });
        }

        const provider = await User.findOneAndUpdate(
            { userId: providerId, userType: 'provider' },
            { $set: { rating } },
            { new: true }
        ).select('-password');

        if (!provider) {
            return res.status(404).json({
                success: false,
                message: 'Provider not found'
            });
        }

        res.status(200).json({
            success: true,
            message: 'Rating updated successfully',
            data: { provider }
        });

    } catch (error) {
        console.error('Update rating error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to update rating',
            error: error.message
        });
    }
});

// @route   PUT /api/providers/:providerId/availability
// @desc    Update provider availability
// @access  Private (would need authentication middleware)
router.put('/:providerId/availability', async (req, res) => {
    try {
        const { providerId } = req.params;
        const { availability } = req.body;

        if (!availability || !['available', 'busy', 'offline'].includes(availability)) {
            return res.status(400).json({
                success: false,
                message: 'Availability must be: available, busy, or offline'
            });
        }

        const provider = await User.findOneAndUpdate(
            { userId: providerId, userType: 'provider' },
            { $set: { availability } },
            { new: true }
        ).select('-password');

        if (!provider) {
            return res.status(404).json({
                success: false,
                message: 'Provider not found'
            });
        }

        res.status(200).json({
            success: true,
            message: 'Availability updated successfully',
            data: { provider }
        });

    } catch (error) {
        console.error('Update availability error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to update availability',
            error: error.message
        });
    }
});

// @route   GET /api/providers/stats
// @desc    Get provider statistics
// @access  Private (would need authentication middleware)
router.get('/stats/overview', async (req, res) => {
    try {
        const totalProviders = await User.countDocuments({ userType: 'provider' });
        const activeProviders = await User.countDocuments({ 
            userType: 'provider', 
            status: 'active' 
        });
        const availableProviders = await User.countDocuments({ 
            userType: 'provider', 
            status: 'active',
            availability: 'available'
        });
        const newProvidersThisMonth = await User.countDocuments({
            userType: 'provider',
            registrationDate: {
                $gte: new Date(new Date().getFullYear(), new Date().getMonth(), 1)
            }
        });

        // Top rated providers
        const topRatedProviders = await User.find({ 
            userType: 'provider', 
            status: 'active' 
        })
        .select('-password')
        .sort({ rating: -1 })
        .limit(5);

        res.status(200).json({
            success: true,
            data: {
                totalProviders,
                activeProviders,
                availableProviders,
                newProvidersThisMonth,
                topRatedProviders
            }
        });

    } catch (error) {
        console.error('Get provider stats error:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to get provider statistics',
            error: error.message
        });
    }
});

module.exports = router;
