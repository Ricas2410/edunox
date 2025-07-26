"""
ImageKit Storage Backend for Edunox GH
Handles file uploads to ImageKit CDN for both development and production
"""

from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible
from imagekitio import ImageKit
import uuid
import logging
import mimetypes
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

@deconstructible
class ImageKitStorage(Storage):
    """
    Custom storage backend for ImageKit CDN
    """
    
    def __init__(self):
        """Initialize ImageKit client"""
        try:
            self.imagekit = ImageKit(
                private_key=settings.IMAGEKIT_PRIVATE_KEY,
                public_key=settings.IMAGEKIT_PUBLIC_KEY,
                url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
            )
            logger.info("ImageKit storage initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ImageKit: {e}")
            raise
    
    def _save(self, name, content):
        """
        Save file to ImageKit
        """
        try:
            # Generate unique filename if needed
            if not name:
                name = str(uuid.uuid4())
            
            # Get file extension
            file_extension = name.split('.')[-1] if '.' in name else ''
            
            # Create unique file ID
            file_id = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            
            # Determine folder based on file type
            folder = self._get_folder_by_type(name)
            
            # Read file content
            content.seek(0)
            file_content = content.read()
            
            # Upload to ImageKit
            upload_response = self.imagekit.upload_file(
                file=file_content,
                file_name=file_id,
                options={
                    "folder": folder,
                    "use_unique_file_name": True,
                    "response_fields": ["name", "size", "file_id", "url", "thumbnail_url"]
                }
            )
            
            if upload_response.response_metadata.http_status_code == 200:
                # Return the file path for Django to store in database
                uploaded_name = upload_response.response_metadata.raw.get('name', file_id)
                logger.info(f"Successfully uploaded file: {uploaded_name}")
                return uploaded_name
            else:
                logger.error(f"ImageKit upload failed: {upload_response.response_metadata.raw}")
                raise Exception("Failed to upload to ImageKit")
                
        except Exception as e:
            logger.error(f"Error uploading file to ImageKit: {e}")
            # Fallback to local storage in development
            if settings.DEBUG:
                from django.core.files.storage import default_storage
                return default_storage._save(name, content)
            raise
    
    def _get_folder_by_type(self, filename):
        """
        Determine ImageKit folder based on file type
        """
        # Get file extension
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        # Image files
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
            return "/edunox/images/"
        
        # Document files
        elif ext in ['pdf', 'doc', 'docx', 'txt', 'rtf']:
            return "/edunox/documents/"
        
        # Profile pictures
        elif 'profile' in filename.lower():
            return "/edunox/profiles/"
        
        # Service images
        elif 'service' in filename.lower():
            return "/edunox/services/"
        
        # Default folder
        else:
            return "/edunox/uploads/"
    
    def exists(self, name):
        """
        Check if file exists in ImageKit
        Note: ImageKit doesn't provide a direct exists API, 
        so we return False to always allow uploads with unique names
        """
        return False
    
    def url(self, name):
        """
        Return the URL for accessing the file
        """
        if not name:
            return None
            
        # If name is already a full URL, return as is
        if name.startswith('http'):
            return name
            
        # Construct ImageKit URL
        base_url = settings.IMAGEKIT_URL_ENDPOINT.rstrip('/')
        clean_name = name.lstrip('/')
        
        return f"{base_url}/{clean_name}"
    
    def delete(self, name):
        """
        Delete file from ImageKit
        """
        try:
            # Extract file_id from name if possible
            file_id = name.split('/')[-1] if '/' in name else name
            
            # Delete from ImageKit
            delete_response = self.imagekit.delete_file(file_id=file_id)
            
            if delete_response.response_metadata.http_status_code == 204:
                logger.info(f"Successfully deleted file: {name}")
                return True
            else:
                logger.warning(f"Failed to delete file from ImageKit: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file from ImageKit: {e}")
            return False
    
    def size(self, name):
        """
        Return file size (ImageKit doesn't provide direct size API)
        """
        return 0
    
    def get_accessed_time(self, name):
        """
        Return last accessed time (not supported by ImageKit)
        """
        raise NotImplementedError("ImageKit storage doesn't support accessed time")
    
    def get_created_time(self, name):
        """
        Return creation time (not supported by ImageKit)
        """
        raise NotImplementedError("ImageKit storage doesn't support creation time")
    
    def get_modified_time(self, name):
        """
        Return last modified time (not supported by ImageKit)
        """
        raise NotImplementedError("ImageKit storage doesn't support modified time")


@deconstructible
class HybridStorage(Storage):
    """
    Hybrid storage that uses ImageKit for images and local storage for other files
    """
    
    def __init__(self):
        self.imagekit_storage = ImageKitStorage()
        from django.core.files.storage import default_storage
        self.local_storage = default_storage
    
    def _is_image(self, name):
        """Check if file is an image"""
        if not name:
            return False
        ext = name.lower().split('.')[-1] if '.' in name else ''
        return ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
    
    def _save(self, name, content):
        """Route to appropriate storage based on file type"""
        if self._is_image(name):
            return self.imagekit_storage._save(name, content)
        else:
            return self.local_storage._save(name, content)
    
    def url(self, name):
        """Get URL from appropriate storage"""
        if self._is_image(name):
            return self.imagekit_storage.url(name)
        else:
            return self.local_storage.url(name)
    
    def exists(self, name):
        """Check existence in appropriate storage"""
        if self._is_image(name):
            return self.imagekit_storage.exists(name)
        else:
            return self.local_storage.exists(name)
    
    def delete(self, name):
        """Delete from appropriate storage"""
        if self._is_image(name):
            return self.imagekit_storage.delete(name)
        else:
            return self.local_storage.delete(name)
