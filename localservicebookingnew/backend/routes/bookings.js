const express = require('express');
const router = express.Router();
const Booking = require('../models/Booking');

// Create booking
router.post('/', async (req, res) => {
    try {
        const booking = await Booking.create(req.body);
        
        // Emit socket event to provider and admin
        const io = req.app.get('io');
        io.to(booking.providerId).emit('newBooking', booking);
        io.emit('adminNewBooking', booking);
        
        res.status(201).json({ success: true, data: booking });
    } catch (error) {
        console.error('Create booking error:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

// Get user bookings
router.get('/customer/:customerId', async (req, res) => {
    try {
        const bookings = await Booking.findAll({
            where: { customerId: req.params.customerId },
            order: [['createdAt', 'DESC']]
        });
        res.json({ success: true, data: bookings });
    } catch (error) {
        console.error('Get customer bookings error:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

// Get provider bookings
router.get('/provider/:providerId', async (req, res) => {
    try {
        const bookings = await Booking.findAll({
            where: { providerId: req.params.providerId },
            order: [['createdAt', 'DESC']]
        });
        res.json({ success: true, data: bookings });
    } catch (error) {
        console.error('Get provider bookings error:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

// Update booking status
router.patch('/:bookingId/status', async (req, res) => {
    try {
        const { status } = req.body;
        await Booking.update(
            { status },
            { where: { bookingId: req.params.bookingId } }
        );
        
        const booking = await Booking.findOne({ where: { bookingId: req.params.bookingId } });
        
        // Emit socket event to customer and admin
        const io = req.app.get('io');
        io.to(booking.customerId).emit('bookingStatusChanged', {
            bookingId: booking.bookingId,
            status: status
        });
        io.emit('adminBookingStatusChanged', {
            bookingId: booking.bookingId,
            status: status
        });
        
        res.json({ success: true, message: 'Status updated', data: booking });
    } catch (error) {
        console.error('Update status error:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

module.exports = router;
