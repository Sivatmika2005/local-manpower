const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Booking = sequelize.define('Booking', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    bookingId: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: true
    },
    customerId: {
        type: DataTypes.UUID,
        allowNull: false
    },
    customerName: {
        type: DataTypes.STRING,
        allowNull: false
    },
    providerId: {
        type: DataTypes.UUID,
        allowNull: true
    },
    providerName: {
        type: DataTypes.STRING,
        allowNull: false
    },
    serviceType: {
        type: DataTypes.STRING,
        allowNull: false
    },
    serviceLocation: {
        type: DataTypes.TEXT,
        allowNull: false
    },
    preferredDate: {
        type: DataTypes.DATEONLY,
        allowNull: false
    },
    preferredTime: {
        type: DataTypes.STRING,
        allowNull: false
    },
    additionalNotes: {
        type: DataTypes.TEXT,
        allowNull: true
    },
    serviceAmount: {
        type: DataTypes.FLOAT,
        allowNull: true
    },
    serviceFee: {
        type: DataTypes.FLOAT,
        allowNull: true
    },
    hourlyRate: {
        type: DataTypes.FLOAT,
        allowNull: true
    },
    status: {
        type: DataTypes.ENUM('pending', 'pending_payment', 'confirmed', 'completed', 'cancelled'),
        defaultValue: 'pending'
    },
    paymentStatus: {
        type: DataTypes.ENUM('unpaid', 'paid', 'refunded'),
        defaultValue: 'unpaid'
    },
    bookingDate: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW
    }
});

module.exports = Booking;
