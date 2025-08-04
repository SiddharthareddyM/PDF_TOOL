import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Canvas, Toplevel, ttk
import os
import fitz
from PIL import Image, ImageTk, ImageDraw
import tempfile
import io  # Add this import

# Import your modules (make sure these files exist in the same directory)
from pdf_splitter import PDFSplitter
from pdf_merger import PDFMerger
from file_compression import PDFCompressor
from file_converter import FileConverter
from pdf_editor import PDFEditor
from pdf_sign import PDFESignTool  # Using the simplified version

# Initialize feature classes
splitter = PDFSplitter()
merger = PDFMerger()
compressor = PDFCompressor()
converter = FileConverter()
editor = PDFEditor()
signer = PDFESignTool()

# Modern Color Palette
COLORS = {
    'primary': '#1a1a2e',      # Dark navy blue
    'secondary': '#16213e',     # Darker blue
    'accent': '#0f4c75',       # Medium blue
    'highlight': '#3282b8',    # Light blue
    'text_primary': '#ffffff', # White
    'text_secondary': '#b8c6db', # Light blue-gray
    'success': '#4ecdc4',      # Teal
    'warning': '#ffe66d',      # Yellow
    'danger': '#ff6b6b',       # Red
    'info': '#4dabf7',         # Blue
    'purple': '#845ec2',       # Purple
    'orange': '#ff9f43'        # Orange
}

# Helper dialogs
def ask_file(types):
    return filedialog.askopenfilename(filetypes=types)

def ask_files(types):
    return filedialog.askopenfilenames(filetypes=types)

def ask_folder():
    return filedialog.askdirectory()

def draw_signature_window(temp_path, callback):
    draw_win = Toplevel()
    draw_win.title("Draw Signature")
    draw_win.geometry("620x280")
    draw_win.resizable(False, False)
    draw_win.grab_set()  # Make it modal
    draw_win.config(bg=COLORS['secondary'])

    canvas_width, canvas_height = 600, 200
    canvas = Canvas(draw_win, width=canvas_width, height=canvas_height, bg="white", relief="solid", bd=2)
    canvas.pack(pady=10)

    img = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(img)

    button_frame = tk.Frame(draw_win, bg=COLORS['secondary'])
    button_frame.pack(pady=5)

    def clear_canvas():
        canvas.delete("all")
        img.paste(Image.new("RGB", (canvas_width, canvas_height), "white"))

    def save_signature():
        try:
            img.save(temp_path)
            messagebox.showinfo("Success", "Signature saved successfully!")
            draw_win.destroy()
            callback()  # Call the callback to continue processing
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save signature: {str(e)}")

    def cancel():
        draw_win.destroy()

    tk.Button(button_frame, text="Clear", command=clear_canvas, 
              bg=COLORS['danger'], fg=COLORS['text_primary'], 
              font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=10)
    tk.Button(button_frame, text="Cancel", command=cancel, 
              bg=COLORS['accent'], fg=COLORS['text_primary'], 
              font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2").pack(side="right", padx=10)
    tk.Button(button_frame, text="Save Signature", command=save_signature, 
              bg=COLORS['success'], fg=COLORS['text_primary'], 
              font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2").pack(side="right", padx=10)

    last_x, last_y = None, None

    def start_draw(event):
        nonlocal last_x, last_y
        last_x, last_y = event.x, event.y

    def draw_motion(event):
        nonlocal last_x, last_y
        if last_x and last_y:
            canvas.create_line(last_x, last_y, event.x, event.y, fill="black", width=3, capstyle=tk.ROUND)
            draw.line([last_x, last_y, event.x, event.y], fill="black", width=3)
        last_x, last_y = event.x, event.y

    canvas.bind('<Button-1>', start_draw)
    canvas.bind('<B1-Motion>', draw_motion)

def pdf_text_position_selector(pdf_path, page_num, text, font_size):
    """
    Opens a visual PDF page viewer where user can click to select text position
    Returns the selected x, y coordinates or None if cancelled
    """
    try:
        # Open PDF and get the specified page
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]  # Convert to 0-based index
        
        # Convert page to image
        mat = fitz.Matrix(1.5, 1.5)  # Zoom factor for better visibility
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("ppm")
        
        # Create PIL image - Fixed line
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Calculate display size (fit to screen while maintaining aspect ratio)
        screen_width = 900
        screen_height = 700
        img_width, img_height = pil_image.size
        
        scale_x = screen_width / img_width
        scale_y = screen_height / img_height
        scale = min(scale_x, scale_y, 1.0)  # Don't upscale
        
        display_width = int(img_width * scale)
        display_height = int(img_height * scale)
        
        # Resize image for display
        display_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        doc.close()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load PDF page: {str(e)}")
        return None
    
    # Create position selector window
    pos_window = Toplevel()
    pos_window.title(f"Select Text Position - Page {page_num}")
    pos_window.geometry(f"{display_width + 100}x{display_height + 150}")
    pos_window.resizable(True, True)
    pos_window.grab_set()
    pos_window.config(bg=COLORS['secondary'])
    
    selected_pos = None
    
    # Instructions
    instruction_frame = tk.Frame(pos_window, bg=COLORS['primary'], pady=10)
    instruction_frame.pack(fill="x")
    
    tk.Label(instruction_frame, 
             text=f"Click on the PDF to position your text: \"{text}\"",
             font=("Segoe UI", 12, "bold"), 
             bg=COLORS['primary'], fg=COLORS['text_primary']).pack()
    tk.Label(instruction_frame, 
             text="The red crosshair shows where your text will be placed",
             font=("Segoe UI", 10), 
             bg=COLORS['primary'], fg=COLORS['text_secondary']).pack()
    
    # Create canvas with scrollbars
    canvas_frame = tk.Frame(pos_window, bg=COLORS['secondary'])
    canvas_frame.pack(expand=True, fill="both", padx=10, pady=5)
    
    canvas = Canvas(canvas_frame, bg="white", highlightthickness=1, highlightbackground=COLORS['accent'])
    v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
    
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # Pack scrollbars and canvas
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")
    canvas.pack(side="left", expand=True, fill="both")
    
    # Convert PIL image to PhotoImage and display
    photo = ImageTk.PhotoImage(display_image)
    canvas_image = canvas.create_image(0, 0, anchor="nw", image=photo)
    
    # Configure scroll region
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Variables for crosshair
    crosshair_h = None
    crosshair_v = None
    position_indicator = None
    
    def update_crosshair(x, y):
        nonlocal crosshair_h, crosshair_v, position_indicator
        
        # Remove old crosshair
        if crosshair_h:
            canvas.delete(crosshair_h)
        if crosshair_v:
            canvas.delete(crosshair_v)
        if position_indicator:
            canvas.delete(position_indicator)
        
        # Draw new crosshair
        crosshair_h = canvas.create_line(0, y, display_width, y, fill="red", width=1, dash=(3, 3))
        crosshair_v = canvas.create_line(x, 0, x, display_height, fill="red", width=1, dash=(3, 3))
        
        # Add position indicator circle
        position_indicator = canvas.create_oval(x-5, y-5, x+5, y+5, outline="red", width=2, fill="white")
    
    def on_canvas_click(event):
        nonlocal selected_pos
        
        # Get canvas coordinates
        canvas_x = canvas.canvasx(event.x)
        canvas_y = canvas.canvasy(event.y)
        
        # Convert display coordinates back to PDF coordinates
        pdf_x = (canvas_x / scale) / mat.a  # Adjust for zoom and scale
        pdf_y = (canvas_y / scale) / mat.d  # Adjust for zoom and scale
        
        selected_pos = (pdf_x, pdf_y)
        
        # Update crosshair
        update_crosshair(canvas_x, canvas_y)
        
        # Update coordinate display
        coord_label.config(text=f"Selected Position: ({pdf_x:.1f}, {pdf_y:.1f})")
        confirm_btn.config(state="normal", bg=COLORS['success'])
    
    def on_canvas_motion(event):
        # Show preview crosshair on mouse move (lighter color)
        canvas_x = canvas.canvasx(event.x)
        canvas_y = canvas.canvasy(event.y)
        
        # Only show preview if no position is selected yet
        if selected_pos is None:
            canvas.delete("preview_crosshair")
            canvas.create_line(0, canvas_y, display_width, canvas_y, 
                             fill="lightcoral", width=1, dash=(2, 2), tags="preview_crosshair")
            canvas.create_line(canvas_x, 0, canvas_x, display_height, 
                             fill="lightcoral", width=1, dash=(2, 2), tags="preview_crosshair")
    
    # Bind events
    canvas.bind("<Button-1>", on_canvas_click)
    canvas.bind("<Motion>", on_canvas_motion)
    
    # Bottom frame with coordinates and buttons
    bottom_frame = tk.Frame(pos_window, bg=COLORS['primary'], pady=10)
    bottom_frame.pack(fill="x")
    
    # Coordinate display
    coord_label = tk.Label(bottom_frame, text="Click on the PDF to select position", 
                          font=("Segoe UI", 10), 
                          bg=COLORS['primary'], fg=COLORS['text_secondary'])
    coord_label.pack()
    
    # Buttons
    button_frame = tk.Frame(bottom_frame, bg=COLORS['primary'])
    button_frame.pack(pady=10)
    
    def confirm_position():
        pos_window.destroy()
    
    def cancel_selection():
        nonlocal selected_pos
        selected_pos = None
        pos_window.destroy()
    
    def reset_position():
        nonlocal selected_pos
        selected_pos = None
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=photo)
        coord_label.config(text="Click on the PDF to select position")
        confirm_btn.config(state="disabled", bg=COLORS['accent'])
    
    tk.Button(button_frame, text="Reset", command=reset_position, 
              bg=COLORS['warning'], fg=COLORS['primary'], width=12,
              font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=cancel_selection, 
              bg=COLORS['danger'], fg=COLORS['text_primary'], width=12,
              font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)
    confirm_btn = tk.Button(button_frame, text="Confirm Position", command=confirm_position, 
                           bg=COLORS['accent'], fg=COLORS['text_primary'], width=15, state="disabled",
                           font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
    confirm_btn.pack(side="right", padx=5)
    
    # Wait for window to close
    pos_window.wait_window()
    
    return selected_pos

def get_signature_positions(page, sig_width=100, sig_height=50, position="bottom_left"):
    margin = 50
    page_width = page.rect.width
    page_height = page.rect.height
    
    positions = []
    if position == "bottom_left":
        positions.append((margin, page_height - sig_height - margin))
    elif position == "bottom_right":
        positions.append((page_width - sig_width - margin, page_height - sig_height - margin))
    elif position == "both":
        positions.append((margin, page_height - sig_height - margin))
        positions.append((page_width - sig_width - margin, page_height - sig_height - margin))
    elif position == "custom":
        x = simpledialog.askfloat("X Position", "Enter X position (0-based):", minvalue=0)
        y = simpledialog.askfloat("Y Position", "Enter Y position (0-based):", minvalue=0)
        if x is not None and y is not None:
            positions.append((x, y))
    
    return positions

# GUI Handlers
def handle_split_pdf():
    try:
        pdf_path = ask_file([("PDF Files", "*.pdf")])
        if not pdf_path: return
        
        output_dir = ask_folder()
        if not output_dir: return
        
        total_pages = splitter.validate_file_path(pdf_path)
        if not total_pages:
            messagebox.showerror("Error", "Invalid PDF file")
            return

        choice = messagebox.askquestion("Split Method", "Use fixed page size?\n\nYes = Fixed size (e.g., 5 pages each)\nNo = Custom sizes")
        
        if choice == 'yes':
            size = simpledialog.askinteger("Pages per Split", f"Enter pages per split (1-{total_pages}):", 
                                         minvalue=1, maxvalue=total_pages)
            if size:
                success, msg = splitter.split_by_fixed_size(pdf_path, output_dir, size)
        else:
            sizes = simpledialog.askstring("Custom Sizes", f"Enter split sizes (comma-separated)\nExample: 3,2,4 (total must be ≤ {total_pages}):")
            if sizes:
                try:
                    split_list = [int(x.strip()) for x in sizes.split(',') if x.strip()]
                    success, msg = splitter.split_by_custom_sizes(pdf_path, output_dir, split_list)
                except ValueError:
                    messagebox.showerror("Error", "Invalid split sizes format")
                    return
        
        messagebox.showinfo("Split Result", msg)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to split PDF: {str(e)}")

def handle_merge_pdf():
    try:
        files = ask_files([("PDF Files", "*.pdf")])
        if len(files) < 2:
            messagebox.showwarning("Error", "Please select at least 2 PDF files")
            return
        
        output_dir = ask_folder()
        if not output_dir: return
        
        success, msg = merger.merge_pdfs(list(files), output_dir)
        messagebox.showinfo("Merge Result", msg)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to merge PDFs: {str(e)}")

def handle_compress_pdf():
    try:
        pdf_path = ask_file([("PDF Files", "*.pdf")])
        if not pdf_path: return
        
        output_dir = ask_folder()
        if not output_dir: return
        
        output_path = os.path.join(output_dir, "compressed_" + os.path.basename(pdf_path))
        success, msg = compressor.compress_pdf(pdf_path, output_path)
        messagebox.showinfo("Compression Result", msg)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to compress PDF: {str(e)}")

def handle_convert_file():
    try:
        input_file = ask_file([("Supported Files", "*.pdf *.docx *.doc *.jpg *.jpeg *.png *.bmp *.gif")])
        if not input_file: return
        
        output_dir = ask_folder()
        if not output_dir: return
        
        success, msg = converter.convert_file(input_file, output_dir)
        messagebox.showinfo("Conversion Result", msg)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert file: {str(e)}")

def handle_edit_pdf():
    try:
        pdf_path = ask_file([("PDF Files", "*.pdf")])
        if not pdf_path: return
        
        output_dir = ask_folder()
        if not output_dir: return
        
        choice = simpledialog.askinteger(
            "Edit Options",
            "Choose edit type:\n\n1. Delete Pages\n2. Rotate Pages\n3. Extract Pages\n4. Add Text",
            minvalue=1, maxvalue=4
        )
        
        if not choice: return

        if choice in [1, 2, 3]:
            page_input = simpledialog.askstring("Page Numbers", 
                                              "Enter page numbers (comma-separated, 1-based)\nExample: 1,3,5 or 2-5:")
            if not page_input: return
            
            try:
                pages = []
                for part in page_input.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        pages.extend(range(start-1, end))
                    else:
                        pages.append(int(part) - 1)
                pages = sorted(set(pages))
            except ValueError:
                messagebox.showerror("Error", "Invalid page number format")
                return

        if choice == 1:
            output_file = os.path.join(output_dir, "pages_deleted.pdf")
            success, msg = editor.delete_pages(pdf_path, output_file, pages)
        elif choice == 2:
            degrees = simpledialog.askinteger("Rotation", "Enter rotation degrees:", 
                                            initialvalue=90, minvalue=0, maxvalue=360)
            output_file = os.path.join(output_dir, "pages_rotated.pdf")
            success, msg = editor.rotate_pages(pdf_path, output_file, pages, degrees)
        elif choice == 3:
            output_file = os.path.join(output_dir, "pages_extracted.pdf")
            success, msg = editor.extract_pages(pdf_path, output_file, pages)
        elif choice == 4:
            # Enhanced Add Text functionality with visual positioning
            text = simpledialog.askstring("Text", "Enter text to add:")
            if not text: return
            
            # Get page number
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            
            page = simpledialog.askinteger("Page", f"Page number (1-{total_pages}):", 
                                         minvalue=1, maxvalue=total_pages)
            if not page: return
            
            # Get font size
            size = simpledialog.askinteger("Font Size", "Font size:", 
                                         initialvalue=12, minvalue=6, maxvalue=72)
            if not size: return
            
            # Ask user for positioning method
            position_choice = messagebox.askquestion(
                "Position Method",
                "How would you like to position the text?\n\n" +
                "Yes = Click on PDF (Visual)\n" +
                "No = Enter coordinates manually"
            )
            
            if position_choice == 'yes':
                # Use visual position selector
                position = pdf_text_position_selector(pdf_path, page, text, size)
                if position is None:
                    messagebox.showinfo("Cancelled", "Text addition cancelled")
                    return
                x, y = position
            else:
                # Manual coordinate entry (original method)
                x = simpledialog.askfloat("X Position", "X position:", minvalue=0)
                y = simpledialog.askfloat("Y Position", "Y position:", minvalue=0)
                if None in [x, y]: return
            
            output_file = os.path.join(output_dir, "text_added.pdf")
            success, msg = editor.add_text_to_pdf(pdf_path, output_file, page, text, x, y, size)
        
        messagebox.showinfo("Edit Result", msg)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to edit PDF: {str(e)}")

def handle_sign_pdf():
    try:
        pdf_path = ask_file([("PDF Files", "*.pdf")])
        if not pdf_path: return
        
        # Get PDF info
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
        
        page_number = simpledialog.askinteger("Page Selection", f"Enter page number (1-{total_pages}):", 
                                            minvalue=1, maxvalue=total_pages)
        if not page_number: return
        
        output_dir = ask_folder()
        if not output_dir: return
        
        output_path = os.path.join(output_dir, "signed_" + os.path.basename(pdf_path))

        # Get signature position
        position_choice = messagebox.askquestion("Position", 
                                               "Use preset position?\n\nYes = Choose preset (bottom-left, etc.)\nNo = Enter custom coordinates")
        
        doc = fitz.open(pdf_path)
        page = doc[page_number - 1]
        
        if position_choice == 'yes':
            position = simpledialog.askstring("Preset Position", 
                                            "Enter position:\n• bottom_left\n• bottom_right\n• both\n", 
                                            initialvalue="bottom_left")
            positions = get_signature_positions(page, position=position)
        else:
            positions = get_signature_positions(page, position="custom")
        
        doc.close()
        
        if not positions:
            messagebox.showwarning("Error", "No valid position selected")
            return

        # Get signature type
        sig_choice = simpledialog.askinteger(
            "Signature Type",
            "Choose signature type:\n\n1. Text Signature\n2. Image Signature\n3. Draw Signature",
            minvalue=1, maxvalue=3
        )
        
        if not sig_choice: return

        if sig_choice == 1:
            # Text signature
            text = simpledialog.askstring("Text Signature", "Enter signature text:")
            if not text: return
            
            size = simpledialog.askinteger("Font Size", "Font size:", initialvalue=14, minvalue=8, maxvalue=48)
            
            for x, y in positions:
                signer.add_text(pdf_path, output_path, page_number, text, x, y, size)
            
            messagebox.showinfo("Success", f"Text signature added successfully!\nSaved: {output_path}")

        elif sig_choice == 2:
            # Image signature
            img_path = ask_file([("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
            if not img_path: return
            
            width = simpledialog.askinteger("Width", "Signature width:", initialvalue=150, minvalue=50, maxvalue=500)
            height = simpledialog.askinteger("Height", "Signature height:", initialvalue=75, minvalue=25, maxvalue=250)
            
            for x, y in positions:
                signer.add_image(pdf_path, output_path, page_number, img_path, x, y, width, height)
            
            messagebox.showinfo("Success", f"Image signature added successfully!\nSaved: {output_path}")

        elif sig_choice == 3:
            # Draw signature
            temp_img = os.path.join(output_dir, "temp_drawn_signature.png")
            
            def process_drawn_signature():
                try:
                    if os.path.exists(temp_img):
                        for x, y in positions:
                            signer.add_image(pdf_path, output_path, page_number, temp_img, x, y, 200, 100)
                        
                        # Clean up temp file
                        try:
                            os.remove(temp_img)
                        except:
                            pass
                        
                        messagebox.showinfo("Success", f"Drawn signature added successfully!\nSaved: {output_path}")
                    else:
                        messagebox.showwarning("Error", "No signature was drawn")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add drawn signature: {str(e)}")
            
            draw_signature_window(temp_img, process_drawn_signature)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add signature: {str(e)}")

# GUI Setup
root = tk.Tk()
root.title("📄 PDF Toolkit - Modern Theme")
root.geometry("550x700")
root.config(bg=COLORS['primary'])
root.resizable(False, False)

# Header
header_frame = tk.Frame(root, bg=COLORS['secondary'], height=80)
header_frame.pack(fill="x", pady=(0, 20))
header_frame.pack_propagate(False)

title_label = tk.Label(header_frame, text="📄 PDF Toolkit", 
                      font=("Segoe UI", 24, "bold"), 
                      fg=COLORS['text_primary'], bg=COLORS['secondary'])
title_label.pack(expand=True)

subtitle_label = tk.Label(header_frame, text="Complete PDF Management Solution", 
                         font=("Segoe UI", 10), 
                         fg=COLORS['text_secondary'], bg=COLORS['secondary'])
subtitle_label.pack()

# Button container
button_frame = tk.Frame(root, bg=COLORS['primary'])
button_frame.pack(expand=True, fill="both", padx=30, pady=20)

# Modern button style function
def create_modern_button(parent, text, command, color, row):
    btn = tk.Button(parent, text=text, command=command, 
                   font=("Segoe UI", 12, "bold"), 
                   height=2, width=35,
                   bg=color, fg=COLORS['text_primary'],
                   relief="flat", 
                   cursor="hand2",
                   activebackground=COLORS['highlight'],
                   activeforeground=COLORS['text_primary'])
    btn.pack(pady=8)
    
    # Enhanced hover effects
    def on_enter(event):
        btn.config(bg=COLORS['highlight'], relief="raised")
    
    def on_leave(event):
        btn.config(bg=color, relief="flat")
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

# Button configurations with new modern colors
buttons = [
    ("🔄 Split PDF", handle_split_pdf, COLORS['info']),
    ("📋 Merge PDFs", handle_merge_pdf, COLORS['success']),
    ("🗜️ Compress PDF", handle_compress_pdf, COLORS['purple']),
    ("🔄 Convert Files", handle_convert_file, COLORS['warning']),
    ("✏️ Edit PDF", handle_edit_pdf, COLORS['accent']),
    ("✍️ Digital Signature", handle_sign_pdf, COLORS['orange']),
]

for i, (text, func, color) in enumerate(buttons):
    create_modern_button(button_frame, text, func, color, i)

# Footer
footer_frame = tk.Frame(root, bg=COLORS['primary'], height=40)
footer_frame.pack(fill="x", side="bottom")
footer_frame.pack_propagate(False)

footer_label = tk.Label(footer_frame, text="PDF Toolkit v2.1 - Modern Theme Edition", 
                       font=("Segoe UI", 8), 
                       fg=COLORS['text_secondary'], bg=COLORS['primary'])
footer_label.pack(expand=True)

if __name__ == "__main__":
    root.mainloop()
