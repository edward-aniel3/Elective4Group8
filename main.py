"""
ELEC 4 - Image Processing System
=================================
Main Menu Application

Unified interface for all 4 image processing modules:
  1. Background Remover
  2. Image Puzzle Shuffle Generator
  3. Minecraft Filter
  4. Mosaic Tile Effect

UI Design based on the Image Puzzle Shuffle Generator GUI style.
Fully responsive — adapts to any window size like a website.
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys

# Ensure we can import sibling modules regardless of cwd
# PyInstaller compatible path handling
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ─── Color Scheme (from Image Puzzle Shuffle Generator) ───
BG_MAIN    = "#f5ede7"
ACCENT     = "#222"
BTN_BLUE   = "#2196f3"
BTN_ORANGE = "#ff9800"
BTN_GREEN  = "#4caf50"
BTN_PURPLE = "#9c27b0"


class MainMenuApp:
    """Main menu window that launches each image processing module."""

    def __init__(self, root):
        self.root = root
        self.root.title("ELECTIVE 4 — Image Processing System")
        self.root.configure(bg=BG_MAIN)
        self.root.geometry("1020x940")
        self.root.minsize(420, 400)

        # Ensure shared folders exist
        os.makedirs(os.path.join(BASE_DIR, "input"), exist_ok=True)
        os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)

        # ── Root uses grid so everything stretches ──
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # ── Container for switching between menu and modules ──
        self.main_container = tk.Frame(root, bg=BG_MAIN)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # ── Module container (hidden by default) ──
        self.module_container = tk.Frame(self.main_container, bg=BG_MAIN)
        self.current_module_widget = None
        
        # ── Menu container ──
        self.menu_container = tk.Frame(self.main_container, bg=BG_MAIN)
        self.menu_container.grid(row=0, column=0, sticky="nsew")
        self.menu_container.grid_rowconfigure(0, weight=1)
        self.menu_container.grid_columnconfigure(0, weight=1)

        # ── Main bordered frame ──
        main_border = tk.Frame(
            self.menu_container, bg=BG_MAIN,
            highlightbackground=ACCENT, highlightthickness=2, bd=8
        )
        main_border.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main_border.grid_rowconfigure(3, weight=1)   # card area row expands
        main_border.grid_columnconfigure(0, weight=1)

        # ── Title section ──
        title_frame = tk.Frame(main_border, bg=BG_MAIN)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(12, 8))

        tk.Label(title_frame, text="Image Processing System",
                 font=("Segoe UI", 28, "bold"), bg=BG_MAIN, fg=ACCENT).pack()
        tk.Label(title_frame,
                 text="ELECTIVE 4 — Midterm Project  |  DevOps & CI Pipeline",
                 font=("Segoe UI", 13), bg=BG_MAIN, fg="#666").pack()

        # separator
        tk.Frame(main_border, bg=ACCENT, height=2).grid(
            row=1, column=0, sticky="ew", padx=30, pady=12)

        tk.Label(main_border,
                 text="Select an image processing module to launch:",
                 font=("Segoe UI", 13), bg=BG_MAIN, fg=ACCENT).grid(
            row=2, column=0, sticky="w", padx=30, pady=(0, 12))

        # ── Scrollable card area ──
        card_container = tk.Frame(main_border, bg=BG_MAIN)
        card_container.grid(row=3, column=0, sticky="nsew", padx=10)
        card_container.grid_rowconfigure(0, weight=1)
        card_container.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(card_container, bg=BG_MAIN,
                                 highlightthickness=0)
        scrollbar = tk.Scrollbar(card_container, orient="vertical",
                                 command=self._canvas.yview)
        self._scrollable = tk.Frame(self._canvas, bg=BG_MAIN)

        self._scrollable.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))

        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._scrollable, anchor="nw")

        self._canvas.configure(yscrollcommand=scrollbar.set)

        # KEY FIX: Stretch inner frame to match canvas width on resize
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # mouse-wheel scrolling
        def _on_mousewheel(event):
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # store card widgets for responsive text wrapping
        self._card_descs = []

        # ── Module definitions ──
        modules = [
            {
                "num": "1",
                "title": "Background Remover",
                "desc": (
                    "Remove image backgrounds using smart HSV analysis with "
                    "GrabCut refinement for automatic subject detection, or "
                    "interactive GrabCut with manual rectangle selection."
                ),
                "techniques": "HSV Analysis  •  GrabCut  •  Foreground Extraction",
                "color": BTN_BLUE,
                "command": self.launch_background_remover,
            },
            {
                "num": "2",
                "title": "Image Puzzle Shuffle",
                "desc": (
                    "Split images into a grid of tiles and shuffle them randomly. "
                    "Solve the puzzle by clicking tiles to swap them back. "
                    "Three difficulty levels: Easy (3×3), Medium (4×4), Hard (5×5)."
                ),
                "techniques": "Image Tiling  •  Random Shuffle  •  Grid Overlay",
                "color": BTN_ORANGE,
                "command": self.launch_puzzle_shuffle,
            },
            {
                "num": "3",
                "title": "Minecraft Filter",
                "desc": (
                    "Transform any image into a Minecraft-style scene by "
                    "mapping each block region to the closest Minecraft block "
                    "color from an 18-color curated palette."
                ),
                "techniques": "Color Quantization  •  Block Palette Mapping  •  Face Detection • Gender Detection",
                "color": BTN_GREEN,
                "command": self.launch_minecraft_filter,
            },
            {
                "num": "4",
                "title": "Mosaic Tile Effect",
                "desc": (
                    "Create mosaic tile effects by down-sampling image "
                    "blocks and up-scaling with nearest-neighbour interpolation, "
                    "producing a retro block-art aesthetic."
                ),
                "techniques": "Down-sampling  •  Nearest-Neighbour Interpolation  •  Mosaic",
                "color": BTN_PURPLE,
                "command": self.launch_mosaic_tile_effect,
            },
        ]

        # Build cards — pack(fill=X) so they always stretch to full width
        for mod in modules:
            self._build_card(self._scrollable, mod)

        # ── Footer ──
        footer = tk.Frame(main_border, bg=BG_MAIN)
        footer.grid(row=4, column=0, sticky="ew", pady=(12, 8))
        tk.Label(footer,
                 text=" ",
                      
                 font=("Segoe UI", 11), bg=BG_MAIN, fg="#999").pack()
        tk.Label(footer,
                 text="Python 3  •  OpenCV  •  GitHub Actions CI  •  Pytest",
                 font=("Segoe UI", 11), bg=BG_MAIN, fg="#999").pack()

        # Center window on screen
        self._center_window()

        # Debounced resize handler for description text wrapping
        self._resize_id = None
        self.root.bind("<Configure>", self._on_root_resize)

    # ───────────────── Card builder ─────────────────

    def _build_card(self, parent, mod):
        """Build one module card that stretches to full width."""
        card = tk.Frame(parent, bg="#ffffff",
                        highlightbackground=mod["color"],
                        highlightthickness=2, bd=0, relief=tk.FLAT)
        card.pack(fill=tk.X, padx=12, pady=8)

        inner = tk.Frame(card, bg="#ffffff")
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # header row
        header = tk.Frame(inner, bg="#ffffff")
        header.pack(fill=tk.X)

        num_label = tk.Label(header, text=f"  {mod['num']}  ",
                 font=("Segoe UI", 14, "bold"),
                 bg=mod["color"], fg="white")
        num_label.pack(side=tk.LEFT, padx=(0, 12))

        title_label = tk.Label(header, text=mod["title"],
                 font=("Segoe UI", 18, "bold"),
                 bg="#ffffff", fg=ACCENT)
        title_label.pack(side=tk.LEFT)

        btn = tk.Button(header, text="Launch  ▶",
                  command=mod["command"],
                  font=("Segoe UI", 12, "bold"),
                  bg=mod["color"], fg="white",
                  activebackground=ACCENT, activeforeground="white",
                  relief=tk.RAISED, bd=2, padx=18, pady=5,
                  cursor="hand2")
        btn.pack(side=tk.RIGHT)

        # description — wraplength updated by resize handler
        desc = tk.Label(inner, text=mod["desc"], font=("Segoe UI", 12),
                        bg="#ffffff", fg="#555", wraplength=600,
                        justify=tk.LEFT, anchor="w")
        desc.pack(fill=tk.X, anchor="w", pady=(8, 5))
        self._card_descs.append(desc)

        # techniques tag
        tech_label = tk.Label(inner, text=f"Techniques: {mod['techniques']}",
                 font=("Segoe UI", 11, "italic"),
                 bg="#ffffff", fg="#888")
        tech_label.pack(anchor="w")
        
        # Card hover effect - "raise" effect with shadow and highlight
        def on_card_enter(e):
            # Create a raised effect
            card.config(
                highlightbackground=self._lighten_color(mod["color"]),
                highlightthickness=3,
                relief=tk.RAISED,
                bd=3
            )
            # Subtle background color change
            inner.config(bg="#fafafa")
            for widget in [header, num_label, title_label, desc, tech_label]:
                if widget != num_label and widget != btn:  # Keep colored widgets as is
                    widget.config(bg="#fafafa")
        
        def on_card_leave(e):
            # Return to normal state
            card.config(
                highlightbackground=mod["color"],
                highlightthickness=2,
                relief=tk.FLAT,
                bd=0
            )
            # Reset background color
            inner.config(bg="#ffffff")
            for widget in [header, num_label, title_label, desc, tech_label]:
                if widget != num_label and widget != btn:
                    widget.config(bg="#ffffff")
        
        # Button-specific hover handlers (card hover + button color change)
        def on_button_enter(e):
            on_card_enter(e)  # Apply card hover effect
            btn.config(bg=self._lighten_color(mod["color"]))  # Lighten button
        
        def on_button_leave(e):
            on_card_leave(e)  # Remove card hover effect
            btn.config(bg=mod["color"])  # Reset button color
        
        # Bind to all widgets so hover works anywhere in the card
        for widget in [card, inner, header, num_label, title_label, desc, tech_label]:
            widget.bind("<Enter>", on_card_enter)
            widget.bind("<Leave>", on_card_leave)
        
        # Button gets special handlers to maintain its own hover effect
        btn.bind("<Enter>", on_button_enter)
        btn.bind("<Leave>", on_button_leave)

    # ───────────────── Responsive helpers ─────────────────

    def _on_canvas_configure(self, event):
        """Stretch the scrollable frame to match the full canvas width.
        This is THE key fix — without it, cards don't fill the space."""
        self._canvas.itemconfigure(self._canvas_window, width=event.width)

    def _on_root_resize(self, event):
        if event.widget is not self.root:
            return
        if self._resize_id:
            try:
                self.root.after_cancel(self._resize_id)
            except Exception:
                pass
        self._resize_id = self.root.after(80, self._update_wraplength)

    def _update_wraplength(self):
        try:
            w = max(300, self._canvas.winfo_width() - 80)
            for lbl in self._card_descs:
                lbl.configure(wraplength=w)
        except Exception:
            pass

    # ───────────────── Launchers ─────────────────

    def launch_background_remover(self):
        try:
            from elective4group8.background_remover import BackgroundRemoverGUI, _show_intro
            _show_intro(self.root)  # Show intro dialog
            
            content_frame = self._show_module_container("Background Remover")
            self.current_module_widget = BackgroundRemoverGUI(content_frame)
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Failed to launch Background Remover:\n{e}")

    def launch_puzzle_shuffle(self):
        try:
            from elective4group8.puzzle_shuffle import PuzzleShuffleGUI, _show_intro
            _show_intro(self.root)  # Show intro dialog
            
            content_frame = self._show_module_container("Image Puzzle Shuffle")
            self.current_module_widget = PuzzleShuffleGUI(content_frame)
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Failed to launch Puzzle Shuffle:\n{e}")

    def launch_minecraft_filter(self):
        try:
            from elective4group8.minecraft_filter import MinecraftFilterGUI, _show_intro
            _show_intro(self.root)  # Show intro dialog
            
            content_frame = self._show_module_container("Minecraft Filter")
            self.current_module_widget = MinecraftFilterGUI(content_frame)
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Failed to launch Minecraft Filter:\n{e}")

    def launch_mosaic_tile_effect(self):
        try:
            from elective4group8.mosaic_tile_effect import MosaicTileEffectGUI, _show_intro
            _show_intro(self.root)  # Show intro dialog
            
            content_frame = self._show_module_container("Mosaic Tile Effect")
            self.current_module_widget = MosaicTileEffectGUI(content_frame)
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Failed to launch Mosaic Tile Effect:\n{e}")

    def _center_window(self):
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
    
    # ───────────────── Module Container Management ─────────────────
    
    def _show_module_container(self, module_name):
        """Hide menu and show module container with back button."""
        self.menu_container.grid_remove()
        self.module_container.grid(row=0, column=0, sticky="nsew")
        self.module_container.grid_rowconfigure(1, weight=1)
        self.module_container.grid_columnconfigure(0, weight=1)
        
        # Clear previous module content
        for widget in self.module_container.winfo_children():
            widget.destroy()
        
        # Back button bar
        back_bar = tk.Frame(self.module_container, bg=BG_MAIN, height=60)
        back_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        
        back_btn = tk.Button(back_bar, text="◀  Back to Menu",
                             command=self._show_menu,
                             font=("Segoe UI", 13, "bold"),
                             bg=ACCENT, fg="white",
                             activebackground="#444", activeforeground="white",
                             relief=tk.RAISED, bd=2, padx=24, pady=10,
                             cursor="hand2")
        back_btn.pack(side=tk.LEFT, padx=5)
        
        # Hover effect for back button
        def on_back_enter(e):
            back_btn.config(bg=self._lighten_color(ACCENT))
        
        def on_back_leave(e):
            back_btn.config(bg=ACCENT)
        
        back_btn.bind("<Enter>", on_back_enter)
        back_btn.bind("<Leave>", on_back_leave)
        
        tk.Label(back_bar, text=f"  |  {module_name}",
                font=("Segoe UI", 22, "bold"), bg=BG_MAIN, fg=ACCENT).pack(side=tk.LEFT)
        
        # Module content frame
        content_frame = tk.Frame(self.module_container, bg=BG_MAIN)
        content_frame.grid(row=1, column=0, sticky="nsew")
        
        return content_frame
    
    def _show_menu(self):
        """Hide module container and show main menu."""
        self.module_container.grid_remove()
        self.menu_container.grid(row=0, column=0, sticky="nsew")
        
        # Clean up module instance if it exists
        if self.current_module_widget:
            try:
                # Try to call cleanup method if exists
                if hasattr(self.current_module_widget, 'cleanup'):
                    self.current_module_widget.cleanup()
            except Exception:
                pass
            self.current_module_widget = None


# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenuApp(root)
    root.mainloop()
