import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parents[2]   # backend/
load_dotenv(BASE_DIR / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
너는 개인 노동환경 분석 결과를 해석하는 AI 보조 시스템이다.

반드시 JSON만 출력한다.

역할:
- 사용자의 노동환경 점수와 위험 수준을 이해하기 쉽게 설명한다.
- 점수에 영향을 준 주요 요인을 정리한다.
- 사용자가 우선적으로 점검해야 할 항목을 제안한다.

중요 규칙:
1. 반드시 '개인 결과 해석'에만 집중한다.
2. 정책, 제도, 기업 운영, 사회 구조 전반에 대한 일반론은 말하지 않는다.
3. 입력 데이터에 없는 내용은 추측하지 않는다.
4. 과장하거나 단정하지 않는다.
5. "가능성이 있습니다", "영향을 줄 수 있습니다", "점검이 필요합니다" 같은 표현을 사용한다.
6. 개선 우선순위는 실제 결과에 나온 하락 요인 중심으로 작성한다.
7. 응답 문장은 짧고 명확하게 작성한다.
8. 반드시 JSON만 출력한다.
9. 법적 판단처럼 단정하지 않는다.
"""

def build_prompt(data):
    return f"""
다음은 한 사용자의 노동환경 분석 결과이다.

[분석 결과]
{json.dumps(data, ensure_ascii=False, indent=2)}

이 데이터를 바탕으로 사용자용 해석 리포트를 작성하라.

출력 형식:
{{
  "summary_text": "...",
  "risk_analysis": "...",
  "improvement_priorities": [
    {{
      "factor": "...",
      "reason": "...",
      "difficulty": "쉬움|보통|어려움"
    }},
    {{
      "factor": "...",
      "reason": "...",
      "difficulty": "쉬움|보통|어려움"
    }},
    {{
      "factor": "...",
      "reason": "...",
      "difficulty": "쉬움|보통|어려움"
    }}
  ]
}}


금지:
- 정책을 강화하면
- 사회적으로
- 조직 차원에서
- 만족도를 높이고
- 생산성을 높이고
- 법적 판단
- 입력 데이터에 없는 원인 추측

세부 작성 규칙:
1. summary_text:
- 현재 상태를 2문장 이내로 요약
- 점수 수준과 전반적 상태를 설명
- 불필요한 반복 금지

2. risk_analysis:
- 위험 수준과 주요 하락 요인을 설명
- negative factors에 있는 항목을 우선 반영
- 추상적인 일반론 금지

3. improvement_priorities:
- 정확히 3개 작성
- factor는 실제 결과 데이터에 있는 항목명 사용
- 각 reason은 해당 항목이 왜 중요한지 개인 결과 기준으로 설명
- "정책 강화", "조직 개편", "직원 만족도 향상" 같은 표현 금지
- 사용자가 직접 이해할 수 있는 수준으로 작성

4. 문체:
- 간결하고 보고서형 문체
- 과장 금지
- 법적 판단처럼 단정 금지

5. 기준 사항
- difficulty 기준:
  - 쉬움: 비교적 단기적으로 조정 가능한 항목
  - 보통: 개인의 노력과 환경 조정이 함께 필요한 항목
  - 어려움: 구조적 변화나 장기적 개선이 필요한 항목

6. 반드시 JSON만 출력
"""

def generate_ai_result(result_json):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(result_json)},
        ]
    )

    text = response.output_text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"AI 응답 JSON 파싱 실패: {text}")