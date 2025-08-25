#!/usr/bin/env python3
"""
Archive Guardian - Protects and verifies the golden archive integrity
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime
import sys
import argparse

class ArchiveGuardian:
    def __init__(self, archive_dir='golden_archive'):
        self.archive_dir = Path(archive_dir)
        self.verification_log = []
        
    def calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def verify_month(self, month_dir):
        """Verify integrity of a single month's archive"""
        checksum_file = month_dir / 'CHECKSUM.sha256'
        
        if not checksum_file.exists():
            return False, f"No checksum file found in {month_dir.name}"
        
        # Read expected checksums
        expected_checksums = {}
        with open(checksum_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('  ')
                if len(parts) == 2:
                    expected_checksums[parts[1]] = parts[0]
        
        # Verify each file
        issues = []
        for file_name, expected_hash in expected_checksums.items():
            file_path = month_dir / file_name
            
            if not file_path.exists():
                issues.append(f"Missing file: {file_name}")
                continue
            
            actual_hash = self.calculate_file_hash(file_path)
            if actual_hash != expected_hash:
                issues.append(f"Hash mismatch for {file_name}")
                issues.append(f"  Expected: {expected_hash}")
                issues.append(f"  Actual:   {actual_hash}")
        
        if issues:
            return False, "\n".join(issues)
        
        return True, "All files verified successfully"
    
    def verify_all(self):
        """Verify entire golden archive"""
        print("=" * 60)
        print("GOLDEN ARCHIVE INTEGRITY VERIFICATION")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Archive Directory: {self.archive_dir.absolute()}")
        print()
        
        if not self.archive_dir.exists():
            print("❌ Archive directory does not exist!")
            return False
        
        all_valid = True
        month_dirs = sorted([d for d in self.archive_dir.iterdir() if d.is_dir()])
        
        for month_dir in month_dirs:
            print(f"\n📁 Verifying {month_dir.name}...")
            
            is_valid, message = self.verify_month(month_dir)
            
            if is_valid:
                print(f"   ✅ {message}")
                
                # Show file summary
                files = list(month_dir.glob('*'))
                for f in files:
                    if f.name != 'CHECKSUM.sha256':
                        size = f.stat().st_size
                        print(f"      - {f.name} ({size:,} bytes)")
            else:
                print(f"   ❌ Verification failed!")
                print(f"      {message}")
                all_valid = False
        
        print("\n" + "=" * 60)
        if all_valid:
            print("✅ ARCHIVE INTEGRITY VERIFIED - All files are intact")
        else:
            print("❌ ARCHIVE INTEGRITY COMPROMISED - Some files have been modified!")
            print("\nTo restore from git:")
            print("  git checkout HEAD -- golden_archive/")
        print("=" * 60)
        
        return all_valid
    
    def protect_archive(self):
        """Add protection mechanisms to the archive"""
        
        # Create .gitattributes to mark as binary
        gitattributes = self.archive_dir / '.gitattributes'
        with open(gitattributes, 'w') as f:
            f.write("# Mark all archive files as binary to prevent merging\n")
            f.write("*.txt binary\n")
            f.write("*.json binary\n")
            f.write("*.sha256 binary\n")
            f.write("\n# Prevent modification\n")
            f.write("* -diff\n")
        
        print(f"✅ Created {gitattributes}")
        
        # Create verification script
        verify_script = self.archive_dir / 'verify.sh'
        with open(verify_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Quick verification script\n")
            f.write("cd ..\n")
            f.write("python3 archive_guardian.py --verify\n")
        
        # Make it executable
        import os
        os.chmod(verify_script, 0o755)
        print(f"✅ Created {verify_script}")
    
    def show_summary(self):
        """Show archive summary"""
        print("\n📊 ARCHIVE SUMMARY")
        print("-" * 40)
        
        month_dirs = sorted([d for d in self.archive_dir.iterdir() if d.is_dir()])
        
        for month_dir in month_dirs:
            json_file = month_dir / 'chronic_summary.json'
            if json_file.exists():
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                print(f"\n{month_dir.name}:")
                print(f"  Total Chronic: {data.get('chronic_count', 'N/A')}")
                print(f"  - Consistent: {data.get('chronic_consistent_count', 'N/A')}")
                print(f"  - Inconsistent: {data.get('chronic_inconsistent_count', 'N/A')}")
                print(f"  - New: {data.get('new_chronic_count', 'N/A')}")

def main():
    parser = argparse.ArgumentParser(description='Golden Archive Guardian')
    parser.add_argument('--verify', action='store_true', help='Verify archive integrity')
    parser.add_argument('--protect', action='store_true', help='Add protection mechanisms')
    parser.add_argument('--summary', action='store_true', help='Show archive summary')
    parser.add_argument('--dir', default='golden_archive', help='Archive directory path')
    
    args = parser.parse_args()
    
    guardian = ArchiveGuardian(args.dir)
    
    if args.verify:
        result = guardian.verify_all()
        sys.exit(0 if result else 1)
    elif args.protect:
        guardian.protect_archive()
    elif args.summary:
        guardian.show_summary()
    else:
        # Default: verify and show summary
        guardian.verify_all()
        guardian.show_summary()

if __name__ == "__main__":
    main()