# Image Processing System

> **ELEC 4 — Midterm Project | DevOps & CI Pipeline**

A Python-based image processing application featuring four modules, a unified GUI, automated testing with pytest, and a GitHub Actions CI pipeline. Built to demonstrate DevOps practices including Continuous Integration, version control, and automated testing.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.7%2B-green)
![License](https://img.shields.io/badge/License-Educational-orange)
![Tests](https://img.shields.io/badge/Tests-12%20passed-brightgreen)

---

## Table of Contents

- [Features](#features)
- [Modules](#modules)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [CI Pipeline](#ci-pipeline)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Team Roles](#team-roles)

---

## Features

- Four image processing modules accessible from a single main menu
- Responsive, modern GUI built with Tkinter
- Automated testing with 12 unit tests
- GitHub Actions CI pipeline that runs on every push
- Batch processing support via input/output folders

---

## Modules

| # | Module | Description | Techniques |
|---|--------|-------------|------------|
| 1 | **Background Remover** | Removes image backgrounds automatically or with manual selection | HSV Analysis, GrabCut Algorithm |
| 2 | **Puzzle Shuffle** | Splits images into tiles and shuffles them into a solvable puzzle | Image Tiling, Random Shuffle, Grid Overlay |
| 3 | **Minecraft Filter** | Transforms images into Minecraft-style pixel art with face overlay | Color Quantization, Block Palette Mapping, Face Detection |
| 4 | **Mosaic Tile Effect** | Creates mosaic tile effects with a retro block-art aesthetic | Down-sampling, Nearest-Neighbour Interpolation |

---

## Getting Started

### Prerequisites

- **Windows 7/8/10/11** (64-bit)
- **Python 3.10 or higher** — [Download here](https://www.python.org) (check "Add Python to PATH" during installation)

### Setup & Run

1. **Clone or download the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   cd YOUR_REPO
   ```

2. **Run the setup script** (one-time only):
   ```
   Double-click: batch_scripts/SETUP_FIRST.bat
   ```
   This will check your Python installation, create a virtual environment, and install all required packages automatically.

3. **Launch the application:**
   ```
   Double-click: batch_scripts/RUN_APP.bat
   ```
   The main menu will open with all four modules ready to use.

### Build Standalone Executable (Optional)

If you want a portable `.exe` that runs without Python installed:

1. Complete the setup above first.
2. Double-click `batch_scripts/BUILD_EXECUTABLE.bat` (takes 5–10 minutes).
3. The executable will be created in the `dist/` folder.
4. Double-click `dist\ImageProcessingSystem.exe` to run it on any Windows PC — no Python needed.

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| opencv-python | >= 4.7.0 | Image processing and computer vision |
| numpy | >= 1.23 | Numerical operations |
| Pillow | >= 9.1.0 | Image display and manipulation |
| pytest | >= 7.0.0 | Automated testing |

---

## Usage

### Running the Application

```
Double-click: batch_scripts/RUN_APP.bat
```

The main menu will open. Select any of the four modules to launch it. Each module allows you to:
1. Load an image (from the `input/` folder or via file dialog)
2. Apply the processing effect
3. Save the result to the `output/` folder

### Input / Output

- Place images in the `input/` folder or use the GUI file dialog to load images.
- Processed images are saved to the `output/` folder.

---

## Running Tests

```bash
pytest -v
```

Expected output: **12 passed**.

Each module has its own test file covering core image processing functions.

| Test File | Tests | What It Covers |
|-----------|-------|----------------|
| `test_background_remover.py` | 3 | Image file detection, smart background removal |
| `test_minecraft_filter.py` | 3 | Filter shape, blockification, uniform input |
| `test_mosaic_tile_effect.py` | 3 | Blockify shape, uniform image, block creation |
| `test_puzzle_shuffle.py` | 3 | Shuffle output, determinism, seed variation |

---

## CI Pipeline

This project uses **GitHub Actions** for Continuous Integration.

**Workflow:** `.github/workflows/ci.yml`

On every push or pull request to `main`, the pipeline automatically:

1. Checks out the repository
2. Sets up Python 3.10
3. Installs all dependencies
4. Runs all 12 tests with pytest

**View results:** Go to the repository → **Actions** tab → click any workflow run.

A green checkmark means all tests passed. A red X means something failed — click the run to see detailed logs.

---

## Project Structure

```
Elective4Group8/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
│
├── src/
│   └── elective4group8/        # Main package directory
│       ├── __init__.py         # Package initialization
│       ├── background_remover.py       # Module 1: Background removal
│       ├── puzzle_shuffle.py           # Module 2: Puzzle shuffle game
│       ├── minecraft_filter.py         # Module 3: Minecraft filter + face overlay
│       ├── mosaic_tile_effect.py       # Module 4: Mosaic tile effect
│
├── tests/
│   ├── __init__.py
│   ├── test_background_remover.py  # Tests for Module 1
│   ├── test_puzzle_shuffle.py      # Tests for Module 2
│   ├── test_minecraft_filter.py    # Tests for Module 3
│   └── test_mosaic_tile_effect.py  # Tests for Module 4
│
├── batch_scripts/              # Batch files for setup and execution
│   ├── SETUP_FIRST.bat         # One-time setup (installs dependencies)
│   ├── RUN_APP.bat             # Launch the application
│   ├── RUN_EXECUTABLE.bat      # Run built executable
│   ├── BUILD_EXECUTABLE.bat    # Build standalone .exe (optional)
│   ├── REBUILD_EXECUTABLE.bat  # Rebuild existing .exe
│   ├── PACKAGE_EXECUTABLE.bat  # Package the executable
│   └── VERIFY_ENVIRONMENT.bat  # Verify Python environment
│
├── referenceImages/              # Reference Images
│   ├── steve_face.png            # Minecraft Steve face overlay asset
│   └── alex_face.png             # Minecraft Alex face overlay asset
│
├── input/                      # Source images (place images here)
├── output/                     # Processed images (generated output)
│
├── main.py                     # Main menu entry point
├── setup.py                    # Package setup configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── .git/                       # Git repository
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

- **Continuous Integration (CI):** Automated build and test pipeline on every push
- **Automated Testing:** 12 unit tests validating all core functions
- **Version Control:** Full commit history with timestamps via Git/GitHub
- **Collaboration:** Branch-based workflow with pull requests and code review
- **Reproducibility:** `requirements.txt` ensures consistent environments
- **Monitoring:** GitHub Actions tab provides transparent pipeline status
