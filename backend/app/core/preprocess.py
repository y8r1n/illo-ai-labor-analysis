from __future__ import annotations

import pandas as pd

from app.core.utils import validate_required_columns


STANDARD_WORK_HOURS = 160.0


def load_and_validate_raw_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        "employment_type",
        "age_group",
        "work_hours",
        "wage",
    ]
    validate_required_columns(raw_df, required_columns)

    data = raw_df.copy()

    data["employment_type"] = data["employment_type"].astype(str).str.strip()
    data["age_group"] = data["age_group"].astype(str).str.strip()

    # work_hours 정리
    data["work_hours"] = (
        data["work_hours"]
        .astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
    )
    data["work_hours"] = pd.to_numeric(data["work_hours"], errors="coerce")

    # wage 정리
    data["wage"] = (
        data["wage"]
        .astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
    )
    data["wage"] = pd.to_numeric(data["wage"], errors="coerce")

    if data["work_hours"].isna().any():
        invalid_rows = data[data["work_hours"].isna()]
        print("[DEBUG] raw_data.csv work_hours 이상 행:")
        print(invalid_rows)
        raise ValueError("raw_data.csv의 work_hours 컬럼에 결측치 또는 숫자가 아닌 값이 있습니다.")

    if data["wage"].isna().any():
        invalid_rows = data[data["wage"].isna()]
        print("[DEBUG] raw_data.csv wage 이상 행:")
        print(invalid_rows)
        raise ValueError("raw_data.csv의 wage 컬럼에 결측치 또는 숫자가 아닌 값이 있습니다.")

    return data


def load_and_validate_analysis_data(analysis_df: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        "employment_type",
        "gender",
        "age_group",
        "work_hours",
        "wage",
    ]
    validate_required_columns(analysis_df, required_columns)

    data = analysis_df.copy()

    for col in ["employment_type", "gender", "age_group"]:
        data[col] = data[col].astype(str).str.strip()

    data["work_hours"] = (
        data["work_hours"]
        .astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
    )
    data["work_hours"] = pd.to_numeric(data["work_hours"], errors="coerce")

    data["wage"] = (
        data["wage"]
        .astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
    )
    data["wage"] = pd.to_numeric(data["wage"], errors="coerce")

    if data["work_hours"].isna().any():
        invalid_rows = data[data["work_hours"].isna()]
        print("[DEBUG] analysis_raw_data.csv work_hours 이상 행:")
        print(invalid_rows)
        raise ValueError("analysis_raw_data.csv의 work_hours 컬럼에 결측치 또는 숫자가 아닌 값이 있습니다.")

    if data["wage"].isna().any():
        invalid_rows = data[data["wage"].isna()]
        print("[DEBUG] analysis_raw_data.csv wage 이상 행:")
        print(invalid_rows)
        raise ValueError("analysis_raw_data.csv의 wage 컬럼에 결측치 또는 숫자가 아닌 값이 있습니다.")

    return data


def get_base_row(raw_df: pd.DataFrame, employment_type: str, age_group: str) -> pd.Series:
    data = load_and_validate_raw_data(raw_df)

    filtered = data[
        (data["employment_type"] == employment_type) &
        (data["age_group"] == age_group)
    ]

    if filtered.empty:
        raise ValueError(
            f"해당 조건의 기본 데이터가 없습니다: employment_type={employment_type}, age_group={age_group}"
        )
    if len(filtered) > 1:
        raise ValueError(
            f"중복된 기본 데이터가 있습니다: employment_type={employment_type}, age_group={age_group}"
        )

    return filtered.iloc[0]


def calculate_work_time_score(work_hours: float) -> float:
    score = 1 - abs(work_hours - STANDARD_WORK_HOURS) / STANDARD_WORK_HOURS
    return max(0.0, min(1.0, score))


def calculate_wage_score(wage: float, max_wage: float) -> float:
    if max_wage <= 0:
        return 0.0
    score = wage / max_wage
    return max(0.0, min(1.0, score))


def calculate_job_intensity_raw(work_hours: float, wage: float) -> float:
    if wage <= 0:
        return 0.0
    return work_hours / wage


def calculate_job_intensity_score(job_intensity_raw: float, raw_df: pd.DataFrame) -> float:
    data = load_and_validate_raw_data(raw_df).copy()
    data["job_intensity_raw"] = data.apply(
        lambda row: calculate_job_intensity_raw(row["work_hours"], row["wage"]),
        axis=1
    )

    min_raw = data["job_intensity_raw"].min()
    max_raw = data["job_intensity_raw"].max()

    if max_raw == min_raw:
        return 1.0

    normalized = (job_intensity_raw - min_raw) / (max_raw - min_raw)
    score = 1 - normalized
    return max(0.0, min(1.0, score))

def parse_currency_to_int(value: str | int | float) -> int:
    text = str(value).replace(",", "").strip()
    return int(float(text))