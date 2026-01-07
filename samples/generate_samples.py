"""
Script to generate sample test files for DQ Inventory
Run this to create sample PDFs and CSVs
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import csv
from datetime import datetime


def create_sample_invoice_pdf(filename, invoice_num, date, items):
    """Create a sample Performance Foodservice invoice PDF"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "PERFORMANCE FOODSERVICE")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"Invoice #: {invoice_num}")
    c.drawString(50, height - 95, f"Date: {date}")
    c.drawString(50, height - 110, "Vendor: Performance Food Group")

    # Column headers
    y_position = height - 150
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y_position, "QTY")
    c.drawString(100, y_position, "UNIT")
    c.drawString(150, y_position, "PACK")
    c.drawString(220, y_position, "ITEM")
    c.drawString(280, y_position, "CODE")
    c.drawString(340, y_position, "DESCRIPTION")
    c.drawString(480, y_position, "PRICE")
    c.drawString(540, y_position, "EXT")

    # Line items
    c.setFont("Helvetica", 8)
    y_position -= 20

    total = 0
    for item in items:
        qty, unit, pack, item_code1, item_code2, description, price, ext = item
        c.drawString(50, y_position, str(qty))
        c.drawString(100, y_position, unit)
        c.drawString(150, y_position, pack)
        c.drawString(220, y_position, item_code1)
        c.drawString(280, y_position, item_code2)
        c.drawString(340, y_position, description)
        c.drawString(480, y_position, f"{price:.2f}")
        c.drawString(540, y_position, f"{ext:.2f}")
        y_position -= 15
        total += ext

        if y_position < 100:
            break

    # Total
    c.setFont("Helvetica-Bold", 10)
    c.drawString(480, 80, "TOTAL:")
    c.drawString(540, 80, f"${total:.2f}")

    c.save()
    print(f"Created {filename}")


def create_sales_csv(filename):
    """Create a sample PAR POS sales CSV"""
    data = [
        ['item_name', 'quantity_sold', 'average_price', 'total', 'percent'],
        ['SM BLIZZARD', '45', '4.99', '224.55', '18.2'],
        ['MD BLIZZARD', '32', '5.99', '191.68', '15.5'],
        ['LG BLIZZARD', '18', '6.99', '125.82', '10.2'],
        ['SM CONE', '67', '2.49', '166.83', '13.5'],
        ['MD CONE', '41', '3.49', '143.09', '11.6'],
        ['DILLY BAR', '28', '1.99', '55.72', '4.5'],
        ['BUSTER BAR', '15', '3.29', '49.35', '4.0'],
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

    print(f"Created {filename}")


def create_starting_inventory_csv(filename):
    """Create a sample starting inventory CSV"""
    data = [
        ['Product Number', 'Current Inventory', 'Pack Size', 'Brand'],
        ['GF662', '8', '1/5 GAL', 'DQ'],
        ['AJW24', '3', '15/40CNTDQ', 'Generic'],
        ['RR730', '2', '1/25 LB', 'Generic'],
        ['SX449', '5', '4/1 GAL', 'DQ'],
        ['PL881', '12', '12/16 OZ', 'Generic'],
        ['QT992', '6', '6/64 OZ', 'DQ'],
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

    print(f"Created {filename}")


if __name__ == '__main__':
    # Create sample invoices
    invoice1_items = [
        (2, 'CS', '1/5GAL', 'GF662', 'SOFT', 'ICE CREAM MIX SFTSRV VAN', 42.50, 85.00),
        (3, 'CS', '15/40CNT', 'AJW24', 'DQ', 'CUP PAPER 32OZ 600', 38.25, 114.75),
        (1, 'CS', '1/25LB', 'RR730', 'GENERIC', 'SUGAR GRANULATED FINE', 45.80, 45.80),
        (4, 'CS', '4/1GAL', 'SX449', 'DQ', 'TOPPING STRAWBERRY', 28.90, 115.60),
        (2, 'CS', '12/16OZ', 'PL881', 'GENERIC', 'SPRINKLES RAINBOW', 22.40, 44.80),
    ]

    invoice2_items = [
        (5, 'CS', '6/64OZ', 'QT992', 'DQ', 'SYRUP CHOCOLATE', 31.20, 156.00),
        (2, 'CS', '1/5GAL', 'GF662', 'SOFT', 'ICE CREAM MIX SFTSRV VAN', 42.50, 85.00),
        (1, 'CS', '4/1GAL', 'SX449', 'DQ', 'TOPPING STRAWBERRY', 28.90, 28.90),
        (3, 'BG', '1/50LB', 'MN334', 'GENERIC', 'FLOUR ALL PURPOSE', 35.60, 106.80),
    ]

    create_sample_invoice_pdf('samples/invoice_2026_001.pdf', 'INV-2026-001', '01/06/2026', invoice1_items)
    create_sample_invoice_pdf('samples/invoice_2026_002.pdf', 'INV-2026-002', '01/03/2026', invoice2_items)

    # Create sample CSVs
    create_sales_csv('samples/sample_sales.csv')
    create_starting_inventory_csv('samples/sample_starting_inventory.csv')

    print("\n✅ All sample files created successfully!")
    print("\nYou can now upload these files to test your app:")
    print("  - samples/invoice_2026_001.pdf (Performance Food Invoice)")
    print("  - samples/invoice_2026_002.pdf (Performance Food Invoice)")
    print("  - samples/sample_sales.csv (PAR POS Sales Data)")
    print("  - samples/sample_starting_inventory.csv (Starting Inventory)")
