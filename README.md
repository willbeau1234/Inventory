# DQ Inventory Management System

A comprehensive web application that manages DQ inventory by processing Performance Foodservice invoices and PAR POS sales data. The system automatically converts order quantities to usable units and deducts inventory based on recipes.

## Features

- **Performance Food Invoice Processing**
  - Upload PDF invoices from Performance Foodservice
  - Automatic conversion from cases to usable units (oz, cups, etc.)
  - Adds items to current inventory using conversion table

- **PAR Sales Data Integration**
  - Upload PAR POS sales CSV files
  - Automatic inventory deduction based on recipes
  - Tracks which items were sold and calculates ingredient usage

- **Manual Inventory Management**
  - Edit inventory quantities directly from the web interface
  - Real-time updates with visual feedback
  - Low stock warnings (items < 10 units)
  - Negative stock highlighting

- **Persistent State**
  - Inventory state saved to JSON file
  - Tracks history of invoices and sales processed
  - Maintains data between server restarts

- **Clean Modern Interface**
  - Tab-based interface for different file types
  - Drag-and-drop file upload
  - Real-time statistics dashboard
  - Color-coded inventory alerts

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

The main dependencies are:
- Flask (web framework)
- pdfplumber (PDF parsing)
- csv, json (data processing)

### 2. Prepare Your Data Files

Make sure you have these CSV files in the `inventory/` folder:

- **DQ inventory - Conversion.csv**: Maps item numbers to conversion factors
  - Columns: `item_number`, `description`, `order_unit`, `items_per_case`, `usable_unit`, `notes`
  - Example: AJW24, CUP PAPER 32OZ 600, 15/40CNTDQ, 600, cup

- **DQ inventory - Recipe.csv**: Maps POS items to inventory ingredients
  - Columns: `pos_item_name`, `inventory_item_number`, `inventory_description`, `quantity_used`, `unit`
  - Example: SM BLIZZARD, GF662, ICE CREAM MIX SFTSRV VAN, 5, oz

### 3. Run the Application

```bash
python app.py
```

The application will:
- Load conversion and recipe data
- Load any existing inventory state
- Start the web server (usually on port 5000)

### 4. Access the Web Interface

Open your browser and go to:
```
http://localhost:5000
```

## Deploying to Vercel

This application can be deployed to Vercel for cloud hosting. Follow these steps:

### Prerequisites
- A [Vercel account](https://vercel.com/signup)
- [Vercel CLI](https://vercel.com/cli) installed (optional, but recommended)

### Deployment Steps

#### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy the application**:
   ```bash
   vercel
   ```

   Follow the prompts:
   - Set up and deploy: Yes
   - Which scope: Select your account
   - Link to existing project: No
   - Project name: (accept default or customize)
   - Directory: ./
   - Override settings: No

4. **Deploy to production**:
   ```bash
   vercel --prod
   ```

#### Option 2: Deploy via Vercel Dashboard

1. **Push your code to GitHub**:
   - Create a new repository on GitHub
   - Push your code to the repository

2. **Import to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Vercel will auto-detect the Python app
   - Click "Deploy"

### Important Notes for Vercel Deployment

**File Storage Limitations:**
- Vercel serverless functions are stateless and ephemeral
- The `uploads/` folder and `inventory_state.json` file will NOT persist between deployments
- For production use, you should integrate with:
  - **Vercel Blob** for file uploads
  - **Vercel KV** or a database (PostgreSQL, MongoDB) for inventory state
  - **Vercel Postgres** for relational data storage

**Current Behavior on Vercel:**
- Each deployment starts with a fresh state
- Uploaded files and inventory data will be lost when the function instance shuts down
- The app will work for testing, but data won't persist long-term

**Recommended for Production:**
- Add a database integration (see Vercel's documentation on Vercel Postgres or Vercel KV)
- Use Vercel Blob Storage for uploaded PDF and CSV files
- Modify the app to use these persistent storage solutions instead of local file storage

### Environment Variables (if needed)

If you need to set environment variables:

```bash
vercel env add FLASK_ENV
```

Then enter `production` when prompted.

## How to Use

### Processing Performance Food Invoices

1. Click the **"Performance Food Invoices"** tab
2. Drag and drop PDF invoice files or click to browse
3. Click **"Upload & Process"**
4. The system will:
   - Extract items from the PDF
   - Match them with the conversion table
   - Convert cases to usable units (oz, cups, etc.)
   - Add the quantities to your inventory

### Processing PAR Sales Data

1. Click the **"PAR Sales Data"** tab
2. Drag and drop your sales CSV file (expected columns: `item_name`, `quantity_sold`)
3. Click **"Upload & Process"**
4. The system will:
   - Look up recipes for each POS item
   - Calculate ingredient usage
   - Deduct the appropriate quantities from inventory

### Loading Starting/Current Inventory

1. Click the **"Starting Inventory"** tab
2. Drag and drop your inventory CSV file (expected columns: `Product Number`, `Current Inventory`)
3. Click **"Upload & Process"**
4. The system will:
   - Read each item and its quantity
   - If quantity is small (< 100), assumes it's in cases and converts to usable units
   - If quantity is large (>= 100), assumes it's already in usable units
   - Sets the inventory level for each item

**Use this feature when:**
- Setting up the system for the first time
- After a physical inventory count
- Resetting inventory to known good values

### Manual Inventory Updates

1. View your current inventory in the table
2. Enter a new quantity in the input field next to any item
3. Click **"Update"**
4. The change is saved immediately

### Understanding the Inventory Display

- **Item Number**: The product code (e.g., GF662)
- **Description**: Product name
- **Quantity**: Current inventory level
  - Red text = low stock (< 10 units)
  - Red background = negative stock (out of stock)
- **Unit**: The measurement unit (oz, cup, lb, etc.)

### Statistics Dashboard

The dashboard shows:
- **Total Items**: Number of unique items in inventory
- **Invoices Processed**: Count of Performance Food invoices added
- **Sales Processed**: Count of PAR sales files processed

## File Structure

```
Webscrapping/
├── app.py                              # Flask backend server
├── templates/
│   └── index.html                     # Web interface
├── inventory/
│   ├── DQ inventory - Conversion.csv  # Conversion table
│   └── DQ inventory - Recipe.csv      # Recipe definitions
├── uploads/                           # Uploaded files (created automatically)
├── inventory_state.json               # Persistent inventory state
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Data Flow

### Adding Inventory (Performance Food Invoice)

1. PDF uploaded → `extract_invoice_data()` extracts items
2. Items matched with conversion table
3. Cases converted to usable units (e.g., 2 cases × 600 cups/case = 1200 cups)
4. Quantity added to `current_inventory`
5. State saved to `inventory_state.json`

### Deducting Inventory (PAR Sales)

1. CSV uploaded → `process_sales_data()` reads sales
2. Each POS item looked up in recipe table
3. For each ingredient in recipe:
   - Calculate total usage (quantity_sold × quantity_per_item)
   - Deduct from `current_inventory`
4. State saved to `inventory_state.json`

### Manual Update

1. User enters new quantity
2. POST to `/update_inventory` endpoint
3. Inventory updated directly
4. State saved to `inventory_state.json`

## API Endpoints

- `GET /` - Main web interface
- `POST /upload` - Upload and process files (PDFs or CSVs)
- `GET /inventory` - Get current inventory state
- `POST /update_inventory` - Manually update item quantity
- `POST /clear` - Clear all inventory data and history

## CSV File Formats

### PAR Sales CSV (pos_sales_sept_2025.csv)
```csv
item_name,quantity_sold,average_price,total,percent
SM BLIZZARD,60,4.99,299.40,22.5
MD BLIZZARD,40,5.99,239.60,18.0
```

### Starting Inventory CSV (SAMPLE_starting_inventory.csv)
```csv
Product Number,Current Inventory,Pack Size,Brand
AJW24,2,15/40CNTDQ,Generic
GF662,8,1/5 GAL,DQ
RR730,1,1/25 LB,Generic
```

**Note:** Only `Product Number` and `Current Inventory` columns are required. The system will:
- Look up the item in the conversion table
- If `Current Inventory` < 100, treat as cases and convert to usable units
- If `Current Inventory` >= 100, treat as already in usable units
- Example: `AJW24,2` → 2 cases × 600 cups/case = 1,200 cups

### Conversion Table CSV
```csv
item_number,description,order_unit,items_per_case,usable_unit,notes
GF662,ICE CREAM MIX SFTSRV VAN,1/5 GAL,112,oz,
AJW24,CUP PAPER 32OZ 600,15/40CNTDQ,600,cup,
```

### Recipe Table CSV
```csv
pos_item_name,inventory_item_number,inventory_description,quantity_used,unit
SM BLIZZARD,GF662,ICE CREAM MIX SFTSRV VAN,5,oz
SM BLIZZARD,AJW24,CUP PAPER 32OZ 600,1,cup
```

## Troubleshooting

### Invoice Not Processing
- Ensure the PDF is text-based (not scanned)
- Check that item descriptions match entries in the conversion table
- Look at the console output for "Warning: Could not find conversion for..." messages

### Sales Not Deducting
- Verify POS item names in the sales CSV match recipe table exactly
- Check that inventory items exist before processing sales
- Review console output for "Warning: No recipe found for..." messages

### Items Not Converting Correctly
- Review the conversion table for the item
- Check that `items_per_case` is a valid number
- Some items have notes like "depends on size" - these need manual adjustment

### Negative Inventory
- This indicates you've sold more than you have in stock
- Either:
  1. Add invoices for missing inventory
  2. Manually update the quantity to the correct amount

## Technologies Used

- **Backend**: Flask (Python web framework)
- **PDF Processing**: pdfplumber (PDF text extraction)
- **Data Storage**: JSON (persistent state), CSV (conversion/recipe tables)
- **Frontend**: HTML, CSS, JavaScript (vanilla)

## Tips for Best Results

1. **Process invoices before sales**: Add inventory first, then deduct sales
2. **Keep conversion table updated**: Add new items as you encounter them
3. **Review low stock warnings**: Red quantities indicate items that may need ordering
4. **Use manual updates for corrections**: If counts are off after physical inventory
5. **Clear data to start fresh**: Use "Clear All Data" to reset and begin a new period

## Example Workflow

### First Time Setup
1. **Initial Setup**: Upload your starting inventory CSV (from physical count or last known inventory)
2. **Configure**: Verify conversion table and recipe table are up to date
3. **Test**: Upload a sample invoice and sales file to ensure conversions work correctly

### Weekly Operations
1. **Week Start**: Upload Performance Food invoice PDFs from last week's deliveries
2. **Mid-Week**: Upload PAR sales CSV from the POS system
3. **Review**: Check inventory levels, note any low stock items (shown in red)
4. **Physical Count** (monthly): Perform manual inventory counts and either:
   - Use manual updates for small adjustments
   - Upload a fresh starting inventory CSV for major resets
5. **Order**: Use the current inventory to determine what to order
6. **Week End**: Upload new invoices and repeat

### Month End / Period Reset
1. **Physical Count**: Conduct full physical inventory
2. **Export**: Export your counts to a CSV with columns: `Product Number`, `Current Inventory`
3. **Reset**: Upload the CSV via the "Starting Inventory" tab
4. **Verify**: Review the inventory table to ensure all quantities are correct

## Support

For issues or questions about:
- Missing conversions in the conversion table
- Incorrect recipe definitions
- Data format questions

Check the console output when running `python app.py` for detailed logging and warnings.
