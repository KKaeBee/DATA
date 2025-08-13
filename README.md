# 금융감독원/금융위원회 규제 공지 크롤러

## 📌 개요
본 프로젝트는 **금융감독원(FSS)** 과 **금융위원회(FSC)** 웹사이트에서  
**최근 제·개정 정보**, **세칙 제·개정 예고**, **입법예고/규정변경예고**를 자동 수집·정제하는  
Python 기반 규제 데이터 수집 및 전처리 시스템입니다.  

수집된 데이터는 `.hwp`, `.xlsx` 파일까지 자동 변환하여 `.pdf` → `.jpg`로 이미지화하고,  
구조화된 JSON으로 저장되어 프롬프트와 함께 **GPT API 분석 입력 데이터**로 사용됩니다.

---

## ✨ 주요 기능
- **2025년 게시글만 수집**, **예고기간 7월까지 필터링**
- 게시글 **제목, 날짜, URL, 첨부파일 정보** 크롤링
- `.hwp`, `.xlsx`, `.pdf` 첨부파일 자동 다운로드
- `.hwp` / `.xlsx` → `.pdf` 변환
- `.pdf` → `.jpg` 변환 (모든 페이지 이미지화)
- 변환된 파일 메타정보를 JSON 파일에 구조화 저장
- 최신 PDF가 이미 존재하면 중복 작업 없이 종료

---

## 📂 디렉토리 구조
```bash
project/
│
├── data/                  # 수집/변환된 실제 파일 저장
│   ├── pdf/               # 변환된 PDF
│   ├── img/               # 변환된 JPG
│   └── json/              # 최종 JSON 저장
│       ├── fss_info.json
│       ├── fss_pre.json
│       └── fsc.json
│
├── crawler/               # 크롤러 모듈
│   ├── fss_info_crawler.py
│   ├── fss_pre_crawler.py
│   └── fsc_crawler.py
│
├── converter/             # 파일 변환 모듈
│   ├── hwp_to_pdf_info.py
│   ├── hwp_to_pdf_pre.py
│   ├── xlsx_to_pdf_info.py
│   ├── xlsx_to_pdf_pre.py
│   └── pdf_to_jpg.py
│
├── gpt/                   # GPT API 호출 모듈
│   ├── fss_info_gpt.py
│   ├── fss_pre_gpt.py
│   └── fsc_gpt.py
│
├── requirements.txt       # 의존성 목록
└── README.md              # 프로젝트 설명
```
---
## 🚀 실행 방법

### 1. 환경 설정

- **운영체제**: Windows
- **Python**: 3.8 이상
- **필수 프로그램**:
  - 한글 (https://www.hancom.com/) (예: 한컴오피스 2020 이상)
  - Microsoft Excel

### 2. 라이브러리 설치

```bash
pip install -r requirements.txt
```
### 3. 크롤러 실행
```bash
python crawler/fss_info_crawler.py
python crawler/fss_pre_crawler.py
python crawler/fsc_crawler.py
```
### 4. GPT API 실행
```bash
python gpt/fss_info_gpt.py
python gpt/fss_pre_gpt.py
python gpt/fsc_gpt.py
```
---
## ✅ JSON 예시

```bash
[
  {
    "title": "개인신용정보 처리에 관한 법률 일부개정안",
    "date": "2025-07-19",
    "source": "금융감독원",
    "url": "https://www.fss.or.kr/fss/job/...",
    "type": "세칙제개정예고",
    "attachments": [
      {
        "filename": "개정안.pdf",
        "imgname": ["개정안_1.jpg", "개정안_2.jpg"],
        "path": "data/pdf/개정안.pdf",
        "imgpath": ["data/img/개정안_1.jpg", "data/img/개정안_2.jpg"]
      },
      {
        "filename": "엑셀.pdf",
        "imgname": ["엑셀_1.jpg"],
        "path": "data/pdf/엑셀.pdf",
        "imgpath": ["data/img/엑셀_1.jpg"]
      }
    ],
    "department": [
      "부서1",
      "부서2"
    ],
    "summary": {     
      "1. 요약": [
        "내용1",
        "내용2"
      ],
      "2. 요약": [
        "내용1",
        "내용2"
      ],
    },
    "checklist": [
      "1. 대응 방안",
      "2. 대응 방안"
    ]
  }
]

```
---
## 🛠 기술 스택
- 언어: Python 3.8+
- 크롤링: BeautifulSoup, selenium, requests
- 파일 변환: pywin32, PyMuPDF
- AI 분석: OpenAI GPT API