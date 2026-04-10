from __future__ import annotations

from typing import Dict
import pandas as pd


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

STRESS_WEIGHT_MAP = {
    "높음": 0.85,
    "보통": 1.00,
    "낮음": 1.10,
}

# 업종 원점수
INDUSTRY_RISK_SCORE_MAP: Dict[str, float] = {
    "건설업": 1.0,
    "기타": 0.607196,
    "서비스업": 0.1,
    "운수업": 1.0,
    "제조업": 1.0,
}

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


def get_stress_weight(stress_level: str) -> float:
    return STRESS_WEIGHT_MAP.get(stress_level, 1.0)


def get_industry_risk_score(industry: str) -> float:
    if industry not in INDUSTRY_RISK_SCORE_MAP:
        raise ValueError(
            f"지원하지 않는 업종입니다: {industry}. "
            f"사용 가능 업종: {list(INDUSTRY_RISK_SCORE_MAP.keys())}"
        )
    return INDUSTRY_RISK_SCORE_MAP[industry]

def get_industry_weight(industry: str) -> float:
    risk_score = get_industry_risk_score(industry)
    return 1.1 - (risk_score * 0.3)

def get_rest_break_weight(level: str) -> float:
    return REST_BREAK_WEIGHT_MAP.get(level, 1.0)


def get_work_pattern_weight(level: str) -> float:
    return WORK_PATTERN_WEIGHT_MAP.get(level, 1.0)

def calculate_recovery_score(physical_weight: float, rest_weight: float) -> float:
    return (physical_weight + rest_weight) / 2


def calculate_workload_burden_score(stress_weight: float, pattern_weight: float) -> float:
    return (stress_weight + pattern_weight) / 2