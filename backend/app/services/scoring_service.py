from __future__ import annotations

from typing import Any, Dict
import pandas as pd

from app.core.preprocess import (
    calculate_job_intensity_raw,
    calculate_job_intensity_score,
    calculate_wage_score,
    calculate_work_time_score,
    load_and_validate_raw_data,
)
from app.core.utils import (
    calculate_recovery_score,
    calculate_stress_index,
    calculate_workload_burden_score,
    classify_score,
    convert_stress_index_to_weight,
    get_age_weight,
    get_employment_score,
    get_industry_risk_score,
    get_industry_weight,
    get_personal_stress_adjustment,
    get_physical_weight,
    get_rest_break_weight,
    get_work_pattern_weight,
    load_stress_reference,
)


def calculate_base_score(
    work_time_score: float,
    wage_score: float,
    job_intensity_score: float,
    employment_score: float,
) -> float:
    return (
        (work_time_score * 0.3)
        + (wage_score * 0.3)
        + (job_intensity_score * 0.2)
        + (employment_score * 0.2)
    )

def calculate_risk_index(workload_score: float) -> float:
    return round(1 - workload_score, 6)


def classify_risk_level(risk_index: float) -> str:
    if risk_index < 0.20:
        return "양호"
    elif risk_index < 0.40:
        return "보통"
    elif risk_index < 0.60:
        return "주의"
    elif risk_index < 0.80:
        return "위험"
    else:
        return "과로 위험"


def get_risk_message(risk_level: str) -> str:
    if risk_level == "양호":
        return "현재 노동환경 위험 수준은 양호한 편입니다."
    elif risk_level == "보통":
        return "현재 노동환경 위험 수준은 보통이며 일부 항목 점검이 필요합니다."
    elif risk_level == "주의":
        return "현재 노동환경 위험 수준은 주의 단계로, 주요 요인을 살펴볼 필요가 있습니다."
    elif risk_level == "위험":
        return "현재 노동환경 위험 수준은 위험 단계로 개선이 필요합니다."
    else:
        return "현재 노동환경 위험 수준은 과로 위험 단계로, 우선적인 점검과 개선이 필요합니다."


def calculate_workload_risk_index(
    raw_df: pd.DataFrame,
    employment_type: str,
    age_group: str,
    industry: str,
    physical_level: str,
    stress_level: str,
    rest_break_level: str,        # 휴게시간
    work_pattern_level: str,      # 근무패턴
    work_hours: float,
    wage: float,
) -> Dict[str, Any]:
    data = load_and_validate_raw_data(raw_df)

    work_hours = float(work_hours)
    wage = float(wage)

    max_wage = float(data["wage"].max())

    work_time_score = calculate_work_time_score(work_hours)
    wage_score = calculate_wage_score(wage, max_wage)

    job_intensity_raw = calculate_job_intensity_raw(work_hours, wage)
    job_intensity_score = calculate_job_intensity_score(job_intensity_raw, data)

    employment_score = get_employment_score(employment_type)

    base_score = calculate_base_score(
        work_time_score=work_time_score,
        wage_score=wage_score,
        job_intensity_score=job_intensity_score,
        employment_score=employment_score,
    )

    age_weight = get_age_weight(age_group)
    industry_risk_score = get_industry_risk_score(industry)
    industry_weight = get_industry_weight(industry)
    physical_weight = get_physical_weight(physical_level)
    stress_ref = load_stress_reference()

    base_stress_index = calculate_stress_index(stress_ref)
    base_stress_weight = convert_stress_index_to_weight(base_stress_index)

    personal_stress_adjustment = get_personal_stress_adjustment(stress_level)
    stress_weight = base_stress_weight * personal_stress_adjustment
    stress_weight = max(0.7, min(1.1, stress_weight))
    stress_weight = base_stress_weight * personal_stress_adjustment

    rest_weight = get_rest_break_weight(rest_break_level)
    pattern_weight = get_work_pattern_weight(work_pattern_level)

    #  묶음 점수
    recovery_score = calculate_recovery_score(physical_weight, rest_weight)
    workload_burden_score = calculate_workload_burden_score(stress_weight, pattern_weight)
    
    workload_score = (
    base_score
    * age_weight
    * industry_weight
    * recovery_score
    * workload_burden_score
)

    score_group = classify_score(workload_score)

    risk_index = calculate_risk_index(workload_score)
    risk_level = classify_risk_level(risk_index)
    risk_message = get_risk_message(risk_level)

    return {
        "employment_type": employment_type,
        "age_group": age_group,
        "industry": industry,
        "physical_level": physical_level,
        "stress_level": stress_level,
        "work_hours": round(work_hours, 3),
        "wage": round(wage, 3),
        "work_time_score": round(work_time_score, 6),
        "wage_score": round(wage_score, 6),
        "job_intensity_raw": round(job_intensity_raw, 6),
        "job_intensity_score": round(job_intensity_score, 6),
        "employment_score": round(employment_score, 6),
        "base_score": round(base_score, 6),
        "age_weight": round(age_weight, 6),
        "industry_risk_score": round(industry_risk_score, 6),
        "industry_weight": round(industry_weight, 6),
        "physical_weight": round(physical_weight, 6),
        "stress_factors": {
            "emotion_labor": round(float(stress_ref["emotion_labor"]), 6),
            "job_insecurity": round(float(stress_ref["job_insecurity"]), 6),
            "time_pressure": round(float(stress_ref["time_pressure"]), 6),
            "shift_work": round(float(stress_ref["shift_work"]), 6),
            "long_working_hours": round(float(stress_ref["long_working_hours"]), 6),
         },
        "base_stress_index": round(base_stress_index, 6),
        "base_stress_weight": round(base_stress_weight, 6),
        "personal_stress_adjustment": round(personal_stress_adjustment, 6),
        "stress_weight": round(stress_weight, 6),

        "rest_break_level": rest_break_level,
        "work_pattern_level": work_pattern_level,

        "recovery_score": round(recovery_score, 6),
        "workload_burden_score": round(workload_burden_score, 6),
        "workload_score": round(workload_score, 6),
        "score_group": score_group,
        "risk_index": round(risk_index, 6),
        "risk_percent": round(risk_index * 100, 2),
        "risk_level": risk_level,
        "risk_message": risk_message,
    }


def calculate_batch_from_user_inputs(
    raw_df: pd.DataFrame,
    user_input_df: pd.DataFrame,
) -> pd.DataFrame:
    required_cols = [
    "employment_type",
    "age_group",
    "industry",
    "physical_level",
    "stress_level",
    "rest_break_level",       # 휴게시간
    "work_pattern_level",     # 근무패턴
    "work_hours",
    "wage",
]
    missing = [col for col in required_cols if col not in user_input_df.columns]
    if missing:
        raise ValueError(f"user_input_df에 필수 컬럼이 없습니다: {missing}")

    results = []
    for _, row in user_input_df.iterrows():
        result = calculate_workload_risk_index(
            raw_df=raw_df,
            employment_type=str(row["employment_type"]).strip(),
            age_group=str(row["age_group"]).strip(),
            industry=str(row["industry"]).strip(),
            physical_level=str(row["physical_level"]).strip(),
            stress_level=str(row["stress_level"]).strip(),
            rest_break_level=str(row["rest_break_level"]).strip(),
            work_pattern_level=str(row["work_pattern_level"]).strip(),
            work_hours=float(row["work_hours"]),
            wage=float(row["wage"]),
        )
        results.append(result)

    return pd.DataFrame(results)