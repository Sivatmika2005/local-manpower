const { Sequelize } = require('sequelize');
require('dotenv').config();

const sequelize = new Sequelize(
    process.env.DB_NAME || 'local_service_booking',
    process.env.DB_USER || 'root',
    process.env.DB_PASSWORD || '',
    {
        host: process.env.DB_HOST || 'localhost',
        dialect: 'mysql',
        logging: false, // Set to console.log to see SQL queries
        pool: {
            max: 5,
            min: 0,
            acquire: 30000,
            idle: 10000
        }
    }
);

const mysql = require('mysql2/promise');

const connectDB = async () => {
    try {
        // Create database if it doesn't exist
        const connection = await mysql.createConnection({
            host: process.env.DB_HOST || 'localhost',
            user: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || ''
        });
        await connection.query(`CREATE DATABASE IF NOT EXISTS \`${process.env.DB_NAME || 'local_service_booking'}\`;`);
        await connection.end();

        await sequelize.authenticate();
        console.log('MySQL Connection has been established successfully.');
        
        // Sync models
        await sequelize.sync({ alter: true });
        console.log('Database models synchronized.');
    } catch (error) {
        console.error('Unable to connect to the database:', error);
        process.exit(1);
    }
};

module.exports = { sequelize, connectDB };
