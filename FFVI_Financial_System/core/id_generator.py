from pathlib import Path
import pandas as pd

def generate_hhid(year: int, history_file: Path) -> str:
    year = int(year)
    if not 1900 <= year <= 2100:
        raise ValueError("年份必须在1900到2100之间。")
    if not history_file.exists():
        return f"{year}000001"
    try:
        df = pd.read_csv(history_file, dtype={"hhid": str})
    except Exception as exc:
        raise RuntimeError(f"无法读取用户历史数据：{exc}") from exc
    if "hhid" not in df.columns:
        return f"{year}000001"
    prefix = str(year)
    ids = df.loc[df["hhid"].astype(str).str.startswith(prefix), "hhid"]
    seqs = [int(str(v)[-6:]) for v in ids if str(v)[-6:].isdigit()]
    sequence = max(seqs) + 1 if seqs else 1
    if sequence > 999999:
        raise RuntimeError(f"{year}年的家庭ID已经超过6位流水号上限。")
    return f"{year}{sequence:06d}"
