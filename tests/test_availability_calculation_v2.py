#!/usr/bin/env python3
"""
Test availability calculation matches v2.20-rc2-p5b reference values
"""

import pandas as pd
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from monthly_builder import ChronicReportBuilder

def test_availability_matches_reference():
    """Test that availability calculation produces reference values"""
    
    print("=== AVAILABILITY REFERENCE REGRESSION TEST ===")
    
    # Expected values from v2.20-rc2-p5b reference
    expected_values = {
        'LZA010663': 78.98,
        'PTH TOK EPL 90030025': 79.98,
        'N2864477L': 83.90,
        '500335805': 84.30,
        '444282783': 87.60
    }
    
    # Run the actual calculation
    builder = ChronicReportBuilder()
    impacts_df, counts_df = builder.load_crosstab_data(
        "/Users/teffy/Downloads/Impacts by CI Type Crosstab (2) (3).xlsx",
        "/Users/teffy/Downloads/Count Months Chronic (3).xlsx"
    )
    
    chronic_data = builder.process_chronic_logic(impacts_df, counts_df)
    metrics = builder.calculate_metrics(chronic_data)
    
    if 'bottom5_availability' not in metrics:
        print("❌ FAIL: No bottom5_availability in metrics")
        return False
    
    actual_values = metrics['bottom5_availability']
    
    print("Comparing availability values:")
    all_passed = True
    
    for circuit_display, expected in expected_values.items():
        # Handle circuit display names (may have provider prefixes)
        matching_circuit = None
        for actual_circuit in actual_values.keys():
            if circuit_display in actual_circuit or actual_circuit in circuit_display:
                matching_circuit = actual_circuit
                break
        
        if matching_circuit:
            actual = actual_values[matching_circuit]
            diff = abs(actual - expected)
            status = "✅ PASS" if diff < 0.1 else "❌ FAIL"
            print(f"  {circuit_display}: {actual:.2f}% (expected {expected:.2f}%, diff {diff:.3f}%) {status}")
            if diff >= 0.1:
                all_passed = False
        else:
            print(f"  {circuit_display}: NOT FOUND ❌ FAIL")
            all_passed = False
    
    if all_passed:
        print(f"\n✅ ALL TESTS PASSED: Availability calculations match reference within 0.1%")
    else:
        print(f"\n❌ SOME TESTS FAILED: Check availability calculation logic")
    
    return all_passed

if __name__ == "__main__":
    test_availability_matches_reference()