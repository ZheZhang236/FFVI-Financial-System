from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
USER_DATA_DIR = DATA_DIR / "user_data"
YEARLY_MODEL_DIR = DATA_DIR / "yearly_model"
REPORT_DIR = DATA_DIR / "reports"
PDF_REPORT_DIR = REPORT_DIR / "pdf"
USER_HISTORY_FILE = USER_DATA_DIR / "user_history.csv"
FACTOR_FILE = "factor.json"
SCALER_FILE = "scaler.json"
THRESHOLD_FILE = "threshold.json"
METADATA_FILE = "metadata.json"
MAX_LIQUID_MONTH = 120.0
MODEL_UPDATE_RECOMMENDED_N = 300
for directory in [USER_DATA_DIR, YEARLY_MODEL_DIR, REPORT_DIR, PDF_REPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
