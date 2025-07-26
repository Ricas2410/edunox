import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from django.apps import apps
from django.conf import settings
from django.core.files.storage import default_storage
import zipfile
import tempfile


class Command(BaseCommand):
    help = 'Create a comprehensive backup of all application data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Output directory for backup files (default: backups/)',
            default='backups'
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            help='Include media files in backup',
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress backup into a zip file',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting comprehensive data backup...')
        
        # Create backup directory
        backup_dir = options['output']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'Edunox_backup_{timestamp}'
        backup_path = os.path.join(backup_dir, backup_name)
        
        os.makedirs(backup_path, exist_ok=True)
        
        try:
            # Backup database data
            self.backup_database_data(backup_path)
            
            # Backup media files if requested
            if options['include_media']:
                self.backup_media_files(backup_path)
            
            # Create backup metadata
            self.create_backup_metadata(backup_path)
            
            # Compress if requested
            if options['compress']:
                zip_path = f'{backup_path}.zip'
                self.compress_backup(backup_path, zip_path)
                self.stdout.write(f'Backup compressed to: {zip_path}')
            else:
                self.stdout.write(f'Backup created at: {backup_path}')
                
            self.stdout.write(
                self.style.SUCCESS('Backup completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Backup failed: {str(e)}')
            )
            raise

    def backup_database_data(self, backup_path):
        """Backup all database data in a database-agnostic format"""
        self.stdout.write('Backing up database data...')
        
        # Get all models from all apps
        all_models = []
        for app_config in apps.get_app_configs():
            if app_config.name.startswith('django.'):
                continue  # Skip Django's built-in apps
            all_models.extend(app_config.get_models())
        
        # Group models by app
        apps_data = {}
        
        for model in all_models:
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            
            if app_label not in apps_data:
                apps_data[app_label] = {}
            
            # Serialize model data
            queryset = model.objects.all()
            if queryset.exists():
                serialized_data = serialize('json', queryset)
                apps_data[app_label][model_name] = json.loads(serialized_data)
                self.stdout.write(f'  Backed up {queryset.count()} {model_name} records')
        
        # Save to JSON files (one per app)
        data_dir = os.path.join(backup_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        for app_label, app_data in apps_data.items():
            if app_data:  # Only save if there's data
                file_path = os.path.join(data_dir, f'{app_label}.json')
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(app_data, f, indent=2, ensure_ascii=False)
                self.stdout.write(f'  Saved {app_label} data to {file_path}')

    def backup_media_files(self, backup_path):
        """Backup media files"""
        self.stdout.write('Backing up media files...')
        
        media_backup_path = os.path.join(backup_path, 'media')
        os.makedirs(media_backup_path, exist_ok=True)
        
        # Copy media files
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            import shutil
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, media_root)
                    dst_path = os.path.join(media_backup_path, rel_path)
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
            
            self.stdout.write(f'  Media files backed up to {media_backup_path}')
        else:
            self.stdout.write('  No media files found to backup')

    def create_backup_metadata(self, backup_path):
        """Create backup metadata file"""
        metadata = {
            'backup_date': datetime.now().isoformat(),
            'django_version': getattr(settings, 'DJANGO_VERSION', 'unknown'),
            'database_engine': settings.DATABASES['default']['ENGINE'],
            'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
            'backup_version': '1.0',
            'apps_included': [app.name for app in apps.get_app_configs() if not app.name.startswith('django.')],
        }
        
        metadata_path = os.path.join(backup_path, 'backup_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(f'  Backup metadata saved to {metadata_path}')

    def compress_backup(self, backup_path, zip_path):
        """Compress backup directory into a zip file"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arc_path)
        
        # Remove uncompressed directory
        import shutil
        shutil.rmtree(backup_path)
