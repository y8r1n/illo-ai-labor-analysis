from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any
import json

import pandas as pd


RADAR_LABELS = ["고용형태", "업종", "근로시간", "임금수준", "체력", "스트레스요인"]
COMPARISON_ACTIVE_AXES = ["고용형태", "근로시간", "임금수준"]
COMPARISON_INACTIVE_AXES = ["업종", "체력", "스트레스요인"]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    return str(value)


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _score_summary_message(score: float, score_group: str) -> str:
    if score_group == "양호":
        return "현재 노동환경 점수는 양호한 수준이며, 전반적으로 안정적인 상태로 해석할 수 있습니다."
    if score_group == "보통":
        return "현재 노동환경 점수는 보통 수준이며, 일부 항목에서 개선이 필요합니다."
    if score_group == "주의 필요":
        return "현재 노동환경 점수는 주의가 필요한 수준으로, 주요 하락 요인을 우선적으로 점검할 필요가 있습니다."
    if score_group == "위험":
        return "현재 노동환경 점수는 위험 수준으로, 노동환경의 여러 요소가 점수 하락에 영향을 주고 있습니다."
    if score_group == "과로 위험":
        return "현재 노동환경 점수는 과로 위험 수준으로, 장시간 노동 또는 구조적 부담 요인에 대한 점검이 필요합니다."
    return f"현재 노동환경 점수는 {score:.2f}점 수준입니다."


def _split_factor_text(text: str) -> list[str]:
    raw = _safe_str(text).strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split("|") if item.strip()]


def _factor_title_from_message(message: str) -> str:
    if "비정규 고용형태" in message or "고용안정성" in message or "정규 고용형태" in message:
        return "고용형태"
    if "업종" in message:
        return "업종"
    if "스트레스" in message:
        return "스트레스"
    if "체력" in message:
        return "체력"
    if "임금" in message:
        return "임금 수준"
    if "업무강도" in message or "근로시간 대비 임금 부담" in message:
        return "업무강도"
    if "근로시간" in message:
        return "근로시간"
    if "연령" in message:
        return "연령 보정"
    return "기타"


def _build_factor_items(row: pd.Series, messages: list[str], factor_type: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    for msg in messages:
        title = _factor_title_from_message(msg)

        value_map = {
            "고용형태": _safe_float(row.get("employment_score")),
            "업종": _safe_float(row.get("industry_weight")),
            "스트레스": _safe_float(row.get("stress_weight")),
            "체력": _safe_float(row.get("physical_weight")),
            "임금 수준": _safe_float(row.get("wage_score")),
            "업무강도": _safe_float(row.get("job_intensity_score")),
            "근로시간": _safe_float(row.get("work_time_score")),
            "연령 보정": _safe_float(row.get("age_weight")),
            "기타": 0.0,
        }

        items.append(
            {
                "type": factor_type,
                "title": title,
                "value": round(value_map.get(title, 0.0), 6),
                "message": msg,
            }
        )

    return items


def _get_summary_average(
    analysis_summary_df: pd.DataFrame,
    summary_type: str,
    group_name: str,
) -> dict[str, float] | None:
    if analysis_summary_df.empty:
        return None

    filtered = analysis_summary_df[
        (analysis_summary_df["summary_type"] == summary_type)
        & (analysis_summary_df["group_name"] == group_name)
    ]

    if filtered.empty:
        return None

    row = filtered.iloc[0]
    return {
        "avg_work_hours": _safe_float(row.get("avg_work_hours")),
        "avg_wage": _safe_float(row.get("avg_wage")),
    }

def _approx_avg_scores_from_summary(
    *,
    avg_work_hours: float,
    avg_wage: float,
    employment_score: float = 0.85,
    max_wage: float = 4383000.0,
) -> dict[str, float]:
    """
    비교 가능한 축(고용형태, 근로시간, 임금수준)만 근사 계산.
    """
    standard_work_hours = 160.0

    work_time_score = max(0.0, min(1.0, 1 - abs(avg_work_hours - standard_work_hours) / standard_work_hours))
    wage_score = max(0.0, min(1.0, avg_wage / max_wage if max_wage > 0 else 0.0))


    # 간단 근사 업무강도 점수 (비교 레이더에는 직접 사용 안 함)
    if avg_wage <= 0:
        job_intensity_score = 0.0
    else:
        raw = avg_work_hours / avg_wage
        job_intensity_score = max(0.0, min(1.0, 1 - min(raw / 0.0001, 1.0)))

    base_score = (
        (work_time_score * 0.3)
        + (wage_score * 0.3)
        + (job_intensity_score * 0.2)
        + (employment_score * 0.2)
    )

    return {
        "work_time_score": round(work_time_score, 6),
        "wage_score": round(wage_score, 6),
        "job_intensity_score": round(job_intensity_score, 6),
        "employment_score": round(employment_score, 6),
        "base_score": round(base_score, 6),
    }

def calculate_difference_with_direction(user_score: float, avg_score: float | None):
    if avg_score is None:
        return None, None

    diff = round(user_score - avg_score, 6)

    if diff > 0:
        direction = "higher"
    elif diff < 0:
        direction = "lower"
    else:
        direction = "same"

    return diff, direction

def build_front_result(
    result_row: pd.Series,
    analysis_summary_df: pd.DataFrame,
) -> dict[str, Any]:
    employment_type = _safe_str(result_row.get("employment_type"))
    age_group = _safe_str(result_row.get("age_group"))

    gender_raw = _safe_str(result_row.get("gender"))
    display_gender = gender_raw
    gender = normalize_gender(gender_raw)

    industry = _safe_str(result_row.get("industry"))
    physical_level = _safe_str(result_row.get("physical_level"))
    stress_level = _safe_str(result_row.get("stress_level"))

    workload_score = _safe_float(result_row.get("workload_score"))
    score_group = _safe_str(result_row.get("score_group"))

    risk_index = _safe_float(result_row.get("risk_index"))
    risk_percent = _safe_float(result_row.get("risk_percent"))
    risk_level = _safe_str(result_row.get("risk_level"))
    risk_message = _safe_str(result_row.get("risk_message"))

    work_time_score = _safe_float(result_row.get("work_time_score"))
    wage_score = _safe_float(result_row.get("wage_score"))
    job_intensity_score = _safe_float(result_row.get("job_intensity_score"))
    employment_score = _safe_float(result_row.get("employment_score"))

    age_weight = _safe_float(result_row.get("age_weight"), 1.0)
    industry_weight = _safe_float(result_row.get("industry_weight"), 1.0)
    physical_weight = _safe_float(result_row.get("physical_weight"), 1.0)
    stress_weight = _safe_float(result_row.get("stress_weight"), 1.0)

    negative_messages = _split_factor_text(_safe_str(result_row.get("negative_factors")))
    positive_messages = _split_factor_text(_safe_str(result_row.get("positive_factors")))

    negative_items = _build_factor_items(result_row, negative_messages, "negative")
    positive_items = _build_factor_items(result_row, positive_messages, "positive")
    now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
    

    # 고용형태 평균 매칭
    if "정규" in employment_type:
        job_avg = _get_summary_average(analysis_summary_df, "employment_type", "정규직")
        job_employment_score = 1.0
    elif "비정규" in employment_type:
        job_avg = _get_summary_average(analysis_summary_df, "employment_type", "비정규직")
        job_employment_score = 0.7
    else:
        job_avg = None
        job_employment_score = 0.85

    age_avg = _get_summary_average(
        analysis_summary_df=analysis_summary_df,
        summary_type="age_group",
        group_name=age_group,   
    )
    
    gender_raw = _safe_str(result_row.get("gender"))
    gender = normalize_gender(gender_raw)
    display_gender = gender_raw

    gender_avg = _get_summary_average(
    analysis_summary_df=analysis_summary_df,
    summary_type="gender",
    group_name=gender,
)

    current_wage = _safe_float(result_row.get("wage"))
    max_wage = max(current_wage / wage_score if wage_score > 0 else current_wage, current_wage, 4383000.0)

    if job_avg:
        job_avg_scores = _approx_avg_scores_from_summary(
            avg_work_hours=job_avg["avg_work_hours"],
            avg_wage=job_avg["avg_wage"],
            employment_score=job_employment_score,
            max_wage=max_wage,
        )
    else:
        job_avg_scores = {
            "work_time_score": 0.0,
            "wage_score": 0.0,
            "job_intensity_score": 0.0,
            "employment_score": 0.0,
            "base_score": 0.0,
        }

    if age_avg:
        age_avg_scores = _approx_avg_scores_from_summary(
            avg_work_hours=age_avg["avg_work_hours"],
            avg_wage=age_avg["avg_wage"],
            employment_score=0.85,
            max_wage=max_wage,
        )
    else:
        age_avg_scores = {
            "work_time_score": 0.0,
            "wage_score": 0.0,
            "job_intensity_score": 0.0,
            "employment_score": 0.0,
            "base_score": 0.0,
        }

    job_diff, job_direction = calculate_difference_with_direction(
        workload_score,
        job_avg_scores["base_score"],
    )

    age_diff, age_direction = calculate_difference_with_direction(
        workload_score,
        age_avg_scores["base_score"],
    )

    user_full_chart = {
        "labels": RADAR_LABELS,
        "datasets": [
            {
                "name": "나의 점수",
                "values": [
                    round(_clip01(employment_score), 6),
                    round(_clip01(industry_weight), 6),
                    round(_clip01(work_time_score), 6),
                    round(_clip01(wage_score), 6),
                    round(_clip01(physical_weight), 6),
                    round(_clip01(stress_weight), 6),
                ],
            }
        ],
    }

    comparison_chart = {
        "labels": RADAR_LABELS,
        "active_axes": COMPARISON_ACTIVE_AXES,
        "inactive_axes": COMPARISON_INACTIVE_AXES,
        "datasets": [
            {
                "name": "나의 점수",
                "values": [
                    round(_clip01(employment_score), 6),
                    None,
                    round(_clip01(work_time_score), 6),
                    round(_clip01(wage_score), 6),
                    None,
                    None,
                ],
            },
            {
                "name": "직종환경이 비슷한 평균",
                "values": [
                    round(_clip01(job_avg_scores["employment_score"]), 6),
                    None,
                    round(_clip01(job_avg_scores["work_time_score"]), 6),
                    round(_clip01(job_avg_scores["wage_score"]), 6),
                    None,
                    None,
                ],
            },
            {
                "name": "나의 연령대 평균",
                "values": [
                    round(_clip01(age_avg_scores["employment_score"]), 6),
                    None,
                    round(_clip01(age_avg_scores["work_time_score"]), 6),
                    round(_clip01(age_avg_scores["wage_score"]), 6),
                    None,
                    None,
                ],
            },
            
        ],
        "note": "업종, 체력, 스트레스 항목은 비교 평균 데이터가 없어 비교 레이더에서 제외되었습니다.",
    }

    tooltip_data = {
        "고용형태": {
            "user_score": round(_clip01(employment_score), 6),
            "job_avg_score": round(_clip01(job_avg_scores["employment_score"]), 6),
            "age_avg_score": round(_clip01(age_avg_scores["employment_score"]), 6),
            "message": "고용형태는 고용안정성 점수에 반영됩니다.",
            "comparable": True,
        },
        "업종": {
            "user_score": round(_clip01(industry_weight), 6),
            "job_avg_score": None,
            "age_avg_score": None,
            "message": "업종은 위험도 보정값 형태로 최종 점수에 반영됩니다.",
            "comparable": False,
        },
        "근로시간": {
            "user_score": round(_clip01(work_time_score), 6),
            "job_avg_score": round(_clip01(job_avg_scores["work_time_score"]), 6),
            "age_avg_score": round(_clip01(age_avg_scores["work_time_score"]), 6),
            "message": "근로시간은 기준 근로시간 160시간에 가까울수록 높은 점수를 받습니다.",
            "comparable": True,
        },
        "임금수준": {
            "user_score": round(_clip01(wage_score), 6),
            "job_avg_score": round(_clip01(job_avg_scores["wage_score"]), 6),
            "age_avg_score": round(_clip01(age_avg_scores["wage_score"]), 6),
            "message": "임금 수준은 전체 최대 임금 대비 상대 점수로 반영됩니다.",
            "comparable": True,
        },
        "체력": {
            "user_score": round(_clip01(physical_weight), 6),
            "job_avg_score": None,
            "age_avg_score": None,
            "message": "체력 수준은 개인의 신체적 부담 수용 능력을 반영합니다.",
            "comparable": False,
        },
        "스트레스요인": {
            "user_score": round(_clip01(stress_weight), 6),
            "job_avg_score": None,
            "age_avg_score": None,
            "message": "스트레스 민감도는 동일 환경에서도 점수에 추가 영향을 줍니다.",
            "comparable": False,
        },
    }

    front_result = {
        "summary": {
            "workload_score": round(workload_score, 6),
            "score_group": score_group,
            "score_percent": round(workload_score * 100, 2),
            "summary_message": _score_summary_message(workload_score, score_group),
        },

        "risk": {
            "risk_index": round(risk_index, 6),
            "risk_percent": round(risk_percent, 2),
            "risk_level": risk_level,
            "risk_message": risk_message,
        },
        
        "user_input": {
            "employment_type": employment_type,
            "gender": gender,
            "age_group": age_group,
            "industry": industry,
            "physical_level": physical_level,
            "stress_level": stress_level,
        },
        "score_breakdown": {
            "work_time_score": round(work_time_score, 6),
            "wage_score": round(wage_score, 6),
            "job_intensity_score": round(job_intensity_score, 6),
            "employment_score": round(employment_score, 6),
            "base_score": round(_safe_float(result_row.get("base_score")), 6),
        },
        "weights": {
            "age_weight": round(age_weight, 6),
            "industry_weight": round(industry_weight, 6),
            "physical_weight": round(physical_weight, 6),
            "stress_weight": round(stress_weight, 6),
        },
        "radar_charts": {
            "user_full": user_full_chart,
            "comparison": comparison_chart,
        },
       "comparisons": {
    "job_average": {
        "group_name": "직종환경이 비슷한 평균",
        "overall_score": round(job_avg_scores["base_score"], 6),
        "difference_from_user": job_diff,
        "direction": job_direction,
    },
    "age_average": {
        "group_name": "나의 연령대 평균",
        "overall_score": round(age_avg_scores["base_score"], 6),
        "difference_from_user": age_diff,
        "direction": age_direction,
    },
     "gender_average": {
        "group_name": f"나의 성별 평균 ({display_gender})",
        "avg_work_hours": gender_avg["avg_work_hours"] if gender_avg else None,
        "avg_wage": gender_avg["avg_wage"] if gender_avg else None,
    },
},
        "factors": {
            "negative": negative_items,
            "positive": positive_items,
        },
        "tooltip_data": tooltip_data,
        "detail_explanations": {
            "employment_type": "고용형태는 고용안정성 점수에 직접 반영됩니다.",
            "industry": "업종 위험도는 보정계수 형태로 최종 점수에 영향을 줍니다.",
            "work_time": "근로시간은 기준 근로시간 160시간과의 차이를 기준으로 점수화됩니다.",
            "wage": "임금 수준은 전체 최대 임금 대비 상대 점수로 계산됩니다.",
            "physical": "체력 수준은 개인의 신체적 부담 수용 능력을 반영합니다.",
            "stress": "스트레스 민감도는 동일 조건에서도 점수에 추가 영향을 줍니다.",
        },
       "report_meta": {
            "generated_at": now_kst.isoformat(timespec="seconds"),
            "generated_at_display": now_kst.strftime("%Y-%m-%d %H:%M:%S"),
            "disclaimer": "본 결과는 참고용 분석 자료이며, 법적 판단을 대체하지 않습니다.",
            "pdf_download_available": True,
        },
    }

    return front_result


def save_front_result_json(front_result: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8-sig") as f:
        json.dump(front_result, f, ensure_ascii=False, indent=2)


def normalize_gender(gender: str) -> str:
    if gender in ["여성", "여"]:
        return "여"
    elif gender in ["남성", "남"]:
        return "남"
    return gender