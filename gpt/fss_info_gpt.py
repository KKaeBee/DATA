import json
from pathlib import Path
from openai import OpenAI
import base64
import re
import os
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
JSON_PATH = Path("data/json/fss_info.json")

SYSTEM_PROMPT = """
현재 나는 "금융 규제 및 법규준수 모니터링 AI 에이전트" 프로젝트를 개발 중입니다.
이 프로젝트는 복잡하고 변화가 많은 금융 규제 환경의 준법 리스크를 예방하기 위해 고안됐습니다.
금융감독원, 금융위원회 등에서 공개하는 법령, 공시 데이터를 분석해 규제 변경사항을 모니터링하고, 준수 여부를 자동 점검합니다.
규제 변경 시, 관련 부서에 실시간 알림을 제공하고 필요한 대응 방안을 제시해야 합니다.

[업무 목적]
다음 정보를 담은 JSON 파일을 생성하기 위함입니다:

1. 규제 게시물의 적절한 알림 수신 부서
2. 게시물의 핵심 내용 요약
3. 부서가 실행해야 할 대응 방안 체크리스트

[부서 선택 목록]
아래 나열된 부서 중에서만 선택해야 합니다:

- 영업그룹: WM추진본부, 지역영업그룹, 지역본부
- 디지털영업그룹: 스타뱅킹영업본부
- 고객컨택영업그룹
- 기업고객그룹: 임베디드영업본부, 기업디지털영업본부, 외환사업본부
- 모바일사업본부
- 수탁사업본부
- CIB영업그룹: 투자영업본부, 인프라영업본부, 구조화영업본부, 대기업영업본부
- 자본시장사업그룹: 채권운용본부, S&T본부
- 글로벌사업그룹: 글로벌성장지원본부
- 기관영업그룹: 기관영업본부
- 개인고객그룹
- WM고객그룹: 연금사업본부
- AI/DT추진그룹: AI데이터본부
- 테크그룹: 테크개발본부, 테크인프라본부
- 여신관리심사그룹: 여신심사본부
- 리스크관리그룹
- 브랜드홍보그룹
- 경영지원그룹: 직원만족본부, 업무지원본부
- 경영기획그룹: 전략본부, ESG본부
- 준법감시인: 자금세탁방지본부, 정보보호본부
- 소비자보호그룹

[처리 방법]
내가 여러 장의 금융감독원 규제 제·개정 예고 게시물 이미지를 전송할 예정이니,
다음 기준에 따라 반드시 하나의 JSON 객체로 작성해 주세요.

각 게시물마다 반드시 다음 필드를 포함해야 합니다:

- "department": [ "부서1", "부서2", ... ]
   → 게시물 내용에 따라 알림을 받아야 할 적절한 부서를 위의 부서 선택 목록에서만 선택할 것

- "summary": {
    "항목1": ["내용1", "내용2"],
    "항목2": ["내용1"]
  }
   → 보낸 이미지 합쳐서, 게시물 핵심 내용을 항목별로 자세하게 정리할 것 (키는 제목/항목명, 값은 설명 리스트)

- "checklist": [
    "체크 항목1",
    "체크 항목2"
  ]
   → 실제 부서가 이 규제에 대응하기 위해 점검하거나 준비해야 할 항목 목록

게시물 하나에 대해 여러 장의 사진이 존재할 수 있으므로, 내가 사진을 전송하며 "이 게시물은 총 N장입니다"라고 알려주면, 모든 사진을 수신한 후 하나의 JSON 객체로 응답해 주세요.
파일 명 맨 뒤가 _1로 되어있는 사진부터 순서대로 해석해주세요.
지금부터 첫 게시물의 사진들을 전송하겠습니다.

JSON 이외의 텍스트는 절대 출력하지 마세요.
[결과 예시]
"department": [
    "투자영업본부",
    "소비자보호그룹",
    "리스크관리그룹"
],
"summary": {
    "1. 외부평가 곤란 자산 안내 의무 신설": [
    "금융투자업규정 제7-36조의2 제4항에 따라 외부 전문기관 평가가 곤란한 자산은 투자자에게 관련 내용을 안내해야 함",
    "자산운용보고서를 통해 평가 대안 및 방법을 투자자에게 명확히 안내해야 함"
    ],
    "2. 자산운용보고서 서식 개정": [
    "외부 평가가 곤란한 자산의 평가 방법을 기재하는 항목 추가",
    "신설된 '집합투자재산의 평가' 항목에는 사유, 평가방법, 향후 평가계획, 계약의 타당성 등을 포함"
    ],
    "3. 적용 시점 및 부칙": [
    "2025년 9월 19일부터 시행",
    "시행일 이후 작성되는 자산운용보고서부터 개정 서식 적용"
    ]
    },
"checklist": [
    "자산운용보고서 양식에 평가 관련 항목 추가 여부 확인",
    "외부 평가 곤란 자산에 대한 평가 사유 및 대체 방법 사전 수립",
    "향후 평가 계획 수립 및 문서화",
    "외부계약 체결 시 계약의 타당성 검토 및 내부 검토 기록 유지",
    "2025년 9월 19일 시행일 이전 보고서와의 구분 적용 방안 마련"
]
[결과 예시]
"department": [
    "리스크관리그룹",
    "여신심사본부",
    "투자영업본부",
    "채권운용본부",
    "전략본부"
],
"summary": {
    "1. 토지신탁 한도 규제 및 신용위험액 산정기준 신설": [
    "책임준공확약형 및 차입형 토지신탁 계약에 대해 자기자본 및 총 예상위험액 한도를 산정하는 기준 신설",
    "신탁계정대 잔액 기준 계약, 신탁업자의 손해배상위험까지 고려한 산식 도입"
    ],
    "2. NCR 신용위험 산정 기준 정교화": [
        "NCR 신용위험액 산정 시 손해배상가능성에 따른 차등 적용 방식 도입",
        "시공사/위탁자 신용등급이 낮거나, 공정률 차이 큰 경우 등 상황별 위험비율(15~100%) 구간 설정"
    ],
    "3. 회계처리 및 차입금 인식 요건 명확화": [
        "신탁업자가 차입한 자금을 고유계정의 차입금으로 인식하지 않기 위한 요건 명확화",
        "국가나 공공기관의 보증 또는 대출일 경우에만 예외 인정"
    ],
    "4. 시행 시기 및 부칙": [
        "일반 규정은 2025년 7월 1일부터, 부칙 제10의2·표10의2는 2025년 12월 31일부터 시행"
    ]
    },
"checklist": [
      "토지신탁계약 분류 기준에 따른 위험액 산정 방식 내부 지침 반영",
      "책임준공확약형 신탁계약 시 손해배상위험 평가 절차 수립",
      "신탁계정대 관련 계약에 적용될 예상위험액 및 한도 계산 공식 반영",
      "NCR 비율 산정 시 새 기준(위험비율, 차감항목 등) 적용 테스트 및 시스템 수정",
      "차입금 회계 처리 요건 검토 및 예외 사유 관련 문서화"
    ]
  },
반드시 JSON 이외의 텍스트는 절대 출력하지 마세요.
"""
def encode_image_to_data_uri(path):
    try:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        print(f"이미지 인코딩 실패: {path}, {e}")
        return None
    

def is_empty_field(value):
    """빈 리스트, 빈 dict, None, 빈 문자열 다 빈 값으로 처리"""
    if value is None:
        return True
    if isinstance(value, (list, dict, str)) and not value:
        return True
    return False



def fill_missing_fields(item):
    dept = item.get("department")
    summ = item.get("summary")
    check = item.get("checklist")

    print(f"\n처리 중: {item.get('title')}")
    print("   department:", dept, type(dept))
    print("   summary:", summ, type(summ))
    print("   checklist:", check, type(check))

    if is_empty_field(dept) or is_empty_field(summ) or is_empty_field(check):
        print("GPT 호출 시작")

        images = item["attachments"][0].get("imgpath", [])
        img_inputs = []
        for path in images:
            data_uri = encode_image_to_data_uri(path)
            if data_uri:
                img_inputs.append({"type": "image_url", "image_url": {"url": data_uri}})

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"이 게시물은 총 {len(images)}장입니다. 모든 이미지를 해석하고 JSON만 반환해."},
                    *img_inputs
                ]
            }
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0,
                response_format={"type": "json_object"}
            )

            raw_content = response.choices[0].message.content
            print("GPT 응답 원문:", raw_content)

            try:
                result = json.loads(raw_content)
            except json.JSONDecodeError as e:
                print("JSON 디코딩 실패:", e)
                return item

            item["department"] = result.get("department") or []
            item["summary"] = result.get("summary") or {}
            item["checklist"] = result.get("checklist") or []

        except Exception as e:
            print("JSON 파싱/호출 오류:", e)
    else:
        print("값 이미 존재, GPT 호출 생략")

    return item


if __name__ == "__main__":
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        filled_data = [fill_missing_fields(item) for item in data]
    else:
        filled_data = fill_missing_fields(data)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(filled_data, f, ensure_ascii=False, indent=2)

    print(f"fss_info.json 업데이트 완료 → {JSON_PATH}")