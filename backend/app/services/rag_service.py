import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAG_DIR = BASE_DIR / "data" / "rag"

EXPLANATION_PATH = RAG_DIR / "explanation_documents.json"
POLICY_PATH = RAG_DIR / "policy_documents.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def overlap_count(a, b):
    return len(set(normalize_list(a)) & set(normalize_list(b)))


def extract_rag_inputs(analysis_result):
    """
    analysis_result 예시:
    {
        "viewer_role": "employee",
        "risk_factors": ["high_stress", "long_working_hours"],
        "related_factors": ["stress", "work_hours", "fatigue"],
        "user_selected_contexts": ["childcare_caregiving"]
    }
    """

    return {
        "viewer_role": analysis_result.get("viewer_role", "employee"),
        "risk_contexts": normalize_list(analysis_result.get("risk_factors", [])),
        "related_factors": normalize_list(analysis_result.get("related_factors", [])),
        "user_selected_contexts": normalize_list(
            analysis_result.get("user_selected_contexts", [])
        ),
    }


def score_explanation(expl, rag_inputs):
    score = 0
    reasons = []

    role = rag_inputs["viewer_role"]
    risk_contexts = rag_inputs["risk_contexts"]
    user_contexts = rag_inputs["user_selected_contexts"]
    related_factors = rag_inputs["related_factors"]

    if role in expl.get("viewer_roles", []):
        score += 1
        reasons.append("viewer_role_match")

    if expl.get("topic") in risk_contexts:
        score += 4
        reasons.append("topic_match")

    auto_match = overlap_count(expl.get("auto_contexts", []), risk_contexts)
    if auto_match:
        score += auto_match * 3
        reasons.append("auto_context_match")

    user_context_match = overlap_count(
        expl.get("user_selected_contexts", []),
        user_contexts
    )
    if user_context_match:
        score += user_context_match * 4
        reasons.append("user_selected_context_match")

    factor_match = overlap_count(expl.get("related_factors", []), related_factors)
    if factor_match:
        score += factor_match * 2
        reasons.append("related_factor_match")

    return score, reasons


def score_policy(policy, rag_inputs, linked_policy_ids):
    score = 0
    reasons = []

    role = rag_inputs["viewer_role"]
    risk_contexts = rag_inputs["risk_contexts"]
    user_contexts = rag_inputs["user_selected_contexts"]
    related_factors = rag_inputs["related_factors"]

    if policy.get("policy_id") in linked_policy_ids:
        score += 6
        reasons.append("linked_policy_match")

    if role in policy.get("viewer_roles", []):
        score += 1
        reasons.append("viewer_role_match")

    context_match = overlap_count(
        policy.get("special_contexts", []),
        risk_contexts + user_contexts
    )
    if context_match:
        score += context_match * 3
        reasons.append("special_context_match")

    factor_match = overlap_count(policy.get("related_factors", []), related_factors)
    if factor_match:
        score += factor_match * 2
        reasons.append("related_factor_match")

    return score, reasons


def get_top_explanations(explanations, rag_inputs, limit=2):
    scored = []

    for expl in explanations:
        score, reasons = score_explanation(expl, rag_inputs)

        if score > 0:
            item = {
                **expl,
                "match_score": score,
                "match_reasons": reasons
            }
            scored.append(item)

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:limit]


def get_top_policies(policies, rag_inputs, matched_explanations, limit=3):
    linked_policy_ids = []

    for expl in matched_explanations:
        linked_policy_ids.extend(expl.get("linked_policy_ids", []))

    linked_policy_ids = list(dict.fromkeys(linked_policy_ids))

    scored = []

    for policy in policies:
        score, reasons = score_policy(policy, rag_inputs, linked_policy_ids)

        if score > 0:
            item = {
                **policy,
                "match_score": score,
                "match_reasons": reasons
            }
            scored.append(item)

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:limit]


def match_rag_resources(analysis_result):
    explanations = load_json(EXPLANATION_PATH)
    policies = load_json(POLICY_PATH)

    rag_inputs = extract_rag_inputs(analysis_result)

    matched_explanations = get_top_explanations(
        explanations=explanations,
        rag_inputs=rag_inputs,
        limit=2
    )

    recommended_policies = get_top_policies(
        policies=policies,
        rag_inputs=rag_inputs,
        matched_explanations=matched_explanations,
        limit=3
    )

    return {
        "matched_explanations": matched_explanations,
        "recommended_policies": recommended_policies,
        "match_debug": rag_inputs
    }


# 테스트용
if __name__ == "__main__":
    sample_result = {
        "viewer_role": "employee",
        "risk_factors": ["high_stress", "long_working_hours"],
        "related_factors": ["stress", "work_hours", "fatigue", "recovery"],
        "user_selected_contexts": []
    }

    result = match_rag_resources(sample_result)
    print(json.dumps(result, ensure_ascii=False, indent=2))