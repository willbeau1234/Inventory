"""
Firebase Realtime Database Helper Module
Handles all Firebase database operations for the DQ Inventory system.
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, db
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Global Firebase app instance
_firebase_app = None
_database_ref = None


def initialize_firebase():
    """
    Initialize Firebase Admin SDK.
    Supports both local development (service account file) and Vercel deployment (environment variable).

    Returns:
        bool: True if initialization successful, False otherwise
    """
    global _firebase_app, _database_ref

    # Check if already initialized
    if _firebase_app is not None:
        logger.info("Firebase already initialized")
        return True

    try:
        # Get database URL from environment
        database_url = os.environ.get('FIREBASE_DATABASE_URL')
        if not database_url:
            logger.error("FIREBASE_DATABASE_URL not set in environment variables")
            return False

        # Try to get credentials from environment variable first (for Vercel)
        service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')

        if service_account_json:
            # Parse JSON from environment variable
            logger.info("Using Firebase credentials from environment variable")
            cred_dict = json.loads(service_account_json)
            cred = credentials.Certificate(cred_dict)
        else:
            # Fall back to service account file (for local development)
            service_account_path = os.environ.get(
                'FIREBASE_SERVICE_ACCOUNT_PATH',
                'firebase-service-account.json'
            )

            if not os.path.exists(service_account_path):
                logger.error(f"Service account file not found: {service_account_path}")
                return False

            logger.info(f"Using Firebase credentials from file: {service_account_path}")
            cred = credentials.Certificate(service_account_path)

        # Initialize Firebase app
        _firebase_app = firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })

        _database_ref = db.reference()
        logger.info("Firebase initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        return False


def get_database_ref(path: str = '/'):
    """
    Get a reference to a specific path in the database.

    Args:
        path: Database path (default: root)

    Returns:
        Database reference or None if not initialized
    """
    if _database_ref is None:
        if not initialize_firebase():
            return None

    return db.reference(path)


# ============================================================================
# INVENTORY STATE OPERATIONS
# ============================================================================

def save_inventory_state(inventory_data: Dict[str, Any]) -> bool:
    """
    Save the complete inventory state to Firebase.

    Args:
        inventory_data: Dictionary containing inventory state

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ref = get_database_ref('inventory_state')
        if ref is None:
            return False

        ref.set(inventory_data)
        logger.info("Inventory state saved to Firebase")
        return True

    except Exception as e:
        logger.error(f"Failed to save inventory state: {str(e)}")
        return False


def load_inventory_state() -> Optional[Dict[str, Any]]:
    """
    Load the complete inventory state from Firebase.

    Returns:
        Dictionary containing inventory state, or None if not found/error
    """
    try:
        ref = get_database_ref('inventory_state')
        if ref is None:
            return None

        data = ref.get()
        logger.info("Inventory state loaded from Firebase")
        return data

    except Exception as e:
        logger.error(f"Failed to load inventory state: {str(e)}")
        return None


def update_inventory_item(item_name: str, updates: Dict[str, Any]) -> bool:
    """
    Update a specific inventory item.

    Args:
        item_name: Name of the inventory item
        updates: Dictionary of fields to update

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ref = get_database_ref(f'inventory_state/items/{item_name}')
        if ref is None:
            return False

        ref.update(updates)
        logger.info(f"Updated inventory item: {item_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to update inventory item: {str(e)}")
        return False


# ============================================================================
# FILE METADATA OPERATIONS
# ============================================================================

def save_file_metadata(file_type: str, filename: str, metadata: Dict[str, Any]) -> bool:
    """
    Save metadata about an uploaded file (PDF invoice or CSV sales data).

    Args:
        file_type: Type of file ('invoice' or 'sales')
        filename: Name of the uploaded file
        metadata: Dictionary containing file metadata (upload time, items, etc.)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ref = get_database_ref(f'files/{file_type}/{filename}')
        if ref is None:
            return False

        ref.set(metadata)
        logger.info(f"Saved metadata for {file_type}: {filename}")
        return True

    except Exception as e:
        logger.error(f"Failed to save file metadata: {str(e)}")
        return False


def get_file_history(file_type: str, limit: int = 50) -> Optional[Dict[str, Any]]:
    """
    Get upload history for a specific file type.

    Args:
        file_type: Type of file ('invoice' or 'sales')
        limit: Maximum number of records to return

    Returns:
        Dictionary of file metadata, or None if error
    """
    try:
        ref = get_database_ref(f'files/{file_type}')
        if ref is None:
            return None

        data = ref.order_by_key().limit_to_last(limit).get()
        logger.info(f"Retrieved file history for {file_type}")
        return data

    except Exception as e:
        logger.error(f"Failed to get file history: {str(e)}")
        return None


# ============================================================================
# CONVERSION TABLE OPERATIONS
# ============================================================================

def save_conversion_table(conversion_data: Dict[str, Any]) -> bool:
    """
    Save the conversion table to Firebase.

    Args:
        conversion_data: Dictionary mapping item numbers to conversion data

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ref = get_database_ref('conversion_table')
        if ref is None:
            return False

        ref.set(conversion_data)
        logger.info("Conversion table saved to Firebase")
        return True

    except Exception as e:
        logger.error(f"Failed to save conversion table: {str(e)}")
        return False


def load_conversion_table() -> Optional[Dict[str, Any]]:
    """
    Load the conversion table from Firebase.

    Returns:
        Dictionary containing conversion data, or None if not found/error
    """
    try:
        ref = get_database_ref('conversion_table')
        if ref is None:
            return None

        data = ref.get()
        logger.info("Conversion table loaded from Firebase")
        return data

    except Exception as e:
        logger.error(f"Failed to load conversion table: {str(e)}")
        return None


# ============================================================================
# RECIPE TABLE OPERATIONS
# ============================================================================

def save_recipe_table(recipe_data: Dict[str, Any]) -> bool:
    """
    Save the recipe table to Firebase.

    Args:
        recipe_data: Dictionary mapping POS items to recipes

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ref = get_database_ref('recipe_table')
        if ref is None:
            return False

        ref.set(recipe_data)
        logger.info("Recipe table saved to Firebase")
        return True

    except Exception as e:
        logger.error(f"Failed to save recipe table: {str(e)}")
        return False


def load_recipe_table() -> Optional[Dict[str, Any]]:
    """
    Load the recipe table from Firebase.

    Returns:
        Dictionary containing recipe data, or None if not found/error
    """
    try:
        ref = get_database_ref('recipe_table')
        if ref is None:
            return None

        data = ref.get()
        logger.info("Recipe table loaded from Firebase")
        return data

    except Exception as e:
        logger.error(f"Failed to load recipe table: {str(e)}")
        return None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_firebase_configured() -> bool:
    """
    Check if Firebase is properly configured.

    Returns:
        bool: True if Firebase environment variables are set
    """
    database_url = os.environ.get('FIREBASE_DATABASE_URL')
    has_credentials = (
        os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON') or
        os.path.exists(os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json'))
    )

    return bool(database_url and has_credentials)


def test_firebase_connection() -> bool:
    """
    Test the Firebase connection by attempting to read from the database.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        if not initialize_firebase():
            return False

        # Try to read from root
        ref = get_database_ref('/')
        ref.get()

        logger.info("Firebase connection test successful")
        return True

    except Exception as e:
        logger.error(f"Firebase connection test failed: {str(e)}")
        return False
