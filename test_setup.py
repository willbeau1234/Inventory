#!/usr/bin/env python3
"""
Test script to verify DQ Inventory Manager setup
"""

import os
import sys

print("=" * 60)
print("DQ Inventory Manager - Setup Test")
print("=" * 60)
print()

# Test 1: Check Python version
print("✓ Python version:", sys.version.split()[0])

# Test 2: Check required files
files_to_check = [
    'app.py',
    'templates/index.html',
    'inventory/DQ inventory - Conversion.csv',
    'inventory/DQ inventory - Recipe.csv',
    'requirements.txt'
]

print("\nChecking required files:")
all_exist = True
for file in files_to_check:
    exists = os.path.exists(file)
    all_exist = all_exist and exists
    status = "✓" if exists else "✗"
    print(f"  {status} {file}")

if not all_exist:
    print("\n⚠ Some files are missing!")
    sys.exit(1)

# Test 3: Try importing Flask
print("\nChecking dependencies:")
try:
    import flask
    print(f"  ✓ Flask installed (version {flask.__version__})")
except ImportError:
    print("  ✗ Flask not installed")
    print("\n  Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import pdfplumber
    print(f"  ✓ pdfplumber installed")
except ImportError:
    print("  ✗ pdfplumber not installed")
    print("\n  Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 4: Check conversion and recipe files can be read
print("\nChecking data files:")
try:
    import csv

    with open('inventory/DQ inventory - Conversion.csv', 'r') as f:
        reader = csv.DictReader(f)
        conversion_count = len(list(reader))
    print(f"  ✓ Conversion file: {conversion_count} items")

    with open('inventory/DQ inventory - Recipe.csv', 'r') as f:
        reader = csv.DictReader(f)
        recipe_count = len(list(reader))
    print(f"  ✓ Recipe file: {recipe_count} recipe entries")

except Exception as e:
    print(f"  ✗ Error reading data files: {e}")
    sys.exit(1)

# Test 5: Try importing the app
print("\nTesting app.py:")
try:
    # Add current directory to path
    sys.path.insert(0, os.getcwd())

    # Try to import app (this will load conversion and recipe data)
    import app as inventory_app

    print(f"  ✓ app.py loads successfully")
    print(f"  ✓ Conversions loaded: {len(inventory_app.conversions)} items")
    print(f"  ✓ Recipes loaded: {len(inventory_app.recipes)} POS items")

except Exception as e:
    print(f"  ✗ Error loading app.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print("\nYou're ready to run the app:")
print("  python app.py")
print("\nThen open: http://localhost:5000")
print()
