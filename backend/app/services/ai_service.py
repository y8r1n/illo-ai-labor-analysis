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
- 점수에 영향을 준 주요 노동환경 요인을 정리한다.
- 사용자가 우선적으로 점검해야 할 항목을 제안한다.
- 각 해석은 가능한 경우 입력값, 점수, 결과를 연결해서 설명한다.

중요 규칙:
1. 반드시 개인 결과 해석에만 집중한다.
2. 정책, 제도, 기업 운영, 사회 구조 전반에 대한 일반론은 말하지 않는다.
3. 입력 데이터와 결과 데이터에 없는 내용은 추측하지 않는다.
4. 과장하거나 단정하지 않는다.
5. "가능성이 있습니다", "영향을 줄 수 있습니다", "점검이 필요합니다" 같은 표현을 사용한다.
6. 개선 우선순위는 실제 결과에 나온 하락 요인 중심으로 작성한다.
7. 응답 문장은 짧고 명확하게 작성한다.
8. 반드시 JSON만 출력한다.
9. 법적 판단처럼 단정하지 않는다.
10. 체력, 스트레스 같은 개별 입력값이 있더라도 결과 해석에서는 가능하면 상위 개념인 "회복여건", "업무부담", "고용안정성", "근로시간", "임금수준" 중심으로 설명한다.
11. 단일 항목만 나열하지 말고, 가능한 경우 2개 이상의 요인을 연결해 설명한다.
12. 예를 들어 "스트레스 수준이 높고 업무부담 점수가 낮게 나타나", "업종 가중치와 회복여건을 함께 고려하면" 같은 방식으로 원인 연결형 문장을 작성한다.
13. summary_text와 risk_analysis는 반드시 "입력값 또는 결과값 + 점수/가중치 + 해석" 구조가 드러나야 한다.
14. improvement_priorities의 각 항목에는 반드시 score, label, input_basis, expected_effect를 포함한다.
15. label은 반드시 "양호", "주의", "개선 필요" 중 하나만 사용한다.
"""

def build_prompt(data):
    return f"""
다음은 한 사용자의 노동환경 분석 결과이다.

[분석 결과]
{json.dumps(data, ensure_ascii=False, indent=2)}

이 데이터를 바탕으로 사용자용 해석 리포트를 작성하라.

반드시 아래 JSON 형식만 출력하라.
설명 문장은 간결하되, 가능한 경우 입력값 + 점수 + 해석이 연결되도록 작성하라.

출력 형식:
{{
  "summary_text": "...",
  "risk_analysis": "...",
  "improvement_priorities": [
    {{
      "factor": "...",
      "reason": "...",
      "difficulty": "쉬움|보통|어려움",
      "score": 0.0,
      "label": "양호|주의|개선 필요",
      "input_basis": "...",
      "expected_effect": "..."
    }},
    {{
      "factor": "...",
      "reason": "...",
      "difficulty": "쉬움|보통|어려움",
      "score": 0.0,
      "label": "양호|주의|개선 필요",
      "input_basis": "...",
      "expected_effect": "..."
    }},
    {{
      "factor": "...",
      "reason": "...",
      "difficulty": "쉬움|보통|어려움",
      "score": 0.0,
      "label": "양호|주의|개선 필요",
      "input_basis": "...",
      "expected_effect": "..."
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

1. summary_text
- 2문장 이내로 작성한다.
- 현재 점수 수준과 전반적 상태를 설명한다.
- 가능한 경우 입력값이나 가중치, 점수 요소를 함께 연결한다.
- 예: "현재 노동환경 점수는 보통 수준이며, 스트레스 수준과 업무부담 점수가 전체 점수에 영향을 주고 있습니다."

2. risk_analysis
- 위험 수준과 주요 하락 요인을 설명한다.
- factors.negative, score_breakdown, environment_scores, weights를 우선 반영한다.
- 단순 요약이 아니라 "입력값 또는 가중치 + 점수 + 해석" 구조로 작성한다.
- risk_analysis는 반드시 최소 1개 이상의 수치(점수 또는 가중치)를 포함하여 작성한다.
- 가능한 경우 2개 이상의 요인을 연결해서 설명한다.
- 예: "스트레스 수준이 높고 업무부담 점수가 낮게 나타나 전체 위험 수준 상승에 영향을 주고 있습니다."

3. improvement_priorities
- 정확히 3개 작성한다.
- factor는 반드시 아래 목록 중 하나만 사용한다:
["근로시간", "임금수준", "고용안정성", "회복여건", "업무부담"]
이 외의 값은 사용하지 않는다.
- 우선 사용 권장 항목:
  "근로시간", "임금수준", "고용안정성", "회복여건", "업무부담"
- 가능하면 "체력", "스트레스" 같은 개별 입력명보다 상위 개념을 우선 사용한다.
- factors.negative가 있으면 최우선 반영한다.
- simulation.main, simulation.sub에 개선 가능 항목이 있으면 우선 반영한다.
- 각 항목에는 아래 정보를 반드시 포함한다:
  - factor: 개선 우선 항목명
  - reason: 왜 이 항목이 중요한지 결과 기준으로 설명
  - difficulty: 쉬움/보통/어려움
  - score: 해당 항목과 가장 가까운 실제 점수값 또는 관련 결과값
  - label: score 기준으로 "양호", "주의", "개선 필요" 중 하나
  - input_basis: 해당 판단의 근거가 되는 입력값 또는 결과값 요약
  - expected_effect: 개선 시 기대할 수 있는 변화

-improvement_priorities는 반드시 score가 낮은 순으로 정렬하여 작성한다.
- label이 "양호"인 항목은 원칙적으로 improvement_priorities에서 제외한다.
- "개선 필요"와 "주의" 항목을 우선 포함하고, 다른 후보가 부족한 경우에만 "양호" 항목을 마지막 순위에 제한적으로 포함한다.

4. score 작성 규칙
- score는 반드시 숫자(float)로 작성한다.
- score는 반드시 아래 기준에 맞춰 선택한다:

- 업무부담 → workload_burden_score 또는 job_intensity_score
- 임금수준 → wage_score
- 근로시간 → work_time_score
- 고용안정성 → employment_score
- 회복여건 → recovery_score

가능한 경우 summary 또는 score_breakdown에서 직접 가져온 값을 사용한다.
임의로 생성하지 않는다.
- 예:
  - 업무부담 → job_intensity_score 또는 workload_burden_score 계열
  - 임금수준 → wage_score
  - 근로시간 → work_time_score
  - 고용안정성 → employment_score
  - 회복여건 → recovery_score
- 적절한 값이 없으면 가장 관련 있는 결과값을 사용하되, 임의 추정은 하지 않는다.

5. label 작성 규칙
- score < 0.4 → "개선 필요"
- 0.4 <= score < 0.7 → "주의"
- score >= 0.7 → "양호"

6. input_basis 작성 규칙
- 실제 user_input, factors, weights, score_breakdown 등에서 근거를 짧게 정리한다.
- 예: "스트레스 수준 높음, 업무부담 점수 낮음"
- 예: "월 급여 수준과 임금 점수가 함께 반영됨"

7. expected_effect 작성 규칙
- 해당 항목을 개선했을 때 어떤 변화가 기대되는지 짧게 작성한다.
- 예: "업무부담 완화 시 전체 노동환경 점수 개선 가능성이 있습니다."

8. 문체
- 간결하고 보고서형 문체
- 과장 금지
- 법적 판단처럼 단정 금지
- 사용자에게 직접 보여줄 결과물이므로 이해하기 쉽게 작성

9. 반드시 JSON만 출력한다.
"""

def _normalize_ai_factor_names(ai_result: dict) -> dict:
    replace_map = {
        "체력": "회복여건",
        "스트레스": "업무부담",
        "스트레스요인": "업무부담",
        "고용형태": "고용안정성",
        "업종": "업종환경",
        "회복 환경": "회복여건",
        "업무 강도": "업무부담",
        "근무패턴": "회복여건",
    }

    for item in ai_result.get("improvement_priorities", []):
        factor = item.get("factor")
        if factor in replace_map:
            item["factor"] = replace_map[factor]

    return ai_result

def _normalize_ai_fields(ai_result: dict) -> dict:
    priorities = ai_result.get("improvement_priorities")
    if not isinstance(priorities, list):
        ai_result["improvement_priorities"] = []
        return ai_result

    for item in ai_result["improvement_priorities"]:
        if not isinstance(item, dict):
            continue

        try:
            if "score" in item:
                item["score"] = float(item["score"])
        except Exception:
            item["score"] = 0.0

        if item.get("label") not in ["양호", "주의", "개선 필요"]:
            score = item.get("score", 0.0)
            if score < 0.4:
                item["label"] = "개선 필요"
            elif score < 0.7:
                item["label"] = "주의"
            else:
                item["label"] = "양호"

    return ai_result

def _clean_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1).strip()
    if text.startswith("```"):
        text = text.replace("```", "", 1).strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def generate_ai_result(result_json):
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(result_json)},
            ]
        )

        text = (response.output_text or "").strip()
        print("[AI RAW TEXT]", text)

        if not text:
            raise ValueError("AI 응답 output_text가 비어 있습니다.")

        cleaned = _clean_json_text(text)
        print("[AI CLEANED TEXT]", cleaned)

        parsed = json.loads(cleaned)
        print("[AI PARSED]", parsed)

        normalized = _normalize_ai_factor_names(parsed)
        normalized = _normalize_ai_fields(normalized)
        print("[AI NORMALIZED]", normalized)

        return normalized

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("[AI SERVICE ERROR]", repr(e))
        raise