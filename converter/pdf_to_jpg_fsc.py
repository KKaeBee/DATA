import os
import json
import fitz  # PyMuPDF

# 경로 설정
PDF_DIR = "data/pdf"
IMG_DIR = "data/img"
FSC_JSON_PATH = "data/json/fsc.json"

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

        rel_imgpath = os.path.relpath(imgpath).replace("\\", "/")
        imgnames.append(imgname)
        imgpaths.append(rel_imgpath)

    return imgnames, imgpaths

# fsc.json 불러오기
with open(FSC_JSON_PATH, "r", encoding="utf-8") as f:
    fsc_data = json.load(f)

# 각 attachment에 대해 이미지 변환 및 재구성
converted = []
for entry in fsc_data:
    new_entry = {
        "title": entry.get("title", ""),
        "date": entry.get("date", ""),
        "source": entry.get("source", ""),
        "url": entry.get("url", ""),
        "type": {
            "notice_type": entry.get("notice_type", ""),
            "law_type": entry.get("law_type", "")
        },
        "attachments": [],
        "text": ""
    }

    for att in entry.get("attachments", []):
        pdf_path = att["path"]
        full_pdf_path = os.path.join(os.getcwd(), pdf_path)

        if os.path.exists(full_pdf_path):
            imgnames, imgpaths = convert_pdf_to_jpg(full_pdf_path, IMG_DIR)
        else:
            print(f"[경고] PDF 파일 없음: {full_pdf_path}")
            imgnames, imgpaths = [], []

        new_att = {
            "filename": att["filename"],
            "path": att["path"],
            "imgname": imgnames,
            "imgpath": imgpaths
        }

        new_entry["attachments"].append(new_att)

    converted.append(new_entry)

# 덮어쓰기 저장
with open(FSC_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=2, ensure_ascii=False)

print("fsc.json이 성공적으로 업데이트되었습니다.")
