# DQ Inventory Manager - File Manifest

This folder contains everything needed to run the DQ Inventory Management System.

## Essential Files (Required)

### Application Files
- **app.py** - Main Flask application (Python backend)
- **requirements.txt** - Python package dependencies
- **templates/index.html** - Web interface (HTML/CSS/JavaScript)

### Data Files
- **inventory/DQ inventory - Conversion.csv** - Conversion table (cases to usable units)
- **inventory/DQ inventory - Recipe.csv** - Recipe definitions (POS items to ingredients)

## Sample/Example Files

- **inventory/SAMPLE_starting_inventory.csv** - Example starting inventory CSV format

## Documentation

- **README.md** - Complete documentation with examples and troubleshooting
- **SETUP.md** - Quick setup guide
- **FILE_MANIFEST.md** - This file

## Helper Files

- **start.sh** - One-click startup script (Mac/Linux)
- **.gitignore** - Git ignore rules (if using version control)

## Created During Use

These files/folders are created automatically when you run the app:

- **inventory_state.json** - Current inventory state (created on first run)
- **uploads/** - Uploaded PDF and CSV files
- **.venv/** - Python virtual environment (created by start.sh)

## File Sizes

```
app.py                              ~22 KB
templates/index.html                ~18 KB
inventory/DQ inventory - Conversion.csv  ~5 KB (97 items)
inventory/DQ inventory - Recipe.csv      ~12 KB (367 recipes)
requirements.txt                    <1 KB
README.md                           ~10 KB
```

## Minimum Requirements to Run

1. Python 3.7 or higher
2. Internet connection (first time only, to install dependencies)
3. These files:
   - app.py
   - templates/index.html
   - requirements.txt
   - inventory/DQ inventory - Conversion.csv
   - inventory/DQ inventory - Recipe.csv

## How Files Work Together

```
┌─────────────┐
│   app.py    │  ← Main application
└──────┬──────┘
       │
       ├─→ Loads: inventory/DQ inventory - Conversion.csv
       ├─→ Loads: inventory/DQ inventory - Recipe.csv
       ├─→ Reads: inventory_state.json (if exists)
       ├─→ Serves: templates/index.html
       └─→ Processes: uploads/*.pdf and uploads/*.csv
```

## Backup Recommendations

Always backup these files:
- inventory_state.json (your current inventory)
- inventory/DQ inventory - Conversion.csv (your conversion table)
- inventory/DQ inventory - Recipe.csv (your recipes)
- uploads/*.pdf and uploads/*.csv (your source data)

## Version Information

- Created: December 2025
- Python Version Required: 3.7+
- Flask Version: 3.1.0 (from requirements.txt)
