# EduBridge Ghana - Production Deployment Guide

This guide provides comprehensive instructions for deploying EduBridge Ghana to production environments.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Domain name configured
- SSL certificates obtained
- Environment variables configured

### One-Command Deployment

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Deploy to production
./scripts/deploy.sh deploy
```

## 📋 Detailed Deployment Instructions

### 1. Server Requirements

**Minimum Requirements:**
- 2 CPU cores
- 4GB RAM
- 50GB SSD storage
- Ubuntu 20.04+ or similar Linux distribution

**Recommended for Production:**
- 4 CPU cores
- 8GB RAM
- 100GB SSD storage
- Load balancer for high availability

### 2. Domain and SSL Setup

#### Domain Configuration
1. Point your domain to your server's IP address
2. Configure DNS records:
   ```
   A     edubridge.com        -> YOUR_SERVER_IP
   A     www.edubridge.com    -> YOUR_SERVER_IP
   CNAME api.edubridge.com    -> edubridge.com
   ```

#### SSL Certificate
Option 1: Let's Encrypt (Free)
```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d edubridge.com -d www.edubridge.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

Option 2: Commercial Certificate
- Place certificate files in `nginx/ssl/`
- Update paths in `nginx/conf.d/edubridge.conf`

### 3. Environment Configuration

#### Copy and Configure Environment File
```bash
cp .env.example .env
```

#### Required Environment Variables
```bash
# Security
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=edubridge.com,www.edubridge.com

# Database
POSTGRES_DB=edubridge
POSTGRES_USER=edubridge
POSTGRES_PASSWORD=your-secure-password
DATABASE_URL=postgres://edubridge:password@db:5432/edubridge

# Email (using SendGrid)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@edubridge.com

# Monitoring
SENTRY_DSN=your-sentry-dsn
GOOGLE_ANALYTICS_ID=your-ga-id

# Site
SITE_URL=https://edubridge.com
```

### 4. Docker Deployment

#### Build and Start Services
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Build application
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

#### Verify Deployment
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs web

# Health check
curl -f https://edubridge.com/health/
```

### 5. Database Setup

#### Initial Data
```bash
# Load initial data (if available)
docker-compose -f docker-compose.prod.yml exec web python manage.py loaddata initial_data.json

# Create service categories
docker-compose -f docker-compose.prod.yml exec web python manage.py shell
```

#### Backup Configuration
```bash
# Create backup directory
mkdir -p backups

# Set up automated backups
crontab -e
# Add: 0 2 * * * /path/to/scripts/backup.sh
```

### 6. Monitoring Setup

#### Enable Monitoring Stack
```bash
# Start monitoring services
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Access Grafana
# URL: http://your-server:3000
# Username: admin
# Password: (from GRAFANA_PASSWORD env var)
```

#### Configure Alerts
1. Set up Sentry for error tracking
2. Configure email alerts for critical issues
3. Set up uptime monitoring (e.g., UptimeRobot)

### 7. Performance Optimization

#### Enable Caching
```bash
# Redis is automatically configured
# Verify cache is working
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

#### CDN Setup (Optional)
1. Configure Cloudflare or AWS CloudFront
2. Update static file URLs
3. Enable compression and caching

### 8. Security Hardening

#### Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

#### Regular Updates
```bash
# System updates
sudo apt update && sudo apt upgrade

# Docker image updates
docker-compose -f docker-compose.prod.yml pull
./scripts/deploy.sh deploy
```

## 🔧 Maintenance

### Regular Tasks

#### Daily
- Monitor application logs
- Check system resources
- Verify backup completion

#### Weekly
- Review security logs
- Update dependencies
- Performance analysis

#### Monthly
- Security audit
- Database optimization
- Backup testing

### Common Commands

```bash
# View logs
./scripts/deploy.sh logs [service]

# Check status
./scripts/deploy.sh status

# Create backup
./scripts/deploy.sh backup

# Health check
./scripts/deploy.sh health

# Rollback deployment
./scripts/deploy.sh rollback
```

### Troubleshooting

#### Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs [service]

# Check configuration
docker-compose -f docker-compose.prod.yml config

# Restart service
docker-compose -f docker-compose.prod.yml restart [service]
```

#### Database Issues
```bash
# Connect to database
docker-compose -f docker-compose.prod.yml exec db psql -U edubridge -d edubridge

# Check connections
docker-compose -f docker-compose.prod.yml exec db pg_stat_activity

# Backup database
./scripts/deploy.sh backup
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor database queries
docker-compose -f docker-compose.prod.yml logs web | grep "SLOW QUERY"

# Check Redis memory
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory
```

## 🌐 Alternative Deployment Options

### Heroku Deployment

1. Install Heroku CLI
2. Create Heroku app
3. Configure environment variables
4. Deploy:
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### AWS ECS Deployment

1. Build and push Docker image to ECR
2. Create ECS cluster and service
3. Configure load balancer
4. Set up RDS for database

### DigitalOcean App Platform

1. Connect GitHub repository
2. Configure environment variables
3. Set up managed database
4. Deploy automatically

## 📊 Monitoring and Analytics

### Key Metrics to Monitor

- Response time
- Error rate
- Database performance
- Memory usage
- Disk space
- User registrations
- Service bookings
- Email delivery rates

### Alerting Setup

Configure alerts for:
- Application errors (>1% error rate)
- High response time (>2 seconds)
- Database connection issues
- Low disk space (<10% free)
- High memory usage (>80%)

## 🔒 Security Checklist

- [ ] SSL certificate installed and configured
- [ ] Security headers enabled
- [ ] Database credentials secured
- [ ] API keys rotated regularly
- [ ] Firewall configured
- [ ] Fail2ban installed
- [ ] Regular security updates
- [ ] Backup encryption enabled
- [ ] Access logs monitored
- [ ] CSRF protection enabled

## 📞 Support

For deployment support:
- Email: admin@edubridge.com
- Documentation: [Internal Wiki]
- Emergency: [Emergency Contact]

## 📝 Changelog

### v1.0.0 (2024-01-XX)
- Initial production deployment
- Docker containerization
- Nginx reverse proxy
- PostgreSQL database
- Redis caching
- Celery background tasks
- Monitoring stack
- Automated backups
