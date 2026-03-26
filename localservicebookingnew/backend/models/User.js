const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
    userId: {
        type: String,
        required: true,
        unique: true
    },
    fullName: {
        type: String,
        required: [true, 'Full name is required'],
        trim: true,
        maxlength: [100, 'Full name cannot exceed 100 characters']
    },
    email: {
        type: String,
        required: [true, 'Email is required'],
        unique: true,
        lowercase: true,
        trim: true,
        match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
    },
    phone: {
        type: String,
        required: [true, 'Phone number is required'],
        trim: true
    },
    dob: {
        type: Date,
        required: [true, 'Date of birth is required']
    },
    address: {
        type: String,
        required: [true, 'Address is required'],
        trim: true,
        maxlength: [200, 'Address cannot exceed 200 characters']
    },
    username: {
        type: String,
        required: [true, 'Username is required'],
        unique: true,
        trim: true,
        minlength: [3, 'Username must be at least 3 characters'],
        maxlength: [30, 'Username cannot exceed 30 characters']
    },
    password: {
        type: String,
        required: [true, 'Password is required'],
        minlength: [6, 'Password must be at least 6 characters']
    },
    userType: {
        type: String,
        required: true,
        enum: ['customer', 'provider'],
        default: 'customer'
    },
    status: {
        type: String,
        enum: ['active', 'inactive', 'suspended'],
        default: 'active'
    },
    registrationDate: {
        type: Date,
        default: Date.now
    },
    lastLogin: {
        type: Date
    },
    profileImage: {
        type: String,
        default: ''
    },
    // Provider specific fields
    businessName: {
        type: String,
        trim: true
    },
    serviceCategory: {
        type: String,
        trim: true
    },
    experience: {
        type: String,
        trim: true
    },
    description: {
        type: String,
        maxlength: [500, 'Description cannot exceed 500 characters']
    },
    hourlyRate: {
        type: Number,
        min: 0
    },
    availability: {
        type: String,
        default: 'available'
    },
    rating: {
        type: Number,
        default: 0,
        min: 0,
        max: 5
    },
    totalBookings: {
        type: Number,
        default: 0
    }
}, {
    timestamps: true
});

// Hash password before saving
userSchema.pre('save', async function(next) {
    // Only hash the password if it has been modified (or is new)
    if (!this.isModified('password')) return next();
    
    try {
        // Hash password with cost of 12
        const salt = await bcrypt.genSalt(12);
        this.password = await bcrypt.hash(this.password, salt);
        next();
    } catch (error) {
        next(error);
    }
});

// Compare password method
userSchema.methods.comparePassword = async function(candidatePassword) {
    return await bcrypt.compare(candidatePassword, this.password);
};

// Update last login
userSchema.methods.updateLastLogin = function() {
    this.lastLogin = new Date();
    return this.save();
};

// Get user profile without sensitive data
userSchema.methods.getProfile = function() {
    const userObject = this.toObject();
    delete userObject.password;
    return userObject;
};

// Static method to generate unique userId
userSchema.statics.generateUserId = function(prefix) {
    const random = Math.floor(Math.random() * 10000);
    return `${prefix}${random.toString().padStart(4, '0')}`;
};

module.exports = mongoose.model('User', userSchema);
