#!/usr/bin/env python3
import pandas as pd
import sys

def analyze_excel_file(filepath):
    """Analyze Excel file structure and show sample data"""
    print(f"\n=== ANALYZING: {filepath} ===")
    try:
        # Try to read the Excel file
        xl_file = pd.ExcelFile(filepath)
        print(f"Sheet names: {xl_file.sheet_names}")
        
        for sheet_name in xl_file.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print(f"First 3 rows:\n{df.head(3)}")
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use command line arguments if provided
        for file_path in sys.argv[1:]:
            analyze_excel_file(file_path)
    else:
        print("Usage: python analyze_data.py <excel_file1> [excel_file2] ...")
        print("Example: python analyze_data.py impacts.xlsx counts.xlsx")