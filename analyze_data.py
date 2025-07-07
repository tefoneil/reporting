#!/usr/bin/env python3
import pandas as pd
import sys
from datetime import datetime, timedelta

def get_rolling_ticket_total(canonical_circuit_id, data, months=3):
    """
    Calculate rolling ticket total for a canonical circuit ID over specified months.
    
    Args:
        canonical_circuit_id: Canonical circuit identifier (normalized) to calculate tickets for
        data: DataFrame containing ticket data with 'canonical_id' and 'Distinct count of Inc Nbr'
        months: Number of months to roll back (default 3)
        
    Returns:
        int: Total ticket count for the circuit over the rolling period
    """
    # Filter data for the canonical circuit ID
    if 'canonical_id' in data.columns:
        circuit_data = data[data['canonical_id'] == canonical_circuit_id]
    else:
        # Fallback to original behavior if canonical_id not available
        circuit_data = data[data['Config Item Name'] == canonical_circuit_id]
    
    if len(circuit_data) == 0:
        return 0
    
    # Use only "Distinct count of Inc Nbr" column for ticket counts (v0.1.5 requirement)
    ticket_column = 'Distinct count of Inc Nbr'
    if ticket_column in circuit_data.columns:
        # Sum all tickets for this canonical ID, handling NaN values
        total_tickets = circuit_data[ticket_column].fillna(0).sum()
        return int(total_tickets)
    
    # Fallback: look for other ticket-related columns (legacy support)
    ticket_columns = []
    for col in circuit_data.columns:
        if any(keyword in col.lower() for keyword in ['ticket', 'count', 'incident']):
            ticket_columns.append(col)
    
    # Sum numeric ticket-related columns
    total_tickets = 0
    for col in ticket_columns:
        try:
            total_tickets += circuit_data[col].fillna(0).sum()
        except (TypeError, ValueError):
            continue
    
    # If no ticket columns found, count rows as incidents
    if total_tickets == 0:
        total_tickets = len(circuit_data)
    
    return int(total_tickets)

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