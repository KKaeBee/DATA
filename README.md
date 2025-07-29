# 금융감독원/금융위원회 크롤러

### 금융감독원(FSS)과 금융위원회(FSC) 웹사이트에서 **최근 제개정 정보**와 **세칙 제·개정 예고**, **입법예고/규정변경예고**를 크롤링하고, 첨부된 `.hwp`, `.xlsx` 파일을 자동으로 `.pdf`, `.jpg`로 변환하여 저장한 뒤, 구조화된 JSON으로 결과를 저장하는 Python 기반 크롤러입니다.
---
## 🛠 주요 기능

- **2025년도 게시글만 수집**
- **예고 기간이 7월인 것까지 수집**
- **게시글 제목, 날짜, URL, 첨부파일 정보 크롤링**
- **`.hwp`, `.xlsx`, `.pdf` 첨부파일 자동 저장**
- **`.hwp`/`.xlsx` → `.pdf` 자동 변환**
- **`.pdf` → `.jpg` (모든 페이지 이미지화)**
- **변환된 파일 메타정보를 JSON 파일에 구조화 저장**
- **가장 최신 게시글의 PDF가 이미 존재하면 즉시 종료**
---
## 📂 프로젝트 구조

```bash
project/
│
├── 📁 data/                     # 수집/변환된 실제 파일 저장소
│   ├── 📁 pdf/                  # 변환된 PDF 저장소
│   ├── 📁 img/                  # 변환된 jpg 저장소
│   └── 📁 json/                 # 최종 JSON 저장 결과
│       └── fss_info.json         # 금융감독원 json 파일1
│       └── fss_pre.json          # 금융감독원 json 파일2
│       └── fsc.json              # 금융위원회 json 파일
│
├── 📁 crawler/                  # 웹 크롤링 관련 코드
│   ├── fss_info_crawler.py       # 금융감독원 크롤러1
│   ├── fss_pre_crawler.py        # 금융감독원 크롤러2
│   └── fsc_crawler.py            # 금융위원회 크롤러
│
├── 📁 converter/                # 파일 변환 로직
│   └── hwp_to_pdf_info.py        # pywin32 기반 HWP → PDF 변환기
│   └── hwp_to_pdf_pre.py         # pywin32 기반 HWP → PDF 변환기
│   └── xlsx_to_pdf_info.py       # XLSX → PDF 변환기
│   └── xlsx_to_pdf_pre.py        # XLSX → PDF 변환기
|   └── pdf_to_jpg.py             # PDF에서 이미지 추출
|
├── requirements.txt            # 필요한 라이브러리 목록
└── README.md                   # 프로젝트 설명
```
---
## 🚀 실행 방법

### 1️⃣ 환경 설정

- **운영체제**: Windows
- **Python**: 3.8 이상
- **필수 프로그램**:
  - 한글 (https://www.hancom.com/) (예: 한컴오피스 2020 이상)
  - Microsoft Excel

### 2️⃣ 라이브러리 설치

```bash
pip install -r requirements.txt
```
### 3️⃣ 크롤러 실행
```bash
python crawler/fss_info_crawler.py
python crawler/fss_pre_crawler.py
python crawler/fsc_crawler.py
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
    "text": ""
  }
]

```