#!/usr/bin/env python3
"""
Clean test data from SQLite database and prepare for real reports
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def clean_test_data():
    """Remove test August/September data from database"""
    conn = sqlite3.connect('rbuilder.db')
    cursor = conn.cursor()
    
    print("=== Cleaning Test Data from Database ===")
    
    # First, show what we're about to delete
    cursor.execute("SELECT id, month_year, run_timestamp FROM monthly_runs WHERE month_year IN ('August', 'September')")
    test_runs = cursor.fetchall()
    
    if test_runs:
        print(f"\nFound {len(test_runs)} test runs to remove:")
        for run in test_runs:
            print(f"  - Run ID {run[0]}: {run[1]} (created {run[2]})")
        
        # Delete related chronic_circuits data first (foreign key constraint)
        run_ids = [run[0] for run in test_runs]
        placeholders = ','.join('?' * len(run_ids))
        
        cursor.execute(f"DELETE FROM chronic_circuits WHERE run_id IN ({placeholders})", run_ids)
        deleted_circuits = cursor.rowcount
        print(f"\nDeleted {deleted_circuits} test chronic circuit records")
        
        cursor.execute(f"DELETE FROM incident_data WHERE run_id IN ({placeholders})", run_ids)
        deleted_incidents = cursor.rowcount
        print(f"Deleted {deleted_incidents} test incident records")
        
        # Now delete the monthly_runs
        cursor.execute(f"DELETE FROM monthly_runs WHERE id IN ({placeholders})", run_ids)
        deleted_runs = cursor.rowcount
        print(f"Deleted {deleted_runs} test monthly run records")
        
        conn.commit()
        print("\n✅ Test data cleaned successfully")
    else:
        print("\n✅ No test data found - database is clean")
    
    # Show what remains
    cursor.execute("SELECT month_year, COUNT(*) FROM monthly_runs GROUP BY month_year")
    remaining = cursor.fetchall()
    if remaining:
        print("\nRemaining data in database:")
        for month, count in remaining:
            print(f"  - {month}: {count} run(s)")
    else:
        print("\nDatabase is now empty and ready for real data")
    
    conn.close()

def backup_database():
    """Create a backup of the database before modifications"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"rbuilder_backup_{timestamp}.db"
    
    if Path('rbuilder.db').exists():
        shutil.copy2('rbuilder.db', backup_name)
        print(f"\n✅ Database backed up to: {backup_name}")
        return backup_name
    return None

if __name__ == "__main__":
    print("Database Cleanup Script")
    print("=" * 50)
    
    # Create backup first
    backup_file = backup_database()
    
    # Clean test data
    clean_test_data()
    
    print("\n" + "=" * 50)
    print("Cleanup complete!")
    if backup_file:
        print(f"Backup saved as: {backup_file}")
    print("\nDatabase is now ready for importing May/June/July historical data")
    print("and generating the real August 2025 report.")