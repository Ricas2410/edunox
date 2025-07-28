"""
Management command to test database connectivity
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Test database connectivity and show current database configuration'

    def handle(self, *args, **options):
        try:
            # Get database configuration
            db_config = settings.DATABASES['default']
            
            self.stdout.write(
                self.style.SUCCESS('=== Database Configuration ===')
            )
            self.stdout.write(f"Engine: {db_config['ENGINE']}")
            
            if 'sqlite' in db_config['ENGINE']:
                self.stdout.write(f"Database file: {db_config['NAME']}")
                self.stdout.write(f"DEBUG mode: {settings.DEBUG}")
            else:
                self.stdout.write(f"Database: {db_config['NAME']}")
                self.stdout.write(f"Host: {db_config['HOST']}")
                self.stdout.write(f"Port: {db_config['PORT']}")
                self.stdout.write(f"User: {db_config['USER']}")
                self.stdout.write(f"DEBUG mode: {settings.DEBUG}")
            
            # Test connection
            self.stdout.write('\n=== Testing Connection ===')
            with connection.cursor() as cursor:
                if 'sqlite' in db_config['ENGINE']:
                    cursor.execute("SELECT sqlite_version();")
                    version = cursor.fetchone()[0]
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ SQLite connection successful! Version: {version}')
                    )
                else:
                    cursor.execute("SELECT VERSION();")
                    version = cursor.fetchone()[0]
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ MySQL connection successful! Version: {version}')
                    )
                
                # Test a simple query
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()[0]
                if result == 1:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Database query test passed!')
                    )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Database connection failed: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('\nTroubleshooting tips:')
            )
            if 'mysql' in str(e).lower():
                self.stdout.write('- Check MySQL server is running')
                self.stdout.write('- Verify database credentials in .env file')
                self.stdout.write('- Ensure mysqlclient is installed: pip install mysqlclient')
            else:
                self.stdout.write('- Check database configuration in settings.py')
                self.stdout.write('- Verify .env file exists and is properly configured')
