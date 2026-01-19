import cloudinary
from cloudinary.uploader import upload
from app.core.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUD_NAME,
    api_key=settings.API_KEY,
    api_secret=settings.API_SECRET,
    # secure=True
)

def upload_to_cloudinary(file):
    """Upload file to Cloudinary and return secure URL"""
    result = upload(
        file,
        folder="social_media_posts",
        resource_type="auto"
    )
    return result["secure_url"]
