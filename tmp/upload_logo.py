import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name='dd8pvzw7m',
    api_key='912472937759221',
    api_secret='T1QYlLmFXQk_ZL5BFo8JTtRHYhQ'
)

result = cloudinary.uploader.upload(
    'static/images/logo.png',
    public_id='adietalk_email_logo',
    overwrite=True,
    invalidate=True
)
print(f"SUCCESS - Logo URL: {result['secure_url']}")
