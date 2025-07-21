import os
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter


class PDFEditor:
    def __init__(self):
        pass

    def delete_pages(self, input_pdf, output_pdf, pages_to_delete):
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        for i in range(total_pages):
            if i not in pages_to_delete:
                writer.add_page(reader.pages[i])

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return True, f"Deleted pages {pages_to_delete} and saved to: {output_pdf}"

    def rotate_pages(self, input_pdf, output_pdf, rotate_pages, rotation=90):
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        for i, page in enumerate(reader.pages):
            if i in rotate_pages:
                page.rotate(rotation)
            writer.add_page(page)

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return True, f"Rotated pages {rotate_pages} by {rotation} degrees and saved to: {output_pdf}"

    def extract_pages(self, input_pdf, output_pdf, pages_to_extract):
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        for i in pages_to_extract:
            writer.add_page(reader.pages[i])

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return True, f"Extracted pages {pages_to_extract} to: {output_pdf}"

    def add_text_to_pdf(self, input_pdf, output_pdf, page_number, text, x, y, font_size=12):
        try:
            doc = fitz.open(input_pdf)

            if page_number < 1 or page_number > len(doc):
                return False, f"Invalid page number: {page_number}"

            page = doc[page_number - 1]
            page.insert_text((x, y), text, fontsize=font_size, fontname="helv", fill=(0, 0, 0))

            doc.save(output_pdf)
            doc.close()
            return True, f"Text added on page {page_number} and saved to: {output_pdf}"
        except Exception as e:
            return False, f"Failed to add text: {str(e)}"


def get_pdf_path():
    while True:
        path = input("Enter path to PDF file: ").strip().strip('"').strip("'")
        if os.path.isfile(path) and path.lower().endswith(".pdf"):
            return path
        print("❌ Invalid PDF file. Try again.")


def get_output_folder():
    while True:
        path = input("Enter output folder path: ").strip().strip('"').strip("'")
        if not path:
            path = os.getcwd()
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                print(f"✅ Created directory: {path}")
            except Exception as e:
                print(f"❌ Failed to create directory: {e}")
                continue
        if os.path.isdir(path):
            return path
        else:
            print("❌ Not a valid directory.")


def get_output_filename(default_name):
    name = input(f"Enter output filename (default: {default_name}): ").strip()
    return f"{name}.pdf" if name else default_name


def main():
    editor = PDFEditor()
    input_pdf = get_pdf_path()
    output_dir = get_output_folder()

    print("\nAvailable editing options:")
    print("1. Delete specific pages")
    print("2. Rotate specific pages")
    print("3. Extract specific pages")
    print("4. Add text to a page")
    choice = input("Select option (1-4): ").strip()

    if choice not in ["1", "2", "3", "4"]:
        print("❌ Invalid choice. Exiting.")
        return

    try:
        if choice in ["1", "2", "3"]:
            reader = PdfReader(input_pdf)
            total_pages = len(reader.pages)
            print(f"\nPDF has {total_pages} pages.")
            page_input = input("Enter page numbers (1-based, comma separated): ")
            pages = sorted(set(int(p) - 1 for p in page_input.split(",") if p.strip().isdigit()))

            if any(p < 0 or p >= total_pages for p in pages):
                print("❌ Invalid page numbers.")
                return

            if choice == "1":
                output_file = os.path.join(output_dir, get_output_filename("deleted_pages.pdf"))
                success, message = editor.delete_pages(input_pdf, output_file, pages)
            elif choice == "2":
                degrees = int(input("Enter rotation in degrees (90, 180, 270): ").strip())
                output_file = os.path.join(output_dir, get_output_filename("rotated_pages.pdf"))
                success, message = editor.rotate_pages(input_pdf, output_file, pages, degrees)
            elif choice == "3":
                output_file = os.path.join(output_dir, get_output_filename("extracted_pages.pdf"))
                success, message = editor.extract_pages(input_pdf, output_file, pages)

        elif choice == "4":
            text = input("Enter the text to add: ").strip()
            page_number = int(input("Enter page number to add text (1-based): ").strip())
            x = float(input("Enter X position (in points): ").strip())
            y = float(input("Enter Y position (in points): ").strip())
            font_size = int(input("Enter font size (default 12): ").strip() or "12")

            output_file = os.path.join(output_dir, get_output_filename("text_added.pdf"))
            success, message = editor.add_text_to_pdf(input_pdf, output_file, page_number, text, x, y, font_size)

        print(message)

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
