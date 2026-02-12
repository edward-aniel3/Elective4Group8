# 🚀 Quick Start Guide - Image Processing System

## 📋 Overview

This project can be used in two ways:
1. **Development Mode** - Run with Python (for development/testing)
2. **Standalone Executable** - Windows .exe (for distribution)

---

## 🔧 Development Mode (Python)

### First Time Setup

1. **Run Setup Script**
   ```
   Double-click: SETUP_FIRST.bat
   ```
   This will:
   - Check Python installation
   - Create virtual environment
   - Install all dependencies

2. **Run the Application**
   ```
   Double-click: RUN_APP.bat
   ```

### Running Tests

```bash
# Activate virtual environment first
venv\Scripts\activate.bat

# Run all tests
pytest

# Run specific test file
pytest test_background_remover.py
```

---

## 📦 Building Standalone Executable

### Build the .exe

1. **Complete First Time Setup** (if not done)
   ```
   Double-click: SETUP_FIRST.bat
   ```

2. **Build Executable**
   ```
   Double-click: BUILD_EXECUTABLE.bat
   ```
   This will:
   - Install PyInstaller
   - Clean previous builds
   - Create standalone .exe in `dist/` folder
   - Takes 5-10 minutes

3. **Package for Distribution** (Optional)
   ```
   Double-click: PACKAGE_EXECUTABLE.bat
   ```
   Creates a portable ZIP package with:
   - ImageProcessingSystem.exe
   - Required folders (input/output)
   - README and launcher script

### Run the Executable

After building:
```
Double-click: dist\ImageProcessingSystem.exe
```

Or use the launcher:
```
Copy RUN_EXECUTABLE.bat to dist/ folder
Double-click: RUN_EXECUTABLE.bat
```

---

## 📁 Project Structure

```
Elec4Group8/
├── main.py                      # Main application entry point
├── background_remover.py        # Background removal module
├── puzzle_shuffle.py            # Puzzle shuffle module
├── minecraft_filter.py          # Minecraft filter module
├── mosaic_tile_effect.py        # Mosaic effect module
├── path_helper.py               # Path utilities for exe compatibility
│
├── test_*.py                    # Unit tests
├── requirements.txt             # Python dependencies
│
├── SETUP_FIRST.bat              # Initial setup script
├── RUN_APP.bat                  # Run in development mode
├── BUILD_EXECUTABLE.bat         # Build standalone .exe
├── PACKAGE_EXECUTABLE.bat       # Package for distribution
├── RUN_EXECUTABLE.bat           # Run the built .exe
│
├── ImageProcessingSystem.spec   # PyInstaller configuration
├── EXECUTABLE_README.md         # Documentation for exe distribution
│
├── input/                       # Source images folder
├── output/                      # Processed images folder
└── venv/                        # Virtual environment (created by setup)
```

---

## 🎨 Using the Application

### 1. Launch the Application
- Development: Run `RUN_APP.bat`
- Executable: Run `ImageProcessingSystem.exe`

### 2. Main Menu
Select one of 4 modules:
- **Background Remover** - Remove image backgrounds
- **Puzzle Shuffle** - Create image puzzles
- **Minecraft Filter** - Minecraft-style pixel art
- **Mosaic Tile Effect** - Retro block art

### 3. Process Images
Each module has:
- **Load Image** - Select source image
- **Process** - Apply the effect
- **Save** - Export processed image
- **Back to Menu** - Return to main menu

---

## 🔍 Troubleshooting

### Development Mode Issues

**"Python not found"**
- Install Python from https://www.python.org
- Check "Add Python to PATH" during installation

**"Failed to install packages"**
- Check internet connection
- Try running setup again
- Manual install: `pip install opencv-python numpy Pillow pytest pyinstaller`

**"Virtual environment not found"**
- Run `SETUP_FIRST.bat` before `RUN_APP.bat`

### Executable Build Issues

**"Build failed"**
- Make sure setup completed successfully
- Check disk space (need ~1GB free)
- Try cleaning: Delete `build/` and `dist/` folders, run build again

**"Module not found" error in exe**
- Make sure all path fixes are applied
- Check `ImageProcessingSystem.spec` includes all modules

### Runtime Issues

**"No images found"**
- Place images in the `input/` folder
- Supported formats: JPG, PNG, BMP

**"Cannot save image"**
- Check `output/` folder exists and is writable
- Run as Administrator if needed

**Application freezes**
- Large images may take time to process
- Check CPU/RAM usage in Task Manager

---

## 💡 Tips

### For Development
- Use `pytest` to run tests before building
- Check `compilation_notes.txt` for detailed info
- Modify modules in `*.py` files
- Test changes with `RUN_APP.bat` before building exe

### For Distribution
- Build exe creates a ~150-250MB file (includes all dependencies)
- Exe is portable - copy anywhere on Windows
- Include `input/` and `output/` folders with the exe
- First run may take a few seconds (unpacking)
- No Python installation needed on target PC

### For Performance
- Resize large images before processing (>5000px may be slow)
- Close other applications when processing
- Use SSD for faster load times

---

## 📝 System Requirements

### Development Mode
- **OS**: Windows 7/8/10/11
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for venv + dependencies

### Executable Mode
- **OS**: Windows 7/8/10/11 (64-bit)
- **RAM**: 2GB minimum, 4GB recommended  
- **Disk**: 300MB for exe + processed images
- **No Python required**

---

## 🆘 Getting Help

1. Check error messages in console
2. Review `WORKFLOW_GUIDE.txt`
3. Check `compilation_notes.txt` for known issues
4. Run tests: `pytest -v` to identify problems
5. Verify all files are present and unmodified

---

## ✅ Verification Checklist

Before distributing the executable:

- [ ] SETUP_FIRST.bat completed successfully
- [ ] All tests pass (`pytest`)
- [ ] RUN_APP.bat works in development mode
- [ ] BUILD_EXECUTABLE.bat completed without errors
- [ ] ImageProcessingSystem.exe launches
- [ ] All 4 modules load and work
- [ ] Images can be loaded, processed, and saved
- [ ] Tested on a clean Windows PC (no Python)

---

**ELECTIVE 4 - Midterm Project**  
**DevOps & CI Pipeline**
