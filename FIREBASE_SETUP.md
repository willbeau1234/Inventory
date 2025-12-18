# Firebase Realtime Database Setup Guide

This guide will walk you through setting up Firebase Realtime Database for the DQ Inventory system.

## Prerequisites

- A Google account
- Firebase project created in [Firebase Console](https://console.firebase.google.com/)
- Python dependencies installed (`pip install -r requirements.txt`)

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select an existing project
3. Follow the setup wizard to create your project
4. Once created, you'll be taken to the project dashboard

## Step 2: Enable Realtime Database

1. In your Firebase project dashboard, click on "Realtime Database" in the left sidebar
2. Click "Create Database"
3. Choose a location for your database (select the one closest to your users)
4. Select security rules:
   - Start in **locked mode** for production
   - You can start in **test mode** for development (expires after 30 days)
5. Click "Enable"
6. Your database URL will be displayed at the top: `https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com`

## Step 3: Generate Service Account Credentials

1. In Firebase Console, click the gear icon (⚙️) next to "Project Overview"
2. Select "Project settings"
3. Go to the "Service accounts" tab
4. Click "Generate new private key"
5. Click "Generate key" in the confirmation dialog
6. A JSON file will be downloaded - **keep this file secure!**
7. Rename the downloaded file to `firebase-service-account.json`
8. Move it to your project root directory: `/Users/william/Desktop/DQ_Inventory/`

## Step 4: Configure Environment Variables

### For Local Development:

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Firebase configuration:
   ```
   FIREBASE_DATABASE_URL=https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com
   FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json
   ```

3. Replace `YOUR-PROJECT-ID` with your actual Firebase project ID

### For Vercel Deployment:

1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add the following environment variables:

   **FIREBASE_DATABASE_URL**
   - Value: `https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com`

   **FIREBASE_SERVICE_ACCOUNT_JSON**
   - Value: Paste the entire contents of your `firebase-service-account.json` file as a single line
   - This should be a JSON string like: `{"type":"service_account","project_id":"...","private_key":"...","client_email":"..."}`

4. Save and redeploy your application

## Step 5: Set Database Security Rules

1. In Firebase Console, go to Realtime Database → Rules
2. For production, use these security rules:

```json
{
  "rules": {
    ".read": false,
    ".write": false,
    "inventory_state": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "conversion_table": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "recipe_table": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "files": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

3. Click "Publish" to save the rules

> **Note**: These rules require authentication. Since we're using the Admin SDK (service account), it will have full access regardless of these rules.

## Step 6: Test the Connection

Run the test script to verify your Firebase connection:

```bash
python -c "from firebase_db import test_firebase_connection; print('Success!' if test_firebase_connection() else 'Failed!')"
```

If successful, you should see: `Success!`

## Database Structure

Your Firebase Realtime Database will have the following structure:

```
/
├── inventory_state/
│   ├── items/
│   │   ├── <item_name>/
│   │   │   ├── quantity: number
│   │   │   ├── unit: string
│   │   │   ├── last_updated: timestamp
│   │   │   └── ...
│   └── metadata/
│       ├── last_sync: timestamp
│       └── version: string
│
├── conversion_table/
│   ├── <item_number>/
│   │   ├── name: string
│   │   ├── unit: string
│   │   └── conversion_factor: number
│
├── recipe_table/
│   ├── <pos_item>/
│   │   ├── ingredients/
│   │   │   ├── <ingredient_name>: quantity
│   │   │   └── ...
│
└── files/
    ├── invoice/
    │   ├── <filename>/
    │   │   ├── uploaded_at: timestamp
    │   │   ├── items: array
    │   │   └── metadata: object
    │
    └── sales/
        ├── <filename>/
        │   ├── uploaded_at: timestamp
        │   ├── items: array
        │   └── metadata: object
```

## Using Firebase in Your Application

The `firebase_db.py` module provides helper functions for all database operations:

### Initialize Firebase (automatic on first use)
```python
from firebase_db import initialize_firebase

if initialize_firebase():
    print("Firebase initialized successfully")
```

### Save/Load Inventory State
```python
from firebase_db import save_inventory_state, load_inventory_state

# Save
inventory_data = {"items": {...}, "metadata": {...}}
save_inventory_state(inventory_data)

# Load
data = load_inventory_state()
```

### Update Individual Items
```python
from firebase_db import update_inventory_item

update_inventory_item("Vanilla Syrup", {
    "quantity": 5.5,
    "unit": "gallons",
    "last_updated": "2025-12-18T10:30:00Z"
})
```

### Save File Metadata
```python
from firebase_db import save_file_metadata

metadata = {
    "uploaded_at": "2025-12-18T10:30:00Z",
    "items": ["item1", "item2"],
    "total_items": 42
}
save_file_metadata("invoice", "invoice_2025-12-18.pdf", metadata)
```

### Check Configuration
```python
from firebase_db import is_firebase_configured, test_firebase_connection

if is_firebase_configured():
    if test_firebase_connection():
        print("Firebase is ready!")
```

## Troubleshooting

### Error: "FIREBASE_DATABASE_URL not set"
- Make sure you created the `.env` file from `.env.example`
- Verify the environment variable is set correctly

### Error: "Service account file not found"
- Check that `firebase-service-account.json` is in the project root
- Verify the file path in your `.env` file

### Error: "Permission denied"
- Check your Firebase security rules
- Verify your service account has the correct permissions
- Make sure you're using the Admin SDK (not the client SDK)

### Connection Test Fails
- Verify your database URL is correct
- Check that your service account JSON is valid
- Ensure you have internet connectivity
- Check Firebase Console for any issues with your database

## Migration from JSON Files

To migrate your existing local data to Firebase:

1. The system currently stores data in `inventory_state.json`
2. You can bulk upload this data using:

```python
import json
from firebase_db import save_inventory_state

# Load existing data
with open('inventory_state.json', 'r') as f:
    data = json.load(f)

# Upload to Firebase
save_inventory_state(data)
```

## Next Steps

After setting up Firebase, you'll need to:

1. Update `app.py` to use Firebase functions instead of local JSON files
2. Update `api/index.py` for Vercel deployment
3. Test all functionality (uploads, inventory updates, etc.)
4. Deploy to Vercel with environment variables configured

## Security Best Practices

- **NEVER** commit `firebase-service-account.json` to version control (already in `.gitignore`)
- **NEVER** commit `.env` to version control (already in `.gitignore`)
- Rotate your service account keys periodically
- Use environment variables for all sensitive configuration
- Monitor Firebase usage in the Firebase Console
- Set up billing alerts to avoid unexpected charges

## Support

For Firebase-specific issues:
- [Firebase Documentation](https://firebase.google.com/docs/database)
- [Firebase Admin SDK for Python](https://firebase.google.com/docs/admin/setup)
- [Firebase Support](https://firebase.google.com/support)
