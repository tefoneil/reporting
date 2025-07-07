#!/usr/bin/env python3
"""
Demo script to show the power of chart-based trend analysis
Creates mock data to demonstrate all the different insights
"""

import json
from pathlib import Path
from datetime import datetime

def create_demo_data():
    """Create demo data showing various trend scenarios"""
    
    # Create May data (baseline)
    may_data = {
        "version": "0.1.5-patch1",
        "consistency_mode": "hybrid",
        "chronic_data": {
            "total_chronic_circuits": 25,
            "media_chronics": 11
        },
        "metrics": {
            "total_chronic_circuits": 25,
            "media_chronics": 11,
            "new_chronic_count": 1,
            "total_providers": 11,
            "top5_tickets": {
                "CIRCUIT_A": 45,
                "CIRCUIT_B": 38,
                "CIRCUIT_C": 32,
                "CIRCUIT_D": 28,
                "CIRCUIT_E": 25
            },
            "top5_cost": {
                "CIRCUIT_X": 25000,
                "CIRCUIT_Y": 22000,
                "CIRCUIT_Z": 18500,
                "CIRCUIT_A": 16000,
                "CIRCUIT_W": 15200
            },
            "bottom5_availability": {
                "CIRCUIT_P": 75.2,
                "CIRCUIT_Q": 78.8,
                "CIRCUIT_R": 81.5,
                "CIRCUIT_S": 83.2,
                "CIRCUIT_T": 85.1
            },
            "bottom5_mtbf": {
                "CIRCUIT_M": 1.2,
                "CIRCUIT_N": 2.8,
                "CIRCUIT_O": 3.4,
                "CIRCUIT_P": 4.1,
                "CIRCUIT_Q": 4.7
            }
        },
        "generated_at": "2025-07-06T10:00:00.000000"
    }
    
    # Create June data (with dramatic changes for demo)
    june_data = {
        "version": "0.1.5-patch1",
        "consistency_mode": "hybrid", 
        "chronic_data": {
            "total_chronic_circuits": 28,  # +3 circuits
            "media_chronics": 11
        },
        "metrics": {
            "total_chronic_circuits": 28,  # +3 circuits (RED FLAG)
            "media_chronics": 11,
            "new_chronic_count": 2,
            "total_providers": 12,
            "top5_tickets": {
                "CIRCUIT_F": 65,    # NEW PROBLEM CIRCUIT! 
                "CIRCUIT_A": 52,    # +7 tickets (degraded)
                "CIRCUIT_B": 38,    # same
                "CIRCUIT_G": 35,    # NEW ENTRY
                "CIRCUIT_C": 28     # -4 tickets (improved, dropped from #3 to #5)
                # CIRCUIT_D and E dropped out of top 5!
            },
            "top5_cost": {
                "CIRCUIT_NEW": 31000,  # NEW HIGH-COST CIRCUIT!
                "CIRCUIT_X": 27500,    # +$2500 increase
                "CIRCUIT_Y": 22000,    # same
                "CIRCUIT_Z": 18500,    # same
                "CIRCUIT_H": 17800     # NEW ENTRY
                # CIRCUIT_A and W improved out of top 5!
            },
            "bottom5_availability": {
                "CIRCUIT_P": 72.1,     # -3.1% MAJOR DEGRADATION
                "CIRCUIT_WORST": 74.5, # NEW WORST PERFORMER
                "CIRCUIT_Q": 77.2,     # -1.6% degraded
                "CIRCUIT_R": 84.8,     # +3.3% MAJOR IMPROVEMENT
                "CIRCUIT_S": 85.5      # +2.3% improved
                # CIRCUIT_T graduated out of worst 5!
            },
            "bottom5_mtbf": {
                "CIRCUIT_M": 1.1,      # -0.1 days worse
                "CIRCUIT_BAD": 1.8,    # NEW RELIABILITY PROBLEM
                "CIRCUIT_N": 2.9,      # +0.1 slight improvement
                "CIRCUIT_O": 3.6,      # +0.2 improved
                "CIRCUIT_P": 4.3       # +0.2 improved
                # CIRCUIT_Q graduated out!
            }
        },
        "generated_at": "2025-07-06T11:00:00.000000"
    }
    
    # Save demo data
    output_dir = Path('./demo_output')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'chronic_summary_May_2025.json', 'w') as f:
        json.dump(may_data, f, indent=2)
    
    with open(output_dir / 'chronic_summary_June_2025.json', 'w') as f:
        json.dump(june_data, f, indent=2)
    
    print("Demo data created in ./demo_output/")
    print("This shows:")
    print("🚨 Red Flags: New high-cost circuit, major availability degradation, +3 chronic circuits")
    print("🎉 Success Stories: Circuits graduating from worst performers")
    print("📊 Ranking Changes: Major position shifts in all categories")
    print("⚠️ New Problems: New worst performers entering top/bottom 5")

if __name__ == "__main__":
    create_demo_data()