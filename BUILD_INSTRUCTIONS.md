# Build Instructions - Creating the Executable

## 🔨 **For Developers: How to Build the EXE**

This document explains how to create the standalone executable from the Python source code.

---

## 📋 **Prerequisites**

### **Required Software:**
- Python 3.8+ installed
- All dependencies from `requirements.txt`
- PyInstaller 5.0+

### **Required Files:**
- `monthly_builder.py` (main application)
- `utils.py`, `analyze_data.py` (supporting modules)  
- `requirements.txt` (dependencies)
- All files in `docs/` folder (data files)

---

## 🚀 **Quick Build Process**

### **Method 1: Using Build Script (Recommended)**
```bash
python build_exe.py
```

### **Method 2: Manual PyInstaller Command**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Monthly_Report_Builder" monthly_builder.py
```

### **Method 3: Using Spec File**
```bash
pyinstaller monthly_builder.spec
```

---

## ⚙️ **Build Configuration Details**

### **PyInstaller Options Explained:**
- `--onefile`: Creates single executable (not folder)
- `--windowed`: GUI mode (no console window)
- `--name`: Custom executable name
- `--add-data`: Include additional data files
- `--icon`: Add custom icon (optional)

### **Spec File Configuration:**
The `monthly_builder.spec` file includes:
- Hidden imports for GUI libraries
- Data file inclusions
- Size optimization settings
- Version information

---

## 📦 **Output Files**

### **After Successful Build:**
```
dist/
├── Monthly_Report_Builder.exe     # Windows executable
├── Monthly_Report_Builder.app/    # macOS app bundle (Mac only)
└── Monthly_Report_Builder         # Unix executable
```

### **File Sizes:**
- **Windows EXE:** ~50-80MB
- **macOS App:** ~70-100MB  
- **Linux Binary:** ~60-90MB

---

## 🧪 **Testing the Executable**

### **Basic Functionality Test:**
1. Double-click the executable
2. GUI should open without errors
3. Try file selection dialogs
4. Test report generation with sample data

### **Advanced Testing:**
1. Test with real monthly data files
2. Verify all charts generate correctly
3. Check Word document output formatting
4. Validate trend analysis functionality

---

## 📤 **Distribution Strategy**

### **GitHub Releases (Recommended):**
1. Create new release tag (e.g., `v0.1.9-rc10`)
2. Upload executable as release asset
3. Include release notes and download instructions
4. Link to `README_EXECUTABLE.md` for users

### **File Size Considerations:**
- EXE files are too large for standard git repository
- Use GitHub Releases or Git LFS for binary storage
- Consider creating installer package for professional distribution

---

## 🔧 **Troubleshooting Build Issues**

### **Common Problems:**

**"Module not found" errors:**
```bash
# Add missing imports to spec file hiddenimports
hiddenimports=['missing_module_name']
```

**Large file size:**
```bash
# Use excludes to remove unnecessary packages
excludes=['tkinter.test', 'test', 'unittest']
```

**GUI doesn't work:**
```bash
# Ensure windowed mode and GUI dependencies
--windowed --add-data "path/to/gui/files;."
```

**Missing data files:**
```bash
# Add data files to spec file
datas=[('docs/*.json', 'docs')]
```

---

## 🎯 **Platform-Specific Notes**

### **Windows:**
- Creates `.exe` executable
- May trigger antivirus warnings (false positive)
- Requires Visual C++ redistributables on target machines

### **macOS:**
- Creates `.app` bundle for GUI
- May require code signing for distribution
- Users might need to allow in Security preferences

### **Linux:**
- Creates standard binary executable
- May require additional system libraries
- Test on target distribution before deploying

---

## 📋 **Version Management**

### **Update Version Info:**
1. Edit `version_info.txt` for Windows version details
2. Update version strings in spec file
3. Update documentation with new version number
4. Create corresponding git tag

### **Release Process:**
1. Test all functionality thoroughly
2. Build executable on target platform
3. Create GitHub release with detailed notes
4. Update download links in documentation

---

## 💡 **Optimization Tips**

### **Reduce File Size:**
- Use `--exclude-module` for unused packages
- Remove test/development dependencies
- Consider UPX compression (use cautiously)

### **Improve Performance:**
- Use `--onedir` for faster startup (multiple files)
- Optimize imports in Python code
- Remove unnecessary data files

### **Professional Distribution:**
- Add custom icon with `--icon`
- Include version information
- Create installer with NSIS or similar
- Add digital signatures for security

---

*Build system tested with Python 3.12, PyInstaller 6.14.2 on macOS, Windows 10/11, and Ubuntu 20.04+*