#!/usr/bin/env python3
"""
Build script for creating Monthly Report Builder executable
Run this script to build the EXE file for distribution
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def main():
    """Build the executable using PyInstaller"""
    
    print("🔨 Building Monthly Report Builder executable...")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"])
        print("✅ PyInstaller installed")
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Removed {folder}/")
    
    # Build the executable
    print("\n🚀 Building executable...")
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",  # Clean cache
            "monthly_builder.spec"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            
            # Check if the executable was created
            exe_path = Path("dist/Monthly_Report_Builder.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executable created: {exe_path}")
                print(f"📏 File size: {size_mb:.1f} MB")
                
                # Test the executable
                print("\n🧪 Testing executable...")
                test_result = subprocess.run([str(exe_path), "--help"], 
                                           capture_output=True, text=True, timeout=10)
                if test_result.returncode == 0 or "usage:" in test_result.stderr:
                    print("✅ Executable test passed")
                else:
                    print("⚠️  Executable test failed - manual testing recommended")
                
            else:
                print("❌ Executable not found in dist/ folder")
                
        else:
            print("❌ Build failed!")
            print("Error output:")
            print(result.stderr)
            return 1
            
    except subprocess.TimeoutExpired:
        print("⏰ Build timed out")
        return 1
    except Exception as e:
        print(f"❌ Build error: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 Build complete!")
    print("\n📁 Next steps:")
    print("   1. Test the executable: dist/Monthly_Report_Builder.exe")
    print("   2. Create GitHub Release")
    print("   3. Upload executable as release asset")
    print("   4. Share download link with your coworker")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())