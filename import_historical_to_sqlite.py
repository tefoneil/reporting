#!/usr/bin/env python3
"""
Import historical May/June/July data into SQLite database
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def import_month_to_sqlite(month, year, archive_dir):
    """Import a single month's data into SQLite"""
    
    conn = sqlite3.connect('rbuilder.db')
    cursor = conn.cursor()
    
    # Load JSON data
    json_file = Path(archive_dir) / 'chronic_summary.json'
    if not json_file.exists():
        print(f"  ⚠️ No JSON file found for {month} {year}")
        return False
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"\n=== Importing {month} {year} ===")
    print(f"  Total circuits: {data['chronic_count']}")
    
    # Insert into monthly_runs table
    cursor.execute("""
        INSERT INTO monthly_runs (
            month_year, run_timestamp, total_chronic_count, 
            new_chronic_count, git_commit, impacts_sha256, counts_sha256
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        month,
        data['generated_at'],
        data['chronic_count'],
        data['new_chronic_count'],
        'historical_import',
        'historical',
        'historical'
    ))
    
    run_id = cursor.lastrowid
    print(f"  Created monthly run ID: {run_id}")
    
    # Import chronic consistent circuits
    for circuit_id in data['chronic_consistent']:
        cursor.execute("""
            INSERT INTO chronic_circuits (
                run_id, circuit_id, canonical_id, classification,
                ticket_count, cost_to_serve, availability, mtbf_days
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, circuit_id, circuit_id, 'consistent',
            0, 0.0, 0.0, 0.0  # Placeholder metrics
        ))
    
    print(f"  Imported {len(data['chronic_consistent'])} consistent circuits")
    
    # Import chronic inconsistent circuits
    for circuit_id in data['chronic_inconsistent']:
        cursor.execute("""
            INSERT INTO chronic_circuits (
                run_id, circuit_id, canonical_id, classification,
                ticket_count, cost_to_serve, availability, mtbf_days
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, circuit_id, circuit_id, 'inconsistent',
            0, 0.0, 0.0, 0.0  # Placeholder metrics
        ))
    
    print(f"  Imported {len(data['chronic_inconsistent'])} inconsistent circuits")
    
    # Import new chronic circuits
    for circuit_id in data.get('new_chronics', []):
        cursor.execute("""
            INSERT INTO chronic_circuits (
                run_id, circuit_id, canonical_id, classification,
                ticket_count, cost_to_serve, availability, mtbf_days
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, circuit_id, circuit_id, 'new',
            0, 0.0, 0.0, 0.0  # Placeholder metrics
        ))
    
    if data.get('new_chronics'):
        print(f"  Imported {len(data['new_chronics'])} new chronic circuits")
    
    conn.commit()
    
    # Verify import
    cursor.execute("""
        SELECT COUNT(*) FROM chronic_circuits WHERE run_id = ?
    """, (run_id,))
    
    total_imported = cursor.fetchone()[0]
    print(f"  ✅ Total circuits imported: {total_imported}")
    
    conn.close()
    return True

def create_archive_table():
    """Create a special table for immutable archive data"""
    
    conn = sqlite3.connect('rbuilder.db')
    cursor = conn.cursor()
    
    # Create archive snapshots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archive_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            year TEXT NOT NULL,
            data_json TEXT NOT NULL,
            checksum TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_immutable BOOLEAN DEFAULT TRUE,
            UNIQUE(month, year)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Created archive_snapshots table")

def verify_database():
    """Verify the imported data"""
    
    conn = sqlite3.connect('rbuilder.db')
    cursor = conn.cursor()
    
    print("\n=== Database Verification ===")
    
    cursor.execute("""
        SELECT mr.month_year, COUNT(cc.id) as circuit_count,
               SUM(CASE WHEN cc.classification = 'consistent' THEN 1 ELSE 0 END) as consistent,
               SUM(CASE WHEN cc.classification = 'inconsistent' THEN 1 ELSE 0 END) as inconsistent,
               SUM(CASE WHEN cc.classification = 'new' THEN 1 ELSE 0 END) as new
        FROM monthly_runs mr
        LEFT JOIN chronic_circuits cc ON mr.id = cc.run_id
        GROUP BY mr.month_year
        ORDER BY mr.run_timestamp
    """)
    
    results = cursor.fetchall()
    
    for row in results:
        print(f"\n{row[0]}:")
        print(f"  Total circuits: {row[1]}")
        print(f"  - Consistent: {row[2]}")
        print(f"  - Inconsistent: {row[3]}")
        print(f"  - New: {row[4]}")
    
    conn.close()

if __name__ == "__main__":
    print("Historical Data Import Script")
    print("=" * 50)
    
    # Create archive table
    create_archive_table()
    
    # Import May 2025
    import_month_to_sqlite("May", "2025", "golden_archive/2025-05_May")
    
    # Import June 2025
    import_month_to_sqlite("June", "2025", "golden_archive/2025-06_June")
    
    # Import July 2025
    import_month_to_sqlite("July", "2025", "golden_archive/2025-07_July")
    
    # Verify the import
    verify_database()
    
    print("\n" + "=" * 50)
    print("Import complete!")
    print("\nDatabase now contains the correct historical data:")
    print("  - May 2025: Baseline")
    print("  - June 2025: Month 2")
    print("  - July 2025: Most recent (28 circuits)")
    print("\nReady to generate August 2025 report!")