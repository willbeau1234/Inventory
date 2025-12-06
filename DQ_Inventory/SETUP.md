# Quick Setup Guide

## Getting Started (First Time)

### Option 1: Using the Startup Script (Easiest)

1. Open Terminal
2. Navigate to this folder:
   ```bash
   cd ~/Desktop/DQ_Inventory
   ```
3. Run the startup script:
   ```bash
   ./start.sh
   ```
4. The script will:
   - Create a virtual environment (if needed)
   - Install all dependencies
   - Start the server
   - Open at http://localhost:5000

### Option 2: Manual Setup

1. Open Terminal and navigate to this folder:
   ```bash
   cd ~/Desktop/DQ_Inventory
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser to: `http://localhost:5000`

## Folder Structure

```
DQ_Inventory/
├── app.py                              # Main Flask application
├── templates/
│   └── index.html                     # Web interface
├── inventory/
│   ├── DQ inventory - Conversion.csv  # Item conversion table
│   ├── DQ inventory - Recipe.csv      # Recipe definitions
│   └── SAMPLE_starting_inventory.csv  # Sample starting inventory
├── uploads/                           # Uploaded files (created automatically)
├── inventory_state.json               # Current inventory state (created on first use)
├── requirements.txt                   # Python dependencies
├── README.md                          # Full documentation
├── SETUP.md                           # This file
├── start.sh                           # Startup script (Mac/Linux)
└── .gitignore                         # Git ignore rules
```

## Using the Application

### Three Ways to Update Inventory

1. **Performance Food Invoices (Tab 1)**
   - Upload PDF invoices
   - Automatically converts cases to usable units
   - Adds to inventory

2. **PAR Sales Data (Tab 2)**
   - Upload CSV with sales data
   - Automatically deducts inventory based on recipes
   - Tracks what was sold

3. **Starting Inventory (Tab 3)**
   - Upload CSV with current inventory counts
   - Perfect for initial setup or monthly resets
   - See `inventory/SAMPLE_starting_inventory.csv` for format

### Manual Updates

- Click any quantity field in the inventory table
- Enter new value
- Click "Update"

## Stopping the Application

Press `Ctrl+C` in the Terminal window where the app is running.

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, the app will automatically select another port. Check the Terminal output for the actual port number.

### Dependencies Not Installing
Make sure you're using Python 3.7 or higher:
```bash
python3 --version
```

### Files Not Loading
Ensure the CSV files in the `inventory/` folder have the correct format:
- `DQ inventory - Conversion.csv` - Item conversions
- `DQ inventory - Recipe.csv` - Recipe definitions

## Next Steps

1. Review the conversion table (`inventory/DQ inventory - Conversion.csv`)
2. Review the recipe table (`inventory/DQ inventory - Recipe.csv`)
3. Upload your starting inventory (Tab 3)
4. Start processing invoices and sales!

For detailed documentation, see `README.md`.
