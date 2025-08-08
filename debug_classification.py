#!/usr/bin/env python3

import pandas as pd
import json
from pathlib import Path
from utils import canonical_id
from analyze_data import get_rolling_ticket_total

# The 7 circuits that incorrectly moved from inconsistent to consistent
problem_circuits = ['445979698', '445597814', '443832799', '443463817', 'N2864477L', 'FRO2007133508', 'W1E32092']

print("=== DEBUGGING CIRCUIT CLASSIFICATION LOGIC ===")

# Load the current August data files
impacts_df = pd.read_excel('/Users/teffy/Downloads/Impacts by CI Type Crosstab (2) (4).xlsx')
counts_df = pd.read_excel('/Users/teffy/Downloads/Count Months Chronic (4).xlsx')

# Add canonical IDs
impacts_df['canonical_id'] = impacts_df['Config Item Name'].apply(canonical_id)
counts_df['canonical_id'] = counts_df['Config Item Name'].apply(canonical_id)

# Merge the data (simulating what monthly_builder does)
merged_df = pd.merge(impacts_df, counts_df, on='canonical_id', how='outer', suffixes=('_impacts', '_counts'))

# Load frozen baseline
with open('./docs/frozen_legacy_list.json', 'r') as f:
    baseline_data = json.load(f)

# Load most recent historical data to check previous_classifications
search_dirs = [Path('./final_output'), Path('./history')]
chronic_classifications = {}

for search_dir in search_dirs:
    if not search_dir.exists():
        continue
    
    json_files = []
    if search_dir.name == 'history':
        for subdir in search_dir.iterdir():
            if subdir.is_dir():
                json_files.extend(subdir.glob('chronic_summary_*.json'))
    else:
        json_files = list(search_dir.glob('chronic_summary_*.json'))
    
    json_files = sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    if json_files:
        most_recent_file = json_files[0]
        print(f"\nLoading most recent file: {most_recent_file}")
        
        with open(most_recent_file, 'r') as f:
            data = json.load(f)
        
        chronic_data = data.get('chronic_data', {})
        existing_chronics = chronic_data.get('existing_chronics', {})
        
        # Load classifications from most recent file
        for circuit in existing_chronics.get('chronic_consistent', []):
            canonical = canonical_id(circuit)
            chronic_classifications[canonical] = 'consistent'
        
        for circuit in existing_chronics.get('chronic_inconsistent', []):
            canonical = canonical_id(circuit)
            chronic_classifications[canonical] = 'inconsistent'
            
        for circuit in existing_chronics.get('media_chronics', []):
            canonical = canonical_id(circuit)
            chronic_classifications[canonical] = 'media'
        
        new_chronics = chronic_data.get('new_chronics', {})
        for provider_type, circuits in new_chronics.items():
            for circuit in circuits:
                canonical = canonical_id(circuit)
                chronic_classifications[canonical] = 'pending_promotion'
        
        break

print(f"Loaded {len(chronic_classifications)} classifications from historical data")

# Now trace each problem circuit
print("\n=== TRACING EACH PROBLEM CIRCUIT ===")

for circuit in problem_circuits:
    canonical = canonical_id(circuit)
    print(f"\n--- Circuit: {circuit} (canonical: {canonical}) ---")
    
    # Check baseline status
    in_baseline_consistent = circuit in baseline_data['chronic_consistent']
    in_baseline_inconsistent = circuit in baseline_data['chronic_inconsistent']
    print(f"Baseline status: consistent={in_baseline_consistent}, inconsistent={in_baseline_inconsistent}")
    
    # Check historical classification from previous file
    prev_status = chronic_classifications.get(canonical, 'NOT FOUND')
    print(f"Previous classification: {prev_status}")
    
    # Check current ticket count
    rolling_tickets = get_rolling_ticket_total(canonical, merged_df)
    print(f"Current rolling tickets: {rolling_tickets}")
    
    # Determine what SHOULD happen based on the logic
    if prev_status == 'inconsistent':
        print(f"EXPECTED: Should stay inconsistent (line 731 logic)")
        print(f"ACTUAL: Got promoted to consistent - THIS IS THE BUG!")
    elif prev_status == 'consistent':
        print(f"EXPECTED: Should stay consistent")
    elif prev_status == 'pending_promotion':
        if rolling_tickets >= 6:
            print(f"EXPECTED: Should become consistent (new chronic with ≥6 tickets)")
        else:
            print(f"EXPECTED: Should become inconsistent (new chronic with <6 tickets)")
    elif prev_status == 'NOT FOUND':
        print(f"ISSUE: Circuit not found in previous classifications - may be treated as new")
        if canonical in baseline_data['chronic_inconsistent']:
            print(f"But it IS in baseline as inconsistent - this is a lookup problem!")

print(f"\n=== SUMMARY ===")
print(f"Problem: 7 circuits marked as inconsistent in baseline are showing up as consistent")
print(f"Root cause investigation needed in the classification logic chain")