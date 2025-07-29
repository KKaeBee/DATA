import os
import fitz  # PyMuPDF

def convert_pdf_to_jpg(pdf_dir: str, img_dir: str) -> list[dict]:
    os.makedirs(img_dir, exist_ok=True)
    results = []

    for pdf_filename in os.listdir(pdf_dir):
        if not pdf_filename.lower().endswith('.pdf'):
            continue

        pdf_path = os.path.join(pdf_dir, pdf_filename)
        doc = fitz.open(pdf_path)

        base_name = os.path.splitext(pdf_filename)[0]
        imgnames = []
        imgpaths = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)
            img_filename = f"{base_name}_{page_num + 1}.jpg"
            img_path = os.path.join(img_dir, img_filename)
            pix.save(img_path)

            imgrel_path = os.path.relpath(img_path, start=os.getcwd()).replace("\\", "/")
            imgnames.append(img_filename)
            imgpaths.append(imgrel_path)

        results.append({
            "filename": pdf_filename,
            "path": os.path.relpath(pdf_path, start=os.getcwd()).replace("\\", "/"),
            "imgname": imgnames,
            "imgpath": imgpaths
        })

    return results
