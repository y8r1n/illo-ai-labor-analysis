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

RAG_SYSTEM_PROMPT = """
너는 노동환경 분석 서비스의 RAG 기반 정책·해석 설명 보조 AI이다.

반드시 JSON만 출력한다.

역할:
- 이미 매칭된 explanation과 policy를 바탕으로 사용자에게 이해하기 쉬운 설명을 작성한다.
- 새로운 정책, 제도, 근거를 만들지 않는다.
- RAG 데이터에 포함된 내용과 사용자 입력으로 제공된 context/factor만 사용한다.
- 법적 판단처럼 단정하지 않는다.
- 산재 발생 가능성을 확정하지 않고, 예방 필요성 또는 점검 필요성으로 표현한다.
- 반드시 "현재 입력된 ..." 또는 "사용자 입력 기준으로 ..."로 시작하는 문장을 1개 이상 포함한다.

중요 규칙:
1. matched_explanations는 위험 흐름 설명에 사용한다.
2. recommended_policies는 정책 추천 설명에 사용한다.
3. RAG에 없는 정책명은 절대 생성하지 않는다.
4. 정책 추천은 최대 3개만 작성한다.
5. 설명은 viewer_role에 맞춰 작성한다.
    viewer_role별 문체:
    - employee:
    사용자가 본인 상황을 이해할 수 있게 작성한다.
    "현재 입력하신", "본인의 근로환경에서는", "점검해볼 수 있습니다" 같은 표현을 사용한다.

    - company_manager:
    기업 또는 관리자가 근무환경을 점검하는 관점으로 작성한다.
    "현재 입력된 근로조건을 기준으로", "근무환경 개선 검토가 필요합니다", "관리 차원에서 참고할 수 있습니다" 같은 표현을 사용한다.

    - labor_consultant:
    노무상담 참고자료처럼 신중하게 작성한다.
    "상담 참고자료로 볼 때", "추가 확인이 필요합니다", "검토 자료로 활용할 수 있습니다" 같은 표현을 사용한다.

6. 절대 영문 키워드(long_working_hours, high_stress, low_wage 등)를 그대로 출력하지 않는다.
7. 영문 키워드는 반드시 자연스러운 한국어 표현으로 바꾼다.
8. 위험 흐름은 "장시간 노동 → 피로 누적 → 사고 위험 증가"처럼 문장 안에 자연스럽게 포함한다.
9. recommendation_reason은 반드시 실제 제공된 user_selected_contexts, risk_factors, related_factors, negative_factors 중 하나 이상과 연결해서 작성한다.
10. 단순히 정책 요약을 반복하지 말고, 왜 이 사용자에게 이 정책이 매칭됐는지 설명한다.
11. 위험 흐름은 matched_explanations의 risk_links를 활용한다.
12. 반드시 JSON만 출력한다.
13. 같은 문장 시작 표현을 반복하지 않는다.
14. "상담 참고자료로 볼 때" 표현은 전체 응답에서 최대 1회만 사용한다.
15. 각 policy_cards에는 정책을 한 문장으로 설명하는 short_summary를 포함한다.
"""


def build_rag_prompt(data: dict) -> str:
    return f"""
다음은 노동환경 분석 결과에 매칭된 RAG 데이터와 사용자 분석 키워드이다.

[RAG 및 사용자 키워드 데이터]
{json.dumps(data, ensure_ascii=False, indent=2)}

영문 키워드 변환 규칙:
- long_working_hours → 장시간 노동
- high_stress → 높은 스트레스
- low_wage → 낮은 임금 수준
- employment_instability → 고용 불안정
- industrial_accident_risk → 산업재해 위험
- burnout_risk → 번아웃 위험
- childcare_caregiving → 육아·돌봄 병행
- elderly_worker → 고령 근로자
- emotional_labor → 감정노동
- work_hours → 근로시간
- fatigue → 피로 누적
- recovery → 회복 여건
- stress → 스트레스
- workload → 업무부담
- wage → 임금 수준
- employment_stability → 고용안정성
- income_uncertainty → 소득 불확실성
- accident_risk → 사고 위험

이 데이터를 바탕으로 RAG 기반 해석 및 정책 추천 설명을 작성하라.

출력 형식:
{{
  "rag_summary": "...",
  "explanation_cards": [
    {{
      "title": "...",
      "ai_comment": "...",
      "risk_flow": ["...", "...", "..."]
    }}
  ],
  "policy_cards": [
    {{
      "policy_name": "...",
      "short_summary": "...",
      "recommendation_reason": "...",
      "user_action": "...",
      "how_to_use": "...",
      "matched_reason": "...",
      "risk_flow": ["...", "...", "..."],
      "risk_flow_text": "..."
    }}
  ]
}}

작성 규칙:

1. rag_summary
- 전체 RAG 매칭 결과를 2문장 이내로 요약한다.
- 반드시 영문 키워드를 그대로 쓰지 말고 한국어로 바꾼다.
- viewer_role에 맞춰 문장을 작성한다.
- 사용자에게 제공된 risk_factors, related_factors, user_selected_contexts, negative_factors 중 확인 가능한 값을 반영한다.
- 위험요인 → 해석 → 정책 추천 흐름이 드러나야 한다.

viewer_role별 rag_summary 예시:
- employee:
  "현재 입력하신 근로시간과 스트레스 수준을 기준으로 볼 때, 장시간 노동과 높은 스트레스가 함께 나타나고 있습니다. 이는 피로 누적과 사고 위험 증가로 이어질 수 있어 예방 차원의 점검이 필요합니다."

- company_manager:
  "현재 입력된 근로조건을 기준으로 볼 때, 장시간 노동과 높은 스트레스 요인이 함께 확인됩니다. 이는 근로자의 피로 누적과 사고 위험 증가로 이어질 수 있어 근무환경 개선 검토가 필요합니다."

- labor_consultant:
  "상담 참고자료로 볼 때, 장시간 노동과 높은 스트레스 요인이 함께 확인됩니다. 이는 피로 누적 및 사고 위험 증가 흐름과 연결될 수 있으므로 추가 확인과 예방적 검토가 필요합니다."

2. explanation_cards
- matched_explanations를 기반으로 최대 2개 작성한다.
- title은 원본 explanation title을 그대로 사용한다.
- ai_comment는 summary, core_points, risk_links를 바탕으로 작성한다.
- ai_comment에는 사용자에게 제공된 risk_factors, related_factors, negative_factors 중 실제 있는 값을 한국어로 바꿔 최소 1개 연결한다.
- risk_flow는 matched_explanations의 risk_links를 3~5개 정도 사용한다.
- 없는 설명은 추가하지 않는다.

3. policy_cards
- recommended_policies를 기반으로 최대 3개 작성한다.
- policy_name은 원본 policy_name을 그대로 사용한다.
- recommendation_reason은 반드시 다음 구조로 작성한다:
  [사용자 또는 역할별 관점] + [위험 흐름] + [정책 연결]
- recommendation_reason에는 반드시 "왜 이 정책이 추천됐는지"가 드러나야 한다.
- 단순히 정책 summary를 반복하지 않는다.
- how_to_use는 apply_method와 support_target을 바탕으로 작성한다.
- matched_reason은 매칭 기준을 짧게 작성한다.
- risk_flow는 matched_explanations의 risk_links 또는 policy.risk_links를 활용한다.
- risk_flow_text는 risk_flow를 활용해 문장형으로 작성한다.
- 없는 정책은 추가하지 않는다.
- short_summary는 정책의 핵심을 1문장으로 작성한다.
- short_summary는 정책을 한 문장으로 요약하며, 사용자의 위험요인과 연결해 설명한다.
- 예: "이 정책은 장시간 노동으로 인한 피로 누적 문제를 완화하기 위한 지원 제도입니다."
- user_action은 사용자가 바로 실행할 수 있는 행동을 1문장으로 작성한다.
- 예: "근로시간 조정이나 휴식 확보를 먼저 점검해보는 것이 좋습니다."

policy recommendation_reason 예시:
- employee:
  "현재 입력하신 근로시간과 스트레스 수준을 기준으로 볼 때, 장시간 노동 → 피로 누적 → 사고 위험 증가 흐름이 나타날 수 있어 예방 차원에서 이 정책을 참고할 수 있습니다."

- company_manager:
  "현재 입력된 근로조건에서는 장시간 노동 → 피로 누적 → 사고 위험 증가 흐름이 확인될 수 있어, 기업 차원에서 근무환경 개선과 지원제도 활용을 검토할 수 있습니다."

- labor_consultant:
  "상담 참고자료로 볼 때, 장시간 노동 → 피로 누적 → 사고 위험 증가 흐름과 관련된 위험 신호가 있어, 해당 정책을 검토 자료로 활용할 수 있습니다."

4. viewer_role별 표현
- viewer_role이 employee이면 개인이 이해하기 쉬운 말로 작성한다.
- viewer_role이 company_manager이면 기업·관리자가 점검하거나 제도 도입을 검토하는 말로 작성한다.
- viewer_role이 labor_consultant이면 상담 참고자료처럼 신중하게 작성한다.

5. 표현 규칙
- "확정됩니다", "반드시 산재입니다", "법적으로 인정됩니다" 같은 표현 금지.
- "점검할 수 있습니다", "검토할 수 있습니다", "예방 차원에서 참고할 수 있습니다"처럼 작성한다.
- 산재는 확정 표현이 아니라 "산재 예방", "산재 위험 신호 점검", "사전 예방" 맥락으로만 사용한다.
- 반드시 JSON만 출력한다.
"""

def _replace_rag_keywords(text: str) -> str:
    if not isinstance(text, str):
        return text

    replace_map = {
        "long_working_hours": "장시간 노동",
        "high_stress": "높은 스트레스",
        "low_wage": "낮은 임금 수준",
        "employment_instability": "고용 불안정",
        "industrial_accident_risk": "산업재해 위험",
        "burnout_risk": "번아웃 위험",
        "childcare_caregiving": "육아·돌봄 병행",
        "elderly_worker": "고령 근로자",
        "emotional_labor": "감정노동",
        "work_hours": "근로시간",
        "fatigue": "피로 누적",
        "recovery": "회복 여건",
        "stress": "스트레스",
        "workload": "업무부담",
        "wage": "임금 수준",
        "employment_stability": "고용안정성",
        "income_uncertainty": "소득 불확실성",
        "accident_risk": "사고 위험",
    }

    for key, value in replace_map.items():
        text = text.replace(key, value)

    return text

def _normalize_rag_ai_result(ai_result: dict, source_payload: dict) -> dict:
    if not isinstance(ai_result, dict):
        return {
            "rag_summary": "",
            "explanation_cards": [],
            "policy_cards": []
        }

    rag = source_payload.get("rag", source_payload)

    source_explanations = rag.get("matched_explanations", [])
    source_policies = rag.get("recommended_policies", [])

    allowed_titles = {
        item.get("title")
        for item in source_explanations
        if isinstance(item, dict) and item.get("title")
    }

    allowed_policy_names = {
        item.get("policy_name")
        for item in source_policies
        if isinstance(item, dict) and item.get("policy_name")
    }

    explanation_cards = ai_result.get("explanation_cards", [])
    if not isinstance(explanation_cards, list):
        explanation_cards = []

    policy_cards = ai_result.get("policy_cards", [])
    if not isinstance(policy_cards, list):
        policy_cards = []

    if not isinstance(ai_result.get("rag_summary"), str):
        ai_result["rag_summary"] = ""

    ai_result["rag_summary"] = _replace_rag_keywords(ai_result["rag_summary"])

    ai_result["explanation_cards"] = [
        item for item in explanation_cards
        if isinstance(item, dict) and item.get("title") in allowed_titles
    ][:2]

    ai_result["policy_cards"] = [
        item for item in policy_cards
        if isinstance(item, dict) and item.get("policy_name") in allowed_policy_names
    ][:3]

    for item in ai_result["explanation_cards"]:
        item["ai_comment"] = _replace_rag_keywords(item.get("ai_comment", ""))

        if not isinstance(item.get("risk_flow"), list):
            item["risk_flow"] = []

        item["risk_flow"] = [
            _replace_rag_keywords(flow)
            for flow in item["risk_flow"]
            if isinstance(flow, str)
        ]

    for item in ai_result["policy_cards"]:
        item["short_summary"] = _replace_rag_keywords(item.get("short_summary", ""))
        item["user_action"] = _replace_rag_keywords(item.get("user_action", ""))
        item["recommendation_reason"] = _replace_rag_keywords(
            item.get("recommendation_reason", "")
        )
        item["how_to_use"] = _replace_rag_keywords(item.get("how_to_use", ""))
        item["matched_reason"] = _replace_rag_keywords(item.get("matched_reason", ""))
        item["risk_flow_text"] = _replace_rag_keywords(item.get("risk_flow_text", ""))

        if not isinstance(item.get("risk_flow"), list):
            item["risk_flow"] = []

        item["risk_flow"] = [
            _replace_rag_keywords(flow)
            for flow in item["risk_flow"]
            if isinstance(flow, str)
        ]

    return ai_result


def generate_rag_ai_result(rag_payload: dict) -> dict:
    
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                {"role": "user", "content": build_rag_prompt(rag_payload)},
            ]
        )

        text = (response.output_text or "").strip()
        print("[RAG AI RAW TEXT]", text)

        if not text:
            raise ValueError("RAG AI 응답 output_text가 비어 있습니다.")

        cleaned = _clean_json_text(text)
        print("[RAG AI CLEANED TEXT]", cleaned)

        parsed = json.loads(cleaned)
        print("[RAG AI PARSED]", parsed)

        normalized = _normalize_rag_ai_result(parsed, rag_payload)
        print("[RAG AI NORMALIZED]", normalized)

        return normalized

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("[RAG AI SERVICE ERROR]", repr(e))
        raise