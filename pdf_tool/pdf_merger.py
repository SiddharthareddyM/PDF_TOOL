import os
from pypdf import PdfReader, PdfWriter

class PDFMerger:
    def __init__(self):
        pass
    
    def get_file_info(self, file_path):
        """Get file information for display"""
        try:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            if file_path.lower().endswith('.pdf'):
                reader = PdfReader(file_path)
                pages = len(reader.pages)
                return f"{filename} ({pages} pages, {file_size:.1f} MB)"
            else:
                return f"{filename} ({file_size:.1f} MB)"
                
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def validate_files(self, pdf_paths):
        """Validate that all files exist and are readable"""
        if not pdf_paths:
            raise ValueError("No files provided")
        
        if len(pdf_paths) < 2:
            raise ValueError("At least two PDF files are required for merging")
        
        for path in pdf_paths:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"File not found: {path}")
            
            if not path.lower().endswith('.pdf'):
                raise ValueError(f"File is not a PDF: {os.path.basename(path)}")
    
    def merge_pdfs(self, pdf_paths, output_dir, output_filename="merged_output.pdf"):
        """Merge multiple PDF files into one"""
        try:
            # Validate inputs
            self.validate_files(pdf_paths)
            
            if not output_filename.endswith('.pdf'):
                output_filename += '.pdf'
            
            # Create output directory if it doesn't exist
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            
            # Merge PDFs
            writer = PdfWriter()
            total_pages = 0
            
            print("\nMerging files...")
            for i, path in enumerate(pdf_paths, 1):
                print(f"Processing file {i}/{len(pdf_paths)}: {os.path.basename(path)}")
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
                total_pages += len(reader.pages)
            
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            return True, f"Successfully merged {len(pdf_paths)} files ({total_pages} total pages)\nSaved as: {output_path}"
            
        except Exception as e:
            return False, f"Merge failed: {str(e)}"
    
    def get_merge_preview(self, pdf_paths):
        """Get a preview of what will be merged"""
        try:
            self.validate_files(pdf_paths)
            
            total_pages = 0
            file_details = []
            
            for i, path in enumerate(pdf_paths, 1):
                reader = PdfReader(path)
                pages = len(reader.pages)
                total_pages += pages
                filename = os.path.basename(path)
                file_details.append(f"{i}. {filename} - {pages} pages")
            
            preview = f"Merge Preview:\n" + "\n".join(file_details)
            preview += f"\n\nTotal files: {len(pdf_paths)}"
            preview += f"\nTotal pages: {total_pages}"
            
            return preview
            
        except Exception as e:
            return f"Preview error: {str(e)}"

def get_user_input():
    """Get input from user for PDF files and output settings"""
    print("=== PDF Merger Tool ===\n")
    
    # Get PDF files from user
    pdf_files = []
    print("Enter PDF file paths (press Enter after each path, type 'done' when finished):")
    
    while True:
        file_path = input(f"PDF file {len(pdf_files) + 1}: ").strip()
        
        if file_path.lower() == 'done':
            break
        
        if file_path:
            # Handle quoted paths (remove quotes)
            file_path = file_path.strip('"\'')
            
            # Check if file exists
            if os.path.isfile(file_path):
                if file_path.lower().endswith('.pdf'):
                    pdf_files.append(file_path)
                    print(f"✓ Added: {os.path.basename(file_path)}")
                else:
                    print(f"✗ Error: Not a PDF file")
            else:
                print(f"✗ Error: File not found")
        
        if len(pdf_files) >= 2:
            continue_adding = input(f"\nYou have {len(pdf_files)} files. Add more? (y/n): ").lower()
            if continue_adding not in ['y', 'yes']:
                break
    
    if len(pdf_files) < 2:
        print(f"Error: Need at least 2 PDF files. You provided {len(pdf_files)}.")
        return None, None, None
    
    # Get output directory
    print(f"\nOutput Settings:")
    while True:
        output_dir = input("Enter output directory path: ").strip().strip('"\'')
        
        if not output_dir:
            output_dir = os.getcwd()  # Use current directory if empty
            print(f"Using current directory: {output_dir}")
            break
        
        # Create directory if it doesn't exist
        try:
            if not os.path.exists(output_dir):
                create_dir = input(f"Directory '{output_dir}' doesn't exist. Create it? (y/n): ").lower()
                if create_dir in ['y', 'yes']:
                    os.makedirs(output_dir)
                    print(f"✓ Created directory: {output_dir}")
                    break
                else:
                    continue
            else:
                print(f"✓ Using directory: {output_dir}")
                break
        except Exception as e:
            print(f"✗ Error with directory: {e}")
    
    # Get output filename
    output_filename = input("Enter output filename (press Enter for 'merged_output.pdf'): ").strip()
    if not output_filename:
        output_filename = "merged_output.pdf"
    elif not output_filename.lower().endswith('.pdf'):
        output_filename += '.pdf'
    
    return pdf_files, output_dir, output_filename

def main():
    """Main function to run the interactive PDF merger"""
    merger = PDFMerger()
    
    try:
        # Get user input
        pdf_files, output_dir, output_filename = get_user_input()
        
        if not pdf_files:
            return
        
        # Show file information
        print(f"\n{'='*50}")
        print("File Information:")
        for i, file_path in enumerate(pdf_files, 1):
            info = merger.get_file_info(file_path)
            print(f"{i}. {info}")
        
        # Show preview
        print(f"\n{'='*50}")
        preview = merger.get_merge_preview(pdf_files)
        print(preview)
        
        # Confirm merge
        print(f"\n{'='*50}")
        print(f"Output will be saved as: {os.path.join(output_dir, output_filename)}")
        confirm = input("\nProceed with merge? (y/n): ").lower()
        
        if confirm not in ['y', 'yes']:
            print("Merge cancelled.")
            return
        
        # Perform merge
        print(f"\n{'='*50}")
        success, message = merger.merge_pdfs(pdf_files, output_dir, output_filename)
        
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()