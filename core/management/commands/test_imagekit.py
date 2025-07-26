"""
Management command to test ImageKit integration
Usage: python manage.py test_imagekit
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from imagekitio import ImageKit
import tempfile
import os
from PIL import Image
import io

class Command(BaseCommand):
    help = 'Test ImageKit integration and upload functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--upload-test',
            action='store_true',
            help='Test file upload to ImageKit',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧪 Testing ImageKit Integration for Edunox GH')
        )
        
        # Test 1: Check configuration
        self.test_configuration()
        
        # Test 2: Initialize ImageKit client
        imagekit_client = self.test_client_initialization()
        
        if imagekit_client and options['upload_test']:
            # Test 3: Upload test file
            self.test_file_upload(imagekit_client)
        
        self.stdout.write(
            self.style.SUCCESS('✅ ImageKit integration test completed!')
        )

    def test_configuration(self):
        """Test ImageKit configuration"""
        self.stdout.write('\n📋 Testing Configuration...')
        
        try:
            private_key = getattr(settings, 'IMAGEKIT_PRIVATE_KEY', None)
            public_key = getattr(settings, 'IMAGEKIT_PUBLIC_KEY', None)
            url_endpoint = getattr(settings, 'IMAGEKIT_URL_ENDPOINT', None)
            
            if not private_key:
                self.stdout.write(
                    self.style.ERROR('❌ IMAGEKIT_PRIVATE_KEY not configured')
                )
                return False
            
            if not public_key:
                self.stdout.write(
                    self.style.ERROR('❌ IMAGEKIT_PUBLIC_KEY not configured')
                )
                return False
            
            if not url_endpoint:
                self.stdout.write(
                    self.style.ERROR('❌ IMAGEKIT_URL_ENDPOINT not configured')
                )
                return False
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Private Key: {private_key[:20]}...')
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Public Key: {public_key[:20]}...')
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ URL Endpoint: {url_endpoint}')
            )
            
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Configuration error: {e}')
            )
            return False

    def test_client_initialization(self):
        """Test ImageKit client initialization"""
        self.stdout.write('\n🔌 Testing Client Initialization...')
        
        try:
            imagekit = ImageKit(
                private_key=settings.IMAGEKIT_PRIVATE_KEY,
                public_key=settings.IMAGEKIT_PUBLIC_KEY,
                url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ ImageKit client initialized successfully')
            )
            
            return imagekit
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Client initialization failed: {e}')
            )
            return None

    def test_file_upload(self, imagekit_client):
        """Test file upload to ImageKit"""
        self.stdout.write('\n📤 Testing File Upload...')
        
        try:
            # Create a test image
            test_image = Image.new('RGB', (100, 100), color='red')
            
            # Save to bytes
            img_bytes = io.BytesIO()
            test_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Upload to ImageKit
            upload_response = imagekit_client.upload_file(
                file=img_bytes.getvalue(),
                file_name='test_upload.png',
                options={
                    "folder": "/edunox/test/",
                    "use_unique_file_name": True,
                    "response_fields": ["name", "size", "file_id", "url"]
                }
            )
            
            if upload_response.response_metadata.http_status_code == 200:
                file_data = upload_response.response_metadata.raw
                
                self.stdout.write(
                    self.style.SUCCESS('✅ File uploaded successfully!')
                )
                self.stdout.write(f'   📁 File Name: {file_data.get("name", "N/A")}')
                self.stdout.write(f'   📏 File Size: {file_data.get("size", "N/A")} bytes')
                self.stdout.write(f'   🆔 File ID: {file_data.get("file_id", "N/A")}')
                self.stdout.write(f'   🔗 URL: {file_data.get("url", "N/A")}')
                
                # Test deletion
                self.test_file_deletion(imagekit_client, file_data.get("file_id"))
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Upload failed: {upload_response.response_metadata.raw}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Upload test failed: {e}')
            )

    def test_file_deletion(self, imagekit_client, file_id):
        """Test file deletion from ImageKit"""
        if not file_id:
            return
            
        self.stdout.write('\n🗑️  Testing File Deletion...')
        
        try:
            delete_response = imagekit_client.delete_file(file_id=file_id)
            
            if delete_response.response_metadata.http_status_code == 204:
                self.stdout.write(
                    self.style.SUCCESS('✅ File deleted successfully!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Delete response: {delete_response.response_metadata.http_status_code}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Deletion test failed: {e}')
            )

    def test_storage_backend(self):
        """Test Django storage backend"""
        self.stdout.write('\n💾 Testing Django Storage Backend...')
        
        try:
            from core.storage import ImageKitStorage
            
            storage = ImageKitStorage()
            self.stdout.write(
                self.style.SUCCESS('✅ ImageKitStorage backend initialized')
            )
            
            # Test URL generation
            test_url = storage.url('test-file.jpg')
            self.stdout.write(f'   🔗 Test URL: {test_url}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Storage backend test failed: {e}')
            )
