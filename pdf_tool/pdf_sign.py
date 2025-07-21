import os
import fitz
from PIL import Image, ImageDraw, ImageFont


class PDFESignTool:
    def add_text(self, pdf_path, output_path, page, text, x, y, size=12):
        doc = fitz.open(pdf_path)
        page_obj = doc[page - 1]
        rect = fitz.Rect(x, y, x + 200, y + 30)
        page_obj.insert_textbox(rect, text, fontsize=size, color=(0, 0, 0))
        doc.save(output_path)
        doc.close()
        
    def add_image(self, pdf_path, output_path, page, image_path, x, y, width=100, height=50):
        doc = fitz.open(pdf_path)
        page_obj = doc[page - 1]
        rect = fitz.Rect(x, y, x + width, y + height)
        page_obj.insert_image(rect, filename=image_path)
        doc.save(output_path)
        doc.close()
        
    def create_signature_image(self, text, output_path):
        img = Image.new("RGB", (200, 60), "white")
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((10, 20), text, font=font, fill="black")
        img.save(output_path)


def main():
    signer = PDFESignTool()
    
    print("PDF E-Sign Tool")
    pdf_path = input("PDF file: ").strip('"')
    page = int(input("Page number: "))
    x = float(input("X position: "))
    y = float(input("Y position: "))
    output = input("Output filename: ") + ".pdf"
    
    choice = input("1=Text, 2=Image, 3=Draw: ")
    
    if choice == "1":
        text = input("Signature text: ")
        size = int(input("Font size (12): ") or 12)
        signer.add_text(pdf_path, output, page, text, x, y, size)
        
    elif choice == "2":
        img_path = input("Image path: ").strip('"')
        width = int(input("Width (100): ") or 100)
        height = int(input("Height (50): ") or 50)
        signer.add_image(pdf_path, output, page, img_path, x, y, width, height)
        
    elif choice == "3":
        text = input("Signature text: ")
        temp_img = "temp_sig.png"
        signer.create_signature_image(text, temp_img)
        signer.add_image(pdf_path, output, page, temp_img, x, y)
        os.remove(temp_img)
    
    print(f"Done! Saved as: {output}")


if __name__ == "__main__":
    main()
