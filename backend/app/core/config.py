from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BACKEND_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = BACKEND_DIR / "outputs"

RAW_DATA_PATH = RAW_DATA_DIR / "raw_data.csv"
ANALYSIS_RAW_DATA_PATH = RAW_DATA_DIR / "analysis_raw_data.csv"

RESULT_PATH = PROCESSED_DATA_DIR / "result.csv"
ANALYSIS_SUMMARY_PATH = PROCESSED_DATA_DIR / "analysis_summary.csv"
REPORT_JSON_PATH = OUTPUTS_DIR / "report_data.json"