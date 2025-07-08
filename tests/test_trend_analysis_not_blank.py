#!/usr/bin/env python3
"""
Test for trend analysis completeness
Validates that trend analysis DOC/TXT are generated and contain no placeholder tokens
"""

import pytest
from pathlib import Path
import tempfile
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from monthly_builder import ChronicReportBuilder


def test_trend_analysis_text_not_blank():
    """
    Test that TXT trend analysis has content and no placeholders
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "test_output"
        output_dir.mkdir()
        
        # Create mock previous month data
        history_dir = Path(temp_dir) / "history" / "2025-05"
        history_dir.mkdir(parents=True)
        
        mock_may_data = {
            "metrics": {
                "total_chronic_circuits": 23,
                "top5_tickets": {"CIRCUIT_A": 45, "CIRCUIT_B": 38},
                "top5_cost": {"CIRCUIT_X": 25000, "CIRCUIT_Y": 22000},
                "bottom5_availability": {"CIRCUIT_P": 75.2, "CIRCUIT_Q": 78.8},
                "bottom5_mtbf": {"CIRCUIT_M": 1.2, "CIRCUIT_N": 2.8}
            },
            "chronic_data": {
                "existing_chronics": {
                    "chronic_consistent": ["CIRCUIT_1"],
                    "chronic_inconsistent": ["CIRCUIT_2"]
                }
            }
        }
        
        # Create current month data
        mock_june_data = {
            "metrics": {
                "total_chronic_circuits": 24,
                "new_chronic_count": 1,
                "top5_tickets": {"SR216187": 51, "500334193": 33},
                "top5_cost": {"NTT": 27645, "Telstra": 26324},
                "bottom5_availability": {"LZA010634": 7.4, "INT-BRW1": 12.2},
                "bottom5_mtbf": {"PCCW": 1.8, "500334193": 2.7}
            },
            "chronic_data": {
                "existing_chronics": {
                    "chronic_consistent": ["CIRCUIT_1", "CIRCUIT_3"],
                    "chronic_inconsistent": ["CIRCUIT_2"]
                }
            }
        }
        
        # Save mock data files
        with open(history_dir / "chronic_summary_May_2025.json", 'w') as f:
            json.dump(mock_may_data, f)
            
        with open(output_dir / "chronic_summary_June.json", 'w') as f:
            json.dump(mock_june_data, f)
        
        # Test trend analysis generation
        builder = ChronicReportBuilder()
        
        # Change working directory temporarily for history lookup
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            trend_analysis = builder.generate_trend_analysis("June", output_dir)
        finally:
            os.chdir(original_cwd)
        
        # Validate content
        assert len(trend_analysis) > 0, "Trend analysis should not be empty"
        assert len(trend_analysis) > 100, "Trend analysis should have substantial content"
        
        # Check for required sections
        assert "NETWORK HEALTH OVERVIEW" in trend_analysis, "Should contain network health section"
        assert "TOP TICKET GENERATORS" in trend_analysis, "Should contain ticket analysis"
        assert "COST TO SERVE" in trend_analysis, "Should contain cost analysis"
        assert "AVAILABILITY PERFORMANCE" in trend_analysis, "Should contain availability analysis"
        assert "RELIABILITY (MTBF)" in trend_analysis, "Should contain MTBF analysis"
        
        # Check no placeholder tokens remain (but "Improved Circuits:" section header is OK)
        prohibited_tokens = ["PLACEHOLDER", "TODO", "FIXME", "TBD", "Improved Circuit placeholder"]
        for token in prohibited_tokens:
            assert token not in trend_analysis, f"Should not contain placeholder token: {token}"
        
        # The section header "Improved Circuits:" is acceptable
        assert "🎉 Improved Circuits:" in trend_analysis, "Should contain improved circuits section"
        
        print(f"✅ Trend analysis generated successfully ({len(trend_analysis)} characters)")
        print("✅ All required sections present")
        print("✅ No placeholder tokens found")


def test_trend_analysis_word_generation():
    """
    Test that Word document trend analysis is generated
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "test_output"
        output_dir.mkdir()
        
        # Create minimal trend analysis content
        trend_content = """# MONTHLY PERFORMANCE TREND ANALYSIS
## Test Month Analysis
This is a test trend analysis with sufficient content."""
        
        trend_file = output_dir / "monthly_trend_analysis_Test.txt"
        with open(trend_file, 'w') as f:
            f.write(trend_content)
        
        # Test Word document generation
        builder = ChronicReportBuilder()
        word_output = builder.generate_trend_analysis_word("Test", output_dir)
        
        # Check that Word file was created
        assert word_output is not None, "Word output path should be returned"
        assert word_output.exists(), "Word document should be created"
        assert word_output.suffix == '.docx', "Should be a Word document"
        
        print(f"✅ Word document created: {word_output}")


def test_trend_analysis_handles_missing_data():
    """
    Test that trend analysis handles missing previous month data gracefully
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        
        builder = ChronicReportBuilder()
        
        # Test with no history data
        trend_analysis = builder.generate_trend_analysis("June", output_dir)
        
        # Should return informative message, not crash
        assert ("No previous month data available" in trend_analysis or 
                "Current month data not found" in trend_analysis)
        assert len(trend_analysis) > 0
        
        print("✅ Gracefully handles missing data")


if __name__ == "__main__":
    test_trend_analysis_text_not_blank()
    test_trend_analysis_word_generation()
    test_trend_analysis_handles_missing_data()
    print("🎉 All trend analysis tests passed!")