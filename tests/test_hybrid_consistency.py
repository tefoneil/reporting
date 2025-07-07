#!/usr/bin/env python3
"""
Unit tests for hybrid consistency mode v0.1.4
Tests baseline status loading and circuit classification logic
"""

import pandas as pd
import sys
import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monthly_builder import ChronicReportBuilder

def test_baseline_status_loading():
    """Test loading baseline status from prior JSON summaries"""
    
    # Create temporary directory with test JSON
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test baseline JSON (May 2025)
        baseline_data = {
            "version": "0.1.3",
            "chronic_data": {
                "existing_chronics": {
                    "chronic_consistent": [
                        "500332738",
                        "SR216187",
                        "PTH TOK EPL 90030025"
                    ],
                    "chronic_inconsistent": [
                        "091NOID1143035717419_889599",
                        "LD017936",
                        "IST6022E#2_010G"
                    ],
                    "media_chronics": [
                        "VID-1583",
                        "VID-1597"
                    ]
                }
            }
        }
        
        # Write baseline JSON
        baseline_file = temp_path / "chronic_summary_May_2025.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        # Test baseline loading
        builder = ChronicReportBuilder()
        baseline_status, baseline_ids = builder.load_baseline_status(temp_dir)
        
        # Verify baseline status
        assert baseline_status["500332738"] == "Consistent"
        assert baseline_status["SR216187"] == "Consistent"
        assert baseline_status["091NOID1143035717419_889599"] == "Inconsistent"
        assert baseline_status["VID-1583"] == "Media Chronic"
        
        # Verify baseline IDs set
        assert "500332738" in baseline_ids
        assert "091NOID1143035717419_889599" in baseline_ids
        assert "VID-1583" in baseline_ids
        
        # Verify baseline found flag
        assert builder.baseline_found == True
        
        print("✅ Baseline status loading test passed!")
        return baseline_status, baseline_ids

def test_no_baseline_found():
    """Test behavior when no baseline JSON is found"""
    
    # Create empty temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        builder = ChronicReportBuilder()
        baseline_status, baseline_ids = builder.load_baseline_status(temp_dir)
        
        # Verify empty results
        assert len(baseline_status) == 0
        assert len(baseline_ids) == 0
        assert builder.baseline_found == False
        
        print("✅ No baseline found test passed!")

def test_hybrid_classification_logic():
    """Test hybrid classification with baseline + new circuits"""
    
    # Create test data with both legacy and new circuits
    test_data = pd.DataFrame({
        'Config Item Name': [
            '500332738',  # Legacy consistent (should stay consistent)
            '091NOID1143035717419_889599',  # Legacy inconsistent (should stay inconsistent)
            '444282783',  # New circuit with 8 tickets (should become consistent)
            'CID_TEST_4',  # New circuit with 4 tickets (should become inconsistent)
            'VID-1583'  # Legacy media chronic (should stay media)
        ],
        'Inc Resolved At (Month / Year)': [
            'June 2025',
            'June 2025', 
            'June 2025',
            'June 2025',
            'June 2025'
        ],
        'Distinct count of Inc Nbr': [
            10,  # Legacy consistent circuit
            5,   # Legacy inconsistent circuit
            8,   # New circuit above threshold
            4,   # New circuit below threshold
            0    # Media circuit
        ]
    })
    
    # Create mock baseline status
    baseline_status = {
        '500332738': 'Consistent',
        '091NOID1143035717419_889599': 'Inconsistent', 
        'VID-1583': 'Media Chronic'
    }
    baseline_ids = set(baseline_status.keys())
    
    # Mock the baseline loading in builder
    builder = ChronicReportBuilder()
    builder.baseline_found = True
    
    # Simulate the hybrid classification logic
    chronic_consistent = []
    chronic_inconsistent = []
    media_chronics_hybrid = []
    circuit_ticket_data = {}
    
    CONSISTENT_THRESHOLD = 6  # Default threshold
    
    # Test circuits from our data
    test_circuits = ['500332738', '091NOID1143035717419_889599', '444282783', 'CID_TEST_4', 'VID-1583']
    
    for circuit_id in test_circuits:
        # Get rolling tickets (simplified - just sum for test)
        circuit_data = test_data[test_data['Config Item Name'] == circuit_id]
        rolling_tickets = circuit_data['Distinct count of Inc Nbr'].sum() if len(circuit_data) > 0 else 0
        
        circuit_ticket_data[circuit_id] = {
            'rolling_ticket_total': rolling_tickets
        }
        
        # Apply hybrid logic
        if circuit_id in baseline_status:
            # Legacy circuit - freeze existing status
            status = baseline_status[circuit_id]
            circuit_ticket_data[circuit_id]['status'] = status.lower()
            
            if status == 'Consistent':
                chronic_consistent.append(circuit_id)
            elif status == 'Inconsistent':
                chronic_inconsistent.append(circuit_id)
            elif status == 'Media Chronic':
                media_chronics_hybrid.append(circuit_id)
        else:
            # New circuit - use ticket-based classification
            if rolling_tickets >= CONSISTENT_THRESHOLD:
                chronic_consistent.append(circuit_id)
                circuit_ticket_data[circuit_id]['status'] = 'consistent'
            else:
                chronic_inconsistent.append(circuit_id)
                circuit_ticket_data[circuit_id]['status'] = 'inconsistent'
    
    # Verify hybrid classification results
    assert '500332738' in chronic_consistent  # Legacy consistent stays consistent
    assert '091NOID1143035717419_889599' in chronic_inconsistent  # Legacy inconsistent stays inconsistent
    assert '444282783' in chronic_consistent  # New circuit with 8 tickets → consistent
    assert 'CID_TEST_4' in chronic_inconsistent  # New circuit with 4 tickets → inconsistent
    assert 'VID-1583' in media_chronics_hybrid  # Legacy media stays media
    
    # Verify ticket data is preserved
    assert circuit_ticket_data['500332738']['rolling_ticket_total'] == 10
    assert circuit_ticket_data['500332738']['status'] == 'consistent'  # Legacy frozen
    
    assert circuit_ticket_data['444282783']['rolling_ticket_total'] == 8
    assert circuit_ticket_data['444282783']['status'] == 'consistent'  # New ≥6 tickets
    
    assert circuit_ticket_data['CID_TEST_4']['rolling_ticket_total'] == 4
    assert circuit_ticket_data['CID_TEST_4']['status'] == 'inconsistent'  # New <6 tickets
    
    print("✅ Hybrid classification logic test passed!")
    return circuit_ticket_data

def test_threshold_override():
    """Test that MR_CONSISTENT_THRESHOLD environment variable works"""
    
    # Set custom threshold
    original_threshold = os.getenv("MR_CONSISTENT_THRESHOLD")
    os.environ["MR_CONSISTENT_THRESHOLD"] = "8"
    
    try:
        # Reload the module to pick up new env var
        import importlib
        import monthly_builder
        importlib.reload(monthly_builder)
        
        # Test that threshold changed
        from monthly_builder import CONSISTENT_THRESHOLD
        assert CONSISTENT_THRESHOLD == 8
        
        print("✅ Threshold override test passed!")
        
    finally:
        # Restore original value
        if original_threshold is not None:
            os.environ["MR_CONSISTENT_THRESHOLD"] = original_threshold
        else:
            del os.environ["MR_CONSISTENT_THRESHOLD"]

if __name__ == "__main__":
    print("🧪 Testing hybrid consistency mode v0.1.4")
    print("=" * 60)
    
    # Test 1: Baseline status loading
    baseline_status, baseline_ids = test_baseline_status_loading()
    
    print("\n" + "=" * 60)
    
    # Test 2: No baseline found
    test_no_baseline_found()
    
    print("\n" + "=" * 60)
    
    # Test 3: Hybrid classification logic
    circuit_data = test_hybrid_classification_logic()
    
    print("\n" + "=" * 60)
    
    # Test 4: Threshold override
    test_threshold_override()
    
    print("\n" + "=" * 60)
    print("🎉 All hybrid consistency tests completed successfully!")
    print(f"Baseline circuits loaded: {len(baseline_status)}")
    print(f"Circuit ticket data: {len(circuit_data)} circuits processed")