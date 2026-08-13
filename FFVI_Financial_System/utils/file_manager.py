import csv
import json
from pathlib import Path
from typing import Any
import pandas as pd

def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"找不到文件：{path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON文件格式错误：{path}") from exc

def write_json(path: Path, data: dict[str, Any]) -> None:
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def append_user_record(path: Path, record: dict[str, Any]) -> None:
    ensure_directory(path.parent)
    row = {k: record[k] for k in record}
    if path.exists():
        df = pd.read_csv(path)
        # 兼容新增字段：统一对齐列
        for col in row:
            if col not in df.columns:
                df[col] = None
        for col in df.columns:
            if col not in row:
                row[col] = None
        row_df = pd.DataFrame([row], columns=df.columns)
        df = pd.concat([df, row_df], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(path, index=False, encoding="utf-8-sig")

def read_user_history(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)
