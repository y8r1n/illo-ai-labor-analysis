from __future__ import annotations

import pandas as pd

from app.core.preprocess import load_and_validate_analysis_data

def build_analysis_summary(analysis_df: pd.DataFrame) -> pd.DataFrame:
    data = load_and_validate_analysis_data(analysis_df)

    summary_frames = []

    # 1. 성별 평균
    gender_summary = (
        data.groupby("gender", as_index=False)
        .agg(
            avg_work_hours=("work_hours", "mean"),
            avg_wage=("wage", "mean"),
        )
    )
    gender_summary["summary_type"] = "gender"

    # 2. 고용형태 평균
    employment_summary = (
        data.groupby("employment_type", as_index=False)
        .agg(
            avg_work_hours=("work_hours", "mean"),
            avg_wage=("wage", "mean"),
        )
    )
    employment_summary["summary_type"] = "employment_type"

    # 3. 연령대 평균
    age_summary = (
        data.groupby("age_group", as_index=False)
        .agg(
            avg_work_hours=("work_hours", "mean"),
            avg_wage=("wage", "mean"),
        )
    )
    age_summary["summary_type"] = "age_group"

    # 4. 고용형태 + 성별 평균
    emp_gender_summary = (
        data.groupby(["employment_type", "gender"], as_index=False)
        .agg(
            avg_work_hours=("work_hours", "mean"),
            avg_wage=("wage", "mean"),
        )
    )
    emp_gender_summary["summary_type"] = "employment_type_gender"

    # 컬럼 통일
    gender_summary = gender_summary.rename(columns={"gender": "group_name"})
    employment_summary = employment_summary.rename(columns={"employment_type": "group_name"})
    age_summary = age_summary.rename(columns={"age_group": "group_name"})
    emp_gender_summary["group_name"] = (
        emp_gender_summary["employment_type"] + "_" + emp_gender_summary["gender"]
    )
    emp_gender_summary = emp_gender_summary[["group_name", "avg_work_hours", "avg_wage", "summary_type"]]

    gender_summary = gender_summary[["group_name", "avg_work_hours", "avg_wage", "summary_type"]]
    employment_summary = employment_summary[["group_name", "avg_work_hours", "avg_wage", "summary_type"]]
    age_summary = age_summary[["group_name", "avg_work_hours", "avg_wage", "summary_type"]]

    summary_frames.extend([
        gender_summary,
        employment_summary,
        age_summary,
        emp_gender_summary,
    ])

    result = pd.concat(summary_frames, ignore_index=True)

    result["avg_work_hours"] = result["avg_work_hours"].round(3)
    result["avg_wage"] = result["avg_wage"].round(3)

    return result

def extract_explanation_factors(row: dict) -> dict:
    negative_candidates = []
    positive_candidates = []

    # 하락 요인 후보 (우선순위 높은 순서)
    if row["industry_weight"] < 1.0:
        negative_candidates.append("업종 특성상 노동환경 점수에 불리한 보정이 적용되었습니다.")
    if row["employment_score"] < 1.0:
        negative_candidates.append("비정규 고용형태로 인해 고용안정성 점수가 낮게 반영되었습니다.")
    if row["stress_weight"] < 1.0:
        negative_candidates.append("스트레스 민감도가 높아 점수 하락 요인으로 작용했습니다.")
    if row["physical_weight"] < 1.0:
        negative_candidates.append("체력 수준이 낮게 반영되어 최종 점수 하락에 영향을 주었습니다.")
    if row["wage_score"] < 0.6:
        negative_candidates.append("임금 수준이 상대적으로 낮아 점수 하락에 영향을 주었습니다.")
    if row["job_intensity_score"] < 0.6:
        negative_candidates.append("근로시간 대비 임금 부담이 커 업무강도 점수가 낮게 나타났습니다.")
    if row["work_time_score"] < 0.7:
        negative_candidates.append("기준 근로시간과 차이가 커 점수 하락에 영향을 주었습니다.")
    if row["age_weight"] < 1.0:
        negative_candidates.append("연령 보정계수가 최종 점수에 다소 불리하게 작용했습니다.")

    # 양호 요인 후보
    if row["employment_score"] == 1.0:
        positive_candidates.append("정규 고용형태로 인해 고용안정성 측면에서 긍정적으로 반영되었습니다.")
    if row["wage_score"] >= 0.8:
        positive_candidates.append("임금 수준은 상대적으로 양호한 편입니다.")
    if row["work_time_score"] >= 0.9:
        positive_candidates.append("근로시간은 기준값에 가까워 안정적으로 반영되었습니다.")
    if row["job_intensity_score"] >= 0.8:
        positive_candidates.append("근로시간 대비 임금 부담이 비교적 안정적인 수준입니다.")
    if row["industry_weight"] >= 1.0:
        positive_candidates.append("업종 보정이 비교적 안정적으로 적용되었습니다.")
    if row["physical_weight"] > 1.0:
        positive_candidates.append("체력 수준이 긍정적으로 반영되었습니다.")
    if row["stress_weight"] > 1.0:
        positive_candidates.append("스트레스 민감도 측면에서 비교적 안정적인 조건으로 반영되었습니다.")
    if row["age_weight"] > 1.0:
        positive_candidates.append("연령 보정계수가 점수에 긍정적으로 반영되었습니다.")

    return {
        "negative_factors": negative_candidates[:3],
        "positive_factors": positive_candidates[:3],
    }


def add_explanation_columns(result_df: pd.DataFrame) -> pd.DataFrame:
    data = result_df.copy()

    negative_texts = []
    positive_texts = []

    for _, row in data.iterrows():
        factors = extract_explanation_factors(row.to_dict())
        negative_texts.append(" | ".join(factors["negative_factors"]))
        positive_texts.append(" | ".join(factors["positive_factors"]))

    data["negative_factors"] = negative_texts
    data["positive_factors"] = positive_texts

    return data