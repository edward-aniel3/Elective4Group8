"""
Minecraft Filter Module
=======================
Transforms images into Minecraft-style pixel art by mapping each block
region to the closest colour in a curated 18-colour Minecraft palette.

Image Processing Techniques Used:
  - Block averaging (mean colour per NxN region)
  - Euclidean distance colour matching
  - Colour quantisation to a fixed palette

Fully responsive UI — adapts to any window size.
"""

import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import shutil
import sys

# ─── Paths ────────────────────────────────────────────────
# PyInstaller compatible path handling
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = os.path.dirname(sys.executable)
    # PyInstaller extracts bundled files to sys._MEIPASS
    RESOURCE_DIR = sys._MEIPASS
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Resource files are in reference-imgs folder (2 levels up, then into reference-imgs)
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
    RESOURCE_DIR = os.path.join(PROJECT_ROOT, "reference-imgs")
    
INPUT_DIR  = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# ─── Design tokens ────────────────────────────────────────
BG_MAIN   = "#f5ede7"
ACCENT    = "#222"
BTN_BLUE  = "#2196f3"
BTN_GREEN = "#4caf50"
BTN_RED   = "#f44336"

# ─── Minecraft block colour palette ──────────────────────
MINECRAFT_PALETTE = np.array([
    [125, 125, 125],   # Stone
    [151, 109,  77],   # Dirt
    [222, 222, 222],   # Iron
    [102, 142,  60],   # Grass
    [255, 255, 255],   # Snow
    [154, 123,  80],   # Wood
    [ 29,  70, 168],   # Water
    [112,   2,   0],   # Nether
    [  0,   0,   0],   # Coal / Obsidian
    [255, 216,  61],   # Sand
    [249, 202,  35],   # Gold
    [255,   0,   0],   # Redstone
    [  0, 255,   0],   # Emerald
    [  0,   0, 255],   # Lapis
    [255, 127,  39],   # Orange Terracotta
    [255, 255,   0],   # Yellow Wool
    [255,   0, 255],   # Magenta Wool
    [  0, 255, 255],   # Cyan Wool
], dtype=np.uint8)


# ══════════════════════════════════════════════════════════
#  CORE IMAGE PROCESSING FUNCTIONS
# ══════════════════════════════════════════════════════════

def minecraft_filter(image, block_size=10):
    """Apply a Minecraft-style colour mapping filter.

    Each *block_size* x *block_size* block is replaced with the
    closest colour from the Minecraft palette (Euclidean distance).
    """
    h, w = image.shape[:2]
    out = image.copy()
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            block = image[y:y + block_size, x:x + block_size]
            avg = block.mean(axis=(0, 1))[:3]
            dists = np.sqrt(np.sum(
                (MINECRAFT_PALETTE.astype(float) - avg) ** 2, axis=1))
            idx = int(np.argmin(dists))
            out[y:y + block_size, x:x + block_size] = MINECRAFT_PALETTE[idx]
    return out


def get_image_files(input_dir):
    """Return a list of image file paths found in *input_dir*."""
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    files = []
    if not os.path.isdir(input_dir):
        return files
    for fname in os.listdir(input_dir):
        if os.path.splitext(fname)[1].lower() in exts:
            files.append(os.path.join(input_dir, fname))
    return files


def process_all_images(input_dir=None, output_dir=None, block_size=10):
    """Batch-process every image in *input_dir* (CI pipeline)."""
    input_dir  = input_dir  or INPUT_DIR
    output_dir = output_dir or OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    for img_path in get_image_files(input_dir):
        img = cv2.imread(img_path)
        if img is None:
            continue
        filtered = minecraft_filter(img, block_size)
        out_name = f"minecraft_{os.path.basename(img_path)}"
        out_path = os.path.join(output_dir, out_name)
        cv2.imwrite(out_path, filtered)
        print(f"Processed {img_path} -> {out_path}")


# ══════════════════════════════════════════════════════════
#  FACE DETECTION, GENDER ESTIMATION & OVERLAY
# ══════════════════════════════════════════════════════════

def is_valid_face_region(image, face_rect):
    """Validate if detected region is actually a face based on color analysis."""
    x, y, w, h = face_rect
    if y + h > image.shape[0] or x + w > image.shape[1]:
        return False
    
    roi = image[y:y+h, x:x+w]
    if roi.size == 0:
        return False
    
    # Check if region has skin-like colors
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    # Skin tone range in HSV
    lower_skin = np.array([0, 20, 50], dtype=np.uint8)
    upper_skin = np.array([30, 200, 255], dtype=np.uint8)
    skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
    skin_ratio = np.sum(skin_mask > 0) / skin_mask.size
    
    # Face should have at least 15% skin-colored pixels
    if skin_ratio < 0.15:
        return False
    
    # Check color variance - faces shouldn't be too uniform
    if np.std(roi) < 15:
        return False
    
    return True


def detect_faces(image):
    """Detect faces using OpenCV's built-in Haar cascade."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    # Increased minNeighbors to 10 and minSize to 60x60 to further reduce false positives
    faces = cascade.detectMultiScale(
        gray, scaleFactor=1.15, minNeighbors=10, minSize=(60, 60))
    
    # Validate each detected face
    valid_faces = []
    for face in faces:
        if is_valid_face_region(image, face):
            valid_faces.append(face)
    
    return np.array(valid_faces) if valid_faces else np.array([])


def estimate_gender(image, face_rect):
    """Estimate gender from a face region using simple image analysis.

    Uses basic heuristics: hair region variance and face aspect ratio.
    Returns 'male' for Steve, 'female' for Alex.
    """
    x, y, w, h = face_rect
    
    # Get face region with some padding
    pad = int(0.05 * w)
    y1, y2 = max(0, y - pad), min(image.shape[0], y + h + pad)
    x1, x2 = max(0, x - pad), min(image.shape[1], x + w + pad)
    roi = image[y1:y2, x1:x2]
    
    if roi.size == 0:
        return "male"

    score = 0  # Start neutral

    # 1. Hair region analysis - check area above face
    hair_y1 = max(0, y - int(h * 0.3))
    hair_y2 = y
    if hair_y1 < hair_y2 and x + w <= image.shape[1]:
        hair_region = image[hair_y1:hair_y2, x:x+w]
        if hair_region.size > 0:
            hair_std = np.std(hair_region)
            # Longer hair tends to have more variation
            if hair_std > 45:
                score -= 2.0  # Likely female
            elif hair_std < 25:
                score += 1.5  # Short hair, likely male

    # 2. Face aspect ratio
    aspect = w / h
    if aspect > 0.90:
        score += 1.0  # Wider face → male
    elif aspect < 0.75:
        score -= 1.0  # Narrower face → female

    # 3. Color variance (simple smoothness check)
    roi_variance = np.var(roi)
    if roi_variance < 800:
        score -= 1.0  # Smoother/more uniform → female
    elif roi_variance > 1500:
        score += 1.0  # More variation → male

    # Return based on final score
    return "male" if score >= 0 else "female"


def overlay_minecraft_face(image, faces, gender_mode="auto",
                           detected_image=None):
    """Overlay Steve or Alex face on every detected face rectangle.

    Args:
        image:          The Minecraft-filtered image.
        faces:          Array of (x, y, w, h) face rectangles.
        gender_mode:    'auto', 'male', or 'female'.
        detected_image: Original (un-filtered) image used when
                        *gender_mode* is 'auto' for better accuracy.
    Returns:
        Image with Steve / Alex overlaid on each face.
    """
    # Use RESOURCE_DIR to find bundled PNG files
    steve_path = os.path.join(RESOURCE_DIR, "steve_face.png")
    alex_path  = os.path.join(RESOURCE_DIR, "alex_face.png")
    steve = cv2.imread(steve_path)
    alex  = cv2.imread(alex_path)

    if steve is None and alex is None:
        print(f"[WARNING] Face overlay PNGs not found in {RESOURCE_DIR}")
        return image

    out = image.copy()
    ref = detected_image if detected_image is not None else image

    for (x, y, w, h) in faces:
        # Choose character
        if gender_mode == "auto":
            gender = estimate_gender(ref, (x, y, w, h))
        else:
            gender = gender_mode

        template = steve if gender == "male" else alex
        if template is None:                       # fallback
            template = alex if steve is None else steve

        # Scale template ~1.4× face size to cover the whole head
        scale = 1.4
        nw, nh = int(w * scale), int(h * scale)
        ox, oy = (nw - w) // 2, (nh - h) // 2

        x1, y1 = max(0, x - ox), max(0, y - oy)
        x2 = min(out.shape[1], x1 + nw)
        y2 = min(out.shape[0], y1 + nh)
        aw, ah = x2 - x1, y2 - y1

        if aw > 0 and ah > 0:
            resized = cv2.resize(template, (aw, ah),
                                 interpolation=cv2.INTER_NEAREST)
            out[y1:y2, x1:x2] = resized

    return out


# ══════════════════════════════════════════════════════════
#  GUI  (Tkinter — fully responsive grid layout)
# ══════════════════════════════════════════════════════════

class MinecraftFilterGUI:
    """Tkinter GUI for the Minecraft colour-palette filter."""

    def __init__(self, root):
        self.root = root
        
        # Only set window properties if root is a window (Tk/Toplevel, not Frame)
        try:
            if isinstance(root, (tk.Tk, tk.Toplevel)):
                self.root.title("Minecraft Filter")
                self.root.geometry("1120x900")
                self.root.minsize(500, 400)
        except:
            pass
        
        # Configure background for all cases
        self.root.configure(bg=BG_MAIN)

        self.image = None
        self.processed_image = None
        self.source_filename = ""
        self.block_size = tk.IntVar(value=10)
        self.gender_mode = tk.StringVar(value="auto")
        self.face_overlay = tk.BooleanVar(value=True)
        self.fill_box = tk.BooleanVar(value=False)

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

        # ── Left column ──
        left = tk.Frame(main_border, bg=BG_MAIN)
        left.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)

        desc = (
            "Transform images into\n"
            "minecraft-style art.\n\n"
            "Techniques used:\n"
            "- Block Colour Averaging\n"
            "- Euclidean Palette Matching\n"
            "- Face Detection (Haar)\n"
            "- Gender Estimation\n"
            "- Steve / Alex Overlay\n\n"
            "Adjust settings below."
        )
        tk.Label(left, text=desc, font=("Segoe UI", 12),
                 bg=BG_MAIN, fg="#555", justify=tk.LEFT,
                 wraplength=210).pack(anchor="w", pady=(0, 8))

        tk.Label(left, text="Block Size:",
                 font=("Segoe UI", 13, "bold"), bg=BG_MAIN, fg=ACCENT
                 ).pack(anchor="w")
        tk.Scale(left, from_=4, to=30, orient=tk.HORIZONTAL,
                 variable=self.block_size,
                 showvalue=True,
                 length=180, bg=BG_MAIN).pack(anchor="w", pady=(0, 8))

        # ── Face overlay toggle ──
        tk.Checkbutton(left, text="Enable Face Overlay",
                       variable=self.face_overlay,
                       font=("Segoe UI", 12, "bold"), bg=BG_MAIN, fg=ACCENT,
                       activebackground=BG_MAIN, selectcolor="#fff"
                       ).pack(anchor="w", pady=(5, 2))

        # Fill Box checkbox
        tk.Checkbutton(left, text="Fill Box",
                      variable=self.fill_box,
                      command=self._refresh_display,
                      font=("Segoe UI", 13, "bold"), bg=BG_MAIN,
                      fg=ACCENT, selectcolor="#e0d6ce",
                      relief=tk.FLAT
                      ).pack(anchor="w", pady=(8, 4))

        # ── Character / gender selection ──
        tk.Label(left, text="Character Mode:",
                 font=("Segoe UI", 13, "bold"), bg=BG_MAIN, fg=ACCENT
                 ).pack(anchor="w", pady=(5, 0))
        for txt, val in [("Auto-Detect", "auto"),
                         ("Steve (Boy)", "male"),
                         ("Alex (Girl)", "female")]:
            tk.Radiobutton(left, text=txt, variable=self.gender_mode,
                           value=val, font=("Segoe UI", 12),
                           bg=BG_MAIN, fg="#555", activebackground=BG_MAIN,
                           selectcolor="#fff"
                           ).pack(anchor="w", padx=(10, 0))

        for txt, cmd, clr in [
            ("Open Image",   self.open_image,   BTN_BLUE),
            ("Apply Filter", self.apply_filter,  BTN_GREEN),
            ("Save Output",  self.save_output,   BTN_RED),
        ]:
            btn = tk.Button(left, text=txt, command=cmd,
                      font=("Segoe UI", 13, "bold"), bg=clr, fg="white",
                      activebackground=ACCENT, activeforeground="white",
                      width=22, relief=tk.RAISED, bd=2, cursor="hand2")
            btn.pack(anchor="w", pady=3)
            # Hover effect with raise
            btn.bind("<Enter>", lambda e, b=btn, c=clr: (b.config(bg=self._lighten_color(c), relief=tk.RIDGE, bd=3)))
            btn.bind("<Leave>", lambda e, b=btn, c=clr: (b.config(bg=c, relief=tk.RAISED, bd=2)))

        self.status = tk.Label(left, text="Open an image to begin.",
                               font=("Segoe UI", 12), bg=BG_MAIN, fg="#666",
                               wraplength=210, justify=tk.LEFT)
        self.status.pack(anchor="w", pady=(15, 0))

        # ── Right column — fully responsive ──
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

        # Responsive resize
        self._resize_job = None
        self.root.bind('<Configure>', self._on_configure)

        self._center_window()

    # ──────────── actions ────────────

    def open_image(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not path:
            return
        self.image = cv2.imread(path)
        if self.image is None:
            self.status.config(text="Failed to load image.")
            return
        self.processed_image = None
        self.source_filename = os.path.basename(path)
        try:
            dest = os.path.join(INPUT_DIR, self.source_filename)
            if not os.path.exists(dest):
                shutil.copy2(path, dest)
        except Exception:
            pass
        self._show(self.image)
        self.status.config(text=f"Loaded: {self.source_filename}")

    def apply_filter(self, silent=False):
        if self.image is None:
            if not silent:
                self.status.config(text="Load an image first.")
            return
        bs = self.block_size.get()
        if not silent:
            self.status.config(text=f"Applying filter (block {bs})...")
            self.root.update()
        
        # Determine which image to process based on Fill Box setting
        if self.fill_box.get():
            # Fill Box mode: crop image to what's visible in the panel
            self.root.update_idletasks()
            pw = max(self.img_panel.winfo_width(), 200)
            ph = max(self.img_panel.winfo_height(), 200)
            h, w = self.image.shape[:2]
            
            # Calculate scale to fill panel
            scale_fill = max(pw / w, ph / h)
            scaled_w = int(w * scale_fill)
            scaled_h = int(h * scale_fill)
            
            # Resize image
            img_scaled = cv2.resize(self.image, (scaled_w, scaled_h))
            
            # Calculate crop area (centered)
            crop_x = max(0, (scaled_w - pw) // 2)
            crop_y = max(0, (scaled_h - ph) // 2)
            
            # Crop to panel size
            source_img = img_scaled[crop_y:crop_y + ph, crop_x:crop_x + pw]
        else:
            source_img = self.image
        
        filtered = minecraft_filter(source_img, bs)

        # ── Face overlay (Steve / Alex) ──
        if self.face_overlay.get():
            if not silent:
                self.status.config(text="Detecting faces...")
                self.root.update()
            faces = detect_faces(source_img)   # detect on source
            if len(faces) > 0:
                mode = self.gender_mode.get()
                filtered = overlay_minecraft_face(
                    filtered, faces,
                    gender_mode=mode,
                    detected_image=source_img)
                # Build status summary
                labels = []
                for (fx, fy, fw, fh) in faces:
                    if mode == "auto":
                        g = estimate_gender(source_img, (fx, fy, fw, fh))
                    else:
                        g = mode
                    labels.append("Steve" if g == "male" else "Alex")
                if not silent:
                    self.status.config(
                        text=f"Done! {len(faces)} face(s): {', '.join(labels)}")
            else:
                if not silent:
                    self.status.config(
                        text="Done! Filter applied (no faces detected).")
        else:
            if not silent:
                self.status.config(text="Done! Minecraft filter applied.")

        self.processed_image = filtered
        self._show(self.processed_image)

    def save_output(self):
        if self.processed_image is None:
            self.status.config(text="Apply the filter first.")
            return
        name, ext = os.path.splitext(self.source_filename or "image.png")
        out_name = f"minecraft_{name}{ext}"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        cv2.imwrite(out_path, self.processed_image)
        self._show(self.processed_image)
        self.status.config(text=f"Saved: {out_name}")

    # ──────────── display ────────────

    def _show(self, img):
        if img is None:
            return
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.root.update_idletasks()
        pw = max(self.img_panel.winfo_width(), 200)
        ph = max(self.img_panel.winfo_height(), 200)
        pil = Image.fromarray(rgb)
        
        if self.fill_box.get():
            # Fill mode: crop and resize to fill the entire canvas
            fitted = ImageOps.fit(pil, (pw, ph), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        else:
            # Fit mode: scale to fit within panel without cropping
            img_w, img_h = pil.size
            scale = min(pw / img_w, ph / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            
            # Create background and center the image
            background = Image.new('RGB', (pw, ph), '#ffffff')
            resized = pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
            offset_x = (pw - new_w) // 2
            offset_y = (ph - new_h) // 2
            background.paste(resized, (offset_x, offset_y))
            fitted = background
        
        tk_img = ImageTk.PhotoImage(fitted)
        self.img_panel.config(image=tk_img, text="")
        self.img_panel.image = tk_img

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
            if self.processed_image is not None:
                self._show(self.processed_image)
            elif self.image is not None:
                self._show(self.image)
        finally:
            self._resize_job = None

    def _refresh_display(self):
        """Refresh the display when fill box option changes."""
        if self.processed_image is not None:
            # Re-apply filter silently with new Fill Box setting
            self.apply_filter(silent=True)
        elif self.image is not None:
            self._show(self.image)

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
    dialog.title("Minecraft Filter — Introduction")
    dialog.configure(bg=BG_MAIN)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.withdraw()  # Hide initially to prevent flash
    
    # Main content frame with border
    main_frame = tk.Frame(dialog, bg=BG_MAIN, highlightbackground=ACCENT,
                         highlightthickness=2, bd=8)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    # Title
    tk.Label(main_frame, text="Minecraft Filter",
            font=("Segoe UI", 24, "bold"), bg=BG_MAIN, fg=ACCENT).pack(pady=(10, 5))
    
    tk.Frame(main_frame, bg=ACCENT, height=2).pack(fill=tk.X, padx=30, pady=8)
    
    # Content
    content = (
        "Welcome to the Minecraft Filter!\n\n"
        "This module transforms any image into a\n"
        "Minecraft-style scene and overlays\n"
        "Steve or Alex on detected faces!\n\n"
        "How it works:\n"
        "  - The image is divided into small blocks\n"
        "  - Each block's colour is matched to the\n"
        "    closest Minecraft block palette colour\n"
        "  - Faces are detected automatically\n"
        "  - Gender is estimated to choose Steve or Alex\n\n"
        "Steps:\n"
        "  1. Click 'Open Image'\n"
        "  2. Adjust Block Size & Character Mode\n"
        "  3. Click 'Apply Filter'\n"
        "  4. Click 'Save Output' to save the result"
    )
    
    tk.Label(main_frame, text=content, font=("Segoe UI", 13),
            bg=BG_MAIN, fg="#555", justify=tk.LEFT).pack(padx=20, pady=10)
    
    # OK button
    btn = tk.Button(main_frame, text="Got it!", command=dialog.destroy,
                   font=("Segoe UI", 14, "bold"), bg=BTN_GREEN, fg="white",
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


def launch_minecraft_filter(parent=None):
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
    MinecraftFilterGUI(window)
    if not parent:
        window.mainloop()

if __name__ == "__main__":
    launch_minecraft_filter()
