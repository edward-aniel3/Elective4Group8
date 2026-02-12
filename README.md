# Image Processing System

> **ELEC 4 — Midterm Project | DevOps & CI/CD Pipeline**

An automated image processing system powered by GitHub Actions. Upload images to the repository and get 6 processed outputs automatically — no local setup required. Features automated CI/CD pipeline with 4 image processing modules running in the cloud.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.7%2B-green)
![License](https://img.shields.io/badge/License-Educational-orange)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-brightgreen)

---

## Table of Contents

- [Features](#features)
- [How to Use (Remote Processing)](#how-to-use-remote-processing)
- [CI Pipeline](#ci-pipeline)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Team Roles](#team-roles)
- [DevOps Concepts Demonstrated](#devops-concepts-demonstrated)

---

## Features

- 🤖 **Fully Automated Cloud Processing** — Upload images, get results automatically
- 🔵 **Background Remover** — HSV Analysis + GrabCut Algorithm
- 🟢 **Minecraft Filter** — Color quantization with face detection (Steve/Alex overlay)
- 🟣 **Mosaic Tile Effect** — Retro block-art aesthetic
- 🟠 **Puzzle Shuffle** — Creates 3 difficulty levels (Easy, Medium, Hard)
- ⚡ **Zero Local Setup** — Process images directly through GitHub
- 📦 **Batch Processing** — Handle multiple images simultaneously
- 📊 **Real-time Monitoring** — View progress in GitHub Actions tab

---

## How to Use (Remote Processing)

### Step 1: Upload Images

**Option A: Via GitHub Website**
1. Go to your repository on GitHub
2. Navigate to the `input/` folder
3. Click **Add file** → **Upload files**
4. Upload your image(s) (`.png`, `.jpg`, `.jpeg`, `.bmp`)
5. Commit to `main` or `development` branch

**Option B: Via Command Line**
```bash
# Clone the repository (first time only)
git clone https://github.com/YOUR_USERNAME/Elective4Group8.git
cd Elective4Group8

# Add your images
cp /path/to/your/image.png input/

# Commit and push
git add input/
git commit -m "Add images for processing"
git push origin main
```

### Step 2: Automatic Processing

GitHub Actions automatically:
- ✅ Detects your images
- ✅ Processes through all 4 modules
- ✅ Creates 6 output files per image
- ✅ Commits results back to repository
- ⏱️ Takes ~2-3 minutes

### Step 3: Get Results

```bash
# Pull the processed images
git pull origin main
```

**Output Structure:**
```
output/
├── background_removed/
│   └── your-image_bg_removed.png
├── minecraft/
│   └── your-image_minecraft.png
├── mosaic/
│   └── your-image_mosaic.png
└── puzzle/
    ├── your-image_puzzle_easy.png
    ├── your-image_puzzle_medium.png
    └── your-image_puzzle_hard.png
```

### Monitor Progress

1. Go to repository → **Actions** tab
2. Click latest "Auto-Process Input Images" workflow
3. View real-time logs and processing status
4. Green checkmark = Success! 🎉

---

## CI Pipeline

This project uses **GitHub Actions** for Continuous Integration and automated image processing.

**Workflow:** `.github/workflows/ci.yml`

### Automated Image Processing Job

On every push to `main` or `development`, the pipeline automatically:

1. ✅ Checks out the repository
2. ✅ Sets up Python 3.10 and installs dependencies
3. ✅ Detects images in the `input/` folder
4. ✅ Processes each image through **all 4 modules**:
   - 🔵 Background Remover
   - 🟢 Minecraft Filter (with face detection)
   - 🟣 Mosaic Tile Effect
   - 🟠 Puzzle Shuffle (Easy, Medium, Hard)
5. ✅ Saves outputs to organized `output/` subdirectories
6. ✅ Automatically commits and pushes results back to the repository

**View results:** Go to the repository → **Actions** tab → click "Auto-Process Input Images" workflow run.

A green checkmark means processing succeeded. Click any run to see:
- Which images were processed
- Output file paths and sizes
- Complete processing logs

### Supported Image Formats

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- Bitmap (`.bmp`)

**Note:** Images are case-insensitive. Both `Image.PNG` and `image.png` work.

---

## Project Structure

```
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions CI/CD pipeline
│
├── input/                      # Source images (place images here)
│   └── .gitkeep                # Keeps folder in git when empty
│
├── output/                     # Processed images (auto-generated)
│   ├── background_removed/     # Background removal outputs
│   ├── minecraft/              # Minecraft filter outputs
│   ├── mosaic/                 # Mosaic tile outputs
│   └── puzzle/                 # Puzzle shuffle outputs
│
├── reference-imgs/             # Assets for image processing
│   ├── steve_face.png          # Minecraft Steve face overlay
│   └── alex_face.png           # Minecraft Alex face overlay
│
├── src/elective4group8/        # Source code package
│   ├── __init__.py
│   ├── background_remover.py   # Module 1: Background removal
│   ├── minecraft_filter.py     # Module 2: Minecraft filter + face overlay
│   ├── mosaic_tile_effect.py   # Module 3: Mosaic tile effect
│   └── puzzle_shuffle.py       # Module 4: Puzzle shuffle game
│
├── tests/                      # Test suite
│   ├── test_background_remover.py
│   ├── test_minecraft_filter.py
│   ├── test_mosaic_tile_effect.py
│   └── test_puzzle_shuffle.py
│
├── main.py                     # Main menu entry point (GUI)
├── setup.py                    # Package setup configuration
├── requirements.txt            # Python dependencies
│
├── SETUP_FIRST.bat             # One-time setup (installs dependencies)
├── RUN_APP.bat                 # Launch the GUI application
├── BUILD_EXECUTABLE.bat        # Build standalone .exe (optional)
│
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Programming language |
| **OpenCV** | Computer vision and image processing |
| **NumPy** | Numerical array operations |
| **Pillow** | Image manipulation and GUI display |
| **Tkinter** | Cross-platform GUI framework |
| **pytest** | Unit testing framework |
| **GitHub Actions** | CI/CD automation |
| **Git** | Version control |

---

## Team Roles

| Role | Responsibility |
|------|----------------|
| Image Processing Lead | Image processing algorithms and filters |
| DevOps Engineer | GitHub repository, CI pipeline, and workflow |
| Tester | Automated test cases with pytest |
| Documenter / Presenter | Documentation, README, and presentation |

---

## DevOps Concepts Demonstrated

- **Continuous Integration (CI):** Automated pipeline runs on every push
- **Continuous Deployment (CD):** Automatically processes images and commits results
- **Automated Testing:** Unit tests validating all core functions
- **Version Control:** Full commit history with timestamps via Git/GitHub
- **Collaboration:** Branch-based workflow with pull requests and code review
- **Reproducibility:** `requirements.txt` ensures consistent environments
- **Monitoring:** GitHub Actions tab provides transparent pipeline status
- **Infrastructure as Code:** CI/CD pipeline defined in `.github/workflows/ci.yml`
- **Event-Driven Automation:** Processing triggered automatically by git push events
