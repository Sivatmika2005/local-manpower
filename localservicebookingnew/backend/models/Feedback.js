const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Feedback = sequelize.define('Feedback', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    bookingId: {
        type: DataTypes.STRING,
        allowNull: false
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
        allowNull: false
    },
    rating: {
        type: DataTypes.INTEGER,
        allowNull: false,
        validate: {
            min: 1,
            max: 5
        }
    },
    comment: {
        type: DataTypes.TEXT,
        allowNull: true
    },
    timestamp: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW
    }
});

module.exports = Feedback;
