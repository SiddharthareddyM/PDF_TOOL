import os
import fitz  # PyMuPDF


class PDFCompressor:
    def __init__(self):
        pass

    def compress_pdf(self, input_path, output_path):
        """
        Compress PDF by rewriting the document with garbage collection and object deflation.
        This reduces file size for many PDFs with unused objects or uncompressed streams.
        """
        try:
            doc = fitz.open(input_path)
            doc.save(output_path, garbage=4, deflate=True, clean=True)
            doc.close()
            return True, f"✅ PDF compressed and saved to: {output_path}"
        except Exception as e:
            return False, f"❌ Compression failed: {str(e)}"


def get_input_file():
    while True:
        path = input("Enter path to PDF file: ").strip().strip('"').strip("'")
        if os.path.isfile(path) and path.lower().endswith(".pdf"):
            return path
        print("❌ Invalid file. Try again.")


def get_output_folder():
    while True:
        path = input("Enter output directory path: ").strip().strip('"').strip("'")
        if not path:
            path = os.getcwd()
            break
        if os.path.isdir(path):
            break
        else:
            try:
                os.makedirs(path)
                print(f"✅ Created directory: {path}")
                break
            except Exception as e:
                print(f"❌ Failed to create directory: {e}")
    return path


def get_output_filename():
    name = input("Enter output filename (without extension): ").strip()
    return f"{name}.pdf" if name else "compressed_output.pdf"


def main():
    compressor = PDFCompressor()
    input_file = get_input_file()
    output_dir = get_output_folder()
    output_filename = get_output_filename()
    output_path = os.path.join(output_dir, output_filename)

    print(f"\n🔄 Compressing: {input_file}")
    print(f"📁 Saving to: {output_path}")

    success, message = compressor.compress_pdf(input_file, output_path)
    print(message)


if __name__ == "__main__":
    main()
