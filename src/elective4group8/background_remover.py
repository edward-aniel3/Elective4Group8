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

# ─── Design tokens (Puzzle Shuffle style) ─────────────────
BG_MAIN  = "#f5ede7"
ACCENT   = "#222"
BTN_BLUE = "#2196f3"
BTN_GREEN = "#4caf50"
BTN_RED  = "#f44336"
BTN_ORANGE = "#ff9800"

# ══════════════════════════════════════════════════════════
#  CORE IMAGE PROCESSING FUNCTIONS
# ══════════════════════════════════════════════════════════

def is_image_file(filename):
    """Return True if *filename* has a supported image extension."""
    return filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))


def remove_background_smart(image):
    """Smart background removal using HSV analysis + GrabCut refinement.

    1. Convert to HSV and create a foreground probability mask
    2. Use the mask to initialize GrabCut for precise segmentation
    3. Apply the final mask with white background
    """
    # Resize large images to prevent CPU/RAM spikes
    oh, ow = image.shape[:2]
    max_dim = 800
    gc_scale = 1.0
    work_img = image
    if max(oh, ow) > max_dim:
        gc_scale = max_dim / max(oh, ow)
        work_img = cv2.resize(image, (int(ow * gc_scale), int(oh * gc_scale)),
                              interpolation=cv2.INTER_AREA)

    h, w = work_img.shape[:2]

    # Step 1: HSV-based foreground estimation
    hsv = cv2.cvtColor(work_img, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    # Pixels with very low saturation AND high value are likely background
    fg_prob = np.zeros((h, w), dtype=np.uint8)
    fg_prob[sat > 30] = 255                        # visible colour
    fg_prob[(sat <= 30) & (val < 200)] = 255        # dark unsaturated

    # Step 2: Initialize GrabCut with HSV mask
    gc_mask = np.zeros((h, w), np.uint8)
    gc_mask[:] = cv2.GC_BGD
    gc_mask[fg_prob == 255] = cv2.GC_PR_FGD

    # Centre region is more likely foreground
    margin_h, margin_w = h // 6, w // 6
    gc_mask[margin_h:h - margin_h, margin_w:w - margin_w] = cv2.GC_PR_FGD

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(work_img, gc_mask, None, bgdModel, fgdModel,
                    5, cv2.GC_INIT_WITH_MASK)
    except cv2.error:
        pass

    final_mask = np.where(
        (gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)

    # Scale mask back to original size if we downscaled
    if gc_scale != 1.0:
        final_mask = cv2.resize(final_mask, (ow, oh),
                                interpolation=cv2.INTER_NEAREST)

    result = image.copy()
    result[final_mask == 0] = [255, 255, 255]
    return result


def resize_for_display(image, max_width=800, max_height=600):
    """Resize *image* to fit within max dimensions, preserving aspect ratio."""
    h, w = image.shape[:2]
    scale = min(max_width / w, max_height / h, 1.0)
    if scale < 1.0:
        new_size = (int(w * scale), int(h * scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA), scale
    return image, 1.0


def remove_background_grabcut(image):
    """Remove background using OpenCV GrabCut with interactive rectangle selection."""
    display_img, scale = resize_for_display(image)
    mask     = np.zeros(image.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    r = cv2.selectROI(
        "Draw rectangle around subject — press ENTER",
        display_img, fromCenter=False, showCrosshair=True
    )
    cv2.destroyWindow("Draw rectangle around subject — press ENTER")

    if r == (0, 0, 0, 0):
        return image

    if scale != 1.0:
        x, y, w, h = (int(c / scale) for c in r)
    else:
        x, y, w, h = r

    cv2.grabCut(image, mask, (x, y, w, h), bgdModel, fgdModel,
                5, cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

    result   = image * mask2[:, :, np.newaxis]
    white_bg = np.ones_like(image, dtype=np.uint8) * 255
    final    = np.where(mask2[:, :, np.newaxis] == 0, white_bg, result)
    return final


def process_images(input_dir=None, output_dir=None):
    """Batch-process all images in *input_dir* (CI pipeline).
    Applies smart background removal."""
    input_dir  = input_dir  or INPUT_DIR
    output_dir = output_dir or OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    for fname in os.listdir(input_dir):
        if not is_image_file(fname):
            continue
        img = cv2.imread(os.path.join(input_dir, fname))
        if img is None:
            continue
        no_bg = remove_background_smart(img)
        out   = os.path.join(output_dir, f"bgremoved_{fname}")
        cv2.imwrite(out, no_bg)
        print(f"Processed: {out}")


# ══════════════════════════════════════════════════════════
#  RESPONSIVE GUI HELPER — used by all module GUIs
# ══════════════════════════════════════════════════════════

def _build_responsive_module_layout(root, title_text, desc_text,
                                    controls_builder, min_left_width=220):
    """Build a responsive two-column layout: controls (left) + image (right).

    Uses grid geometry so everything stretches properly on resize.
    Returns (left_frame, img_panel, status_label).
    """
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    main_border = tk.Frame(root, bg=BG_MAIN,
                           highlightbackground=ACCENT,
                           highlightthickness=2, bd=8)
    main_border.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    main_border.grid_rowconfigure(0, weight=1)
    main_border.grid_columnconfigure(1, weight=1)  # right column expands

    # ── Left column (controls) — fixed minimum, grows slightly ──
    left = tk.Frame(main_border, bg=BG_MAIN)
    left.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)

    tk.Label(left, text=desc_text, font=("Segoe UI", 12),
             bg=BG_MAIN, fg="#555", justify=tk.LEFT,
             wraplength=210).pack(anchor="w", pady=(0, 10))

    # Let caller add their specific controls
    controls_builder(left)

    status = tk.Label(left, text="Open an image to begin.",
                      font=("Segoe UI", 12), bg=BG_MAIN, fg="#666",
                      wraplength=210, justify=tk.LEFT)
    status.pack(anchor="w", pady=(15, 0))

    # ── Right column (image display) — expands to fill ──
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

    img_panel = tk.Label(inner, bg="#ffffff",
                         text="No image loaded",
                         font=("Segoe UI", 18), fg="#ccc")
    img_panel.grid(row=0, column=0, sticky="nsew")

    return left, img_panel, status


# ══════════════════════════════════════════════════════════
#  GUI  (Tkinter — fully responsive)
# ══════════════════════════════════════════════════════════

class BackgroundRemoverGUI:
    """Tkinter GUI for interactive background removal."""

    def __init__(self, root):
        self.root = root
        
        # Only set window properties if root is a window (Tk/Toplevel, not Frame)
        try:
            if isinstance(root, (tk.Tk, tk.Toplevel)):
                self.root.title("Background Remover")
                self.root.geometry("1120x900")
                self.root.minsize(500, 400)
        except:
            pass
        
        # Configure background for all cases
        self.root.configure(bg=BG_MAIN)

        self.image = None
        self.processed_image = None
        self.source_filename = ""
        self.mode_var = tk.StringVar(value="smart")
        self.fill_box = tk.BooleanVar(value=False)
        self._temp_source_img = None

        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        desc = (
            "Remove image backgrounds using\n"
            "two techniques:\n\n"
            "• Smart — HSV analysis +\n"
            "  GrabCut refinement\n"
            "  (automatic subject detection)\n"
            "• Manual — Interactive GrabCut\n"
            "  (draw a rectangle manually)"
        )

        def add_controls(left):
            # mode selection
            tk.Label(left, text="Processing Mode:",
                     font=("Segoe UI", 13, "bold"), bg=BG_MAIN, fg=ACCENT
                     ).pack(anchor="w", pady=(5, 0))
            for val, label in [
                ("smart",  "Smart (Auto-Detect Subject)"),
                ("grabcut", "Manual (GrabCut Rectangle)"),
            ]:
                tk.Radiobutton(left, text=label,
                               variable=self.mode_var, value=val,
                               font=("Segoe UI", 12), bg=BG_MAIN, fg=ACCENT,
                               selectcolor="#e0d6ce"
                               ).pack(anchor="w")

            # Fill Box checkbox
            tk.Checkbutton(left, text="Fill Box",
                          variable=self.fill_box,
                          command=self._refresh_display,
                          font=("Segoe UI", 13, "bold"), bg=BG_MAIN,
                          fg=ACCENT, selectcolor="#e0d6ce",
                          relief=tk.FLAT
                          ).pack(anchor="w", pady=(8, 4))

            # buttons
            for txt, cmd, clr in [
                ("Open Image",  self.open_image,  BTN_BLUE),
                ("Process",     self.process,      BTN_GREEN),
                ("Save Output", self.save_output,  BTN_RED),
            ]:
                btn = tk.Button(left, text=txt, command=cmd,
                          font=("Segoe UI", 13, "bold"), bg=clr, fg="white",
                          activebackground=ACCENT, activeforeground="white",
                          width=22, relief=tk.RAISED, bd=2, cursor="hand2")
                btn.pack(anchor="w", pady=3)
                # Hover effect with raise
                btn.bind("<Enter>", lambda e, b=btn, c=clr: (b.config(bg=self._lighten_color(c), relief=tk.RIDGE, bd=3)))
                btn.bind("<Leave>", lambda e, b=btn, c=clr: (b.config(bg=c, relief=tk.RAISED, bd=2)))

        self._left, self.img_panel, self.status = \
            _build_responsive_module_layout(
                root, "Background\nRemover", desc, add_controls)

        # Replace Label with Canvas for interactive rectangle drawing
        parent_frame = self.img_panel.master
        self.img_panel.destroy()
        self.img_canvas = tk.Canvas(parent_frame, bg="#ffffff",
                                     highlightthickness=0)
        self.img_canvas.grid(row=0, column=0, sticky="nsew")
        self.img_panel = self.img_canvas  # keep ref for layout helper
        
        # Add placeholder text to canvas (will be positioned on first update)
        self._placeholder_text = None
        self.img_canvas.bind("<Configure>", self._update_placeholder)

        # Display-state for coordinate mapping
        self._display_scale = 1.0
        self._display_offset_x = 0
        self._display_offset_y = 0
        self._tk_img = None

        # Rectangle-selection state
        self._selecting = False
        self._rect_start = None
        self._rect_id = None
        self.img_canvas.bind("<ButtonPress-1>", self._on_press)
        self.img_canvas.bind("<B1-Motion>", self._on_drag)
        self.img_canvas.bind("<ButtonRelease-1>", self._on_release)

        self._center_window()

        # Responsive resize
        self._resize_job = None
        self.root.bind('<Configure>', self._on_configure)

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

    def process(self, silent=False):
        if self.image is None:
            if not silent:
                self.status.config(text="Load an image first.")
            return
        mode = self.mode_var.get()
        
        # Determine which image to process based on Fill Box setting
        if self.fill_box.get():
            # Fill Box mode: crop image to what's visible in the panel
            self.root.update_idletasks()
            pw = max(self.img_canvas.winfo_width(), 200)
            ph = max(self.img_canvas.winfo_height(), 200)
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
        
        if mode == "smart":
            if not silent:
                self.status.config(
                    text="Processing (smart detection)... please wait")
                self.root.update()
            self.processed_image = remove_background_smart(source_img)
            self._show(self.processed_image)
            if not silent:
                self.status.config(text="Done! Background removed.")
        else:
            # Manual GrabCut — enter rectangle-selection mode
            self._temp_source_img = source_img  # Store for _run_grabcut
            self._show(source_img)  # reset display to cropped/original source
            self._selecting = True
            self._rect_start = None
            if self._rect_id:
                self.img_canvas.delete(self._rect_id)
                self._rect_id = None
            self.img_canvas.config(cursor="crosshair")
            self.status.config(
                text="Draw a rectangle around the subject on the image...")

    def save_output(self):
        if self.processed_image is None:
            self.status.config(text="Process an image first.")
            return
        name, ext = os.path.splitext(self.source_filename or "image.png")
        out_name = f"bgremoved_{name}{ext}"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        cv2.imwrite(out_path, self.processed_image)
        self._show(self.processed_image)
        self.status.config(text=f"Saved: {out_name}")

    # ──────────── display ────────────

    def _show(self, img):
        if img is None:
            return
        if len(img.shape) == 2:
            rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.root.update_idletasks()
        pw = max(self.img_canvas.winfo_width(), 200)
        ph = max(self.img_canvas.winfo_height(), 200)
        h, w = rgb.shape[:2]
        
        pil = Image.fromarray(rgb)
        
        if self.fill_box.get():
            # Fill mode: scale to cover entire panel
            self._display_scale = max(pw / w, ph / h)
            nw = max(1, int(w * self._display_scale))
            nh = max(1, int(h * self._display_scale))
            self._display_offset_x = (pw - nw) // 2
            self._display_offset_y = (ph - nh) // 2
            pil = pil.resize((nw, nh), Image.Resampling.LANCZOS)
        else:
            # Fit mode: scale to fit within panel
            self._display_scale = min(pw / w, ph / h)
            nw = max(1, int(w * self._display_scale))
            nh = max(1, int(h * self._display_scale))
            self._display_offset_x = (pw - nw) // 2
            self._display_offset_y = (ph - nh) // 2
            pil = pil.resize((nw, nh), Image.Resampling.LANCZOS)

        self._tk_img = ImageTk.PhotoImage(pil)
        self.img_canvas.delete("all")
        self.img_canvas.create_image(
            self._display_offset_x, self._display_offset_y,
            image=self._tk_img, anchor="nw")

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
            # Re-process silently if smart mode
            if self.mode_var.get() == "smart":
                self.process(silent=True)
            else:
                # Manual mode: just display as-is
                self._show(self.processed_image)
        elif self.image is not None:
            self._show(self.image)

    def _update_placeholder(self, event=None):
        """Update placeholder text position to center of canvas."""
        if self.image is None and self.processed_image is None:
            w = self.img_canvas.winfo_width()
            h = self.img_canvas.winfo_height()
            if w > 1 and h > 1:
                if self._placeholder_text:
                    self.img_canvas.delete(self._placeholder_text)
                self._placeholder_text = self.img_canvas.create_text(
                    w // 2, h // 2,
                    text="No image loaded",
                    font=("Segoe UI", 18),
                    fill="#ccc"
                )

    def _on_press(self, event):
        if not self._selecting:
            return
        self._rect_start = (event.x, event.y)
        if self._rect_id:
            self.img_canvas.delete(self._rect_id)
            self._rect_id = None

    def _on_drag(self, event):
        if not self._selecting or not self._rect_start:
            return
        if self._rect_id:
            self.img_canvas.delete(self._rect_id)
        x0, y0 = self._rect_start
        self._rect_id = self.img_canvas.create_rectangle(
            x0, y0, event.x, event.y,
            outline="red", width=2, dash=(5, 3))

    def _on_release(self, event):
        if not self._selecting or not self._rect_start:
            return
        self._selecting = False
        self.img_canvas.config(cursor="")
        x0, y0 = self._rect_start
        x1, y1 = event.x, event.y
        self._rect_start = None

        # Map canvas coordinates → original image coordinates
        ix0, iy0 = self._canvas_to_image(min(x0, x1), min(y0, y1))
        ix1, iy1 = self._canvas_to_image(max(x0, x1), max(y0, y1))
        rw, rh = ix1 - ix0, iy1 - iy0
        if rw < 5 or rh < 5:
            self.status.config(text="Rectangle too small — try again.")
            return
        self._run_grabcut(ix0, iy0, rw, rh)

    def _canvas_to_image(self, cx, cy):
        """Convert canvas pixel position to original image coordinates."""
        ix = int((cx - self._display_offset_x) / self._display_scale)
        iy = int((cy - self._display_offset_y) / self._display_scale)
        h, w = self.image.shape[:2]
        return max(0, min(ix, w - 1)), max(0, min(iy, h - 1))

    def _run_grabcut(self, x, y, w, h):
        """Run GrabCut on the source image with the selected rectangle."""
        self.status.config(text="Processing GrabCut... please wait")
        self.root.update()

        # Use temp source image (respects Fill Box setting)
        img = getattr(self, '_temp_source_img', self.image)
        ih, iw = img.shape[:2]
        max_dim = 800
        gc_scale = 1.0
        if max(ih, iw) > max_dim:
            gc_scale = max_dim / max(ih, iw)
            img = cv2.resize(img, (int(iw * gc_scale), int(ih * gc_scale)),
                             interpolation=cv2.INTER_AREA)
            x, y, w, h = (int(x * gc_scale), int(y * gc_scale),
                          int(w * gc_scale), int(h * gc_scale))

        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        try:
            cv2.grabCut(img, mask, (x, y, w, h),
                        bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        except cv2.error as e:
            self.status.config(text=f"GrabCut failed: {e}")
            return
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

        # Scale mask back to original size if we downscaled
        if gc_scale != 1.0:
            mask2 = cv2.resize(mask2, (iw, ih),
                               interpolation=cv2.INTER_NEAREST)

        # Use temp source image for final result
        source_img = getattr(self, '_temp_source_img', self.image)
        result = source_img * mask2[:, :, np.newaxis]
        white_bg = np.ones_like(source_img, dtype=np.uint8) * 255
        self.processed_image = np.where(
            mask2[:, :, np.newaxis] == 0, white_bg, result)
        self._show(self.processed_image)
        self.status.config(text="Done! Background removed.")

    def _center_window(self):
        # Only center if root is a window, not a frame
        if isinstance(self.root, (tk.Tk, tk.Toplevel)):
            self.root.update_idletasks()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
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
    dialog.title("Background Remover — Introduction")
    dialog.configure(bg=BG_MAIN)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.withdraw()  # Hide initially to prevent flash
    
    # Main content frame with border
    main_frame = tk.Frame(dialog, bg=BG_MAIN, highlightbackground=ACCENT,
                         highlightthickness=2, bd=8)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    # Title
    tk.Label(main_frame, text="Background Remover",
            font=("Segoe UI", 24, "bold"), bg=BG_MAIN, fg=ACCENT).pack(pady=(10, 5))
    
    tk.Frame(main_frame, bg=ACCENT, height=2).pack(fill=tk.X, padx=30, pady=8)
    
    # Content
    content = (
        "Welcome to the Background Remover!\n\n"
        "This module removes image backgrounds using:\n\n"
        "  • Smart Mode — HSV analysis +\n"
        "    GrabCut refinement\n"
        "    (automatic subject detection)\n\n"
        "  • Manual Mode — Interactive GrabCut\n"
        "    (draw a rectangle around the subject)\n\n"
        "Steps:\n"
        "  1. Click 'Open Image' to load a photo\n"
        "  2. Choose a processing mode\n"
        "  3. Click 'Process'\n"
        "  4. Click 'Save Output' to save the result\n\n"
        "Processed images are saved in the 'output/' folder."
    )
    
    tk.Label(main_frame, text=content, font=("Segoe UI", 13),
            bg=BG_MAIN, fg="#555", justify=tk.LEFT).pack(padx=20, pady=10)
    
    # OK button
    btn = tk.Button(main_frame, text="Got it!", command=dialog.destroy,
                   font=("Segoe UI", 14, "bold"), bg=BTN_BLUE, fg="white",
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


def launch_background_remover(parent=None):
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
    BackgroundRemoverGUI(window)
    if not parent:
        window.mainloop()


if __name__ == "__main__":
    launch_background_remover()
