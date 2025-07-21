import os
import sys

# Import conversion libraries with error handling
try:
    from pdf2docx import Converter
    from docx import Document
    from docx2pdf import convert as docx_to_pdf
    PDF_WORD_AVAILABLE = True
except ImportError:
    PDF_WORD_AVAILABLE = False

try:
    from PIL import Image
    IMAGE_CONVERSION_AVAILABLE = True
except ImportError:
    IMAGE_CONVERSION_AVAILABLE = False

class FileConverter:
    def __init__(self):
        self.supported_formats = {
            'pdf_to_word': ['.pdf'],
            'word_to_pdf': ['.docx', '.doc'],
            'image_to_pdf': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        }
    
    def get_file_info(self, file_path):
        """Get file information for display"""
        try:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            if file_path.lower().endswith('.pdf'):
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(file_path)
                    pages = len(reader.pages)
                    return f"{filename} ({pages} pages, {file_size:.1f} MB)"
                except ImportError:
                    return f"{filename} (PDF, {file_size:.1f} MB)"
            elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')):
                if IMAGE_CONVERSION_AVAILABLE:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        return f"{filename} ({width}x{height}px, {file_size:.1f} MB)"
                else:
                    return f"{filename} ({file_size:.1f} MB)"
            else:
                return f"{filename} ({file_size:.1f} MB)"
                
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def get_conversion_type(self, file_path):
        """Determine what type of conversion is possible"""
        if not file_path:
            return None, "No file selected"
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return 'pdf_to_word', "PDF → Word conversion"
        elif ext in ['.docx', '.doc']:
            return 'word_to_pdf', "Word → PDF conversion"
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            return 'image_to_pdf', "Image → PDF conversion"
        else:
            return None, f"Unsupported file type: {ext}"
    
    def check_dependencies(self, conversion_type):
        """Check if required dependencies are available"""
        if conversion_type in ['pdf_to_word', 'word_to_pdf']:
            if not PDF_WORD_AVAILABLE:
                return False, "Required libraries missing. Install with: pip install pdf2docx python-docx docx2pdf"
        elif conversion_type == 'image_to_pdf':
            if not IMAGE_CONVERSION_AVAILABLE:
                return False, "Required library missing. Install with: pip install pillow"
        
        return True, "Dependencies available"
    
    def pdf_to_word(self, pdf_path, output_dir, output_filename=None):
        """Convert PDF to Word document"""
        try:
            if not PDF_WORD_AVAILABLE:
                raise ImportError("Required libraries not installed. Please install: pip install pdf2docx python-docx")
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            if not output_filename:
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                output_filename = f"{base_name}_converted.docx"
            
            if not output_filename.endswith('.docx'):
                output_filename += '.docx'
            
            output_path = os.path.join(output_dir, output_filename)
            
            # Convert PDF to Word
            cv = Converter(pdf_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()
            
            return True, f"PDF converted to Word successfully!\nSaved as: {output_path}"
            
        except Exception as e:
            return False, f"PDF to Word conversion failed: {str(e)}"
    
    def word_to_pdf(self, word_path, output_dir, output_filename=None):
        """Convert Word document to PDF"""
        try:
            if not PDF_WORD_AVAILABLE:
                raise ImportError("Required libraries not installed. Please install: pip install python-docx docx2pdf")
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            if not output_filename:
                base_name = os.path.splitext(os.path.basename(word_path))[0]
                output_filename = f"{base_name}_converted.pdf"
            
            if not output_filename.endswith('.pdf'):
                output_filename += '.pdf'
            
            output_path = os.path.join(output_dir, output_filename)
            
            # Convert Word to PDF
            docx_to_pdf(word_path, output_path)
            
            return True, f"Word document converted to PDF successfully!\nSaved as: {output_path}"
            
        except Exception as e:
            return False, f"Word to PDF conversion failed: {str(e)}"
    
    def image_to_pdf(self, image_path, output_dir, output_filename=None):
        """Convert image to PDF"""
        try:
            if not IMAGE_CONVERSION_AVAILABLE:
                raise ImportError("Required library not installed. Please install: pip install pillow")
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            if not output_filename:
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_filename = f"{base_name}_converted.pdf"
            
            if not output_filename.endswith('.pdf'):
                output_filename += '.pdf'
            
            output_path = os.path.join(output_dir, output_filename)
            
            # Open and convert image to PDF
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as PDF
                img.save(output_path, "PDF", resolution=100.0)
            
            return True, f"Image converted to PDF successfully!\nSaved as: {output_path}"
            
        except Exception as e:
            return False, f"Image to PDF conversion failed: {str(e)}"
    
    def convert_file(self, input_path, output_dir, output_filename=None):
        """Universal conversion method"""
        conversion_type, type_desc = self.get_conversion_type(input_path)
        
        if not conversion_type:
            return False, type_desc
        
        # Check dependencies
        deps_ok, deps_msg = self.check_dependencies(conversion_type)
        if not deps_ok:
            return False, deps_msg
        
        # Perform conversion
        if conversion_type == 'pdf_to_word':
            return self.pdf_to_word(input_path, output_dir, output_filename)
        elif conversion_type == 'word_to_pdf':
            return self.word_to_pdf(input_path, output_dir, output_filename)
        elif conversion_type == 'image_to_pdf':
            return self.image_to_pdf(input_path, output_dir, output_filename)
        else:
            return False, f"Conversion type '{conversion_type}' not implemented"

def get_user_input():
    """Get input file path from user with validation"""
    print("=" * 60)
    print("           FILE CONVERTER UTILITY")
    print("=" * 60)
    print("Supported conversions:")
    print("• PDF → Word (.docx)")
    print("• Word (.docx/.doc) → PDF")
    print("• Image (jpg, png, bmp, tiff) → PDF")
    print("=" * 60)
    
    while True:
        input_file = input("\nEnter the path to your input file: ").strip()
        
        # Handle empty input
        if not input_file:
            print("❌ Please enter a valid file path.")
            continue
        
        # Remove quotes if user added them
        input_file = input_file.strip('"').strip("'")
        
        # Check if file exists
        if not os.path.exists(input_file):
            print(f"❌ File not found: {input_file}")
            retry = input("Try again? (y/n): ").lower().strip()
            if retry != 'y':
                return None, None, None
            continue
        
        # Check if it's a file (not directory)
        if not os.path.isfile(input_file):
            print(f"❌ Path is not a file: {input_file}")
            continue
        
        return input_file
    
def get_output_location():
    """Get output directory from user"""
    while True:
        print("\nOutput location options:")
        print("1. Use current directory")
        print("2. Specify custom directory")
        
        choice = input("Choose option (1 or 2): ").strip()
        
        if choice == '1':
            return os.getcwd()
        elif choice == '2':
            output_dir = input("Enter output directory path: ").strip()
            output_dir = output_dir.strip('"').strip("'")
            
            # Create directory if it doesn't exist
            try:
                if not os.path.exists(output_dir):
                    create = input(f"Directory doesn't exist. Create '{output_dir}'? (y/n): ").lower().strip()
                    if create == 'y':
                        os.makedirs(output_dir)
                        print(f"✅ Directory created: {output_dir}")
                        return output_dir
                    else:
                        continue
                else:
                    return output_dir
            except Exception as e:
                print(f"❌ Error with directory: {str(e)}")
                continue
        else:
            print("❌ Please enter 1 or 2")

def get_output_filename():
    """Get custom output filename from user"""
    filename = input("\nEnter custom output filename (or press Enter for auto-generated): ").strip()
    return filename if filename else None

def main():
    """Main interactive function"""
    converter = FileConverter()
    
    try:
        # Get input file
        input_file = get_user_input()
        if not input_file:
            print("Exiting...")
            return
        
        # Display file info
        print(f"\n📁 File info: {converter.get_file_info(input_file)}")
        
        # Get conversion type
        conv_type, conv_desc = converter.get_conversion_type(input_file)
        if not conv_type:
            print(f"❌ {conv_desc}")
            return
        
        print(f"🔄 Conversion type: {conv_desc}")
        
        # Check dependencies
        deps_ok, deps_msg = converter.check_dependencies(conv_type)
        print(f"📦 Dependencies: {deps_msg}")
        
        if not deps_ok:
            print("❌ Cannot proceed - missing dependencies")
            return
        
        # Get output location
        output_dir = get_output_location()
        if not output_dir:
            print("Exiting...")
            return
        
        # Get custom filename (optional)
        output_filename = get_output_filename()
        
        # Perform conversion
        print(f"\n🔄 Converting file...")
        print(f"   Input: {input_file}")
        print(f"   Output Directory: {output_dir}")
        if output_filename:
            print(f"   Output Filename: {output_filename}")
        
        success, message = converter.convert_file(input_file, output_dir, output_filename)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

def batch_convert():
    """Batch conversion for multiple files"""
    converter = FileConverter()
    
    print("\n" + "=" * 60)
    print("           BATCH CONVERSION MODE")
    print("=" * 60)
    
    files_to_convert = []
    
    # Get multiple files
    while True:
        file_path = input(f"\nEnter file path #{len(files_to_convert) + 1} (or press Enter to finish): ").strip()
        
        if not file_path:
            if files_to_convert:
                break
            else:
                print("❌ Please add at least one file.")
                continue
        
        file_path = file_path.strip('"').strip("'")
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            files_to_convert.append(file_path)
            print(f"✅ Added: {os.path.basename(file_path)}")
        else:
            print(f"❌ File not found: {file_path}")
    
    if not files_to_convert:
        print("No files to convert.")
        return
    
    # Get output directory
    output_dir = get_output_location()
    if not output_dir:
        return
    
    # Convert all files
    print(f"\n🔄 Converting {len(files_to_convert)} file(s)...")
    
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(files_to_convert, 1):
        print(f"\n[{i}/{len(files_to_convert)}] Converting {os.path.basename(file_path)}...")
        
        success, message = converter.convert_file(file_path, output_dir)
        
        if success:
            print(f"✅ {message}")
            successful += 1
        else:
            print(f"❌ {message}")
            failed += 1
    
    print(f"\n" + "=" * 60)
    print(f"BATCH CONVERSION COMPLETE")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(files_to_convert)}")
    print("=" * 60)

if __name__ == "__main__":
    while True:
        print("\n" + "=" * 60)
        print("           FILE CONVERTER MENU")
        print("=" * 60)
        print("1. Convert single file")
        print("2. Batch convert multiple files")
        print("3. Exit")
        print("=" * 60)
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == '1':
            main()
        elif choice == '2':
            batch_convert()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("❌ Please enter 1, 2, or 3")
        
        # Ask if user wants to continue
        if choice in ['1', '2']:
            continue_choice = input("\nPerform another conversion? (y/n): ").lower().strip()
            if continue_choice != 'y':
                print("Goodbye!")
                break