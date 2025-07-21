import os
from pypdf import PdfReader, PdfWriter

class PDFSplitter:
    def __init__(self):
        pass
    
    def get_pdf_info(self, file_path):
        """Get PDF file information"""
        try:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            reader = PdfReader(file_path)
            pages = len(reader.pages)
            return f"{filename} ({pages} pages, {file_size:.1f} MB)"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def validate_file_path(self, file_path):
        """Validate if the PDF file exists and is readable"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF (.pdf extension)")
        
        try:
            reader = PdfReader(file_path)
            return len(reader.pages)
        except Exception as e:
            raise ValueError(f"Cannot read PDF file: {str(e)}")
    
    def validate_output_directory(self, output_dir):
        """Validate and create output directory if needed"""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            elif not os.path.isdir(output_dir):
                raise ValueError(f"Output path exists but is not a directory: {output_dir}")
        except Exception as e:
            raise ValueError(f"Cannot create output directory: {str(e)}")
    
    def validate_split_input(self, sizes_input, fixed_size_input, start_page, total_pages):
        """Validate split input parameters"""
        if start_page < 1 or start_page > total_pages:
            raise ValueError(f"Start page must be between 1 and {total_pages}")
        
        if sizes_input:
            split_sizes = [int(x.strip()) for x in sizes_input.split(',') if x.strip().isdigit()]
            if not split_sizes or any(s <= 0 for s in split_sizes):
                raise ValueError("Custom split sizes must be positive numbers")
            
            remaining_pages = total_pages - start_page + 1
            if sum(split_sizes) > remaining_pages:
                raise ValueError(f"Total pages in split sizes ({sum(split_sizes)}) exceeds remaining pages ({remaining_pages})")
            
            return split_sizes, None
        else:
            pages_per_split = int(fixed_size_input) if fixed_size_input else 1
            if pages_per_split <= 0:
                raise ValueError("Pages per split must be positive")
            return None, pages_per_split
    
    def split_by_custom_sizes(self, pdf_path, output_dir, split_sizes, start_page=1):
        """Split PDF by custom page sizes"""
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)

            if start_page < 1 or start_page > total_pages:
                raise ValueError("Start page is out of range.")

            current_page = start_page - 1  # 0-based
            part = 1

            for count in split_sizes:
                if current_page >= total_pages:
                    break

                writer = PdfWriter()
                end_page = min(current_page + count, total_pages)

                for i in range(current_page, end_page):
                    writer.add_page(reader.pages[i])

                output_path = os.path.join(
                    output_dir,
                    f"{os.path.splitext(os.path.basename(pdf_path))[0]}_part_{part}.pdf"
                )

                with open(output_path, "wb") as f:
                    writer.write(f)

                print(f"Created: {output_path} (pages {current_page + 1}-{end_page})")
                current_page = end_page
                part += 1

            return True, f"Split completed into {part - 1} parts.\nSaved in: {output_dir}"
            
        except Exception as e:
            return False, f"An error occurred: {str(e)}"
    
    def split_by_fixed_size(self, pdf_path, output_dir, pages_per_split, start_page=1):
        """Split PDF by fixed page size"""
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)

            if start_page < 1 or start_page > total_pages:
                raise ValueError("Start page is out of range.")

            current_page = start_page - 1
            part = 1

            while current_page < total_pages:
                writer = PdfWriter()
                end_page = min(current_page + pages_per_split, total_pages)

                for i in range(current_page, end_page):
                    writer.add_page(reader.pages[i])

                output_path = os.path.join(
                    output_dir,
                    f"{os.path.splitext(os.path.basename(pdf_path))[0]}_part_{part}.pdf"
                )

                with open(output_path, "wb") as f:
                    writer.write(f)

                print(f"Created: {output_path} (pages {current_page + 1}-{end_page})")
                current_page = end_page
                part += 1

            return True, f"PDF split into {part - 1} parts.\nSaved in: {output_dir}"
            
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

def get_user_input():
    """Get user input for file paths and split options"""
    print("=" * 50)
    print("         PDF SPLITTER TOOL")
    print("=" * 50)
    
    # Get input PDF file
    while True:
        pdf_path = input("\nEnter the path to your PDF file: ").strip()
        if not pdf_path:
            print("Please enter a valid file path.")
            continue
        
        # Handle quotes around path
        pdf_path = pdf_path.strip('"').strip("'")
        
        try:
            splitter = PDFSplitter()
            total_pages = splitter.validate_file_path(pdf_path)
            print(f"\nFile info: {splitter.get_pdf_info(pdf_path)}")
            break
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            print("Please try again.")
    
    # Get output directory
    while True:
        output_dir = input("\nEnter output directory path: ").strip()
        if not output_dir:
            print("Please enter a valid directory path.")
            continue
        
        # Handle quotes around path
        output_dir = output_dir.strip('"').strip("'")
        
        try:
            splitter.validate_output_directory(output_dir)
            break
        except ValueError as e:
            print(f"Error: {e}")
            print("Please try again.")
    
    # Get start page
    while True:
        start_input = input(f"\nEnter start page (1-{total_pages}) [default: 1]: ").strip()
        if not start_input:
            start_page = 1
            break
        
        try:
            start_page = int(start_input)
            if 1 <= start_page <= total_pages:
                break
            else:
                print(f"Start page must be between 1 and {total_pages}")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get split method
    print("\nChoose split method:")
    print("1. Fixed size (same number of pages per file)")
    print("2. Custom sizes (specify pages for each file)")
    
    while True:
        method = input("Enter choice (1 or 2): ").strip()
        if method in ['1', '2']:
            break
        print("Please enter 1 or 2.")
    
    if method == '1':
        # Fixed size
        while True:
            try:
                pages_per_split = input("Enter pages per split file: ").strip()
                pages_per_split = int(pages_per_split)
                if pages_per_split > 0:
                    return pdf_path, output_dir, start_page, total_pages, None, pages_per_split
                else:
                    print("Pages per split must be positive.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        # Custom sizes
        remaining_pages = total_pages - start_page + 1
        print(f"\nRemaining pages to split: {remaining_pages}")
        print("Enter page counts separated by commas (e.g., 3,2,4)")
        
        while True:
            sizes_input = input("Enter custom sizes: ").strip()
            try:
                split_sizes = [int(x.strip()) for x in sizes_input.split(',') if x.strip().isdigit()]
                if not split_sizes or any(s <= 0 for s in split_sizes):
                    print("Custom split sizes must be positive numbers")
                    continue
                
                if sum(split_sizes) > remaining_pages:
                    print(f"Total pages in split sizes ({sum(split_sizes)}) exceeds remaining pages ({remaining_pages})")
                    continue
                
                return pdf_path, output_dir, start_page, total_pages, split_sizes, None
            except ValueError:
                print("Please enter valid numbers separated by commas.")

def main():
    """Main function to run the PDF splitter with user input"""
    try:
        pdf_path, output_dir, start_page, total_pages, split_sizes, pages_per_split = get_user_input()
        
        splitter = PDFSplitter()
        
        print(f"\nProcessing...")
        print(f"Input file: {pdf_path}")
        print(f"Output directory: {output_dir}")
        print(f"Starting from page: {start_page}")
        
        if split_sizes:
            print(f"Custom split sizes: {split_sizes}")
            success, message = splitter.split_by_custom_sizes(pdf_path, output_dir, split_sizes, start_page)
        else:
            print(f"Pages per split: {pages_per_split}")
            success, message = splitter.split_by_fixed_size(pdf_path, output_dir, pages_per_split, start_page)
        
        print(f"\n{'SUCCESS' if success else 'ERROR'}: {message}")
        
        if success:
            print(f"\nAll split files have been saved to: {os.path.abspath(output_dir)}")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    main()