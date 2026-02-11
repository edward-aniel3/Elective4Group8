"""
Image Puzzle Shuffle Generator
==============================
Splits an image into a grid of tiles, shuffles them randomly, and lets
the user solve the puzzle by clicking tiles to swap them.

Difficulty levels:
  - Easy   — 3x3 grid  (9 tiles)
  - Medium — 4x4 grid (16 tiles)
  - Hard   — 5x5 grid (25 tiles)

Image Processing Techniques Used:
  - Image slicing / tiling
  - Random permutation (numpy RNG)
  - Grid-line and numbered overlay rendering
  - Aspect-ratio-aware resizing

Fully responsive UI — adapts to any window size.
"""

import os
import cv2
import numpy as np
import json
import random
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import sys

# ─── Paths ────────────────────────────────────────────────
# PyInstaller compatible path handling
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
INPUT_DIR  = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# ─── Design tokens ────────────────────────────────────────
BG_MAIN    = "#f5ede7"
ACCENT     = "#222"
BTN_BLUE   = "#2196f3"
BTN_ORANGE = "#ff9800"
BTN_RED    = "#f44336"
BTN_GREEN  = "#4caf50"

DIFFICULTY_GRID = {
    "easy":   (3, 3),
    "medium": (4, 4),
    "hard":   (5, 5),
}


# ══════════════════════════════════════════════════════════
#  CORE IMAGE PROCESSING FUNCTIONS
# ══════════════════════════════════════════════════════════

def overlay_grid_and_numbers(img, grid_size, tile_order):
    """Draw grid lines and tile numbers on *img* (copy returned)."""
    img = img.copy()
    h, w = img.shape[:2]
    gh, gw = grid_size
    th, tw = h // gh, w // gw

    for i in range(1, gh):
        cv2.line(img, (0, i * th), (w, i * th), (0, 0, 0), 2)
    for j in range(1, gw):
        cv2.line(img, (j * tw, 0), (j * tw, h), (0, 0, 0), 2)

    font = cv2.FONT_HERSHEY_SIMPLEX
    for idx, tile_num in enumerate(tile_order):
        i, j = divmod(idx, gw)
        cx = j * tw + tw // 2
        cy = i * th + th // 2
        cv2.putText(img, str(tile_num), (cx - 10, cy + 10),
                    font, 1, (0, 0, 255), 2, cv2.LINE_AA)
    return img


def shuffle_image_puzzle(img, grid_size, seed):
    """Return *(shuffled_image, tile_order)* given a grid and a seed."""
    h, w = img.shape[:2]
    gh, gw = grid_size
    th, tw = h // gh, w // gw
    tiles = []
    for i in range(gh):
        for j in range(gw):
            tiles.append(img[i * th:(i + 1) * th,
                             j * tw:(j + 1) * tw])
    order = list(range(len(tiles)))
    random.Random(seed).shuffle(order)
    shuffled = np.zeros_like(img)
    for idx, (i, j) in enumerate(
            [(r, c) for r in range(gh) for c in range(gw)]):
        shuffled[i * th:(i + 1) * th,
                 j * tw:(j + 1) * tw] = tiles[order[idx]]
    return shuffled, order


def process_all_images(input_dir=None, output_dir=None, difficulty="medium"):
    """Batch-process every image: shuffle and save (CI pipeline)."""
    input_dir  = input_dir  or INPUT_DIR
    output_dir = output_dir or OUTPUT_DIR
    grid_size  = DIFFICULTY_GRID[difficulty]
    os.makedirs(output_dir, exist_ok=True)

    for fname in os.listdir(input_dir):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            continue
        img = cv2.imread(os.path.join(input_dir, fname))
        if img is None:
            continue
        seed = hash(fname) & 0xFFFFFFFF
        shuffled, order = shuffle_image_puzzle(img, grid_size, seed)
        vis = overlay_grid_and_numbers(shuffled, grid_size, order)
        cv2.imwrite(os.path.join(output_dir, f"shuffled_{fname}"), vis)
        sol = {"tile_order": order}
        sol_path = os.path.join(
            output_dir,
            f"solution_map_{os.path.splitext(fname)[0]}.json")
        with open(sol_path, "w") as f:
            json.dump(sol, f)
        print(f"Processed {fname}")


# ══════════════════════════════════════════════════════════
#  GUI  (fully responsive grid layout)
# ══════════════════════════════════════════════════════════

class PuzzleShuffleGUI:
    """Interactive puzzle-shuffle game with tile-swap solving."""

    def __init__(self, root):
        self.root = root
        
        # Only set window properties if root is a window (Tk/Toplevel, not Frame)
        try:
            if isinstance(root, (tk.Tk, tk.Toplevel)):
                self.root.title("Image Puzzle Shuffle Game")
                self.root.geometry("1120x900")
                self.root.minsize(500, 400)
        except:
            pass
        
        # Configure background for all cases
        self.root.configure(bg=BG_MAIN)

        self.img = None
        self.orig_img = None
        self.grid_size = (3, 3)
        self.difficulty = tk.StringVar(value="medium")
        self.fill_box = tk.BooleanVar(value=False)
        self.tile_order = None
        self.selected = []
        self.tiles = None
        self.input_path = None
        # Display tracking for click detection
        self._displayed_img_w = 0
        self._displayed_img_h = 0
        self._displayed_offset_x = 0
        self._displayed_offset_y = 0

        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # ── Root grid ──
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        main_border = tk.Frame(root, bg=BG_MAIN,
                               highlightbackground=ACCENT,
                               highlightthickness=2, bd=8)
        main_border.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_border.grid_rowconfigure(0, weight=1)
        main_border.grid_columnconfigure(1, weight=1)

        # ── Left column (controls) ──
        left = tk.Frame(main_border, bg=BG_MAIN)
        left.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)

        self.status = tk.Label(left,
                               text="Select an image and difficulty, "
                                    "then click Shuffle.",
                               font=("Segoe UI", 12), fg="#555", bg=BG_MAIN,
                               wraplength=180, justify=tk.LEFT)
        self.status.pack(anchor="w", pady=(0, 10))

        # Techniques description
        techniques_text = (
            "Techniques Used:\n"
            "• Image Tiling\n"
            "• Random Shuffle\n"
            "• Grid Overlay\n"
            "• Numbered Tiles"
        )
        tk.Label(left, text=techniques_text,
                 font=("Segoe UI", 12), bg=BG_MAIN, fg="#555",
                 justify=tk.LEFT, wraplength=180).pack(anchor="w", pady=(0, 15))

        btn = tk.Button(left, text="Open Image", command=self.open_image,
                  font=("Segoe UI", 13, "bold"), bg=BTN_BLUE, fg="#fff",
                  activebackground="#1976d2", activeforeground="#fff",
                  relief=tk.RAISED, bd=2, width=18, cursor="hand2")
        btn.pack(anchor="w", pady=(0, 6))
        btn.bind("<Enter>", lambda e: btn.config(bg=self._lighten_color(BTN_BLUE), relief=tk.RIDGE, bd=3))
        btn.bind("<Leave>", lambda e: btn.config(bg=BTN_BLUE, relief=tk.RAISED, bd=2))

        for level in ("easy", "medium", "hard"):
            tk.Radiobutton(left, text=level.title(),
                           variable=self.difficulty, value=level,
                           command=self.set_difficulty,
                           font=("Segoe UI", 13, "bold"), bg=BG_MAIN,
                           fg=ACCENT, selectcolor="#e0d6ce",
                           indicatoron=1, relief=tk.FLAT
                           ).pack(anchor="w", pady=1)

        # Fill Box checkbox
        tk.Checkbutton(left, text="Fill Box",
                      variable=self.fill_box,
                      command=self._refresh_display,
                      font=("Segoe UI", 13, "bold"), bg=BG_MAIN,
                      fg=ACCENT, selectcolor="#e0d6ce",
                      relief=tk.FLAT
                      ).pack(anchor="w", pady=(8, 4))

        btn_shuffle = tk.Button(left, text="Shuffle", command=self.shuffle,
                  font=("Segoe UI", 13, "bold"), bg=BTN_ORANGE, fg="#fff",
                  activebackground="#f57c00", activeforeground="#fff",
                  relief=tk.RAISED, bd=2, width=18, cursor="hand2")
        btn_shuffle.pack(anchor="w", pady=(6, 1))
        btn_shuffle.bind("<Enter>", lambda e: btn_shuffle.config(bg=self._lighten_color(BTN_ORANGE), relief=tk.RIDGE, bd=3))
        btn_shuffle.bind("<Leave>", lambda e: btn_shuffle.config(bg=BTN_ORANGE, relief=tk.RAISED, bd=2))
        
        btn_reset = tk.Button(left, text="Reset", command=self.reset,
                  font=("Segoe UI", 13, "bold"), bg=BTN_RED, fg="#fff",
                  activebackground="#d32f2f", activeforeground="#fff",
                  relief=tk.RAISED, bd=2, width=18, cursor="hand2")
        btn_reset.pack(anchor="w", pady=1)
        btn_reset.bind("<Enter>", lambda e: btn_reset.config(bg=self._lighten_color(BTN_RED), relief=tk.RIDGE, bd=3))
        btn_reset.bind("<Leave>", lambda e: btn_reset.config(bg=BTN_RED, relief=tk.RAISED, bd=2))
        
        self.save_btn = tk.Button(
            left, text="Save Output", command=self.save_output,
            state=tk.DISABLED, font=("Segoe UI", 13, "bold"),
            bg=BTN_BLUE, fg="#fff",
            activebackground="#1976d2", activeforeground="#fff",
            disabledforeground="#888", relief=tk.RAISED, bd=2,
            width=18, cursor="hand2")
        self.save_btn.pack(anchor="w", pady=(6, 1))
        self.save_btn.bind("<Enter>", lambda e: self.save_btn.config(bg=self._lighten_color(BTN_BLUE), relief=tk.RIDGE, bd=3) if self.save_btn['state'] == 'normal' else None)
        self.save_btn.bind("<Leave>", lambda e: self.save_btn.config(bg=BTN_BLUE, relief=tk.RAISED, bd=2))
        
        btn_hint = tk.Button(left, text="Show Hint", command=self.show_hint,
                  font=("Segoe UI", 13, "bold"), bg=BTN_GREEN, fg="#fff",
                  activebackground="#388e3c", activeforeground="#fff",
                  relief=tk.RAISED, bd=2, width=18, cursor="hand2")
        btn_hint.pack(anchor="w", pady=(6, 1))
        btn_hint.bind("<Enter>", lambda e: btn_hint.config(bg=self._lighten_color(BTN_GREEN), relief=tk.RIDGE, bd=3))
        btn_hint.bind("<Leave>", lambda e: btn_hint.config(bg=BTN_GREEN, relief=tk.RAISED, bd=2))

        # ── Right column (image) — fully responsive ──
        right = tk.Frame(main_border, bg=BG_MAIN)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        outer = tk.Frame(right, bg=BG_MAIN,
                         highlightbackground=ACCENT, highlightthickness=3)
        outer.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        inner = tk.Frame(outer, bg="#ffffff", bd=2, relief=tk.SOLID)
        inner.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

        self.img_panel = tk.Label(inner, bg="#ffffff",
                                  text="No image loaded",
                                  font=("Segoe UI", 18), fg="#ccc")
        self.img_panel.grid(row=0, column=0, sticky="nsew")
        self.img_panel.bind("<Button-1>", self.on_click)

        # Responsive resize handling
        self._resize_job = None
        self.root.bind('<Configure>', self._on_configure)

        self._center_window()

    # ────────────────────── image I/O ──────────────────────

    def open_image(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            self.status.config(text="Failed to load image.")
            return
        self.orig_img = img.copy()
        self.img = img
        self.tiles = None
        self.tile_order = None
        self.save_btn.config(state=tk.DISABLED)
        self._show_cv(img)
        # copy to input/
        try:
            base = os.path.basename(path)
            name, ext = os.path.splitext(base)
            dest = os.path.join(INPUT_DIR, base)
            i = 1
            while os.path.exists(dest):
                dest = os.path.join(INPUT_DIR, f"{name}_{i}{ext}")
                i += 1
            shutil.copy(path, dest)
            self.input_path = dest
            self.status.config(
                text=f"Loaded: {os.path.basename(dest)}")
        except Exception as e:
            self.status.config(text=f"Could not copy: {e}")

    def _show_cv(self, img_cv, force_fit=False):
        """Display an OpenCV image scaled to fit or fill the panel."""
        if img_cv is None:
            return
        self.root.update_idletasks()
        pw = max(self.img_panel.winfo_width(), 200)
        ph = max(self.img_panel.winfo_height(), 200)
        rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        
        img_w, img_h = pil.size
        
        if self.fill_box.get() and not force_fit:
            # Fill mode: scale to cover entire panel (may crop)
            scale = max(pw / img_w, ph / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            
            # Center crop
            offset_x = (pw - new_w) // 2
            offset_y = (ph - new_h) // 2
            
            # Create and crop
            resized = pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
            background = Image.new('RGB', (pw, ph), '#ffffff')
            background.paste(resized, (offset_x, offset_y))
            
            # Store actual dimensions for click detection (including cropped parts)
            self._displayed_img_w = new_w
            self._displayed_img_h = new_h
            self._displayed_offset_x = offset_x
            self._displayed_offset_y = offset_y
        else:
            # Fit mode: scale to fit within panel without cropping
            scale = min(pw / img_w, ph / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            
            # Center the image in the panel
            offset_x = (pw - new_w) // 2
            offset_y = (ph - new_h) // 2
            
            # Store dimensions for click detection
            self._displayed_img_w = new_w
            self._displayed_img_h = new_h
            self._displayed_offset_x = offset_x
            self._displayed_offset_y = offset_y
            
            # Create background and paste scaled image
            background = Image.new('RGB', (pw, ph), '#ffffff')
            resized = pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
            background.paste(resized, (offset_x, offset_y))
        
        tk_img = ImageTk.PhotoImage(background)
        self.img_panel.config(image=tk_img, text="")
        self.img_panel.image = tk_img

    # ────────────────────── game logic ──────────────────────

    def set_difficulty(self):
        d = self.difficulty.get()
        self.grid_size = DIFFICULTY_GRID[d]
        self.status.config(text=f"Difficulty: {d.title()}")

    def shuffle(self, silent=False):
        if self.orig_img is None:
            if not silent:
                self.status.config(text="Load an image first.")
            return
        self.set_difficulty()
        gh, gw = self.grid_size
        h, w = self.orig_img.shape[:2]
        
        if self.fill_box.get():
            # Fill Box mode: crop to what's visible in the panel
            self.root.update_idletasks()
            pw = max(self.img_panel.winfo_width(), 200)
            ph = max(self.img_panel.winfo_height(), 200)
            
            # Calculate scale to fill panel
            scale_fill = max(pw / w, ph / h)
            scaled_w = int(w * scale_fill)
            scaled_h = int(h * scale_fill)
            
            # Resize image
            img_scaled = cv2.resize(self.orig_img, (scaled_w, scaled_h))
            
            # Calculate crop area (centered)
            crop_x = max(0, (scaled_w - pw) // 2)
            crop_y = max(0, (scaled_h - ph) // 2)
            
            # Crop to panel size
            img_cropped = img_scaled[crop_y:crop_y + ph, crop_x:crop_x + pw]
            
            # Make grid-divisible
            ch, cw = img_cropped.shape[:2]
            nw = (cw // gw) * gw
            nh = (ch // gh) * gh
            self.img = cv2.resize(img_cropped, (nw, nh))
        else:
            # Fit mode: resize to a clean grid-divisible size
            scale = min(700 / w, 650 / h, 1.0)
            nw = int(w * scale) // gw * gw
            nh = int(h * scale) // gh * gh
            self.img = cv2.resize(self.orig_img, (nw, nh))

        H, W = self.img.shape[:2]
        th, tw = H // gh, W // gw
        tiles = []
        for i in range(gh):
            for j in range(gw):
                tiles.append(self.img[i * th:(i + 1) * th,
                                      j * tw:(j + 1) * tw].copy())
        self.tiles = tiles
        order = list(range(len(tiles)))
        np.random.default_rng().shuffle(order)
        self.tile_order = order
        self._assemble_and_show()
        self.save_btn.config(state=tk.NORMAL)
        if not silent:
            self.status.config(text="Shuffled! Click tiles to swap.")

    def reset(self):
        if self.tiles is None:
            return
        self.tile_order = list(range(len(self.tiles)))
        self._assemble_and_show()
        self.status.config(text="Reset to original.")
        self.save_btn.config(state=tk.DISABLED)

    def on_click(self, event):
        if self.tiles is None or self.tile_order is None:
            return
        # Account for displayed image offset and size
        if not hasattr(self, '_displayed_img_w'):
            return
        # Translate click coordinates relative to displayed image
        x = event.x - self._displayed_offset_x
        y = event.y - self._displayed_offset_y
        # Check if click is within image bounds
        if x < 0 or y < 0 or x >= self._displayed_img_w or y >= self._displayed_img_h:
            return
        gh, gw = self.grid_size
        col = int(x // (self._displayed_img_w / gw))
        row = int(y // (self._displayed_img_h / gh))
        if not (0 <= col < gw and 0 <= row < gh):
            return
        idx = row * gw + col
        if not self.selected:
            self.selected = [idx]
            self.status.config(text=f"Selected tile {idx + 1}. Click another.")
        else:
            a = self.selected.pop()
            if a != idx:
                self.tile_order[a], self.tile_order[idx] = \
                    self.tile_order[idx], self.tile_order[a]
                self._assemble_and_show()
                if self.tile_order == list(range(len(self.tile_order))):
                    self.status.config(text="Solved! Congratulations!")
                    self.save_btn.config(state=tk.NORMAL)
                else:
                    self.status.config(
                        text=f"Swapped tiles {a + 1} and {idx + 1}.")

    # ────────────────────── assembly ──────────────────────

    def _assemble(self):
        if self.tiles is None or self.tile_order is None:
            return None
        gh, gw = self.grid_size
        th, tw = self.tiles[0].shape[:2]
        puzzle = np.zeros((th * gh, tw * gw, 3), dtype=self.tiles[0].dtype)
        for idx, (i, j) in enumerate(
                [(r, c) for r in range(gh) for c in range(gw)]):
            puzzle[i * th:(i + 1) * th,
                   j * tw:(j + 1) * tw] = self.tiles[self.tile_order[idx]]
        return puzzle

    def _draw_grid(self, img):
        out = img.copy()
        gh, gw = self.grid_size
        H, W = out.shape[:2]
        th, tw = H // gh, W // gw
        lc = (50, 50, 50)
        lt = max(1, min(tw, th) // 100 + 1)
        for k in range(1, gw):
            cv2.line(out, (k * tw, 0), (k * tw, H), lc, lt)
        for k in range(1, gh):
            cv2.line(out, (0, k * th), (W, k * th), lc, lt)
        return out

    def _assemble_and_show(self):
        puzzle = self._assemble()
        if puzzle is None:
            return
        display = self._draw_grid(puzzle)
        self._show_cv(display, force_fit=True)

    # ────────────────────── resize ──────────────────────

    def _on_configure(self, event):
        if event.widget is not self.root:
            return
        if self._resize_job:
            try:
                self.root.after_cancel(self._resize_job)
            except Exception:
                pass
        self._resize_job = self.root.after(100, self._resize_update)

    def _resize_update(self):
        try:
            if self.tiles is not None and self.tile_order is not None:
                self._assemble_and_show()
            elif self.img is not None:
                self._show_cv(self.img)
        finally:
            self._resize_job = None

    def _refresh_display(self):
        """Refresh the display when fill box option changes."""
        if self.tiles is not None and self.tile_order is not None:
            # Re-shuffle the puzzle with the new fill box setting (silent mode)
            self.shuffle(silent=True)
        elif self.orig_img is not None:
            self._show_cv(self.orig_img)

    # ────────────────────── save / hint ──────────────────────

    def save_output(self):
        if self.tile_order is None:
            self.status.config(text="Nothing to save.")
            return
        puzzle = self._assemble()
        if puzzle is None:
            return
        base = (os.path.basename(self.input_path)
                if self.input_path else "puzzle")
        name, _ = os.path.splitext(base)

        def _unique(d, b):
            p = os.path.join(d, b)
            if not os.path.exists(p):
                return p
            n, e = os.path.splitext(b)
            i = 1
            while True:
                c = os.path.join(d, f"{n}_{i}{e}")
                if not os.path.exists(c):
                    return c
                i += 1

        puz_path = _unique(OUTPUT_DIR, f"{name}_puzzle.png")
        sol_path = _unique(OUTPUT_DIR, f"{name}_solution.png")
        cv2.imwrite(puz_path, self._draw_grid(puzzle))

        sol = cv2.resize(self.img, (puzzle.shape[1], puzzle.shape[0]))
        sol = self._draw_grid(sol)
        gh, gw = self.grid_size
        H, W = sol.shape[:2]
        th, tw = H // gh, W // gw
        font = cv2.FONT_HERSHEY_SIMPLEX
        for idx in range(gh * gw):
            i, j = divmod(idx, gw)
            sc = max(0.6, min(tw, th) / 140.0)
            txt = str(idx + 1)
            (tw2, th2), _ = cv2.getTextSize(txt, font, sc, 2)
            tx = j * tw + tw // 2 - tw2 // 2
            ty = i * th + th // 2 + th2 // 2
            cv2.putText(sol, txt, (tx, ty), font, sc,
                        (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(sol, txt, (tx, ty), font, sc,
                        (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imwrite(sol_path, sol)
        self.status.config(text="Saved puzzle + solution to output/")

    def show_hint(self):
        if self.orig_img is None or self.tiles is None:
            return
        puzzle = self._assemble()
        if puzzle is None:
            return
        sol = cv2.resize(self.img, (puzzle.shape[1], puzzle.shape[0]))
        sol = self._draw_grid(sol)
        self._show_cv(sol, force_fit=True)
        self.root.after(3000, self._assemble_and_show)

    def _center_window(self):
        # Only center if root is a window, not a frame
        if isinstance(self.root, (tk.Tk, tk.Toplevel)):
            self.root.update_idletasks()
            # Use the desired size (920x700) instead of current size to avoid shrinking
            w, h = 920, 700
            x = (self.root.winfo_screenwidth() // 2) - (w // 2)
            y = (self.root.winfo_screenheight() // 2) - (h // 2)
            self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _lighten_color(self, hex_color):
        """Lighten a hex color for hover effect."""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, int(r * 1.15))
        g = min(255, int(g * 1.15))
        b = min(255, int(b * 1.15))
        return f'#{r:02x}{g:02x}{b:02x}'


# ══════════════════════════════════════════════════════════
#  LAUNCH HELPERS
# ══════════════════════════════════════════════════════════

def _show_intro(parent):
    """Show a styled introduction dialog."""
    dialog = tk.Toplevel(parent)
    dialog.title("Image Puzzle Shuffle — Introduction")
    dialog.configure(bg=BG_MAIN)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.withdraw()  # Hide initially to prevent flash
    
    # Main content frame with border
    main_frame = tk.Frame(dialog, bg=BG_MAIN, highlightbackground=ACCENT,
                         highlightthickness=2, bd=8)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    # Title
    tk.Label(main_frame, text="Image Puzzle Shuffle",
            font=("Segoe UI", 24, "bold"), bg=BG_MAIN, fg=ACCENT).pack(pady=(10, 5))
    
    tk.Frame(main_frame, bg=ACCENT, height=2).pack(fill=tk.X, padx=30, pady=8)
    
    # Content
    content = (
        "Welcome to the Image Puzzle Shuffle Generator!\n\n"
        "This module splits an image into a grid of tiles,\n"
        "shuffles them randomly, and lets you solve the\n"
        "puzzle by clicking two tiles to swap them.\n\n"
        "Difficulty Levels:\n"
        "  - Easy   — 3x3 grid  (9 tiles)\n"
        "  - Medium — 4x4 grid (16 tiles)\n"
        "  - Hard   — 5x5 grid (25 tiles)\n\n"
        "Steps:\n"
        "  1. Click 'Open Image' to load a photo\n"
        "  2. Choose a difficulty level\n"
        "  3. Click 'Shuffle' to scramble the tiles\n"
        "  4. Click tiles to swap and solve the puzzle\n"
        "  5. Click 'Save Output' to save the result"
    )
    
    tk.Label(main_frame, text=content, font=("Segoe UI", 13),
            bg=BG_MAIN, fg="#555", justify=tk.LEFT).pack(padx=20, pady=10)
    
    # OK button
    btn = tk.Button(main_frame, text="Got it!", command=dialog.destroy,
                   font=("Segoe UI", 14, "bold"), bg=BTN_ORANGE, fg="white",
                   activebackground=ACCENT, activeforeground="white",
                   relief=tk.RAISED, bd=2, padx=30, pady=8, cursor="hand2")
    btn.pack(pady=(10, 15))
    
    # Center on parent and show
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_reqwidth() // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_reqheight() // 2)
    dialog.geometry(f"+{x}+{y}")
    dialog.deiconify()  # Show after positioning
    dialog.grab_set()
    
    dialog.wait_window()


def launch_puzzle_shuffle(parent=None):
    if parent:
        _show_intro(parent)  # centred on main menu
        window = tk.Toplevel(parent)
        try:
            window.transient(parent)
            window.lift()
            window.focus_force()
        except Exception:
            pass
    else:
        window = tk.Tk()
    PuzzleShuffleGUI(window)
    if not parent:
        window.mainloop()


if __name__ == "__main__":
    launch_puzzle_shuffle()
