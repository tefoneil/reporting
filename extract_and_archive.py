#!/usr/bin/env python3
"""
Extract chronic data from history folders and create golden archive
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
import re

def extract_chronic_data_from_text(text_file_path):
    """Extract chronic circuit data from text file"""
    circuits = {
        'chronic_consistent': [],
        'chronic_inconsistent': [],
        'media_chronics': [],
        'new_chronics': [],
        'total_count': 0
    }
    
    with open(text_file_path, 'r') as f:
        lines = f.readlines()
    
    current_section = None
    for line in lines:
        line = line.strip()
        
        # Detect sections
        if 'CHRONIC CONSISTENT' in line:
            current_section = 'chronic_consistent'
        elif 'CHRONIC INCONSISTENT' in line:
            current_section = 'chronic_inconsistent'
        elif 'MEDIA CHRONICS' in line:
            current_section = 'media_chronics'
        elif 'NEW CHRONIC' in line:
            current_section = 'new_chronics'
        elif 'PERFORMANCE MONITORING' in line or 'TOP 5' in line:
            current_section = None
        
        # Extract circuit IDs
        if current_section and line and line[0].isdigit():
            # Parse lines like "1. 500332738" or "1. 444282783 (Leased Line Circuit)"
            match = re.match(r'\d+\.\s+([A-Z0-9\-_/]+)', line)
            if match:
                circuit_id = match.group(1)
                circuits[current_section].append(circuit_id)
        
        # Get total count
        if 'TOTAL CHRONIC CIRCUITS:' in line:
            match = re.search(r':\s*(\d+)', line)
            if match:
                circuits['total_count'] = int(match.group(1))
    
    return circuits

def create_golden_archive_json(month, year, text_file_path):
    """Create comprehensive JSON for golden archive"""
    
    circuits = extract_chronic_data_from_text(text_file_path)
    
    archive_data = {
        "report_month": month,
        "report_year": year,
        "generated_at": datetime.now().isoformat(),
        "archive_version": "1.0",
        "chronic_count": circuits['total_count'],
        "chronic_consistent_count": len(circuits['chronic_consistent']),
        "chronic_inconsistent_count": len(circuits['chronic_inconsistent']),
        "media_chronic_count": len(circuits['media_chronics']),
        "new_chronic_count": len(circuits['new_chronics']),
        "chronic_consistent": circuits['chronic_consistent'],
        "chronic_inconsistent": circuits['chronic_inconsistent'],
        "media_chronics": circuits['media_chronics'],
        "new_chronics": circuits['new_chronics'],
        "metadata": {
            "source": "Historical archive recovery",
            "data_quality": "Verified from original reports",
            "immutable": True
        }
    }
    
    return archive_data

def generate_checksums(directory):
    """Generate SHA256 checksums for all files in directory"""
    checksums = {}
    
    for file_path in Path(directory).glob('*'):
        if file_path.is_file() and file_path.name != 'CHECKSUM.sha256':
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                checksums[file_path.name] = file_hash
    
    return checksums

def save_checksums(directory, checksums):
    """Save checksums to file"""
    checksum_file = Path(directory) / 'CHECKSUM.sha256'
    
    with open(checksum_file, 'w') as f:
        f.write(f"# SHA256 Checksums - Generated {datetime.now().isoformat()}\n")
        f.write("# DO NOT MODIFY THIS FILE\n\n")
        for filename, hash_value in checksums.items():
            f.write(f"{hash_value}  {filename}\n")

def process_month(month_name, year, source_dir, archive_dir):
    """Process a single month's data"""
    print(f"\n=== Processing {month_name} {year} ===")
    
    # Find chronic list text file
    source_path = Path(source_dir)
    text_files = list(source_path.glob(f'chronic_circuits_list_{month_name}*.txt'))
    
    if not text_files:
        print(f"  ⚠️ No chronic list found for {month_name}")
        return False
    
    text_file = text_files[0]
    print(f"  Found: {text_file.name}")
    
    # Copy text file to archive
    archive_path = Path(archive_dir)
    archive_path.mkdir(parents=True, exist_ok=True)
    
    import shutil
    dest_text = archive_path / 'chronic_circuits_list.txt'
    shutil.copy2(text_file, dest_text)
    print(f"  ✅ Copied chronic list")
    
    # Create JSON archive
    json_data = create_golden_archive_json(month_name, year, text_file)
    json_file = archive_path / 'chronic_summary.json'
    
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"  ✅ Created JSON archive")
    
    # Generate checksums
    checksums = generate_checksums(archive_path)
    save_checksums(archive_path, checksums)
    print(f"  ✅ Generated checksums")
    
    # Show summary
    print(f"  Summary: {json_data['chronic_count']} total circuits")
    print(f"    - Consistent: {json_data['chronic_consistent_count']}")
    print(f"    - Inconsistent: {json_data['chronic_inconsistent_count']}")
    print(f"    - Media: {json_data['media_chronic_count']}")
    print(f"    - New: {json_data['new_chronic_count']}")
    
    return True

if __name__ == "__main__":
    print("Golden Archive Creation Script")
    print("=" * 50)
    
    # Process May 2025
    process_month("May", "2025", "history/2025-05", "golden_archive/2025-05_May")
    
    # Process June 2025
    process_month("June", "2025", "history/2025-06", "golden_archive/2025-06_June")
    
    print("\n" + "=" * 50)
    print("Archive creation complete!")
    print("\nNext step: Extract July data from Word documents")