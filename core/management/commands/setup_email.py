"""
Management command to safely setup and test email configuration
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from core.models import SiteConfiguration
from core.email_utils import test_email_configuration, safe_send_mail
import getpass


class Command(BaseCommand):
    help = 'Setup and test email configuration for Edunox GH'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Only test current configuration without setup',
        )
        parser.add_argument(
            '--gmail',
            action='store_true',
            help='Setup Gmail SMTP configuration',
        )
        parser.add_argument(
            '--console',
            action='store_true',
            help='Switch to console backend (for development)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Edunox GH Email Configuration Setup')
        )
        self.stdout.write('=' * 50)

        if options['test_only']:
            self.test_current_configuration()
        elif options['gmail']:
            self.setup_gmail()
        elif options['console']:
            self.setup_console_backend()
        else:
            self.interactive_setup()

    def test_current_configuration(self):
        """Test current email configuration"""
        self.stdout.write('\n🧪 Testing current email configuration...')
        
        success, message = test_email_configuration()
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'✅ {message}'))
            
            # Try sending a test email
            try:
                result = safe_send_mail(
                    subject='Edunox GH - Configuration Test',
                    message='This is a test email to verify your configuration is working.',
                    recipient_list=['admin@example.com'],  # Won't actually send
                    fail_silently=False
                )
                self.stdout.write(self.style.SUCCESS('✅ Email sending mechanism is working'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Email sending failed: {e}'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ {message}'))

    def setup_gmail(self):
        """Setup Gmail SMTP configuration"""
        self.stdout.write('\n📧 Setting up Gmail SMTP...')
        
        gmail_address = input('Enter your Gmail address: ')
        if not gmail_address:
            self.stdout.write(self.style.ERROR('Gmail address is required'))
            return
        
        self.stdout.write('\n📝 To get your App Password:')
        self.stdout.write('1. Go to Google Account → Security')
        self.stdout.write('2. Enable 2-Factor Authentication')
        self.stdout.write('3. Go to App passwords')
        self.stdout.write('4. Generate password for "Edunox GH"')
        self.stdout.write('5. Copy the 16-character password\n')
        
        app_password = getpass.getpass('Enter your Gmail App Password: ')
        if not app_password:
            self.stdout.write(self.style.ERROR('App Password is required'))
            return
        
        # Remove spaces from app password
        app_password = app_password.replace(' ', '')
        
        # Update configuration
        config = SiteConfiguration.get_config()
        config.email_backend = 'django.core.mail.backends.smtp.EmailBackend'
        config.email_host = 'smtp.gmail.com'
        config.email_port = 587
        config.email_use_tls = True
        config.email_use_ssl = False
        config.email_host_user = gmail_address
        config.email_host_password = app_password
        config.default_from_email = gmail_address
        config.save()
        
        self.stdout.write(self.style.SUCCESS('✅ Gmail configuration saved'))
        
        # Test the configuration
        self.test_current_configuration()

    def setup_console_backend(self):
        """Setup console backend for development"""
        self.stdout.write('\n🖥️  Setting up console backend...')
        
        config = SiteConfiguration.get_config()
        config.email_backend = 'django.core.mail.backends.console.EmailBackend'
        config.email_host = ''
        config.email_port = 587
        config.email_use_tls = False
        config.email_use_ssl = False
        config.email_host_user = ''
        config.email_host_password = ''
        config.default_from_email = 'Edunox GH <noreply@Edunox.com>'
        config.save()
        
        self.stdout.write(self.style.SUCCESS('✅ Console backend configured'))
        self.stdout.write('📧 Emails will be printed to console instead of sent')

    def interactive_setup(self):
        """Interactive setup wizard"""
        self.stdout.write('\n🧙 Email Configuration Wizard')
        self.stdout.write('Choose your email backend:')
        self.stdout.write('1. Gmail SMTP')
        self.stdout.write('2. Console (Development)')
        self.stdout.write('3. Test current configuration')
        self.stdout.write('4. Exit')
        
        choice = input('\nEnter your choice (1-4): ').strip()
        
        if choice == '1':
            self.setup_gmail()
        elif choice == '2':
            self.setup_console_backend()
        elif choice == '3':
            self.test_current_configuration()
        elif choice == '4':
            self.stdout.write('👋 Goodbye!')
        else:
            self.stdout.write(self.style.ERROR('Invalid choice'))

    def show_current_config(self):
        """Show current email configuration"""
        config = SiteConfiguration.get_config()
        
        self.stdout.write('\n📋 Current Email Configuration:')
        self.stdout.write(f'Backend: {config.email_backend}')
        self.stdout.write(f'Host: {config.email_host}')
        self.stdout.write(f'Port: {config.email_port}')
        self.stdout.write(f'TLS: {config.email_use_tls}')
        self.stdout.write(f'SSL: {config.email_use_ssl}')
        self.stdout.write(f'User: {config.email_host_user}')
        self.stdout.write(f'From: {config.default_from_email}')
