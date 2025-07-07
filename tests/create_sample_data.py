#!/usr/bin/env python3
"""
Create sample test data for monthly reporting
Generates small synthetic Excel files for testing
"""

import pandas as pd
from pathlib import Path

def create_sample_impacts_data():
    """Create sample impacts crosstab data"""
    data = {
        'Config Item Name': [
            '500335805', '091NOID1143035717849_889621', 'SR216187', 
            'PTH TOK EPL 90030025', 'LD017936', 'IST6022E#2_010G',
            '444089285', '445082297', 'LZA010663', 'VID-1583',
            'CID_TEST_7', 'CID_TEST_4'  # Test circuits for ticket classification
        ],
        'Incident Network-facing Impacted CI Type': [
            'Cirion', 'Tata', 'PCCW', 'Telstra', 'Orange', 
            'Globenet', 'Lumen', 'Lumen', 'Liquid Telecom', 'Slovak Telekom',
            'Test Provider', 'Test Provider'  # Test providers
        ],
        'Outage Duration': [
            7200, 14400, 3600, 10800, 5400,
            18000, 1800, 9000, 12600, 2700,
            3600, 1800  # 1 hour and 0.5 hour outages for test circuits
        ],
        'SUM Outage (Hours)': [
            2.0, 4.0, 1.0, 3.0, 1.5,
            5.0, 0.5, 2.5, 3.5, 0.75,
            1.0, 0.5  # Test circuit outage hours
        ],
        'Cost to Serve (Sum Impact x $60/hr)': [
            120, 240, 60, 180, 90,
            300, 30, 150, 210, 45,
            60, 30  # Test circuit costs
        ],
        'Distinct count of Inc Nbr': [
            2, 4, 1, 3, 1,
            5, 1, 2, 3, 1,
            7, 4  # Key: 7 tickets for CID_TEST_7, 4 tickets for CID_TEST_4
        ]
    }
    
    df = pd.DataFrame(data)
    return df

def create_sample_counts_data():
    """Create sample counts data"""
    data = {
        'Config Item Name': [
            '500335805', '091NOID1143035717849_889621', 'SR216187', 
            'PTH TOK EPL 90030025', 'LD017936', 'IST6022E#2_010G',
            '444089285', '445082297', 'LZA010663', 'VID-1583',
            'CID_TEST_7', 'CID_TEST_4'  # Test circuits for ticket classification
        ],
        'COUNTD Months': [
            3, 3, 2, 3, 2,
            3, 3, 3, 2, 1,
            4, 4  # Test circuits have been chronic for 4 months (existing chronics)
        ]
    }
    
    df = pd.DataFrame(data)
    return df

def main():
    """Generate sample Excel files"""
    script_dir = Path(__file__).parent
    
    # Create impacts file
    impacts_df = create_sample_impacts_data()
    impacts_path = script_dir / "sample_impacts.xlsx"
    impacts_df.to_excel(impacts_path, index=False)
    print(f"Created: {impacts_path}")
    
    # Create counts file
    counts_df = create_sample_counts_data()
    counts_path = script_dir / "sample_counts.xlsx"
    counts_df.to_excel(counts_path, index=False)
    print(f"Created: {counts_path}")
    
    print("Sample data files created successfully!")

if __name__ == "__main__":
    main()