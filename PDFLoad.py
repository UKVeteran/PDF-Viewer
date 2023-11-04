import tkinter as tk
from tkinter import filedialog
import fitz  # PyMuPDF
from PIL import Image, ImageTk

class PDFViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Viewer")

        self.load_button = tk.Button(root, text="Load PDF", command=self.load_pdf)
        self.load_button.pack()

        self.page_var = tk.StringVar()
        self.page_label = tk.Label(root, textvariable=self.page_var)
        self.page_label.pack()

        self.pdf_canvas = tk.Canvas(root, bg="white")
        self.pdf_canvas.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.scroll_canvas)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.pdf_canvas.config(xscrollcommand=self.scrollbar.set)

        self.current_page = 0
        self.pdf_path = None
        self.pdf_images = []
        self.pdf_document = None

        self.left_button = tk.Button(root, text="Previous Page", command=self.previous_page)
        self.left_button.pack(side=tk.LEFT)

        self.right_button = tk.Button(root, text="Next Page", command=self.next_page)
        self.right_button.pack(side=tk.RIGHT)

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            self.pdf_document = fitz.open(file_path)
            self.pdf_images = self.convert_pdf_to_images()
            self.show_page()

    def convert_pdf_to_images(self):
        images = []
        for page in self.pdf_document:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        return images

    def show_page(self):
        if self.pdf_path and self.pdf_images:
            self.page_var.set(f"Page {self.current_page + 1} / {len(self.pdf_images)}")
            self.render_pdf_page(self.current_page)

    def render_pdf_page(self, page_num):
        self.pdf_canvas.delete("all")
        x0, y0, x1, y1 = 50, 50, 550, 750
        img = self.pdf_images[page_num]
        img = self.resize_image(img, (x1 - x0, y1 - y0))
        self.pdf_canvas.create_image(x0, y0, anchor=tk.NW, image=img)
        self.render_text_overlay(page_num, (x0, y0))
        self.pdf_canvas.config(scrollregion=self.pdf_canvas.bbox("all"))

    def render_text_overlay(self, page_num, offset):
        if self.pdf_document:
            page = self.pdf_document[page_num]
            for block in page.get_text("blocks"):
                for line in block:
                    for span in line:
                        text = span[4]
                        x0, y0, x1, y1 = span[:4]
                        x0, y0, x1, y1 = x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]
                        self.pdf_canvas.create_text(x0, y0, text=text, anchor=tk.NW)

    def resize_image(self, img, size):
        return ImageTk.PhotoImage(img.resize(size, Image.ANTIALIAS))

    def scroll_canvas(self, *args):
        self.pdf_canvas.xview(*args)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def next_page(self):
        if self.current_page < len(self.pdf_images) - 1:
            self.current_page += 1
            self.show_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewerApp(root)
    root.mainloop()
