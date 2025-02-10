import pandas as pd
import numpy as np


class PartsDatabase:
    def __init__(self):
        # Initialize empty DataFrames for all tables
        self.vendors = pd.DataFrame(columns=['vendor_id', 'vendor_name'])
        self.parts = pd.DataFrame(columns=['part_id', 'part_name'])
        self.part_drawings = pd.DataFrame(columns=['part_id', 'file_extension', 'drawing_data'])
        self.vendor_parts = pd.DataFrame(columns=['vendor_id', 'part_id'])

    def save_all(self, folder='data/'):
        """Save all DataFrames to CSV files"""
        self.vendors.to_csv(f'{folder}vendors.csv', index=False)
        self.parts.to_csv(f'{folder}parts.csv', index=False)
        self.part_drawings.to_csv(f'{folder}part_drawings.csv', index=False)
        self.vendor_parts.to_csv(f'{folder}vendor_parts.csv', index=False)
        print("All data saved successfully")

    def load_all(self, folder='data/'):
        """Load all DataFrames from CSV files"""
        try:
            self.vendors = pd.read_csv(f'{folder}vendors.csv')
            self.parts = pd.read_csv(f'{folder}parts.csv')
            self.part_drawings = pd.read_csv(f'{folder}part_drawings.csv')
            self.vendor_parts = pd.read_csv(f'{folder}vendor_parts.csv')
            print("All data loaded successfully")
        except FileNotFoundError as e:
            print(f"Some files not found. Starting with empty tables: {e}")

    def insert_vendor(self, vendor_name):
        """Insert a new vendor"""
        vendor_id = len(self.vendors) + 1
        new_vendor = pd.DataFrame({
            'vendor_id': [vendor_id],
            'vendor_name': [vendor_name]
        })
        self.vendors = pd.concat([self.vendors, new_vendor], ignore_index=True)
        return vendor_id

    def insert_part(self, part_name):
        """Insert a new part"""
        part_id = len(self.parts) + 1
        new_part = pd.DataFrame({
            'part_id': [part_id],
            'part_name': [part_name]
        })
        self.parts = pd.concat([self.parts, new_part], ignore_index=True)
        return part_id

    def insert_part_drawing(self, part_id, file_extension, drawing_data):
        """Insert a part drawing"""
        if part_id not in self.parts['part_id'].values:
            raise ValueError(f"Part ID {part_id} does not exist")

        new_drawing = pd.DataFrame({
            'part_id': [part_id],
            'file_extension': [file_extension],
            'drawing_data': [drawing_data]
        })
        self.part_drawings = pd.concat([self.part_drawings, new_drawing], ignore_index=True)

    def link_vendor_part(self, vendor_id, part_id):
        """Create a vendor-part relationship"""
        if vendor_id not in self.vendors['vendor_id'].values:
            raise ValueError(f"Vendor ID {vendor_id} does not exist")
        if part_id not in self.parts['part_id'].values:
            raise ValueError(f"Part ID {part_id} does not exist")

        new_link = pd.DataFrame({
            'vendor_id': [vendor_id],
            'part_id': [part_id]
        })
        self.vendor_parts = pd.concat([self.vendor_parts, new_link], ignore_index=True)

    def print_all(self):
        """Print all tables"""
        print("\nVendors:")
        print("-" * 50)
        print(self.vendors)

        print("\nParts:")
        print("-" * 50)
        print(self.parts)

        print("\nPart Drawings:")
        print("-" * 50)
        print(self.part_drawings)

        print("\nVendor-Parts Relationships:")
        print("-" * 50)
        print(self.vendor_parts)


# Example usage
if __name__ == '__main__':
    # Create database instance
    db = PartsDatabase()

    # Insert sample vendors
    vendors = [
        '3M Co.',
        'AKM Semiconductor Inc.',
        'Asahi Glass Co Ltd.'
    ]
    for vendor in vendors:
        db.insert_vendor(vendor)

    # Insert sample parts
    parts = [
        'Transistor',
        'Resistor',
        'Capacitor'
    ]
    for part in parts:
        db.insert_part(part)

    # Insert sample drawings
    db.insert_part_drawing(1, 'png', 'binary_data_1')
    db.insert_part_drawing(2, 'jpg', 'binary_data_2')

    # Create vendor-part relationships
    db.link_vendor_part(1, 1)  # Vendor 1 supplies Part 1
    db.link_vendor_part(1, 2)  # Vendor 1 supplies Part 2
    db.link_vendor_part(2, 1)  # Vendor 2 supplies Part 1

    # Print all data
    db.print_all()

    # Save data to CSV files
    db.save_all()

    # Create a new instance and load data
    db2 = PartsDatabase()
    db2.load_all()
