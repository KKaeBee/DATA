import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from converter.hwp_to_pdf import convert_hwp_to_pdf  # 변환 모듈

# 상수 경로 설정
BASE_URL = "https://www.fss.or.kr"
LIST_URL = f"{BASE_URL}/fss/job/lrgRegItnInfo/list.do"
DETAIL_BASE = f"{BASE_URL}/fss/job/lrgRegItnInfo"

HWP_DIR = "data/hwp"
PDF_DIR = "data/pdf"
JSON_PATH = "data/json/fss_info.json"

os.makedirs(HWP_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs("data/json", exist_ok=True)


def crawl():
    results = []
    page_index = 1

    while True:
        print(f"\n[PAGE {page_index}] 크롤링 중...")
        params = {"menuNo": "200488", "pageIndex": str(page_index)}
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(LIST_URL, params=params, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.select("table tbody tr")
        if not rows:
            print("게시글 행 없음, 종료")
            break

        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 3:
                continue

            # 제목 및 상세 URL
            title_cell = tds[1]
            a_tag = title_cell.find("a")
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            relative_url = a_tag.get("href", "")
            detail_url = urljoin(BASE_URL, relative_url)

            # 날짜 추출
            date_str = tds[2].get_text(strip=True)
            if not date_str.startswith("2025"):
                print(f"2025년 금융감독원 최근 제개정 정보 크롤링 완료.")
                return results

            print(f"\n- 게시글: {title} / 날짜: {date_str}")
            print(f"상세 페이지 접속: {detail_url}")

            # 상세 페이지에서 본문과 첨부 추출
            text, attachment = get_detail_info(detail_url)

            results.append(
                {
                    "title": title,
                    "date": date_str,
                    "source": "금융감독원",
                    "url": detail_url,
                    "type": "최근 제개정 정보",
                    "attachments": attachment,
                    "text": text,
                }
            )

        page_index += 1

    return results


def get_detail_info(detail_url):
    res = requests.get(detail_url)
    soup = BeautifulSoup(res.text, "html.parser")

    # 본문 텍스트
    text_block = soup.select_one("ol.number-title")
    text = text_block.get_text(separator="\n", strip=True) if text_block else ""

    # 첨부파일
    attachment_div = soup.select_one("div.file-list__set")
    attachment = None
    if attachment_div:
        a_tags = attachment_div.find_all("a")
        for a_tag in a_tags:
            filename = a_tag.get_text(strip=True)
            file_href = a_tag.get("href", "")
            file_url = urljoin(detail_url, file_href)

            print(f"첨부파일 다운로드: {filename}")
            file_ext = filename.lower().split(".")[-1]

            if file_ext in ["hwp", "hwpx"]:
                hwp_path = os.path.abspath(os.path.join(HWP_DIR, filename))
                with open(hwp_path, "wb") as f:
                    f.write(requests.get(file_url).content)
                print(f"저장된 HWP 경로: {hwp_path}")

                try:
                    text, attachment = convert_hwp_to_pdf(
                        hwp_path, os.path.abspath(PDF_DIR)
                    )
                    print(f"HWP → PDF 변환 완료: {attachment['path']}")
                except Exception as e:
                    print(f"[경고] HWP 변환 실패: {e}")
                    text = ""
                    attachment = {"filename": filename, "path": f"hwp/{filename}"}

                break
            elif file_ext == "pdf" and not attachment:
                pdf_path = os.path.join(PDF_DIR, filename)
                with open(pdf_path, "wb") as f:
                    f.write(requests.get(file_url).content)
                attachment = {"filename": filename, "path": f"pdf/{filename}"}
                print(f"PDF 첨부 저장 완료")

    return text, attachment


if __name__ == "__main__":
    data = crawl()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(
        f"\n2025년 금융감독원 최근 제개정 정보 {len(data)}건 저장 완료\n→ {JSON_PATH}"
    )
