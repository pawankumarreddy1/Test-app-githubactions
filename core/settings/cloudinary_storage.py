"""
Custom Cloudinary storage backend for Django
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.core.files.storage import Storage
from django.conf import settings
from django.utils.deconstruct import deconstructible
import os

# Module-level flag to track if Cloudinary has been configured
_cloudinary_configured = False


@deconstructible
class CloudinaryStorage(Storage):
    """Custom storage backend for Cloudinary"""
    
    def __init__(self):
        super().__init__()
        # Configuration will be done lazily when needed
    
    def _ensure_configured(self):
        """Ensure Cloudinary is configured before use"""
        global _cloudinary_configured
        
        # Check if already configured by verifying cloud_name exists
        config = cloudinary.config()
        if _cloudinary_configured and config.cloud_name:
            return
        
        # Configure Cloudinary using environment variables
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        api_key = os.environ.get('CLOUDINARY_API_KEY')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET')
        
        if cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
            _cloudinary_configured = True
        else:
            # Fallback: try to parse CLOUDINARY_URL
            cloudinary_url = os.environ.get('CLOUDINARY_URL')
            if cloudinary_url:
                # Parse CLOUDINARY_URL format: cloudinary://api_key:api_secret@cloud_name
                import re
                match = re.match(r'cloudinary://(\d+):([^@]+)@([^/]+)', cloudinary_url)
                if match:
                    cloudinary.config(
                        cloud_name=match.group(3),
                        api_key=match.group(1),
                        api_secret=match.group(2)
                    )
                    _cloudinary_configured = True
                else:
                    # Try direct DSN if regex doesn't match
                    try:
                        cloudinary.config(dsn=cloudinary_url)
                        _cloudinary_configured = True
                    except Exception:
                        pass
        
        # Verify configuration is set
        final_config = cloudinary.config()
        if not final_config.cloud_name:
            raise ValueError(
                "Cloudinary not configured. Please set CLOUDINARY_URL environment variable "
                "or set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET"
            )
        
        _cloudinary_configured = True
    
    def _open(self, name, mode='rb'):
        """Open file from Cloudinary"""
        # Cloudinary files are accessed via URL, not file handle
        # This is mainly for compatibility
        raise NotImplementedError("CloudinaryStorage doesn't support opening files directly")
    
    def _save(self, name, content):
        """Save file to Cloudinary"""
        # Ensure Cloudinary is configured before uploading
        self._ensure_configured()
        
        try:
            # Read file content
            if hasattr(content, 'read'):
                content.seek(0)
                file_content = content.read()
            else:
                file_content = content
            
            # Generate unique filename with UUID to avoid conflicts
            import uuid
            folder = "reciepts/"
            file_name = os.path.basename(name)
            # Add UUID prefix to ensure uniqueness
            file_base, file_ext = os.path.splitext(file_name)
            unique_name = f"{uuid.uuid4().hex[:8]}_{file_base}{file_ext}"
            public_id = f"{folder}{unique_name}"
            
            # Upload file to Cloudinary
            result = cloudinary.uploader.upload(
                file_content,
                public_id=public_id,
                folder=folder,
                resource_type="image"  # Assume images for receipts
            )
            
            # Return the public_id for storage
            return result['public_id']
        except Exception as e:
            import traceback
            raise Exception(f"Error uploading to Cloudinary: {str(e)}\n{traceback.format_exc()}")
    
    def exists(self, name):
        """Check if file exists in Cloudinary"""
        try:
            if not name or name.startswith('http'):
                return False
            self._ensure_configured()
            cloudinary.api.resource(name, resource_type="image")
            return True
        except:
            return False
    
    def url(self, name):
        """Get URL for file in Cloudinary"""
        try:
            # If name is already a URL, return it
            if name and name.startswith('http'):
                return name
            
            if not name:
                return ""
            
            self._ensure_configured()
            # Generate Cloudinary URL
            return cloudinary.CloudinaryImage(name).build_url()
        except Exception as e:
            return name or ""
    
    def delete(self, name):
        """Delete file from Cloudinary"""
        try:
            if name and not name.startswith('http'):
                self._ensure_configured()
                cloudinary.uploader.destroy(name, resource_type="image")
        except Exception as e:
            pass  # Silently fail if file doesn't exist
    
    def size(self, name):
        """Get file size"""
        try:
            if name and not name.startswith('http'):
                self._ensure_configured()
                resource = cloudinary.api.resource(name, resource_type="image")
                return resource.get('bytes', 0)
        except:
            pass
        return 0

