#!/bin/bash

# Deployment script for Edunox GH to Fly.io
# Make sure you have flyctl installed and are logged in

set -e  # Exit on any error

echo "🚀 Starting deployment to Fly.io..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   https://fly.io/docs/getting-started/installing-flyctl/"
    exit 1
fi

# Check if user is logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ You are not logged in to Fly.io. Please run:"
    echo "   flyctl auth login"
    exit 1
fi

# Set environment variables
echo "🔧 Setting environment variables..."
flyctl secrets set \
    SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" \
    DEBUG=False \
    ALLOWED_HOSTS="edunox-gh.fly.dev,*.fly.dev" \
    SECURE_SSL_REDIRECT=True \
    SESSION_COOKIE_SECURE=True \
    CSRF_COOKIE_SECURE=True \
    SECURE_HSTS_SECONDS=31536000 \
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True \
    SECURE_HSTS_PRELOAD=True

# Deploy the application
echo "📦 Deploying application..."
flyctl deploy --ha=false

# Run migrations
echo "🗄️  Running database migrations..."
flyctl ssh console -C "python manage.py migrate"

# Create superuser if needed (optional)
echo "👤 Creating superuser (optional)..."
read -p "Do you want to create a superuser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    flyctl ssh console -C "python manage.py createsuperuser"
fi

# Collect static files
echo "📁 Collecting static files..."
flyctl ssh console -C "python manage.py collectstatic --noinput"

echo "✅ Deployment completed successfully!"
echo "🌐 Your application is available at: https://edunox-gh.fly.dev"
echo "🔧 Admin panel: https://edunox-gh.fly.dev/admin/"
echo "📊 Dashboard: https://edunox-gh.fly.dev/dashboard/"

echo ""
echo "📋 Next steps:"
echo "1. Configure your domain name (if you have one)"
echo "2. Set up email configuration"
echo "3. Configure any additional environment variables"
echo "4. Test all functionality"
