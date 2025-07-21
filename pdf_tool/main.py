import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Canvas, Toplevel
import os
import fitz
from PIL import Image, ImageDraw

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

    canvas_width, canvas_height = 600, 200
    canvas = Canvas(draw_win, width=canvas_width, height=canvas_height, bg="white", relief="sunken", bd=2)
    canvas.pack(pady=10)

    img = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(img)

    button_frame = tk.Frame(draw_win)
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

    tk.Button(button_frame, text="Clear", command=clear_canvas, bg="#ff6b6b", fg="white").pack(side="left", padx=10)
    tk.Button(button_frame, text="Cancel", command=cancel, bg="#6c757d", fg="white").pack(side="left", padx=10)
    tk.Button(button_frame, text="Save Signature", command=save_signature, bg="#28a745", fg="white").pack(side="right", padx=10)

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
            text = simpledialog.askstring("Text", "Enter text to add:")
            if not text: return
            
            page = simpledialog.askinteger("Page", "Page number (1-based):", minvalue=1)
            x = simpledialog.askfloat("X Position", "X position:", minvalue=0)
            y = simpledialog.askfloat("Y Position", "Y position:", minvalue=0)
            size = simpledialog.askinteger("Font Size", "Font size:", initialvalue=12, minvalue=6, maxvalue=72)
            
            if None in [page, x, y, size]: return
            
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
root.title("📄 PDF Toolkit")
root.geometry("550x700")
root.config(bg="#2c3e50")
root.resizable(False, False)

# Header
header_frame = tk.Frame(root, bg="#34495e", height=80)
header_frame.pack(fill="x", pady=(0, 20))
header_frame.pack_propagate(False)

title_label = tk.Label(header_frame, text="📄 PDF Toolkit", 
                      font=("Segoe UI", 24, "bold"), 
                      fg="white", bg="#34495e")
title_label.pack(expand=True)

subtitle_label = tk.Label(header_frame, text="Complete PDF Management Solution", 
                         font=("Segoe UI", 10), 
                         fg="#bdc3c7", bg="#34495e")
subtitle_label.pack()

# Button container
button_frame = tk.Frame(root, bg="#2c3e50")
button_frame.pack(expand=True, fill="both", padx=30, pady=20)

# Button configurations
buttons = [
    ("🔄 Split PDF", handle_split_pdf, "#e74c3c"),
    ("📋 Merge PDFs", handle_merge_pdf, "#3498db"),
    ("🗜️ Compress PDF", handle_compress_pdf, "#9b59b6"),
    ("🔄 Convert Files", handle_convert_file, "#f39c12"),
    ("✏️ Edit PDF", handle_edit_pdf, "#27ae60"),
    ("✍️ Digital Signature", handle_sign_pdf, "#e67e22"),
]

for i, (text, func, color) in enumerate(buttons):
    btn = tk.Button(button_frame, text=text, command=func, 
                   font=("Segoe UI", 12, "bold"), 
                   height=2, width=35,
                   bg=color, fg="white",
                   relief="flat", 
                   cursor="hand2")
    btn.pack(pady=8)
    
    # Hover effects
    def on_enter(event, btn=btn, original_color=color):
        btn.config(bg="#34495e")
    
    def on_leave(event, btn=btn, original_color=color):
        btn.config(bg=original_color)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# Footer
footer_frame = tk.Frame(root, bg="#2c3e50", height=40)
footer_frame.pack(fill="x", side="bottom")
footer_frame.pack_propagate(False)

footer_label = tk.Label(footer_frame, text="PDF Toolkit v2.0 - Drag & Drop Support Coming Soon", 
                       font=("Segoe UI", 8), 
                       fg="#7f8c8d", bg="#2c3e50")
footer_label.pack(expand=True)

if __name__ == "__main__":
    root.mainloop()