"""
Firebase Storage Helper Module
Handles file uploads and downloads from Firebase Storage
"""

from firebase_admin import storage
import os
from datetime import datetime


def upload_file(file_obj, filename):
    """
    Upload a file to Firebase Storage

    Args:
        file_obj: File object from Flask request
        filename: Name to save the file as

    Returns:
        str: Storage path of uploaded file
    """
    try:
        bucket = storage.bucket()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        storage_path = f'uploads/{timestamp}_{filename}'

        blob = bucket.blob(storage_path)
        blob.upload_from_file(file_obj, content_type=file_obj.content_type)

        print(f"File uploaded to Firebase Storage: {storage_path}")
        return storage_path
    except Exception as e:
        print(f"Error uploading file to storage: {e}")
        return None


def download_file_to_temp(storage_path):
    """
    Download a file from Firebase Storage to local temp directory

    Args:
        storage_path: Path in Firebase Storage

    Returns:
        str: Local temp file path
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(storage_path)

        # Create temp file path
        temp_dir = '/tmp'
        os.makedirs(temp_dir, exist_ok=True)
        local_path = os.path.join(temp_dir, os.path.basename(storage_path))

        # Download file
        blob.download_to_filename(local_path)
        print(f"File downloaded from storage to: {local_path}")
        return local_path
    except Exception as e:
        print(f"Error downloading file from storage: {e}")
        return None


def get_file_url(storage_path):
    """
    Get a signed URL for a file in Firebase Storage

    Args:
        storage_path: Path in Firebase Storage

    Returns:
        str: Public URL for the file
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(storage_path)

        # Generate a signed URL valid for 1 hour
        url = blob.generate_signed_url(
            version='v4',
            expiration=3600,  # 1 hour
            method='GET'
        )
        return url
    except Exception as e:
        print(f"Error generating file URL: {e}")
        return None


def list_uploaded_files():
    """
    List all files in the uploads folder

    Returns:
        list: List of file paths in storage
    """
    try:
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix='uploads/')
        return [blob.name for blob in blobs]
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def delete_file(storage_path):
    """
    Delete a file from Firebase Storage

    Args:
        storage_path: Path in Firebase Storage

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(storage_path)
        blob.delete()
        print(f"File deleted from storage: {storage_path}")
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False
