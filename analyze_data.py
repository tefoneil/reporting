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
    files = [
        "/Users/teffy/Downloads/Impacts by CI Type Crosstab (2) (1).xlsx",
        "/Users/teffy/Downloads/Count Months Chronic (1) (1).xlsx"
    ]
    
    for file in files:
        analyze_excel_file(file)