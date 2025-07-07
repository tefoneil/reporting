#!/usr/bin/env python3
"""
Test the enhanced trend analysis with demo data
"""

from monthly_builder import ChronicReportBuilder
from pathlib import Path

def test_demo_trends():
    """Test trend analysis with demo data"""
    builder = ChronicReportBuilder()
    
    # Point to demo output directory
    demo_dir = Path('./demo_output')
    
    # Generate trend analysis
    trend_analysis = builder.generate_trend_analysis('June_2025', demo_dir)
    
    # Save and display results
    with open(demo_dir / 'demo_trend_analysis.txt', 'w') as f:
        f.write(trend_analysis)
    
    print("="*80)
    print("ENHANCED CHART-BASED TREND ANALYSIS DEMO")
    print("="*80)
    print(trend_analysis)
    print("="*80)
    print(f"Full analysis saved to: {demo_dir / 'demo_trend_analysis.txt'}")

if __name__ == "__main__":
    test_demo_trends()