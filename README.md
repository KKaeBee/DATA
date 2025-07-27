# 금융감독원 세칙제개정예고 크롤러

금융감독원(FSS) 웹사이트에서 **세칙 제·개정 예고**를 크롤링하고, 첨부된 `.hwp` 문서를 자동으로 `.pdf`로 변환하여 저장한 뒤, 본문과 메타데이터를 구조화된 JSON으로 저장하는 Python 기반 크롤러입니다.
---
## 🛠 주요 기능

- **2025년도 게시글만 수집**
- **게시글 제목, 본문, 날짜, URL, 첨부파일 메타데이터 추출**
- **첨부파일(`.hwp`, `.pdf`) 자동 저장**
- **`.hwp` → `.pdf` 자동 변환** (Windows + 한글 설치 필수)
- **JSON 형식으로 저장 (`fss_pre.json`)**
---
## 📂 프로젝트 구조

```bash
DATA/
├── crawler/
│ └── fss_pre_crawler.py # 메인 크롤러 스크립트
├── converter/
│ └── hwp_to_pdf.py # HWP → PDF 변환 스크립트
├── data/
│ ├── hwp/ # 다운로드된 .hwp 파일 저장 경로
│ ├── pdf/ # 변환된 .pdf 파일 저장 경로
│ └── json/
│ └── fss_pre.json # 크롤링 결과 저장 JSON
├── requirements.txt # 필요한 파이썬 라이브러리 목록
└── README.md # 이 문서
```
---
## 🚀 실행 방법

### 1️⃣ 환경 설정

- Python 3.8 이상 설치
- Windows 운영체제 필수
- 한글 설치 필요 (예: 한컴오피스 2020 이상)

### 2️⃣ 라이브러리 설치

```bash
pip install -r requirements.txt
```
### 3️⃣ 크롤러 실행
```bash
python crawler/fss_pre_crawler.py
```
---
## ✅ JSON 예시

```bash
[
  {
    "title": "보험업감독업무시행세칙",
    "date": "2025-07-22",
    "source": "금융감독원",
    "url": "https://www.fss.or.kr/...",
    "type": "세칙제개정예고",
    "attachments": {
      "filename": "보험업감독업무시행세칙.pdf",
      "path": "pdf/보험업감독업무시행세칙.pdf"
    },
    "text": "1. 규정의 명칭\n보험업감독업무시행세칙\n..."
  }
]
```