import json
import os
import zipfile
import tempfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.db import transaction, connection
from django.conf import settings
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Restore data from a backup (works across different database engines)'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_path',
            type=str,
            help='Path to backup directory or zip file'
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            help='Restore media files from backup',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before restore (DANGEROUS!)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be restored without actually doing it',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompts (for API usage)',
        )

    def handle(self, *args, **options):
        backup_path = options['backup_path']
        
        self.stdout.write('Starting data restore...')
        
        # Handle zip files
        temp_dir = None
        if backup_path.endswith('.zip'):
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            backup_path = temp_dir
        
        try:
            # Validate backup
            if not self.validate_backup(backup_path):
                self.stdout.write(
                    self.style.ERROR('Invalid backup format or missing files')
                )
                return
            
            # Show backup info
            self.show_backup_info(backup_path)
            
            if options['dry_run']:
                self.stdout.write('DRY RUN - No changes will be made')
                self.show_restore_plan(backup_path)
                return
            
            # Confirm restore (skip if force flag is used)
            if not options['force']:
                if not options['clear_existing']:
                    confirm = input('This will add data to your database. Continue? (y/N): ')
                    if confirm.lower() != 'y':
                        self.stdout.write('Restore cancelled')
                        return
                else:
                    confirm = input('WARNING: This will CLEAR ALL EXISTING DATA and restore from backup. Are you sure? (type "yes" to confirm): ')
                    if confirm != 'yes':
                        self.stdout.write('Restore cancelled')
                        return
            
            # Perform restore
            with transaction.atomic():
                if options['clear_existing']:
                    self.clear_existing_data()
                
                self.restore_database_data(backup_path)
                
                if options['include_media']:
                    self.restore_media_files(backup_path)
            
            self.stdout.write(
                self.style.SUCCESS('Restore completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Restore failed: {str(e)}')
            )
            raise
        finally:
            # Clean up temp directory
            if temp_dir:
                import shutil
                shutil.rmtree(temp_dir)

    def validate_backup(self, backup_path):
        """Validate backup structure"""
        required_files = ['backup_metadata.json']
        required_dirs = ['data']
        
        for file in required_files:
            if not os.path.exists(os.path.join(backup_path, file)):
                self.stdout.write(f'Missing required file: {file}')
                return False
        
        for dir in required_dirs:
            if not os.path.exists(os.path.join(backup_path, dir)):
                self.stdout.write(f'Missing required directory: {dir}')
                return False
        
        return True

    def show_backup_info(self, backup_path):
        """Display backup information"""
        metadata_path = os.path.join(backup_path, 'backup_metadata.json')
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.stdout.write('\n=== BACKUP INFORMATION ===')
        self.stdout.write(f'Backup Date: {metadata.get("backup_date", "Unknown")}')
        self.stdout.write(f'Django Version: {metadata.get("django_version", "Unknown")}')
        self.stdout.write(f'Source Database: {metadata.get("database_engine", "Unknown")}')
        self.stdout.write(f'Target Database: {settings.DATABASES["default"]["ENGINE"]}')
        self.stdout.write(f'Apps Included: {", ".join(metadata.get("apps_included", []))}')
        self.stdout.write('=' * 27 + '\n')

    def show_restore_plan(self, backup_path):
        """Show what would be restored"""
        data_dir = os.path.join(backup_path, 'data')
        
        self.stdout.write('\n=== RESTORE PLAN ===')
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                app_name = filename[:-5]  # Remove .json extension
                file_path = os.path.join(data_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    app_data = json.load(f)
                
                self.stdout.write(f'\nApp: {app_name}')
                for model_name, records in app_data.items():
                    self.stdout.write(f'  {model_name}: {len(records)} records')
        
        self.stdout.write('=' * 20 + '\n')

    def clear_existing_data(self):
        """Clear existing data from database"""
        self.stdout.write('Clearing existing data...')
        
        # Get all models in reverse dependency order
        all_models = []
        for app_config in apps.get_app_configs():
            if app_config.name.startswith('django.'):
                continue
            all_models.extend(app_config.get_models())
        
        # Clear data (in reverse order to handle foreign keys)
        for model in reversed(all_models):
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'  Cleared {count} {model._meta.model_name} records')

    def restore_database_data(self, backup_path):
        """Restore database data from backup"""
        self.stdout.write('Restoring database data...')
        
        data_dir = os.path.join(backup_path, 'data')
        
        # Process apps in dependency order
        app_order = self.get_app_dependency_order()
        
        for app_name in app_order:
            file_path = os.path.join(data_dir, f'{app_name}.json')
            if os.path.exists(file_path):
                self.restore_app_data(app_name, file_path)

    def get_app_dependency_order(self):
        """Get apps in dependency order"""
        # Basic dependency order - customize as needed
        return ['core', 'accounts', 'services', 'bookings', 'resources', 'contact', 'dashboard']

    def restore_app_data(self, app_name, file_path):
        """Restore data for a specific app"""
        self.stdout.write(f'  Restoring {app_name} data...')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            app_data = json.load(f)
        
        for model_name, records in app_data.items():
            try:
                # Get the model class
                model = apps.get_model(app_name, model_name)
                
                # Restore records
                restored_count = 0
                for record_data in records:
                    fields = record_data['fields']
                    pk = record_data['pk']
                    
                    # Handle foreign keys and many-to-many fields
                    fields = self.process_fields(model, fields)
                    
                    # Create or update record
                    obj, created = model.objects.update_or_create(
                        pk=pk,
                        defaults=fields
                    )
                    if created:
                        restored_count += 1
                
                self.stdout.write(f'    Restored {restored_count} {model_name} records')
                
            except Exception as e:
                self.stdout.write(f'    Error restoring {model_name}: {str(e)}')

    def process_fields(self, model, fields):
        """Process fields to handle special cases"""
        processed_fields = {}
        
        for field_name, value in fields.items():
            try:
                field = model._meta.get_field(field_name)
                
                # Handle different field types
                if hasattr(field, 'related_model') and field.related_model:
                    # Foreign key field
                    if value is not None:
                        processed_fields[field_name] = value
                    else:
                        processed_fields[field_name] = None
                elif field.many_to_many:
                    # Skip many-to-many fields for now (handle separately)
                    continue
                else:
                    processed_fields[field_name] = value
                    
            except Exception:
                # If field doesn't exist or other error, skip it
                continue
        
        return processed_fields

    def restore_media_files(self, backup_path):
        """Restore media files"""
        self.stdout.write('Restoring media files...')
        
        media_backup_path = os.path.join(backup_path, 'media')
        if not os.path.exists(media_backup_path):
            self.stdout.write('  No media files in backup')
            return
        
        media_root = settings.MEDIA_ROOT
        os.makedirs(media_root, exist_ok=True)
        
        import shutil
        for root, dirs, files in os.walk(media_backup_path):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, media_backup_path)
                dst_path = os.path.join(media_root, rel_path)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
        
        self.stdout.write(f'  Media files restored to {media_root}')
