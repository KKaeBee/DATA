import os
import json
import time
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PyPDF2 import PdfReader
import mimetypes

# MIME 수동 매핑 함수
def get_mime_type_by_extension(ext):
    print(f"MIME 매핑용 확장자 입력: {ext}")
    if ext == ".pdf":
        return "application/pdf"
    else:
        return "application/octet-stream"

BASE_URL = "https://www.fsc.go.kr"
LIST_URL = f"{BASE_URL}/po040301"

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PDF_DIR = os.path.join(BASE_DIR, "pdf")
JSON_DIR = os.path.join(BASE_DIR, "json")
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)


def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def is_valid_pdf(filepath):
    try:
        with open(filepath, 'rb') as f:
            return f.read(4) == b'%PDF'
    except:
        return False

def fetch_notice_list(page):
    url = f"{LIST_URL}?curPage={page}"
    driver = setup_driver()
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    notice_list = []
    items = soup.select(".board-list-wrap li")

    for item in items:
        title_tag = item.select_one(".subject a")
        info_tags = item.select(".info span")

        if not title_tag or not info_tags:
            continue

        title = title_tag.text.strip()
        href = title_tag['href']
        full_url = BASE_URL + href.replace("./", "/")

        info_map = {span.text.split(" : ")[0].strip(): span.text.split(" : ")[-1].strip() for span in info_tags}
        notice_type = info_map.get("구분", "")
        law_type = info_map.get("법률구분", "")
        period = info_map.get("예고기간", "")

        if "~" not in period:
            continue

        end_date_str = period.split("~")[-1].strip()
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except:
            continue

        if end_date > datetime.today().date():
            notice_list.append({
                "title": title,
                "date": period,
                "source": "금융위원회",
                "url": full_url,
                "notice_type": notice_type,
                "law_type": law_type,
                                
                "attachments": []
            })

    print(f"필터링된 공지 수: {len(notice_list)}")
    return notice_list

def get_full_download_links(detail_url):
    driver = setup_driver()
    driver.get(detail_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    files = []
    file_divs = soup.select("div.file-list")
    for div in file_divs:
        name_tag = div.select_one("span.name")
        link_tag = div.select_one("span.download a")
        if name_tag and link_tag:
            filename = name_tag.text.strip()
            href = link_tag["href"]
            download_url = BASE_URL + href
            files.append((filename, download_url))
    return files

def extract_pdf_text(filepath):
    try:
        reader = PdfReader(filepath)
        texts = [page.extract_text() or '' for page in reader.pages]
        return '\n'.join(texts).strip()
    except Exception as e:
        print(f"❌ PDF 텍스트 추출 실패: {filepath}, 이유: {e}")
        return ""

def download_file(filename, url):
    filename_clean = re.sub(r"(?<=\.pdf)\s*\(\d+\s*(KB|MB|bytes)\)", "", filename).strip()
    ext = os.path.splitext(filename_clean)[1].lower().strip()

    if ext != ".pdf":
        return None

    mime = mimetypes.guess_type(filename_clean)[0]
    if not mime:
        mime = get_mime_type_by_extension(ext)

    safe_filename = filename_clean.replace("/", "_").replace("\\", "_")
    save_path = os.path.join(PDF_DIR, safe_filename)

    if os.path.exists(save_path):
        print(f"이미 존재함, 스킵: {save_path}")
        return save_path

    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200 or len(response.content) < 1024:
            raise Exception("응답이 비정상 또는 파일이 너무 작음")

        with open(save_path, "wb") as f:
            f.write(response.content)

        print(f"✅ 저장됨: {save_path} (MIME: {mime})")

        if not is_valid_pdf(save_path):
            raise Exception("저장된 파일이 유효한 PDF가 아님")

        return save_path

    except Exception as e:
        print(f"❌ 다운로드 실패: {filename}, 이유: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return None


def main(max_pages=3):
    all_notices = []
    for page in range(1, max_pages + 1):
        print(f"\n{page}번째 리스트 페이지 크롤링 ღ₍ˆ ̳ , ̫ , ̳ˆ₎ ")
        notices = fetch_notice_list(page)

        for notice in notices:
            files = get_full_download_links(notice['url'])
            for filename, url in files:
                save_path = download_file(filename, url)
                if save_path:
                    text = extract_pdf_text(save_path)
                    filename_clean = os.path.basename(save_path)
                    notice["attachments"].append({
                        "filename": filename_clean,
                        "path": "data/pdf/" + filename_clean,
                        "text": ""
                    })

        all_notices.extend(notices)

    json_path = os.path.join(JSON_DIR, "fsc.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_notices, f, indent=2, ensure_ascii=False)

    print(f"\n📁 JSON 저장 완료: {json_path}")

if __name__ == "__main__":
    main(max_pages=3)
