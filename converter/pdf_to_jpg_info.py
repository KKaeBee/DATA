import os
import json
import fitz  # PyMuPDF

# 경로 설정
PDF_DIR = "data/pdf"
IMG_DIR = "data/img"
FSS_INFO_PATH = "data/json/fss_info.json"

# PDF → JPG 변환 함수
def convert_pdf_to_jpg(pdf_path, img_dir):
    os.makedirs(img_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    imgnames, imgpaths = [], []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=200)
        imgname = f"{base_name}_{page_num + 1}.jpg"
        imgpath = os.path.join(img_dir, imgname)
        pix.save(imgpath)

        # 경로는 상대경로로 저장
        rel_imgpath = os.path.relpath(imgpath).replace("\\", "/")
        imgnames.append(imgname)
        imgpaths.append(rel_imgpath)

    return imgnames, imgpaths

# fss_info.json 불러오기
with open(FSS_INFO_PATH, "r", encoding="utf-8") as f:
    fss_info = json.load(f)

# 각 attachment에 대해 이미지 변환 및 결과 추가
for entry in fss_info:
    for att in entry.get("attachments", []):
        pdf_path = att["path"]
        full_pdf_path = os.path.join(os.getcwd(), pdf_path)
        if os.path.exists(full_pdf_path):
            imgnames, imgpaths = convert_pdf_to_jpg(full_pdf_path, IMG_DIR)
            att["imgname"] = imgnames
            att["imgpath"] = imgpaths
        else:
            print(f"[경고] PDF 파일이 존재하지 않음: {full_pdf_path}")

# 업데이트된 fss_info.json 저장
with open(FSS_INFO_PATH, "w", encoding="utf-8") as f:
    json.dump(fss_info, f, indent=2, ensure_ascii=False)

print("fss_info.json이 성공적으로 업데이트되었습니다.")
