#updated gui to integrate the enhancement(customizer.py)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
import numpy as np
from qr_generator import generate_qr
from qr_customizer import QRCustomizer  # ADDED
import sys
from io import StringIO


QUIET_ZONE = 4  # modules of light border required by ISO/IEC 18004


def with_quiet_zone(matrix, border=QUIET_ZONE):
    """Pad a QR matrix with the light-module border scanners rely on."""
    return np.pad(matrix, border, mode='constant', constant_values=0)


class QRGeneratorGUI:
    """
    Interactive GUI for QR code generation with customization.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator - Version 1, ECC L, Mask 0")
        self.root.geometry("950x750")
        self.root.resizable(True, True)
        
        # Store current QR matrix
        self.current_matrix = None
        self.current_text = None
        
        # Initialize customizer (ADDED)
        self.customizer = QRCustomizer()
        
        self._create_widgets()
        self._show_startup_warning()
        
    def _create_widgets(self):
        # Main Screen
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="QR Code Generator", 
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Subtitle
        subtitle = ttk.Label(
            main_frame,
            text="Version 1 • ECC Level L • Mask 0 • Byte Mode",
            font=("Arial", 10, "italic"),
            foreground="gray"
        )
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Text to encode:").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        
        self.text_input = ttk.Entry(input_frame, width=50, font=("Courier", 10))
        self.text_input.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.text_input.bind('<Return>', lambda e: self._generate_qr())
        
        # Character counter
        self.char_count_label = ttk.Label(
            input_frame, 
            text="0/17 characters", 
            foreground="gray"
        )
        self.char_count_label.grid(row=1, column=1, sticky="w", pady=(5, 0))
        self.text_input.bind('<KeyRelease>', self._update_char_count)
        
        # Start of the customization section
        custom_frame = ttk.LabelFrame(main_frame, text="Appearance", padding="10")
        custom_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        custom_frame.columnconfigure(1, weight=1)
        
        ttk.Label(custom_frame, text="Style Preset:").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        
        # Preset dropdown
        self.preset_var = tk.StringVar(value="standard")
        preset_options = list(self.customizer.PRESET_CONFIGS.keys())
        preset_combo = ttk.Combobox(
            custom_frame,
            textvariable=self.preset_var,
            values=preset_options,
            state="readonly",
            width=25
        )
        preset_combo.grid(row=0, column=1, sticky="w", padx=(0, 10))
        preset_combo.bind('<<ComboboxSelected>>', self._on_preset_change)
        
        # Description label
        self.preset_desc = ttk.Label(
            custom_frame,
            text=self.customizer.PRESET_CONFIGS['standard']['description'],
            foreground="gray",
            font=("Arial", 9)
        )
        self.preset_desc.grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        # Warning label
        self.preset_warning = ttk.Label(
            custom_frame,
            text="",
            foreground="orange",
            font=("Arial", 9, "bold")
        )
        self.preset_warning.grid(row=2, column=1, sticky="w", pady=(5, 0))
        # End of the customization section
        
        # Button section
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Generate QR Code", 
            command=self._generate_qr,
            width=20
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Save Image", 
            command=self._save_image,
            width=15
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Clear", 
            command=self._clear_all,
            width=15
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="ℹ Information", 
            command=self._show_info,
            width=15
        ).pack(side="left", padx=5)
        
        # Display area with two columns
        display_container = ttk.Frame(main_frame)
        display_container.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=10)
        display_container.columnconfigure(0, weight=1)
        display_container.columnconfigure(1, weight=1)
        display_container.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # QR Code display
        qr_frame = ttk.LabelFrame(display_container, text="QR Code", padding="10")
        qr_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        qr_frame.rowconfigure(0, weight=1)
        qr_frame.columnconfigure(0, weight=1)
        
        self.canvas_frame = ttk.Frame(qr_frame)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        
        # Log display
        log_frame = ttk.LabelFrame(display_container, text="Generation Log", padding="10")
        log_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        # Text widget with scrollbar
        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.grid(row=0, column=1, sticky="ns")
        
        self.log_text = tk.Text(
            log_frame, 
            wrap="word", 
            width=40, 
            height=20,
            font=("Courier", 9),
            yscrollcommand=log_scroll.set
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll.config(command=self.log_text.yview)
        
        # Status bar
        self.status_label = ttk.Label(
            main_frame, 
            text="Ready to generate QR codes", 
            relief="sunken",
            anchor="w"
        )
        self.status_label.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    
    def _on_preset_change(self, event=None):
        """Handle preset selection change (NEW)"""
        preset_name = self.preset_var.get()
        
        # Suppress print output when applying preset
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        settings = self.customizer.apply_preset(preset_name)
        
        sys.stdout = old_stdout
        
        # Update description
        self.preset_desc.config(text=settings['description'])
        
        # Show warnings if any
        if self.customizer.warnings:
            warning_text = " | ".join(self.customizer.warnings[:2])  # First 2 warnings
            self.preset_warning.config(text="⚠️ " + warning_text)
        else:
            self.preset_warning.config(text="✓ Scan-safe configuration")
        
        # Re-render QR if one exists
        if self.current_matrix is not None:
            self._display_qr(self.current_matrix)
    
    def _show_startup_warning(self):
        """Display data protection warning on startup."""
        warning = """Please check the 'Information' section before entering data.
This tool generates QR codes locally.
No data is transmitted externally."""
        
        messagebox.showwarning("Security Information", warning)
    
    def _update_char_count(self, event=None):
        """Update character count display."""
        text = self.text_input.get()
        count = len(text)
        color = "red" if count > 17 else "gray"
        self.char_count_label.config(
            text=f"{count}/17 characters",
            foreground=color
        )
    
    def _generate_qr(self):
        """Generate and display QR code from input text."""
        text = self.text_input.get()
        
        # Input validation
        if not text:
            messagebox.showwarning("Input Required", "Please enter text to encode.")
            self.status_label.config(text="Error: No input provided")
            return
        
        if len(text) > 17:
            messagebox.showerror(
                "Input Too Long", 
                f"Version 1 QR codes support maximum 17 characters.\n"
                f"Your input: {len(text)} characters."
            )
            self.status_label.config(text="Error: Input exceeds capacity")
            return
        
        try:
            # Capture console output
            old_stdout = sys.stdout
            sys.stdout = log_capture = StringIO()
            
            # Generate QR code
            self.status_label.config(text="Generating QR code...")
            self.root.update()
            
            qr_matrix = generate_qr(text)
            
            # Restore stdout and get log
            sys.stdout = old_stdout
            log_output = log_capture.getvalue()
            
            # Store current state
            self.current_matrix = qr_matrix
            self.current_text = text
            
            # Display QR code with current style
            self._display_qr(qr_matrix)
            
            # Display log
            self._display_log(log_output)
            
            self.status_label.config(
                text=f"✓ QR code generated successfully for '{text}'"
            )
            
        except UnicodeEncodeError as e:
            sys.stdout = old_stdout
            messagebox.showerror(
                "Encoding Error",
                f"Character encoding failed. Ensure text uses ISO-8859-1 compatible characters.\n\n{str(e)}"
            )
            self.status_label.config(text="Error: Character encoding failed")
            
        except Exception as e:
            sys.stdout = old_stdout
            messagebox.showerror(
                "Generation Error",
                f"Failed to generate QR code:\n\n{str(e)}"
            )
            self.status_label.config(text=f"Error: {str(e)}")
    
    def _display_qr(self, matrix):
        """
        Display QR code with current customization (MODIFIED)
        """
        # Clear previous display
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        # Get current style settings
        settings = self.customizer.settings
        colors = settings['colors']
        
        # Create figure
        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create custom colormap from preset colors
        cmap = ListedColormap([colors['light'], colors['dark']])
        
        # Display QR with custom colors
        ax.imshow(with_quiet_zone(matrix), cmap=cmap, interpolation='nearest')
        ax.axis('off')
        fig.tight_layout(pad=0.5)
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def _display_log(self, log_text):
        """Display generation log in text widget."""
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert('1.0', log_text)
        self.log_text.see('1.0')
    
    def _save_image(self):
        """Save current QR code as PNG with current style (MODIFIED)"""
        if self.current_matrix is None:
            messagebox.showwarning("No QR Code", "Generate a QR code first.")
            return
        
        preset_name = self.preset_var.get()
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            initialfile=f"qr_{self.current_text.replace(' ', '_')}_{preset_name}.png"
        )
        
        if filename:
            try:
                # Get current colors
                colors = self.customizer.settings['colors']
                cmap = ListedColormap([colors['light'], colors['dark']])
                
                # Save with high resolution
                fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
                ax.imshow(with_quiet_zone(self.current_matrix), cmap=cmap,
                          interpolation='nearest')
                ax.axis('off')
                plt.tight_layout(pad=0)
                plt.savefig(filename, bbox_inches='tight', pad_inches=0)
                plt.close(fig)
                
                messagebox.showinfo("Success", f"QR code saved to:\n{filename}")
                self.status_label.config(text=f"✓ Image saved: {filename}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save image:\n{str(e)}")
                self.status_label.config(text="Error: Failed to save image")
    
    def _clear_all(self):
        """Clear all inputs and displays."""
        self.text_input.delete(0, tk.END)
        self.log_text.delete('1.0', tk.END)
        
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        self.current_matrix = None
        self.current_text = None
        self.preset_var.set("standard")
        self._on_preset_change()  # Reset to default preset
        self.status_label.config(text="Ready to generate QR codes")
        self._update_char_count()
    
    def _show_info(self):
        """Show detailed information dialog."""
        info_window = tk.Toplevel(self.root)
        info_window.title("Information - QR Code Generator")
        info_window.geometry("600x500")
        info_window.resizable(False, False)
        
        notebook = ttk.Notebook(info_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Data Handling
        tab1 = ttk.Frame(notebook, padding="10")
        notebook.add(tab1, text="Data Handling")
        
        data_info = """DATA HANDLING & PROCESSING

Input Sanitisation:
• Text is encoded using ISO-8859-1 character standard
• Maximum capacity: 17 characters for Version 1
• Invalid characters will cause encoding errors

Processing Steps:
1. Mode indicator: Byte mode (0100)
2. Character count: 8-bit binary encoding
3. Data encoding: ISO-8859-1 to binary
4. Terminator: Up to 4 zero bits
5. Padding: Byte alignment and capacity filling
6. Error correction: Reed-Solomon (7 ECC bytes)
        """
        
        data_text = tk.Text(tab1, wrap="word", font=("Courier", 10))
        data_text.insert('1.0', data_info)
        data_text.config(state='disabled')
        data_text.pack(fill="both", expand=True)
        
        # Tab 2: Customization
        tab2 = ttk.Frame(notebook, padding="10")
        notebook.add(tab2, text="Customization")
        
        custom_info = "CUSTOMIZATION OPTIONS\n\n"
        for name, config in self.customizer.PRESET_CONFIGS.items():
            custom_info += f"{name.upper()}:\n"
            custom_info += f"{config['description']}\n"
            custom_info += f"Colors: {config['colors']['dark']} / {config['colors']['light']}\n\n"
        
        custom_text = tk.Text(tab2, wrap="word", font=("Courier", 10))
        custom_text.insert('1.0', custom_info)
        custom_text.config(state='disabled')
        custom_text.pack(fill="both", expand=True)
        
        ttk.Button(info_window, text="Close", command=info_window.destroy).pack(pady=10)


def main():
    """Launch the QR Generator GUI application."""
    root = tk.Tk()
    app = QRGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()