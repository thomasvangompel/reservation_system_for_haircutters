# Haircutter Reservation System

A modern, mobile-friendly reservation system for haircutters and salons. Easily manage your customers, appointments, skills, and calendar—all in one place.

## Features

- **Online Booking**: Customers can book appointments 24/7 from any device.
- **Smart Calendar**: Visualize and manage your availability with flexible time blocks.
- **Skill Showcase**: Display your haircutting skills, styles, prices, and durations with images.
- **Custom Time Blocks**: Split large calendar blocks into smaller intervals for precise bookings.
- **Reservation Management**: View all reservations in your agenda and keep track of your schedule.
- **Email Notifications**: Customers receive confirmation and reminder emails automatically.
- **Mobile Friendly**: Responsive design for easy use on smartphones and tablets.
- **Secure Authentication**: User registration and login for privacy and data protection.

## Why Use This Tool?

- Save time and reduce no-shows with automated booking and reminders.
- Attract more clients by showcasing your skills and making booking easy.
- Stay organized with a clear agenda and smart calendar.
- Designed specifically for haircutters and salons—no unnecessary features.

## Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/thomasvangompel/reservation_system_for_haircutters.git
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your database:
   ```
   flask db upgrade
   ```
4. Start the server:
   ```
   flask run
   ```
5. Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Configuration
- Edit SMTP settings in `app/routes.py` to enable email notifications.
- Customize skill types, images, and prices in the dashboard.

## License
MIT
