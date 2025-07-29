import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from converter.hwp_to_pdf import convert_hwp_to_pdf
from converter.xlsx_to_pdf import convert_xlsx_to_pdf

BASE_URL = "https://www.fss.or.kr"
LIST_URL = f"{BASE_URL}/fss/job/lrgRegItnPrvntc/list.do"
HWP_DIR = "data/hwp"
XLSX_DIR = "data/xlsx"
PDF_DIR = "data/pdf"
IMG_DIR = "data/img"
JSON_PATH = "data/json/fss_pre.json"

os.makedirs(HWP_DIR, exist_ok=True)
os.makedirs(XLSX_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs("data/json", exist_ok=True)

def crawl():
    results = []
    page_index = 1

    while True:
        print(f"\n[PAGE {page_index}] 크롤링 중...")
        params = {"menuNo": "200489", "pageIndex": str(page_index)}
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(LIST_URL, params=params, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.select("table tbody tr")
        if not rows:
            print("게시글 없음, 종료")
            break

        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 3:
                continue

            a_tag = tds[1].find("a")
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            detail_url = urljoin(BASE_URL, a_tag.get("href"))
            date_str = tds[2].get_text(strip=True)

            if not date_str.startswith("2025"):
                print("2025년 이전 게시물 도달, 종료")
                return results

            print(f"\n게시글: {title} / 날짜: {date_str}")
            print(f"상세 페이지: {detail_url}")

            attachments, already_exists = get_detail_info(detail_url)

            if already_exists:
                print("최신 PDF가 이미 존재함. 크롤링 종료.")
                return results

            results.append({
                "title": title,
                "date": date_str,
                "source": "금융감독원",
                "url": detail_url,
                "type": "세칙제개정예고",
                "attachments": attachments,
                "text": ""
            })

        page_index += 1

    return results

def get_detail_info(detail_url):
    res = requests.get(detail_url)
    soup = BeautifulSoup(res.text, "html.parser")
    attachment_div = soup.select_one("div.file-list__set")

    attachments = []
    if not attachment_div:
        return attachments, False

    for a_tag in attachment_div.find_all("a"):
        filename = a_tag.get_text(strip=True)
        file_url = urljoin(detail_url, a_tag.get("href"))
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".hwp":
            local_path = os.path.abspath(os.path.join(HWP_DIR, filename))
            with open(local_path, "wb") as f:
                f.write(requests.get(file_url).content)

            pdf_path = os.path.join(PDF_DIR, os.path.splitext(filename)[0] + ".pdf")
            if os.path.exists(pdf_path):
                print(f"이미 변환된 PDF 있음: {pdf_path}")
                return [], True

            _, attach = convert_hwp_to_pdf(local_path, PDF_DIR)

        elif ext == ".xlsx":
            local_path = os.path.abspath(os.path.join(XLSX_DIR, filename))
            with open(local_path, "wb") as f:
                f.write(requests.get(file_url).content)

            pdf_path = os.path.join(PDF_DIR, os.path.splitext(filename)[0] + ".pdf")
            if os.path.exists(pdf_path):
                print(f"이미 변환된 PDF 있음: {pdf_path}")
                return [], True

            _, attach = convert_xlsx_to_pdf(local_path, PDF_DIR)

        else:
            continue

        base = os.path.splitext(attach["filename"])[0]
        attach.update({
            "imgname": base + ".jpg",
            "imgpath": f"data/img/{base}.jpg",
            "path": f"data/{attach['path']}"
        })
        attachments.append(attach)

    return attachments, False

if __name__ == "__main__":
    data = crawl()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{len(data)}건 저장 완료 → {JSON_PATH}")
