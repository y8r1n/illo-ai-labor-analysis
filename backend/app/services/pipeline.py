from __future__ import annotations

from pathlib import Path
import pandas as pd

from app.services.scoring_service import calculate_batch_from_user_inputs
from app.services.analysis_service import build_analysis_summary, add_explanation_columns
from app.services.response_formatter import build_front_result
from app.core.config import RAW_DATA_PATH, ANALYSIS_RAW_DATA_PATH
from app.services.simulation_service import run_simulation

def read_csv_flexible(path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    last_error = None

    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError as e:
            last_error = e
            continue

    raise ValueError(f"CSV 파일 인코딩을 읽지 못했습니다: {path}\n마지막 오류: {last_error}")

def _validate_payload(payload: dict) -> None:
    required_fields = [
        "employment_type",
        "age_group",
        "gender",
        "industry",
        "work_hours",
        "wage",
        "physical_level",
        "stress_level",
        "rest_break_level",        # 휴게시간
        "work_pattern_level",      # 근무패턴
    ]

    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise ValueError(f"필수 입력값이 없습니다: {', '.join(missing)}")

    if payload["work_hours"] in [None, ""]:
        raise ValueError("work_hours 값이 비어 있습니다.")

    if payload["wage"] in [None, ""]:
        raise ValueError("wage 값이 비어 있습니다.")


def _normalize_payload(payload: dict) -> dict:
    """
    프론트에서 받은 값을 모델 입력 형식에 맞게 정리
    """
    normalized = {
        "employment_type": str(payload["employment_type"]).strip(),
        "age_group": str(payload["age_group"]).strip(),
        "gender": str(payload["gender"]).strip(),
        "industry": str(payload["industry"]).strip(),
        "work_hours": float(payload["work_hours"]),
        "wage": float(payload["wage"]),
        "physical_level": str(payload["physical_level"]).strip(),
        "stress_level": str(payload["stress_level"]).strip(),
        "rest_break_level": str(payload["rest_break_level"]).strip(),
        "work_pattern_level": str(payload["work_pattern_level"]).strip(),
    }
    return normalized

def extract_rag_match_inputs(front_result: dict) -> dict:
    risk_factors = []
    related_factors = []

    negative_titles = [
        item.get("title", "")
        for item in front_result.get("factors", {}).get("negative", [])
    ]

    negative_text = " ".join(negative_titles)

    if "근로시간" in negative_text or "업무부담" in negative_text:
        risk_factors.append("long_working_hours")
        related_factors.extend(["work_hours", "fatigue", "recovery"])

    if "고용안정성" in negative_text:
        risk_factors.append("employment_instability")
        related_factors.extend([
            "employment_stability",
            "income_uncertainty",
            "stress"
        ])

    if (
        "스트레스" in negative_text
        or front_result.get("weights", {}).get("stress_weight", 1) < 0.95
    ):
        risk_factors.append("high_stress")
        related_factors.extend(["stress", "workload", "recovery"])

    if "임금" in negative_text or "임금수준" in negative_text:
        risk_factors.append("low_wage")
        related_factors.extend(["wage", "income_uncertainty", "employment_stability"])

    return {
        "risk_factors": list(dict.fromkeys(risk_factors)),
        "related_factors": list(dict.fromkeys(related_factors)),
    }

def run_analysis_pipeline(payload: dict) -> dict:
    _validate_payload(payload)
    normalized_payload = _normalize_payload(payload)

    raw_df = read_csv_flexible(RAW_DATA_PATH)
    analysis_raw_df = read_csv_flexible(ANALYSIS_RAW_DATA_PATH)

    user_input_df = pd.DataFrame([normalized_payload])

    result_df = calculate_batch_from_user_inputs(
        raw_df=raw_df,
        user_input_df=user_input_df,
    )

    result_df = add_explanation_columns(result_df)
    analysis_summary_df = build_analysis_summary(analysis_raw_df)
    result_df["gender"] = user_input_df["gender"].values

    if result_df.empty:
        raise ValueError("분석 결과가 생성되지 않았습니다.")

    front_result = build_front_result(
        result_row=result_df.iloc[0],
        analysis_summary_df=analysis_summary_df,
    )

    rag_inputs = extract_rag_match_inputs(front_result)

    front_result["risk_factors"] = rag_inputs["risk_factors"]
    front_result["related_factors"] = rag_inputs["related_factors"]

    simulation_result = run_simulation(
        raw_df=raw_df,
        result_row=result_df.iloc[0],
    )

    front_result["simulation"] = simulation_result

    return front_result
