from __future__ import annotations

from pathlib import Path
import pandas as pd

from app.services.scoring_service import calculate_batch_from_user_inputs
from app.services.analysis_service import build_analysis_summary, add_explanation_columns
from app.services.response_formatter import build_front_result, save_front_result_json


BASE_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = BASE_DIR / "backend"

RAW_DIR = BACKEND_DIR / "data" / "raw"
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"
OUTPUTS_DIR = BACKEND_DIR / "outputs"

RAW_DATA_PATH = RAW_DIR / "raw_data.csv"
ANALYSIS_RAW_DATA_PATH = RAW_DIR / "analysis_raw_data.csv"

RESULT_PATH = PROCESSED_DIR / "result.csv"
ANALYSIS_SUMMARY_PATH = PROCESSED_DIR / "analysis_summary.csv"
REPORT_JSON_PATH = OUTPUTS_DIR / "report_data.json"


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


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = read_csv_flexible(RAW_DATA_PATH)
    analysis_raw_df = read_csv_flexible(ANALYSIS_RAW_DATA_PATH)

    # 사용자 입력 예시 (실제 서비스에서는 프론트에서 받아올 예정)
    user_input_df = pd.DataFrame(
        [
            {
                "employment_type": "정규근로자",
                "age_group": "20대",
                "industry": "서비스업",
                "physical_level": "보통",
                "stress_level": "보통",
            },
            {
                "employment_type": "비정규근로자",
                "age_group": "40대",
                "industry": "건설업",
                "physical_level": "낮음",
                "stress_level": "높음",
            },
            {
                "employment_type": "정규근로자",
                "age_group": "60대",
                "industry": "제조업",
                "physical_level": "보통",
                "stress_level": "높음",
            },
        ]
    )

    result_df = calculate_batch_from_user_inputs(
        raw_df=raw_df,
        user_input_df=user_input_df,
    )
    
    result_df["gender"] = user_input_df["gender"].values

    result_df = add_explanation_columns(result_df)
    result_df.to_csv(RESULT_PATH, index=False, encoding="utf-8-sig")

    analysis_summary_df = build_analysis_summary(analysis_raw_df)
    analysis_summary_df.to_csv(ANALYSIS_SUMMARY_PATH, index=False, encoding="utf-8-sig")

    # 프론트용 JSON 생성: 일단 첫 번째 결과 기준
    if not result_df.empty:
        front_result = build_front_result(
            result_row=result_df.iloc[0],
            analysis_summary_df=analysis_summary_df,
        )
        save_front_result_json(front_result, REPORT_JSON_PATH)

    print(f"[완료] result 저장: {RESULT_PATH}")
    print(f"[완료] analysis summary 저장: {ANALYSIS_SUMMARY_PATH}")
    print(f"[완료] front json 저장: {REPORT_JSON_PATH}")

    


if __name__ == "__main__":
    main()


    