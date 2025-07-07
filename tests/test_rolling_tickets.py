#!/usr/bin/env python3
"""
Unit tests for get_rolling_ticket_total function
Tests handling of blank month cells and ticket counting
"""

import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyze_data import get_rolling_ticket_total

def test_rolling_ticket_total_with_blank_months():
    """Test get_rolling_ticket_total with blank month cells"""
    
    # Create test data with blank month cells (simulating the 091NOID issue)
    test_data = pd.DataFrame({
        'Config Item Name': [
            '091NOID1143035717419_889599',
            '091NOID1143035717419_889599',
            '091NOID1143035717419_889599',
            'SR216187',
            'SR216187'
        ],
        'Inc Resolved At (Month / Year)': [
            None,  # Blank month cell
            None,  # Blank month cell
            None,  # Blank month cell
            'June 2025',
            'June 2025'
        ],
        'Distinct count of Inc Nbr': [
            5,  # These should be counted after forward-fill
            3,
            2,
            10,
            15
        ]
    })
    
    print("Test data before forward-fill:")
    print(test_data)
    
    # Test data simulation: the issue is that blank months cause circuits to be excluded
    # from chronic detection, not that ticket counting returns 0
    
    # Filter data WITH blank months (simulates how chronic detection works)
    data_with_blanks = test_data[test_data['Inc Resolved At (Month / Year)'].notna()]
    tickets_with_blanks = get_rolling_ticket_total('091NOID1143035717419_889599', data_with_blanks)
    print(f"Tickets with blank month filter (before fix): {tickets_with_blanks}")
    
    # Apply forward-fill (simulating the fix)
    test_data_fixed = test_data.copy()
    test_data_fixed.loc[:, 'Inc Resolved At (Month / Year)'] = test_data_fixed['Inc Resolved At (Month / Year)'].ffill()
    
    print("\nTest data after forward-fill:")
    print(test_data_fixed)
    
    # All data should now have valid months after forward-fill
    data_after_fill = test_data_fixed
    tickets_after_fill = get_rolling_ticket_total('091NOID1143035717419_889599', data_after_fill)
    print(f"Tickets after forward-fill: {tickets_after_fill}")
    
    # Test other circuit (should work normally)
    sr_tickets = get_rolling_ticket_total('SR216187', data_after_fill)
    print(f"SR216187 tickets: {sr_tickets}")
    
    # Assertions - the fix allows previously excluded data to be included
    assert tickets_with_blanks == 0, f"Expected 0 tickets with blank filter, got {tickets_with_blanks}"
    assert tickets_after_fill == 10, f"Expected 10 tickets after fill (5+3+2), got {tickets_after_fill}"
    assert sr_tickets == 25, f"Expected 25 tickets for SR216187 (10+15), got {sr_tickets}"
    
    print("\n✅ All tests passed!")
    
    return {
        'before_fill': tickets_with_blanks,
        'after_fill': tickets_after_fill,
        'sr_tickets': sr_tickets
    }

def test_no_blank_months():
    """Test normal operation with no blank months"""
    
    test_data = pd.DataFrame({
        'Config Item Name': [
            'TEST_CIRCUIT',
            'TEST_CIRCUIT',
            'TEST_CIRCUIT'
        ],
        'Inc Resolved At (Month / Year)': [
            'June 2025',
            'June 2025',
            'June 2025'
        ],
        'Distinct count of Inc Nbr': [
            4,
            2,
            1
        ]
    })
    
    tickets = get_rolling_ticket_total('TEST_CIRCUIT', test_data)
    print(f"Normal operation test - tickets: {tickets}")
    
    assert tickets == 7, f"Expected 7 tickets (4+2+1), got {tickets}"
    print("✅ Normal operation test passed!")
    
    return tickets

if __name__ == "__main__":
    print("🧪 Testing get_rolling_ticket_total with blank month cells")
    print("=" * 60)
    
    # Test 1: Blank month handling
    result1 = test_rolling_ticket_total_with_blank_months()
    
    print("\n" + "=" * 60)
    
    # Test 2: Normal operation
    result2 = test_no_blank_months()
    
    print("\n" + "=" * 60)
    print("🎉 All unit tests completed successfully!")
    print(f"Blank month test results: {result1}")
    print(f"Normal operation result: {result2}")