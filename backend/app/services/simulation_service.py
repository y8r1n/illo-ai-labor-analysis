from __future__ import annotations

from typing import Any
import pandas as pd

from app.services.scoring_service import calculate_workload_risk_index


STANDARD_WORK_HOURS = 160.0


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_sim_item(
    *,
    sim_type: str,
    title: str,
    before: Any,
    after: Any,
    before_score: float,
    after_result: dict[str, Any],
    message: str,
) -> dict[str, Any]:
    improved_score = float(after_result["workload_score"])
    diff = round(improved_score - before_score, 6)

    return {
        "type": sim_type,
        "title": title,
        "before": before,
        "after": after,
        "current_score": round(before_score, 6),
        "improved_score": round(improved_score, 6),
        "score_diff": diff,
        "score_group": after_result.get("score_group"),
        "risk_level": after_result.get("risk_level"),
        "message": message,
    }


def run_simulation(
    *,
    raw_df: pd.DataFrame,
    result_row: pd.Series,
) -> dict[str, Any]:
    current_score = _to_float(result_row.get("workload_score"))
    current_work_hours = _to_float(result_row.get("work_hours"), STANDARD_WORK_HOURS)
    current_wage = _to_float(result_row.get("wage"))

    employment_type = str(result_row.get("employment_type", "")).strip()
    age_group = str(result_row.get("age_group", "")).strip()
    industry = str(result_row.get("industry", "")).strip()
    physical_level = str(result_row.get("physical_level", "")).strip()
    stress_level = str(result_row.get("stress_level", "")).strip()

    # A. 메인 시뮬레이션: 근로시간
    # 현재 시간이 160보다 크면 160으로 낮춤
    # 현재 시간이 160보다 작으면 현재값 유지 (무리하게 올리는 시나리오는 만들지 않음)
    recommended_work_hours = min(current_work_hours, STANDARD_WORK_HOURS)

    main_result = calculate_workload_risk_index(
        raw_df=raw_df,
        employment_type=employment_type,
        age_group=age_group,
        industry=industry,
        physical_level=physical_level,
        stress_level=stress_level,
        work_hours=recommended_work_hours,
        wage=current_wage,
    )

    main_simulation = _build_sim_item(
        sim_type="work_hours",
        title="근로시간 조정",
        before=current_work_hours,
        after=recommended_work_hours,
        before_score=current_score,
        after_result=main_result,
        message="근로시간을 기준 근로시간 범위에 가깝게 조정했을 때의 점수 변화입니다.",
    )

    # B. 보조 시뮬레이션
    sub_simulations: list[dict[str, Any]] = []

    # 스트레스: 높음 -> 보통, 보통 -> 낮음
    stress_map = {
        "높음": "보통",
        "보통": "낮음",
    }
    if stress_level in stress_map:
        new_stress = stress_map[stress_level]
        stress_result = calculate_workload_risk_index(
            raw_df=raw_df,
            employment_type=employment_type,
            age_group=age_group,
            industry=industry,
            physical_level=physical_level,
            stress_level=new_stress,
            work_hours=current_work_hours,
            wage=current_wage,
        )
        sub_simulations.append(
            _build_sim_item(
                sim_type="stress",
                title="스트레스 완화 가정",
                before=stress_level,
                after=new_stress,
                before_score=current_score,
                after_result=stress_result,
                message="자기보고형 스트레스 수준이 완화된다고 가정했을 때의 참고 시뮬레이션입니다.",
            )
        )

    # 체력: 낮음 -> 보통, 보통 -> 높음
    physical_map = {
        "낮음": "보통",
        "보통": "높음",
    }
    if physical_level in physical_map:
        new_physical = physical_map[physical_level]
        physical_result = calculate_workload_risk_index(
            raw_df=raw_df,
            employment_type=employment_type,
            age_group=age_group,
            industry=industry,
            physical_level=new_physical,
            stress_level=stress_level,
            work_hours=current_work_hours,
            wage=current_wage,
        )
        sub_simulations.append(
            _build_sim_item(
                sim_type="physical",
                title="체력 개선 가정",
                before=physical_level,
                after=new_physical,
                before_score=current_score,
                after_result=physical_result,
                message="자기보고형 체력 수준이 개선된다고 가정했을 때의 참고 시뮬레이션입니다.",
            )
        )

    # 고용형태: 비정규근로자 -> 정규근로자
    if employment_type == "비정규근로자":
        new_employment_type = "정규근로자"
        employment_result = calculate_workload_risk_index(
            raw_df=raw_df,
            employment_type=new_employment_type,
            age_group=age_group,
            industry=industry,
            physical_level=physical_level,
            stress_level=stress_level,
            work_hours=current_work_hours,
            wage=current_wage,
        )
        sub_simulations.append(
            _build_sim_item(
                sim_type="employment",
                title="고용안정성 개선 가정",
                before=employment_type,
                after=new_employment_type,
                before_score=current_score,
                after_result=employment_result,
                message="고용안정성이 개선된다고 가정했을 때의 참고 시뮬레이션입니다.",
            )
        )

    # 개선폭 큰 순으로 정렬
    sub_simulations.sort(key=lambda x: x["score_diff"], reverse=True)

    return {
        "main": main_simulation,
        "sub": sub_simulations,
    }