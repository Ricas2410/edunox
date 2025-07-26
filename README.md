# 🎓 Edunox GH - Educational Consultancy Platform

A modern, production-ready Django platform for educational consultancy services, helping students navigate their academic journey with personalized guidance and comprehensive resources.

## ✨ Recent Major Updates

### 🚀 **Production-Ready Deployment**
- **Fly.io optimized** with health checks and monitoring
- **Performance enhanced** with caching and connection pooling
- **Security hardened** with HTTPS enforcement and secure headers
- **Mobile-first responsive design** with improved UX

### 🎨 **UI/UX Improvements**
- **Fixed mobile navbar** with separate profile dropdown
- **Enhanced dashboard pages** with beautiful hero sections
- **Working email toggles** with clear ON/OFF visual states
- **Consistent blue/purple theme** across all pages
- **Compact layouts** for better space utilization

### 📱 **Mobile Optimizations**
- **Touch-friendly interfaces** with proper sizing
- **Responsive grid layouts** that work on all devices
- **Improved navigation flow** for mobile users
- **Better accessibility** and user experience

## 🛠️ Technology Stack

- **Backend**: Django 4.2+ with Python 3.9+
- **Frontend**: HTML5, Tailwind CSS, Alpine.js
- **Database**: PostgreSQL (production) / SQLite (development)
- **Deployment**: Docker, Fly.io ready with health monitoring
- **Performance**: Redis caching, connection pooling, static file optimization

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip and virtualenv
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/edunox-gh.git
   cd edunox-gh
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

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py populate_initial_data
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to access the platform.

## 🌐 Production Deployment

### Fly.io Deployment (Recommended)

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   flyctl auth login
   ```

2. **Deploy with our automated script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Verify deployment**
   - Visit your app URL
   - Check `/health/` endpoint
   - Test all functionality

### Manual Deployment Steps

```bash
# Set environment variables
flyctl secrets set SECRET_KEY="your-secret-key" DEBUG=False

# Deploy
flyctl deploy

# Run migrations
flyctl ssh console -C "python manage.py migrate"

# Create superuser
flyctl ssh console -C "python manage.py createsuperuser"
```

## 📋 Features

### 👨‍🎓 **For Students**
- **Service Booking**: Book consultations with real-time availability
- **Document Management**: Secure upload and verification system
- **Educational Resources**: Comprehensive guides and materials
- **Profile Management**: Complete academic and personal profiles
- **Progress Tracking**: Monitor application status and milestones

### 👨‍💼 **For Administrators**
- **User Management**: Complete user administration dashboard
- **Service Management**: Create and manage consultancy services
- **Booking Management**: Handle appointments and scheduling
- **Content Management**: Manage resources, FAQs, and site content
- **Analytics Dashboard**: Track platform performance and usage

### 🔧 **Technical Features**
- **Mobile-First Design**: Responsive across all devices
- **Email Integration**: Automated notifications and communications
- **SEO Optimized**: Built-in SEO tools and meta management
- **Security**: CSRF protection, secure authentication, data encryption
- **Performance**: Caching, optimization, efficient database queries
- **Health Monitoring**: Built-in health checks for deployment monitoring

## 📚 Documentation

- [📖 Deployment Guide](DEPLOYMENT.md)
- [✅ Production Checklist](PRODUCTION_CHECKLIST.md)
- [📧 Email Setup Guide](GMAIL_SETUP_GUIDE.md)
- [🎛️ Admin Dashboard Guide](ADMIN_DASHBOARD_ENHANCEMENTS.md)
- [🔒 Security Assessment](PERFORMANCE_SECURITY_ASSESSMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- **Email**: admin@edunoxgh.com
- **Issues**: [GitHub Issues](https://github.com/yourusername/edunox-gh/issues)
- **Documentation**: Check the guides in this repository

## 🎯 Production Status

✅ **Ready for deployment** with:
- Health monitoring endpoints
- Production-optimized settings
- Security hardening
- Performance optimization
- Mobile-responsive design
- Working email notifications

---

**Built with ❤️ for educational excellence in Ghana** 🇬🇭
