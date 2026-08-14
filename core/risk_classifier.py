from pathlib import Path
from utils.file_manager import read_json
from config.settings import YEARLY_MODEL_DIR, THRESHOLD_FILE, METADATA_FILE
from core.ffvi_model import find_nearest_model_year

def assess_risk(year: int, ffvi: float) -> dict:
    model_year = find_nearest_model_year(int(year))
    model_dir = YEARLY_MODEL_DIR / str(model_year)
    if not model_dir.exists():
        return {"available": False, "input_year": int(year), "model_year":model_year,"level": None, "code": None, "description": "当前年份尚未建立模型，无法进行严格的同年度风险分级。"}
    threshold = read_json(model_dir / THRESHOLD_FILE)
    p30, p70 = float(threshold["p30"]), float(threshold["p70"])
    # 严格按照最新Stata：最低30%=绿色，中间40%=黄色，最高30%=红色。
    if ffvi <= p30:
        code, level, desc = 1, "绿色-财务健康", "当前FFVI处于该年度样本的较低区间。"
    elif ffvi <= p70:
        code, level, desc = 2, "黄色-轻度风险", "当前FFVI处于该年度样本的中间区间。"
    else:
        code, level, desc = 3, "红色-高脆弱风险", "当前FFVI处于该年度样本的较高区间。"
    sample_size = None
    metadata_path = model_dir / METADATA_FILE
    if metadata_path.exists():
        metadata = read_json(metadata_path)
        sample_size = metadata.get("sample_size")
    if sample_size is None:
        confidence = "未提供样本量"
    elif int(sample_size) >= 1000:
        confidence = "高"
    elif int(sample_size) >= 300:
        confidence = "中等"
    else:
        confidence = "较低"
    return {"available": True, "year": int(year), "level": level, "code": code, "description": desc, "p30": p30, "p70": p70, "sample_size": sample_size, "confidence": confidence}
