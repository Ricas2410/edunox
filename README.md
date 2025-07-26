# EduBridge Ghana

Your gateway to affordable higher education and digital empowerment.

## Overview

EduBridge Ghana is a grassroots initiative committed to empowering students across Ghana—especially in underserved and rural communities—with access to tuition-free universities, traditional higher institutions, and personalized educational consulting.

## Features

### Core Functionality
- **User Registration & Authentication** - Secure user accounts with email verification
- **Service Booking System** - Book educational services with calendar integration
- **Document Management** - Secure upload and management of academic documents
- **Contact System** - Contact form with file attachments (up to 5MB per file)
- **Resource Library** - Searchable educational resources and guides
- **Admin Dashboard** - Comprehensive admin panel for managing users and services

### Services Offered
- **University Application Support** - Help with applications to UoPeople and other institutions
- **Scholarship Guidance** - Assistance with scholarship applications
- **Digital Literacy Training** - Learn essential online learning skills
- **Personal Application Service** - Complete application assistance for non-tech-savvy users
- **Educational Consultancy** - Career and program guidance

## Tech Stack

- **Backend**: Django 4.2.7 (Python)
- **Frontend**: HTML5, Tailwind CSS, Alpine.js
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Django Allauth
- **File Storage**: Local storage (development), AWS S3 (production)
- **Email**: SMTP configuration
- **Deployment**: Gunicorn, WhiteNoise

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Edubridge
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate Initial Data**
   ```bash
   python manage.py populate_initial_data
   ```

8. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

9. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/edubridge

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@edubridge.com

# AWS S3 (for production file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

## Project Structure

```
Edunox_GH/
├── edubridge/              # Main project settings
├── core/                   # Core app (home, about, FAQ)
├── accounts/               # User management and profiles
├── services/               # Service booking and management
├── resources/              # Educational resources
├── contact/                # Contact form and messaging
├── dashboard/              # User and admin dashboards
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploaded files
├── requirements.txt        # Python dependencies
└── manage.py              # Django management script
```

## Usage

### For Students
1. **Register** - Create an account with email verification
2. **Complete Profile** - Add personal and educational information
3. **Upload Documents** - Submit required documents (ID, academic results)
4. **Browse Services** - Explore available educational services
5. **Book Services** - Schedule consultations and training sessions
6. **Access Resources** - Use the free educational resource library

### For Administrators
1. **Admin Dashboard** - Access via `/my-admin/`
2. **Manage Users** - View and manage user accounts
3. **Review Documents** - Verify uploaded documents
4. **Handle Bookings** - Manage service bookings and assignments
5. **Respond to Contacts** - Handle contact form submissions
6. **Content Management** - Manage services, resources, and FAQs

## API Endpoints

The application includes RESTful API endpoints for:
- User management
- Service booking
- Resource access
- Contact submissions

## Security Features

- CSRF protection
- XSS protection
- File upload validation
- User authentication and authorization
- Secure file storage
- Input sanitization

## SEO Optimization

- Meta tags and Open Graph
- Structured data (JSON-LD)
- XML sitemap
- Robots.txt
- Mobile-first responsive design
- Fast loading times

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email info@edubridge.com or create an issue in the repository.

## Deployment

### Production Deployment

1. **Set Environment Variables**
   - Set `DEBUG=False`
   - Configure `DATABASE_URL` for PostgreSQL
   - Set up email configuration
   - Configure AWS S3 for file storage

2. **Database Migration**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

3. **Web Server**
   - Use Gunicorn as WSGI server
   - Configure Nginx as reverse proxy
   - Set up SSL certificates

4. **Monitoring**
   - Set up logging
   - Configure error tracking
   - Monitor performance

## Changelog

### Version 1.0.0
- Initial release
- User registration and authentication
- Service booking system
- Document management
- Contact form with file attachments
- Resource library
- Admin dashboard
- Mobile-responsive design
- SEO optimization
