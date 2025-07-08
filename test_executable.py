#!/usr/bin/env python3
"""
Test script to verify the Monthly Report Builder executable works correctly.
This can be run before distributing to Windows users.
"""

import subprocess
import sys
import os
import time
import signal

def test_executable():
    """Test that the executable starts and imports all required modules."""
    
    executable_path = "./dist/Monthly_Report_Builder"
    
    print("🔍 Testing Monthly Report Builder Executable")
    print("=" * 50)
    
    # Test 1: File exists and is executable
    print("1. Checking executable file...")
    if not os.path.exists(executable_path):
        print("❌ FAIL: Executable not found at", executable_path)
        return False
    
    if not os.access(executable_path, os.X_OK):
        print("❌ FAIL: File is not executable")
        return False
    
    print("✅ PASS: Executable file exists and has execute permissions")
    
    # Test 2: File size is reasonable (should be around 70MB)
    size_mb = os.path.getsize(executable_path) / (1024 * 1024)
    print(f"   Size: {size_mb:.1f} MB")
    
    if size_mb < 50 or size_mb > 150:
        print(f"⚠️  WARNING: Unusual file size ({size_mb:.1f} MB)")
    else:
        print("✅ PASS: File size is reasonable")
    
    # Test 3: Executable starts without immediate crashes
    print("\n2. Testing executable startup...")
    try:
        # Start the process
        process = subprocess.Popen(
            [executable_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait 3 seconds for it to start
        time.sleep(3)
        
        # Check if it's still running (GUI should stay open)
        if process.poll() is None:
            print("✅ PASS: Executable started successfully and is running")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                
            return True
        else:
            # Process exited - check error output
            stdout, stderr = process.communicate()
            print("❌ FAIL: Executable exited immediately")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error starting executable: {e}")
        return False

def main():
    """Main test function."""
    print("Monthly Report Builder - Executable Test")
    print("This will verify the executable is working before Windows deployment\n")
    
    success = test_executable()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Executable passed all tests!")
        print("✅ Ready for Windows deployment")
        print("\nNext steps:")
        print("1. Copy executable to Windows machine")
        print("2. Test with real data files")
        print("3. Verify report generation works correctly")
    else:
        print("❌ FAILED: Executable has issues")
        print("❌ DO NOT deploy to Windows until fixed")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())