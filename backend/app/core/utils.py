from __future__ import annotations

from typing import Dict
from pathlib import Path
import pandas as pd
import json

BASE_DIR = Path(__file__).resolve().parents[2]
REFERENCE_DIR = BASE_DIR / "data" / "reference"


def load_industry_risk_reference() -> pd.DataFrame:
    path = REFERENCE_DIR / "industry_risk.csv"
    df = pd.read_csv(path, encoding="utf-8")
    print(df["industry"].tolist())

    required_cols = ["industry", "accident_count", "risk_ratio", "weight"]
    validate_required_columns(df, required_cols)

    df["industry"] = df["industry"].astype(str).str.strip()
    df["accident_count"] = pd.to_numeric(df["accident_count"], errors="coerce")
    df["risk_ratio"] = pd.to_numeric(df["risk_ratio"], errors="coerce")
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    df = df.dropna(subset=["industry", "risk_ratio", "weight"])
    return df

def get_industry_reference_row(industry: str) -> pd.Series:
    df = load_industry_risk_reference()
    normalized_industry = normalize_industry_name(industry)

    filtered = df[df["industry"] == normalized_industry]
    if filtered.empty:
        raise ValueError(f"industry_risk.csv에 없는 업종입니다: {industry}")

    return filtered.iloc[0]


def get_industry_risk_score(industry: str) -> float:
    row = get_industry_reference_row(industry)
    return float(row["risk_ratio"])


def get_industry_weight(industry: str) -> float:
    row = get_industry_reference_row(industry)
    return float(row["weight"])


def load_stress_reference() -> dict:
    path = REFERENCE_DIR / "stress_score.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required_keys = [
        "emotion_labor",
        "job_insecurity",
        "time_pressure",
        "shift_work",
        "long_working_hours",
    ]
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ValueError(f"stress_score.json 필수 키 누락: {missing}")

    return data


def calculate_stress_index(stress_ref: dict) -> float:
    values = [
        float(stress_ref["emotion_labor"]),
        float(stress_ref["job_insecurity"]),
        float(stress_ref["time_pressure"]),
        float(stress_ref["shift_work"]),
        float(stress_ref["long_working_hours"]),
    ]
    return sum(values) / len(values)

def convert_stress_index_to_weight(stress_index: float) -> float:
    # 1~5 범위를 0~1로 정규화
    normalized = (stress_index - 1.0) / 4.0
    normalized = max(0.0, min(1.0, normalized))

    # 스트레스 높을수록 가중치 낮아짐
    weight = 1.10 - (normalized * 0.25)
    return round(weight, 6)


AGE_WEIGHT_MAP: Dict[str, float] = {
    "20대": 0.95,
    "30대": 1.00,
    "40대": 1.05,
    "50대": 1.00,
    "60대": 1.10,
}

EMPLOYMENT_SCORE_MAP = {
    "정규근로자": 1.0,
    "비정규근로자": 0.7,
    "정규직": 1.0,
    "비정규직": 0.7,
}

PHYSICAL_WEIGHT_MAP = {
    "낮음": 0.85,
    "보통": 1.00,
    "높음": 1.10,
}

PERSONAL_STRESS_ADJUSTMENT_MAP = {
    "낮음": 1.05,
    "보통": 1.00,
    "높음": 0.95,
}

def get_personal_stress_adjustment(stress_level: str) -> float:
    return PERSONAL_STRESS_ADJUSTMENT_MAP.get(stress_level, 1.0)

#휴게시간
REST_BREAK_WEIGHT_MAP = {
    "부족": 0.85,
    "보통": 1.0,
    "충분": 1.1,
}

#근무패턴

WORK_PATTERN_WEIGHT_MAP = {
    "불규칙": 0.85,
    "보통": 1.0,
    "규칙적": 1.1,
}


def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼이 없습니다: {missing}")


def classify_score(score: float) -> str:
    if pd.isna(score):
        return "판단불가"

    if score < 0.2:
        return "과로 위험"
    elif score < 0.4:
        return "위험"
    elif score < 0.6:
        return "주의 필요"
    elif score < 0.8:
        return "보통"
    else:
        return "양호"


def get_age_weight(age_group: str) -> float:
    return AGE_WEIGHT_MAP.get(age_group, 1.0)


def get_employment_score(employment_type: str) -> float:
    return EMPLOYMENT_SCORE_MAP.get(employment_type, 0.7)


def get_physical_weight(physical_level: str) -> float:
    return PHYSICAL_WEIGHT_MAP.get(physical_level, 1.0)


def get_rest_break_weight(level: str) -> float:
    return REST_BREAK_WEIGHT_MAP.get(level, 1.0)


def get_work_pattern_weight(level: str) -> float:
    return WORK_PATTERN_WEIGHT_MAP.get(level, 1.0)

def calculate_recovery_score(physical_weight: float, rest_weight: float) -> float:
    return (physical_weight + rest_weight) / 2


def calculate_workload_burden_score(stress_weight: float, pattern_weight: float) -> float:
    return (stress_weight + pattern_weight) / 2

def normalize_industry_name(industry: str) -> str:
    text = str(industry).strip()

    mapping = {
        "운수업": "운수창고.통신업",
        "운수/창고/통신업": "운수창고.통신업",
        "기타": "기타의사업",
        "전기가스수도업": "전기.가스.증기.수도사업",
        "전기/가스/증기/수도사업": "전기.가스.증기.수도사업",
    }

    return mapping.get(text, text)