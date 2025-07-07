#!/usr/bin/env python3
"""
Unit tests for canonical ID normalization v0.1.5
Tests ID extraction, aggregation, and baseline compatibility
"""

import pandas as pd
import sys
import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monthly_builder import canonical_id, ChronicReportBuilder
from analyze_data import get_rolling_ticket_total

def test_canonical_id_extraction():
    """Test canonical ID extraction according to v0.1.5 specification"""
    
    test_cases = [
        # (input, expected_output, description)
        ("091NOID1143035717419_889599", "091NOID1143035717419", "Underscore split"),
        ("091NOID1143035717849_889621", "091NOID1143035717849", "Underscore split variant"),
        ("500335805-CH1/EXTRA", "500335805", "Hyphen split (follows ≥3 digits)"),
        ("500335805-CH1", "500335805", "Hyphen split simple"),
        ("LD017936 / FRANFRT-SINGAPOR/PISTA/10GE1", "LD017936", "Space split"),
        ("SR216187", "SR216187", "No split needed"),
        ("VID-1583", "VID-1583", "No split - letters before hyphen"),
        ("VID-1597", "VID-1597", "No split - media chronic"),
        ("PTH TOK EPL 90030025", "PTH", "Space split before TOK"),
        ("", "", "Empty string"),
        (None, "", "None input"),
    ]
    
    for input_id, expected, description in test_cases:
        result = canonical_id(input_id)
        assert result == expected, f"Failed: {description} - Input: '{input_id}' -> Expected: '{expected}', Got: '{result}'"
        print(f"✅ {description}: '{input_id}' -> '{result}'")
    
    print("✅ All canonical ID extraction tests passed!")
    return True

def test_091noid_aggregation():
    """Test that 091NOID variants aggregate properly"""
    
    # Create test data with 091NOID variants
    test_data = pd.DataFrame({
        'Config Item Name': [
            '091NOID1143035717419_889599',
            '091NOID1143035717419_889621', 
            '091NOID1143035717419_1040578',  # Another variant
            'SR216187',
            '500335805-CH1'
        ],
        'Inc Resolved At (Month / Year)': [
            'June 2025',
            'June 2025',
            'June 2025',
            'June 2025',
            'June 2025'
        ],
        'Distinct count of Inc Nbr': [
            2,  # 091NOID variant 1
            3,  # 091NOID variant 2  
            1,  # 091NOID variant 3
            10, # SR216187
            5   # 500335805-CH1
        ]
    })
    
    # Add canonical IDs
    test_data['canonical_id'] = test_data['Config Item Name'].apply(canonical_id)
    
    # Test canonical ID generation
    assert test_data.iloc[0]['canonical_id'] == '091NOID1143035717419'
    assert test_data.iloc[1]['canonical_id'] == '091NOID1143035717419'  # Same as first
    assert test_data.iloc[2]['canonical_id'] == '091NOID1143035717419'  # Same as first
    assert test_data.iloc[3]['canonical_id'] == 'SR216187'
    assert test_data.iloc[4]['canonical_id'] == '500335805'
    
    # Test ticket aggregation using canonical ID
    canonical_091noid = '091NOID1143035717419'
    rolling_tickets = get_rolling_ticket_total(canonical_091noid, test_data)
    
    # Should aggregate all three variants: 2 + 3 + 1 = 6
    assert rolling_tickets == 6, f"Expected 6 tickets for 091NOID aggregation, got {rolling_tickets}"
    
    # Test other circuits
    sr_tickets = get_rolling_ticket_total('SR216187', test_data)
    assert sr_tickets == 10, f"Expected 10 tickets for SR216187, got {sr_tickets}"
    
    cirion_tickets = get_rolling_ticket_total('500335805', test_data)
    assert cirion_tickets == 5, f"Expected 5 tickets for 500335805, got {cirion_tickets}"
    
    print("✅ 091NOID aggregation test passed!")
    print(f"   091NOID variants (2+3+1) = {rolling_tickets} tickets")
    print(f"   SR216187 = {sr_tickets} tickets")
    print(f"   500335805 = {cirion_tickets} tickets")
    
    return rolling_tickets

def test_baseline_canonical_mapping():
    """Test that baseline IDs are correctly canonicalized"""
    
    # Create temporary directory with test JSON
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test baseline JSON with variant IDs
        baseline_data = {
            "version": "0.1.4",
            "chronic_data": {
                "existing_chronics": {
                    "chronic_consistent": [
                        "091NOID1143035717419_889599",  # Will canonicalize to 091NOID1143035717419
                        "500335805-CH1",                # Will canonicalize to 500335805
                        "SR216187"                      # Already canonical
                    ],
                    "chronic_inconsistent": [
                        "091NOID1143035717849_889621",  # Will canonicalize to 091NOID1143035717849
                        "LD017936 / FRANFRT-SINGAPOR", # Will canonicalize to LD017936
                    ],
                    "media_chronics": [
                        "VID-1583",  # Should stay VID-1583
                        "VID-1597"   # Should stay VID-1597
                    ]
                }
            }
        }
        
        # Write baseline JSON
        baseline_file = temp_path / "chronic_summary_May_2025.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        # Test baseline loading with canonical mapping
        builder = ChronicReportBuilder()
        baseline_status, baseline_ids = builder.load_baseline_status(temp_dir)
        
        # Verify canonical mapping worked
        expected_mappings = {
            '091NOID1143035717419': 'Consistent',
            '500335805': 'Consistent', 
            'SR216187': 'Consistent',
            '091NOID1143035717849': 'Inconsistent',
            'LD017936': 'Inconsistent',
            'VID-1583': 'Media Chronic',
            'VID-1597': 'Media Chronic'
        }
        
        for canonical, expected_status in expected_mappings.items():
            assert canonical in baseline_status, f"Missing canonical ID: {canonical}"
            assert baseline_status[canonical] == expected_status, f"Wrong status for {canonical}: got {baseline_status[canonical]}, expected {expected_status}"
        
        # Verify all canonical IDs are in the set
        assert baseline_ids == set(expected_mappings.keys())
        
        print("✅ Baseline canonical mapping test passed!")
        print(f"   Mapped {len(baseline_status)} legacy circuits to canonical form")
        
        return baseline_status

def test_hybrid_classification_with_canonicals():
    """Test hybrid classification using canonical IDs"""
    
    # Create test data with ID variants
    test_data = pd.DataFrame({
        'Config Item Name': [
            '091NOID1143035717419_889599',  # Legacy consistent (variant)
            '091NOID1143035717419_889621',  # Same canonical as above
            '091NOID1143035717849_889621',  # Legacy inconsistent
            'TESTCIRCUIT7',                 # New circuit, high tickets (no underscores)
            'TESTCIRCUIT4'                  # New circuit, low tickets (no underscores)
        ],
        'Inc Resolved At (Month / Year)': [
            'June 2025',
            'June 2025',
            'June 2025',
            'June 2025', 
            'June 2025'
        ],
        'Distinct count of Inc Nbr': [
            5,  # 091NOID variant 1
            3,  # 091NOID variant 2 (same canonical)
            2,  # Different 091NOID circuit
            7,  # TESTCIRCUIT7 (should be consistent ≥6)
            4   # TESTCIRCUIT4 (should be inconsistent <6)
        ]
    })
    
    # Add canonical IDs
    test_data['canonical_id'] = test_data['Config Item Name'].apply(canonical_id)
    
    # Mock baseline status (canonical IDs)
    baseline_status = {
        '091NOID1143035717419': 'Consistent',   # Covers both variants
        '091NOID1143035717849': 'Inconsistent'
    }
    
    # Test hybrid classification logic
    CONSISTENT_THRESHOLD = 6
    test_circuits = ['091NOID1143035717419_889599', '091NOID1143035717849_889621', 'TESTCIRCUIT7', 'TESTCIRCUIT4']
    
    classifications = {}
    
    for circuit_id in test_circuits:
        canonical = canonical_id(circuit_id)
        rolling_tickets = get_rolling_ticket_total(canonical, test_data)
        
        # Apply hybrid logic
        if canonical in baseline_status:
            # Legacy circuit - frozen status
            status = baseline_status[canonical].lower()
        else:
            # New circuit - ticket-based
            status = 'consistent' if rolling_tickets >= CONSISTENT_THRESHOLD else 'inconsistent'
        
        classifications[circuit_id] = {
            'canonical': canonical,
            'tickets': rolling_tickets,
            'status': status
        }
    
    # Verify results
    # 091NOID variants should aggregate to 8 tickets (5+3) but stay consistent (legacy frozen)
    assert classifications['091NOID1143035717419_889599']['tickets'] == 8  # 5+3 aggregated
    assert classifications['091NOID1143035717419_889599']['status'] == 'consistent'  # Legacy frozen
    
    # Different 091NOID circuit with 2 tickets but legacy inconsistent status
    assert classifications['091NOID1143035717849_889621']['tickets'] == 2
    assert classifications['091NOID1143035717849_889621']['status'] == 'inconsistent'  # Legacy frozen
    
    # New circuits based on tickets
    assert classifications['TESTCIRCUIT7']['tickets'] == 7
    assert classifications['TESTCIRCUIT7']['status'] == 'consistent'  # ≥6 tickets
    
    assert classifications['TESTCIRCUIT4']['tickets'] == 4  
    assert classifications['TESTCIRCUIT4']['status'] == 'inconsistent'  # <6 tickets
    
    print("✅ Hybrid classification with canonicals test passed!")
    for circuit, data in classifications.items():
        print(f"   {circuit} ({data['canonical']}) -> {data['tickets']} tickets, {data['status']}")
    
    return classifications

def test_edge_cases():
    """Test edge cases for canonical ID extraction"""
    
    edge_cases = [
        # Complex cases
        ("ABC123-DEF/GHI_JKL", "ABC123", "Multiple delimiters - hyphen wins (≥3 digits)"),
        ("ABC12-DEF_GHI", "ABC12-DEF", "Underscore wins over hyphen (<3 digits)"),
        ("VID-1583-EXTRA", "VID-1583", "Split on second hyphen with ≥3 digits"),
        ("   TRIMMED   ", "TRIMMED", "Whitespace handling"),
        ("NO_DELIMITERS", "NO", "Underscore split"),
        ("JUST-HYPHEN", "JUST-HYPHEN", "Hyphen after letters - no split"),
        ("123456-SPLIT", "123456", "Hyphen after exactly 6 digits"),
        ("12-NOSPLIT", "12-NOSPLIT", "Hyphen after only 2 digits"),
    ]
    
    for input_id, expected, description in edge_cases:
        result = canonical_id(input_id.strip())
        assert result == expected, f"Edge case failed: {description} - Input: '{input_id}' -> Expected: '{expected}', Got: '{result}'"
        print(f"✅ {description}: '{input_id.strip()}' -> '{result}'")
    
    print("✅ All edge case tests passed!")

if __name__ == "__main__":
    print("🧪 Testing canonical ID normalization v0.1.5")
    print("=" * 60)
    
    # Test 1: Canonical ID extraction
    test_canonical_id_extraction()
    
    print("\n" + "=" * 60)
    
    # Test 2: 091NOID aggregation fix
    aggregated_tickets = test_091noid_aggregation()
    
    print("\n" + "=" * 60)
    
    # Test 3: Baseline canonical mapping
    baseline_status = test_baseline_canonical_mapping()
    
    print("\n" + "=" * 60)
    
    # Test 4: Hybrid classification with canonicals
    classifications = test_hybrid_classification_with_canonicals()
    
    print("\n" + "=" * 60)
    
    # Test 5: Edge cases
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("🎉 All canonical ID normalization tests completed successfully!")
    print(f"Key results:")
    print(f"  ✅ 091NOID variants properly aggregate to {aggregated_tickets} tickets")
    print(f"  ✅ {len(baseline_status)} baseline circuits canonicalized")
    print(f"  ✅ {len(classifications)} circuits classified using hybrid logic")
    print(f"  ✅ VID- circuits preserved without incorrect splitting")