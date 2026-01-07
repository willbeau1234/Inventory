# Sample Test Files for DQ Inventory

This folder contains sample files you can use to test the DQ Inventory application.

## Files Included

### 📄 Invoice PDFs

**invoice_2026_001.pdf**
- Performance Foodservice format invoice
- Contains 5 items: Ice cream mix, cups, sugar, strawberry topping, sprinkles
- Total: $405.95
- Date: 01/06/2026

**invoice_2026_002.pdf**
- Performance Foodservice format invoice
- Contains 4 items: Chocolate syrup, ice cream mix, strawberry topping, flour
- Total: $376.70
- Date: 01/03/2026

### 📊 CSV Files

**sample_sales.csv**
- PAR POS sales data format
- Contains 7 items sold: Various sizes of Blizzards, cones, and bars
- Total sales: $957.04
- Includes quantity sold, prices, and percentages

**sample_starting_inventory.csv**
- Starting/current inventory format
- Contains 6 products with current stock levels
- Includes product numbers, quantities, pack sizes, and brands
- Useful for initializing inventory levels

## How to Use

### 1. Testing Invoice Upload

1. Go to your app at https://real-dq.web.app
2. Click on "Performance Food Invoices" tab
3. Drag and drop `invoice_2026_001.pdf` or `invoice_2026_002.pdf`
4. Click "Upload & Process"
5. The app will extract items and add them to inventory

### 2. Testing Sales Processing

1. Go to "PAR Sales Data" tab
2. Upload `sample_sales.csv`
3. Click "Upload & Process"
4. The app will deduct ingredients from inventory based on recipes

### 3. Testing Starting Inventory

1. Go to "Starting Inventory" tab
2. Upload `sample_starting_inventory.csv`
3. Click "Upload & Process"
4. The app will set initial inventory levels

## Regenerating Sample Files

If you need to create new sample files or modify existing ones:

```bash
cd /Users/william/Desktop/DQ_Inventory
python3 samples/generate_samples.py
```

This will regenerate all sample files with the current date.

## Sample Data Details

### Items in Invoices

The sample invoices contain these item numbers (must exist in your conversion table):
- GF662 - Ice Cream Mix
- AJW24 - Paper Cups
- RR730 - Sugar
- SX449 - Strawberry Topping
- PL881 - Rainbow Sprinkles
- QT992 - Chocolate Syrup
- MN334 - All Purpose Flour

### POS Items in Sales

The sample sales CSV contains these POS items (must exist in your recipe table):
- SM BLIZZARD
- MD BLIZZARD
- LG BLIZZARD
- SM CONE
- MD CONE
- DILLY BAR
- BUSTER BAR

## Expected Behavior

**After uploading invoice_2026_001.pdf:**
- Inventory should increase:
  - Ice Cream Mix: +112 oz (2 cases × 56 oz/case)
  - Paper Cups: +1800 cups (3 cases × 600 cups/case)
  - Sugar: +25 lbs
  - Strawberry Topping: +16 gallons (4 cases × 4 gal/case)
  - Rainbow Sprinkles: +192 oz (2 cases × 12 × 16 oz)

**After uploading sample_sales.csv:**
- Inventory should decrease based on recipes
- For example, if SM BLIZZARD uses 5 oz ice cream + 1 cup:
  - Ice Cream: -225 oz (45 sold × 5 oz)
  - Cups: -45 cups (45 sold × 1 cup)

**After uploading sample_starting_inventory.csv:**
- Inventory levels will be set to specified amounts
- Small quantities (< 100) are treated as cases and converted
- Large quantities (≥ 100) are treated as already in usable units

## Troubleshooting

**"Could not find conversion for..."**
- The item number in the invoice doesn't exist in your conversion table
- Add the missing item to `inventory/DQ inventory - Conversion.csv`

**"No recipe found for..."**
- The POS item in the sales CSV doesn't exist in your recipe table
- Add the missing recipe to `inventory/DQ inventory - Recipe.csv`

**"Item not in inventory"**
- Process invoices before processing sales
- Or upload a starting inventory first
