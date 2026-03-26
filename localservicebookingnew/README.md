# Local Service Booking Platform

A comprehensive local service booking platform that connects customers with verified service providers including plumbers, electricians, and mechanics.

## Features

### For Customers
- Browse service providers by category
- View detailed provider profiles with ratings and reviews
- Book appointments with preferred dates and times
- Track booking status
- Provide feedback and ratings

### For Service Providers
- Create professional profiles
- Showcase portfolio and skills
- Manage bookings and schedules
- Receive customer reviews and ratings

### Admin Features
- Manage users and providers
- Monitor bookings and transactions
- Generate reports

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Backend**: Node.js, Express.js
- **Database**: MongoDB
- **Authentication**: Session-based authentication
- **Payment Gateway**: Integrated payment system

## Project Structure

```
local-service-booking/
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── about.html
│   ├── plumber_listing.html
│   ├── electrician_listing.html
│   ├── mechanic_listing.html
│   ├── provider-profile.html
│   ├── booking.html
│   ├── payment.html
│   ├── my-bookings.html
│   ├── feedback.html
│   ├── home.css
│   ├── admin_dashboard.css
│   └── provider_dashboard.css
├── backend/
│   ├── api/
│   ├── models/
│   ├── routes/
│   └── utils/
├── session-manager.js
└── api-service.js
```

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- MongoDB
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/local-service-booking.git
cd local-service-booking
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server:
```bash
npm run dev
```

5. Open your browser and navigate to `http://localhost:3000`

## Features in Detail

### Service Categories
- **Plumbing Services**: Emergency repairs, installations, maintenance
- **Electrical Services**: Wiring, panel upgrades, troubleshooting
- **Mechanical Services**: Vehicle repairs, maintenance, diagnostics

### User Roles
- **Customers**: Can browse, book, and manage services
- **Providers**: Can manage profiles and bookings
- **Admin**: Can manage the entire platform

### Booking Flow
1. Customer selects service category
2. Browse available providers
3. View provider details and reviews
4. Select date and time slot
5. Confirm booking and make payment
6. Track booking status

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Your Name - [@yourusername](https://github.com/yourusername)

## Acknowledgments

- [Bootstrap](https://getbootstrap.com/) for UI framework
- [Font Awesome](https://fontawesome.com/) for icons
- [Unsplash](https://unsplash.com/) for placeholder images
