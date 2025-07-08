#!/usr/bin/env python3
"""
Test deduplication of outage rows (v0.1.9-rc6)
Verifies that duplicate incidents are properly deduplicated before hour calculation
"""

import pandas as pd
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from monthly_builder import ChronicReportBuilder


def test_dedupe_outage_rows():
    """Test that duplicate incident rows are properly deduplicated"""
    
    # Create test data with duplicate incidents
    test_data = pd.DataFrame({
        'Config Item Name': ['SR216187', 'SR216187', 'SR216187', 'LZA010663'],
        'Distinct count of Inc Nbr': ['INC-123', 'INC-123', 'INC-999', 'INC-456'],  # INC-123 is duplicate
        'Outage Duration': ['33,902', '17,511', '100,398', '1,200'],  # Should sum only unique incidents
        'Incident Network-facing Impacted CI Type': ['PCCW', 'PCCW', 'PCCW', 'NTT']
    })
    
    builder = ChronicReportBuilder()
    
    # Test the deduplication function
    cleaned_data = builder._clean_outage(test_data)
    
    print("=== DEDUPLICATION TEST ===")
    print(f"Original rows: {len(test_data)}")
    print(f"After deduplication: {len(cleaned_data)}")
    
    # Verify deduplication worked
    assert len(cleaned_data) == 3, f"Expected 3 rows after deduplication, got {len(cleaned_data)}"
    
    # Verify ImpactHours calculation
    assert 'ImpactHours' in cleaned_data.columns, "ImpactHours column should be created"
    
    # Check SR216187 totals - should only have INC-123 (first occurrence) + INC-999
    sr_data = cleaned_data[cleaned_data['Config Item Name'] == 'SR216187']
    expected_hours = (33902 + 100398) / 60  # Only unique incidents
    actual_hours = sr_data['ImpactHours'].sum()
    
    print(f"SR216187 expected hours: {expected_hours:.2f}")
    print(f"SR216187 actual hours: {actual_hours:.2f}")
    
    assert abs(actual_hours - expected_hours) < 0.01, f"Expected {expected_hours:.2f}h, got {actual_hours:.2f}h"
    
    # Verify no duplicate incident numbers exist
    duplicates = cleaned_data.duplicated(subset=['Config Item Name', 'Distinct count of Inc Nbr'])
    assert not duplicates.any(), "No duplicate circuit+incident combinations should exist"
    
    print("✅ Deduplication test passed!")


if __name__ == "__main__":
    test_dedupe_outage_rows()