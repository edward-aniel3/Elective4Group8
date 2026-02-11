"""
Mosaic Tile Effect Module
==========================
Creates mosaic tile effects by down-sampling image blocks and
up-scaling with nearest-neighbour interpolation, producing a retro
block-art aesthetic.

Image Processing Techniques Used:
  - Block down-sampling (cv2.INTER_LINEAR)
  - Nearest-neighbour up-scaling (cv2.INTER_NEAREST)
  - Adjustable block size

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
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
INPUT_DIR  = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# ─── Design tokens ────────────────────────────────────────
BG_MAIN    = "#f5ede7"
ACCENT     = "#222"
BTN_BLUE   = "#2196f3"
BTN_PURPLE = "#9c27b0"
BTN_RED    = "#f44336"

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")


# ══════════════════════════════════════════════════════════
#  CORE IMAGE PROCESSING FUNCTIONS
# ══════════════════════════════════════════════════════════

def blockify_image(image, block_size=16):
    """Blockify *image* by down-sampling and up-scaling."""
    h, w = image.shape[:2]
    small = cv2.resize(image,
                       (max(1, w // block_size), max(1, h // block_size)),
                       interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def process_images(input_dir=None, output_dir=None, block_size=16):
    """Batch-blockify every image in *input_dir* (CI pipeline)."""
    input_dir  = input_dir  or INPUT_DIR
    output_dir = output_dir or OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if not fname.lower().endswith(SUPPORTED_EXTENSIONS):
            continue
        img = cv2.imread(os.path.join(input_dir, fname))
        if img is None:
            continue
        blk = blockify_image(img, block_size)
        out = os.path.join(output_dir, f"blockified_{fname}")
        cv2.imwrite(out, blk)
        print(f"Processed: {out}")


# ══════════════════════════════════════════════════════════
#  GUI  (Tkinter — fully responsive grid layout)
# ══════════════════════════════════════════════════════════

class MosaicTileEffectGUI:
    """Tkinter GUI for the mosaic tile effect."""

    def __init__(self, root):
        self.root = root
        
        # Only set window properties if root is a window (Tk/Toplevel, not Frame)
        try:
            if isinstance(root, (tk.Tk, tk.Toplevel)):
                self.root.title("Mosaic Tile Effect")
                self.root.geometry("1120x900")
                self.root.minsize(500, 400)
        except:
            pass
        
        # Configure background for all cases
        self.root.configure(bg=BG_MAIN)

        self.image = None
        self.processed_image = None
        self.source_filename = ""
        self.block_size = tk.IntVar(value=16)
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
            "Create retro block-art effects\n"
            "on any image.\n\n"
            "Techniques used:\n"
            "- Linear Down-sampling\n"
            "- Nearest-Neighbour Up-scale\n"
            "- Adjustable Block Size\n\n"
            "Slide the bar below to change\n"
            "the mosaic block size."
        )
        tk.Label(left, text=desc, font=("Segoe UI", 12),
                 bg=BG_MAIN, fg="#555", justify=tk.LEFT,
                 wraplength=210).pack(anchor="w", pady=(0, 8))

        tk.Label(left, text="Block Size:",
                 font=("Segoe UI", 13, "bold"), bg=BG_MAIN, fg=ACCENT
                 ).pack(anchor="w")
        tk.Scale(left, from_=2, to=64, orient=tk.HORIZONTAL,
                 variable=self.block_size,
                 showvalue=True,
                 length=180, bg=BG_MAIN).pack(anchor="w", pady=(0, 8))

        # Fill Box checkbox
        tk.Checkbutton(left, text="Fill Box",
                      variable=self.fill_box,
                      command=self._refresh_display,
                      font=("Segoe UI", 13, "bold"), bg=BG_MAIN,
                      fg=ACCENT, selectcolor="#e0d6ce",
                      relief=tk.FLAT
                      ).pack(anchor="w", pady=(8, 4))

        for txt, cmd, clr in [
            ("Open Image",  self.open_image,  BTN_BLUE),
            ("Blockify",    self.blockify,    BTN_PURPLE),
            ("Save Output", self.save_output, BTN_RED),
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

    def blockify(self, silent=False):
        if self.image is None:
            if not silent:
                self.status.config(text="Load an image first.")
            return
        bs = self.block_size.get()
        if not silent:
            self.status.config(text=f"Blockifying (size {bs})...")
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
        
        self.processed_image = blockify_image(source_img, bs)
        self._show(self.processed_image)
        if not silent:
            self.status.config(text="Done! Mosaic effect applied.")

    def save_output(self):
        if self.processed_image is None:
            self.status.config(text="Blockify an image first.")
            return
        name, ext = os.path.splitext(self.source_filename or "image.png")
        out_name = f"blockified_{name}{ext}"
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
            # Re-apply blockify silently with new Fill Box setting
            self.blockify(silent=True)
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
    dialog.title("Mosaic Tile Effect — Introduction")
    dialog.configure(bg=BG_MAIN)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.withdraw()  # Hide initially to prevent flash
    
    # Main content frame with border
    main_frame = tk.Frame(dialog, bg=BG_MAIN, highlightbackground=ACCENT,
                         highlightthickness=2, bd=8)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    # Title
    tk.Label(main_frame, text="Mosaic Tile Effect",
            font=("Segoe UI", 24, "bold"), bg=BG_MAIN, fg=ACCENT).pack(pady=(10, 5))
    
    tk.Frame(main_frame, bg=ACCENT, height=2).pack(fill=tk.X, padx=30, pady=8)
    
    # Content
    content = (
        "Welcome to the Mosaic Tile Effect module!\n\n"
        "This module creates a retro block-art effect\n"
        "on any image you load.\n\n"
        "How it works:\n"
        "  - The image is shrunk by a factor equal to\n"
        "    the block size (linear interpolation)\n"
        "  - Then scaled back to original dimensions\n"
        "    using nearest-neighbour interpolation\n"
        "  - This produces visible square blocks,\n"
        "    giving a mosaic block-art look\n\n"
        "Steps:\n"
        "  1. Click 'Open Image'\n"
        "  2. Adjust the Block Size slider\n"
        "     (larger = blockier)\n"
        "  3. Click 'Blockify'\n"
        "  4. Click 'Save Output' to save the result"
    )
    
    tk.Label(main_frame, text=content, font=("Segoe UI", 13),
            bg=BG_MAIN, fg="#555", justify=tk.LEFT).pack(padx=20, pady=10)
    
    # OK button
    btn = tk.Button(main_frame, text="Got it!", command=dialog.destroy,
                   font=("Segoe UI", 14, "bold"), bg=BTN_PURPLE, fg="white",
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


def launch_mosaic_tile_effect(parent=None):
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
    MosaicTileEffectGUI(window)
    if not parent:
        window.mainloop()


if __name__ == "__main__":
    launch_mosaic_tile_effect()
