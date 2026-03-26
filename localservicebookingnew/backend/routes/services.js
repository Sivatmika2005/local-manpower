const express = require('express');
const router = express.Router();
const User = require('../models/User');

// Get services by category
router.get('/:category', async (req, res) => {
    try {
        const providers = await User.findAll({
            where: { 
                role: 'provider',
                serviceType: req.params.category
            },
            attributes: { exclude: ['password'] }
        });
        res.json({ success: true, data: providers });
    } catch (error) {
        console.error('Get services error:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

module.exports = router;
