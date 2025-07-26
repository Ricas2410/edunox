#!/bin/bash

# PythonAnywhere Setup Script for Edunox GH
# Run this script in PythonAnywhere bash console after cloning the repository

set -e  # Exit on any error

echo "🚀 Setting up Edunox GH on PythonAnywhere..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the project root directory."
    exit 1
fi

print_info "Current directory: $(pwd)"

# Step 1: Create virtual environment
print_info "Step 1: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Step 2: Activate virtual environment and install dependencies
print_info "Step 2: Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install mysqlclient  # For PythonAnywhere MySQL
print_status "Dependencies installed"

# Step 3: Create environment file
print_info "Step 3: Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status "Environment file created from example"
    print_warning "Please edit .env file with your actual configuration values"
else
    print_warning ".env file already exists"
fi

# Step 4: Test ImageKit integration
print_info "Step 4: Testing ImageKit integration..."
python manage.py test_imagekit
if [ $? -eq 0 ]; then
    print_status "ImageKit integration test passed"
else
    print_warning "ImageKit test had issues - check configuration"
fi

# Step 5: Run Django checks
print_info "Step 5: Running Django system checks..."
python manage.py check
if [ $? -eq 0 ]; then
    print_status "Django system checks passed"
else
    print_error "Django system checks failed"
    exit 1
fi

# Step 6: Collect static files
print_info "Step 6: Collecting static files..."
python manage.py collectstatic --noinput
print_status "Static files collected"

# Step 7: Show next steps
echo ""
echo "🎉 Setup completed successfully!"
echo "================================================"
echo ""
echo "📋 Next Steps:"
echo "1. Configure your MySQL database in PythonAnywhere dashboard"
echo "2. Update .env file with your database credentials"
echo "3. Run: python manage.py migrate"
echo "4. Run: python manage.py createsuperuser"
echo "5. Run: python manage.py populate_initial_data"
echo "6. Configure your web app in PythonAnywhere dashboard"
echo ""
echo "📚 Detailed instructions: pythonganywhere_deploy.md"
echo ""
echo "🔗 Your app will be available at: https://edunox.pythonanywhere.com"
echo ""

# Step 8: Create a quick reference file
cat > PYTHONANYWHERE_QUICK_REFERENCE.md << 'EOF'
# PythonAnywhere Quick Reference for Edunox GH

## Essential Commands

### Activate Virtual Environment
```bash
cd ~/edunox
source venv/bin/activate
```

### Database Operations
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py populate_initial_data
```

### Update Deployment
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# Then reload web app in dashboard
```

### Test ImageKit
```bash
python manage.py test_imagekit --upload-test
```

### Django Management
```bash
python manage.py check --deploy
python manage.py clearsessions
```

## Important Paths

- **Project Root**: `/home/edunox/edunox`
- **Virtual Environment**: `/home/edunox/edunox/venv`
- **Static Files**: `/home/edunox/edunox/staticfiles`
- **WSGI File**: `/var/www/edunox_pythonanywhere_com_wsgi.py`

## Database Configuration

- **Host**: `edunox.mysql.pythonanywhere-services.com`
- **Database**: `edunox$edunox_db`
- **Username**: `edunox`

## URLs

- **Main Site**: https://edunox.pythonanywhere.com
- **Admin**: https://edunox.pythonanywhere.com/admin/
- **Health Check**: https://edunox.pythonanywhere.com/health/

## Troubleshooting

1. **Import Errors**: Check virtual environment activation
2. **Database Issues**: Verify credentials in .env file
3. **Static Files**: Run collectstatic and check web app configuration
4. **ImageKit Issues**: Test with `python manage.py test_imagekit`

## Support

- Check error logs in PythonAnywhere dashboard
- Review pythonganywhere_deploy.md for detailed instructions
- Test locally first before deploying changes
EOF

print_status "Quick reference guide created: PYTHONANYWHERE_QUICK_REFERENCE.md"

echo ""
print_info "Setup script completed! 🎯"
