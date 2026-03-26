const express = require('express');
const router = express.Router();
const Feedback = require('../models/Feedback');
const User = require('../models/User');

// Submit feedback
router.post('/', async (req, res) => {
    try {
        const { bookingId, customerId, customerName, providerId, rating, comment } = req.body;
        
        const feedback = await Feedback.create({
            bookingId,
            customerId,
            customerName,
            providerId,
            rating,
            comment
        });

        // Update provider's average rating
        const feedbacks = await Feedback.findAll({ where: { providerId } });
        const avgRating = feedbacks.reduce((acc, f) => acc + f.rating, 0) / feedbacks.length;
        
        await User.update({ rating: avgRating }, { where: { userId: providerId } });

        res.status(201).json({ success: true, feedback });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

// Get feedback for a provider
router.get('/provider/:providerId', async (req, res) => {
    try {
        const feedback = await Feedback.findAll({
            where: { providerId: req.params.providerId },
            order: [['timestamp', 'DESC']]
        });
        res.json({ success: true, feedback });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
});

module.exports = router;
