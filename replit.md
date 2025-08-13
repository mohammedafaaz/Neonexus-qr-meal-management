# Overview

NEONEXUS36.0 is a Flask-based QR code meal pass management system designed for a 36-hour hackathon event. The application enables administrators to create meal sessions, generate unique QR codes for participants, and manage the redemption process through a real-time scanner interface. The system enforces one-time use validation and provides comprehensive tracking of QR code distribution and usage statistics.

# User Preferences

Preferred communication style: Simple, everyday language.
Design preferences: 
- Replit dark theme (dark backgrounds, light text)
- No gradients in backgrounds or buttons
- Minimal UI elements
- Clean, simplified layout
- Short and soothing audio feedback
- All sessions combined into single email (not separate emails)
- Brand name consistently capitalized as "NEONEXUS36.0"
- Clean home page without excessive descriptive text
- Custom header image integration in emails

# System Architecture

## Backend Framework
Built on Flask with SQLAlchemy ORM for database operations. The application follows a modular structure with separate files for models, routes, and utilities. Database operations use PostgreSQL with connection pooling and pre-ping validation for reliability.

## Database Design
Uses a simple two-table schema:
- **QRCode table**: Stores session-prefixed UUIDs, participant emails, redemption status, timestamps, and JSON payloads
- **Session table**: Manages meal session names and creation timestamps
- Implements one-time use enforcement through boolean flags and timestamp logging

## Authentication & Security
- Session-based authentication using Flask's built-in session management
- QR code validation includes keyword checking ('NEON36') and session matching
- Environment-based configuration for sensitive data like database URLs and email credentials
- ProxyFix middleware for proper header handling in production environments

## QR Code Generation
- Embeds JSON payloads containing session information and validation data
- Uses Python's qrcode library to generate PNG images
- Temporary file storage for generated QR codes during email transmission
- Session-prefixed unique identifiers (e.g., BREAKFAST1-a3abd943)

## Email Integration
- Gmail SMTP integration using Flask-Mail
- HTML-formatted emails with event branding
- One-recipient-per-send approach (no bulk mailing)
- QR codes attached as PNG files to emails

## Frontend Architecture
- Bootstrap 5 for responsive design with custom CSS styling
- HTML5-QRCode library for real-time camera-based scanning
- Vanilla JavaScript for admin dashboard functionality and scanner operations
- Audio feedback system using tone generation for scan results

## Real-time Scanner
- Camera-based QR code scanning with session validation
- Live feedback with success/failure audio cues
- Recent redemption tracking and display
- Session selection dropdown for targeted scanning

# External Dependencies

## Core Backend Libraries
- Flask: Web application framework
- SQLAlchemy: Database ORM and migrations
- Flask-Mail: Email sending capabilities
- Werkzeug ProxyFix: Production deployment support

## Database
- PostgreSQL: Primary data storage with connection pooling

## Email Service
- Gmail SMTP: Email delivery service using app-specific passwords
- Configured sender: teamneonexus@gmail.com

## Frontend Libraries
- Bootstrap 5.3.0: UI framework and responsive design
- Font Awesome 6.4.0: Icon library
- HTML5-QRCode 2.3.4: QR code scanning functionality

## QR Code Generation
- Python qrcode library: QR code image generation
- PIL (Python Imaging Library): Image processing and manipulation

## Audio Feedback
- Tone.js: Audio synthesis for scan feedback sounds (success/failure tones)

## Development Tools
- Python logging: Application monitoring and debugging
- Environment variables: Configuration management for sensitive data