# Image Processing System - Executable Distribution

## 📦 What's Included

This is a **standalone Windows executable** of the Image Processing System. No Python installation required!

### Executable File
- `ImageProcessingSystem.exe` - The main application (standalone, includes all dependencies)

### Required Folders
The application needs these folders in the same directory:
- `input/` - Place your source images here
- `output/` - Processed images are saved here

These folders are created automatically when you first run the app.

## 🚀 How to Run

### Option 1: Double-click
Simply double-click `ImageProcessingSystem.exe`

### Option 2: Use the launcher
Double-click `RUN_EXECUTABLE.bat`

## 🎨 Features

The application includes 4 image processing modules:

1. **Background Remover** - Remove backgrounds using smart HSV analysis and GrabCut
2. **Image Puzzle Shuffle** - Create and solve image puzzles (Easy/Medium/Hard)
3. **Minecraft Filter** - Transform images into Minecraft-style pixel art
4. **Mosaic Tile Effect** - Create retro block-art effects

## 📋 System Requirements

- **OS**: Windows 7/8/10/11 (64-bit)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: ~200MB for the executable + space for your images

## 🔧 Troubleshooting

### Application won't start
- Make sure you extracted all files from the ZIP
- Windows might block the .exe - right-click → Properties → Unblock
- Run as Administrator if needed

### "Missing VCRUNTIME140.dll" error
- Install Microsoft Visual C++ Redistributable:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

### Images not processing
- Check that images are in the `input/` folder
- Supported formats: JPG, PNG, BMP
- Make sure you have write permissions for the `output/` folder

## 📝 Notes

- The first launch may take a few seconds as the executable unpacks
- Large images (>5000px) may take longer to process
- The executable is self-contained and portable - you can copy it anywhere

## 🏗️ Building from Source

If you want to build the executable yourself:

1. Run `SETUP_FIRST.bat` to install dependencies
2. Run `BUILD_EXECUTABLE.bat` to create the .exe
3. Find the executable in `dist\ImageProcessingSystem.exe`

## 📄 License

ELECTIVE 4 - Midterm Project
DevOps & CI Pipeline
