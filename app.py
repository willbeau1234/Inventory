from flask import Flask, render_template, request, jsonify
import os
import pdfplumber
import re
import csv
import json
from datetime import datetime
from collections import defaultdict
import logging
import socket
import firebase_db

# suppress noisy pdfminer/pdfplumber warnings about invalid color tokens
logging.getLogger('pdfminer').setLevel(logging.ERROR)
logging.getLogger('pdfplumber').setLevel(logging.ERROR)

app = Flask(__name__)

# Use /tmp for uploads on Vercel (serverless environment)
# Local development will still use 'uploads' folder
if os.environ.get('VERCEL'):
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    app.config['INVENTORY_STATE_FILE'] = '/tmp/inventory_state.json'
else:
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['INVENTORY_STATE_FILE'] = 'inventory_state.json'

app.config['INVENTORY_FOLDER'] = 'inventory'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Data structures
conversions = {}  # item_number -> conversion info
recipes = defaultdict(list)  # pos_item_name -> list of ingredients
current_inventory = {}  # item_number -> {quantity, unit, description}
invoice_history = []  # list of processed invoices
sales_history = []  # list of processed sales

def load_conversions():
    """Load conversion table from CSV"""
    global conversions
    conversion_file = os.path.join(app.config['INVENTORY_FOLDER'], 'DQ inventory - Conversion.csv')
    if not os.path.exists(conversion_file):
        print(f"Warning: Conversion file not found at {conversion_file}")
        return

    with open(conversion_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_number = row['item_number'].strip()
            if item_number:
                conversions[item_number] = {
                    'description': row['description'].strip(),
                    'order_unit': row['order_unit'].strip(),
                    'items_per_case': row['items_per_case'].strip(),
                    'usable_unit': row['usable_unit'].strip(),
                    'notes': row.get('notes', '').strip()
                }
    print(f"Loaded {len(conversions)} conversion entries")

def load_recipes():
    """Load recipe table from CSV"""
    global recipes
    recipe_file = os.path.join(app.config['INVENTORY_FOLDER'], 'DQ inventory - Recipe.csv')
    if not os.path.exists(recipe_file):
        print(f"Warning: Recipe file not found at {recipe_file}")
        return

    with open(recipe_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pos_item = row['pos_item_name'].strip()
            item_number = row['inventory_item_number'].strip()
            if pos_item and item_number:
                recipes[pos_item].append({
                    'item_number': item_number,
                    'description': row['inventory_description'].strip(),
                    'quantity_used': float(row['quantity_used']) if row['quantity_used'] else 0,
                    'unit': row['unit'].strip()
                })
    print(f"Loaded recipes for {len(recipes)} POS items")

def save_inventory_state():
    """Save current inventory state to Firebase"""
    state = {
        'inventory': current_inventory,
        'invoice_history': invoice_history,
        'sales_history': sales_history,
        'last_updated': datetime.now().isoformat()
    }

    # Try to save to Firebase first
    if firebase_db.is_firebase_configured():
        success = firebase_db.save_inventory_state(state)
        if success:
            print("Inventory state saved to Firebase")
            return
        else:
            print("Failed to save to Firebase, falling back to local file")

    # Fallback to local file if Firebase not configured or fails
    with open(app.config['INVENTORY_STATE_FILE'], 'w') as f:
        json.dump(state, f, indent=2)
    print("Inventory state saved to local file")

def load_inventory_state():
    """Load inventory state from Firebase (with local file fallback)"""
    global current_inventory, invoice_history, sales_history

    # Try to load from Firebase first
    if firebase_db.is_firebase_configured():
        state = firebase_db.load_inventory_state()
        if state:
            current_inventory = state.get('inventory', {})
            invoice_history = state.get('invoice_history', [])
            sales_history = state.get('sales_history', [])
            print(f"Loaded inventory state from Firebase with {len(current_inventory)} items")
            return
        else:
            print("No data in Firebase, checking local file...")

    # Fallback to local file
    if os.path.exists(app.config['INVENTORY_STATE_FILE']):
        with open(app.config['INVENTORY_STATE_FILE'], 'r') as f:
            state = json.load(f)
            current_inventory = state.get('inventory', {})
            invoice_history = state.get('invoice_history', [])
            sales_history = state.get('sales_history', [])
        print(f"Loaded inventory state from local file with {len(current_inventory)} items")
    else:
        print("No existing inventory state found, starting fresh")

def extract_invoice_data(pdf_path):
    """Extract data from PDF invoice"""
    data = {
        'items': [],
        'invoice_number': None,
        'date': None,
        'supplier': None,
        'total': None
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ''
            for page in pdf.pages:
                page_text = page.extract_text() or ''
                full_text += page_text + '\n'

            # Extract invoice number
            invoice_match = re.search(r'invoice\s*#?\s*:?\s*(\w+)', full_text, re.IGNORECASE)
            if invoice_match:
                data['invoice_number'] = invoice_match.group(1)

            # Extract date
            date_patterns = [
                r'date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            ]
            for pattern in date_patterns:
                date_match = re.search(pattern, full_text, re.IGNORECASE)
                if date_match:
                    data['date'] = date_match.group(1)
                    break

            # Extract supplier/vendor
            supplier_match = re.search(r'(?:from|vendor|supplier)\s*:?\s*([A-Za-z\s]+)', full_text, re.IGNORECASE)
            if supplier_match:
                data['supplier'] = supplier_match.group(1).strip()

            # Extract line items - Performance Foodservice format
            # Format: QTY UNIT SIZE BRAND ITEM# DESCRIPTION ... prices at end
            lines = full_text.split('\n')
            for line in lines:
                # Simpler pattern: QTY UNIT SIZE ... DESCRIPTION ... last_two_numbers
                # Match lines starting with number and CS/EA/LB, extract description, get last price
                perf_match = re.search(r'^\s*(\d+)\s+(?:CS|EA|LB|BG|GL|CT|BX)\s+[\d/\.]+\s*\w*\s+(\w+)\s+(\w+)\s+(.+?)\s+([\d,]+\.?\d+)\s+([\d,]+\.?\d+)\s*$', line)

                if perf_match:
                    quantity = int(perf_match.group(1))
                    # Combine brand, item#, and description
                    description = perf_match.group(4).strip()
                    # Use the extension (total) price - last number on the line
                    try:
                        extension = float(perf_match.group(6).replace(',', ''))
                    except Exception:
                        # skip line if price can't be parsed
                        continue

                    # Clean description - remove leading item codes
                    description_parts = description.split()
                    # Skip numeric-looking parts at the start
                    clean_parts = []
                    skip_next = 0
                    for i, part in enumerate(description_parts):
                        if skip_next > 0:
                            skip_next -= 1
                            continue
                        # Keep parts that look like actual product names
                        if not re.match(r'^\d+$', part) or i > 2:
                            clean_parts.append(part)

                    description = ' '.join(clean_parts) if clean_parts else description

                    # Filter out header rows, misc charges, and empty items
                    if (len(description) > 3 and
                        quantity > 0 and
                        extension > 0 and
                        not re.match(r'^(item|description|qty|quantity|price|total|fuel|delivery|perishable|continued)', description, re.IGNORECASE)):
                        data['items'].append({
                            'name': description[:60],  # Limit description length
                            'quantity': quantity,
                            'price': extension  # Total price for that line item
                        })

            # Extract total
            total_match = re.search(r'total\s*:?\s*[\$€£]?([\d,]+\.?\d*)', full_text, re.IGNORECASE)
            if total_match:
                try:
                    data['total'] = float(total_match.group(1).replace(',', ''))
                except Exception:
                    data['total'] = None

    except Exception as e:
        print(f"Error processing PDF: {e}")

    return data

@app.route('/')
def index():
    return render_template('index.html')

def process_invoice_to_inventory(invoice_data):
    """Add invoice items to current inventory using conversions"""
    global current_inventory
    added_items = []

    for item in invoice_data['items']:
        item_name = item['name']
        quantity = item['quantity']

        # Try to match with conversion table
        matched = False
        for item_number, conv in conversions.items():
            # Simple matching - look for product code or description in item name
            if item_number in item_name or conv['description'].upper() in item_name.upper():
                matched = True

                # Convert from cases to usable units
                try:
                    items_per_case = float(conv['items_per_case']) if conv['items_per_case'] not in ['?', '', 'diffreent depending on size'] else 1
                    usable_quantity = quantity * items_per_case
                    usable_unit = conv['usable_unit']

                    # Add to inventory
                    if item_number not in current_inventory:
                        current_inventory[item_number] = {
                            'quantity': 0,
                            'unit': usable_unit,
                            'description': conv['description']
                        }

                    current_inventory[item_number]['quantity'] += usable_quantity
                    added_items.append({
                        'item_number': item_number,
                        'description': conv['description'],
                        'quantity_added': usable_quantity,
                        'unit': usable_unit
                    })
                    break
                except:
                    continue

        if not matched:
            print(f"Warning: Could not find conversion for '{item_name}'")

    return added_items

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('files[]')
    processed = 0
    file_type = request.form.get('file_type', 'invoice')  # 'invoice', 'sales', or 'starting_inventory'

    for file in files:
        if file and file.filename.endswith('.pdf'):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            if file_type == 'invoice':
                invoice_data = extract_invoice_data(filename)
                if invoice_data['items']:
                    added_items = process_invoice_to_inventory(invoice_data)
                    invoice_history.append({
                        'filename': file.filename,
                        'date': invoice_data.get('date', datetime.now().isoformat()),
                        'items_added': len(added_items),
                        'processed_at': datetime.now().isoformat()
                    })
                    processed += 1
                    save_inventory_state()

        elif file and file.filename.endswith('.csv'):
            csv_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(csv_path)

            if file_type == 'sales':
                # Process PAR sales data
                result = process_sales_data(csv_path)
                if result['processed'] > 0:
                    sales_history.append({
                        'filename': file.filename,
                        'items_processed': result['processed'],
                        'processed_at': datetime.now().isoformat()
                    })
                    processed += 1
                    save_inventory_state()

            elif file_type == 'starting_inventory':
                # Process starting/current inventory
                result = process_starting_inventory(csv_path)
                if result['processed'] > 0:
                    processed += 1
                    save_inventory_state()

    return jsonify({
        'success': True,
        'processed': processed,
        'current_items': len(current_inventory)
    })

@app.route('/upload_sales', methods=['POST'])
def upload_sales():
    """Upload and process PAR POS sales data (CSV)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400

    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(csv_path)

    result = process_sales_data(csv_path)

    if result['processed'] > 0:
        sales_history.append({
            'filename': file.filename,
            'items_processed': result['processed'],
            'processed_at': datetime.now().isoformat()
        })
        save_inventory_state()

    return jsonify({
        'success': True,
        'processed': result['processed'],
        'deductions': result['deductions']
    })

def process_sales_data(csv_path):
    """Process PAR POS sales CSV and deduct from inventory using recipes"""
    global current_inventory
    deductions = []
    processed = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Expected columns: item_name, quantity_sold, etc.
            item_name = row.get('item_name', '').strip()
            qty_sold = row.get('quantity_sold', '0').strip()

            if not item_name or not qty_sold:
                continue

            try:
                quantity_sold = float(qty_sold)
            except:
                continue

            # Look up recipe
            if item_name in recipes:
                for ingredient in recipes[item_name]:
                    item_number = ingredient['item_number']
                    qty_per_item = ingredient['quantity_used']
                    total_deduction = quantity_sold * qty_per_item

                    # Deduct from inventory
                    if item_number in current_inventory:
                        current_inventory[item_number]['quantity'] -= total_deduction
                        deductions.append({
                            'pos_item': item_name,
                            'item_number': item_number,
                            'description': ingredient['description'],
                            'deducted': total_deduction,
                            'unit': ingredient['unit']
                        })
                    else:
                        print(f"Warning: {item_number} not in inventory for {item_name}")

                processed += 1
            else:
                print(f"Warning: No recipe found for '{item_name}'")

    return {
        'processed': processed,
        'deductions': deductions
    }

def process_starting_inventory(csv_path):
    """Process starting/current inventory CSV and set inventory levels"""
    global current_inventory
    items_added = []
    processed = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Support multiple column name formats
            item_number = (row.get('Product Number') or
                          row.get('product_number') or
                          row.get('item_number') or
                          row.get('Item Number', '')).strip()

            current_qty = (row.get('Current Inventory') or
                          row.get('current_inventory') or
                          row.get('quantity') or
                          row.get('Quantity', '')).strip()

            if not item_number or not current_qty:
                continue

            try:
                quantity = float(current_qty)
            except:
                continue

            # Check if this item exists in our conversion table
            if item_number in conversions:
                conv = conversions[item_number]

                # If quantity is in cases (< 100 typically), convert to usable units
                # Otherwise assume it's already in usable units
                if quantity < 100:
                    # Likely cases, convert to usable units
                    try:
                        items_per_case = float(conv['items_per_case']) if conv['items_per_case'] not in ['?', '', 'diffreent depending on size'] else 1
                        usable_quantity = quantity * items_per_case
                    except:
                        # Can't convert, use as-is
                        usable_quantity = quantity
                else:
                    # Already in usable units
                    usable_quantity = quantity

                # Set (or update) inventory
                current_inventory[item_number] = {
                    'quantity': usable_quantity,
                    'unit': conv['usable_unit'],
                    'description': conv['description']
                }

                items_added.append({
                    'item_number': item_number,
                    'description': conv['description'],
                    'quantity': usable_quantity,
                    'unit': conv['usable_unit']
                })
                processed += 1
            else:
                print(f"Warning: Item {item_number} not found in conversion table")

    return {
        'processed': processed,
        'items_added': items_added
    }

@app.route('/upload_starting_inventory', methods=['POST'])
def upload_starting_inventory():
    """Upload and process starting/current inventory CSV"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400

    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(csv_path)

    result = process_starting_inventory(csv_path)

    if result['processed'] > 0:
        save_inventory_state()

    return jsonify({
        'success': True,
        'processed': result['processed'],
        'items_added': result['items_added']
    })

@app.route('/inventory')
def get_inventory():
    """Get current inventory state"""
    inventory_list = [
        {
            'item_number': item_number,
            'description': data['description'],
            'quantity': round(data['quantity'], 2),
            'unit': data['unit']
        }
        for item_number, data in sorted(current_inventory.items(), key=lambda x: x[1]['description'])
    ]

    return jsonify({
        'inventory': inventory_list,
        'total_items': len(inventory_list),
        'invoice_count': len(invoice_history),
        'sales_count': len(sales_history)
    })

@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    """Manually update inventory quantity"""
    data = request.get_json()
    item_number = data.get('item_number')
    new_quantity = data.get('quantity')

    if not item_number or new_quantity is None:
        return jsonify({'error': 'Missing item_number or quantity'}), 400

    try:
        new_quantity = float(new_quantity)
    except:
        return jsonify({'error': 'Invalid quantity format'}), 400

    if item_number in current_inventory:
        old_quantity = current_inventory[item_number]['quantity']
        current_inventory[item_number]['quantity'] = new_quantity
        save_inventory_state()

        return jsonify({
            'success': True,
            'item_number': item_number,
            'description': current_inventory[item_number]['description'],
            'old_quantity': old_quantity,
            'new_quantity': new_quantity
        })
    else:
        return jsonify({'error': 'Item not found in inventory'}), 404

@app.route('/clear', methods=['POST'])
def clear_inventory():
    """Clear all inventory data and history"""
    global current_inventory, invoice_history, sales_history
    current_inventory = {}
    invoice_history = []
    sales_history = []

    # Save empty state
    save_inventory_state()

    # Clean up uploaded files
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

    return jsonify({'success': True})

# Load conversion and recipe data on startup
print("Loading conversion and recipe data...")
load_conversions()
load_recipes()
load_inventory_state()

if __name__ == '__main__':
    # Local development server
    default_port = 5000
    # check port availability and pick a free port if 5000 is in use
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            in_use = s.connect_ex(('127.0.0.1', default_port)) == 0
        if in_use:
            # bind to port 0 to get an ephemeral free port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                s2.bind(('127.0.0.1', 0))
                port = s2.getsockname()[1]
            print(f"Port {default_port} in use, starting Flask on port {port} instead")
        else:
            port = default_port
    except Exception as e:
        print(f"Port check failed: {e}. Falling back to {default_port}")
        port = default_port

    app.run(debug=True, port=port)
