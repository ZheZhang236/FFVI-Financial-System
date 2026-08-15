import json
from pathlib import Path
from typing import Mapping, Any
from config.settings import YEARLY_MODEL_DIR, FACTOR_FILE, SCALER_FILE, METADATA_FILE
from utils.file_manager import read_json
from core.data_processor import calculate_indicators
from config.settings import (YEARLY_MODEL_DIR,MIN_MODEL_SAMPLE_SIZE)

def find_nearest_model_year(target_year):
    years = []
    for folder in YEARLY_MODEL_DIR.iterdir():
        if folder.is_dir() and folder.name.isdigit():
            years.append(int(folder.name))
    if len(years)==0:
        raise FileNotFoundError("没有可用FFVI模型")
    if target_year in years:
        if check_model_valid(target_year):
            return target_year
    return min(years,key=lambda x:abs(x-target_year))

def get_model_sample_size(year):
    metadata_path = (YEARLY_MODEL_DIR / str(year) / "metadata.json")
    if not metadata_path.exists():
        return 0
    with open(metadata_path,"r",encoding="utf-8") as f:
        metadata=json.load(f)
    return metadata.get("sample_size",0)

def check_model_valid(year):
    metadata_file = ( YEARLY_MODEL_DIR /str(year) /"metadata.json")
    if not metadata_file.exists():
        return False
    metadata = read_json(metadata_file)
    sample_size = metadata.get("sample_size",0)


    # 最低样本量标准
    if sample_size < 300:
        return False


    return True

class FFVIModel:
    def __init__(self, year: int):
        self.input_year = int(year)
        candidate_year = self.input_year
        model_exists = (YEARLY_MODEL_DIR / str(candidate_year)).exists()
        if model_exists:
            sample_size = get_model_sample_size(candidate_year)
            if sample_size >= MIN_MODEL_SAMPLE_SIZE:
                self.model_year = candidate_year
            else:
                self.model_year = (find_nearest_model_year(candidate_year))
        # 如果不存在，直接寻找最近年份
        else:
            self.model_year = (find_nearest_model_year(candidate_year))
        self.model_dir = (YEARLY_MODEL_DIR  / str(self.model_year))
        self.factor = read_json(self.model_dir / FACTOR_FILE)
        self.scaler = read_json(self.model_dir / SCALER_FILE)
        self.metadata = read_json(self.model_dir / METADATA_FILE)
        self.sample_size = self.metadata.get("sample_size",0)

    def calculate(self, data: Mapping[str, Any]) -> dict[str, Any]:
        indicators = calculate_indicators(data)

        if indicators is None:
            raise ValueError("calculate_indicators没有返回指标，请检查core/data_processor.py")
        standardized = {}
        for var in ["liquid_month","debt_asset_ratio","dep_ratio","insure_rate"]:
            value = indicators[var]
            param = self.scaler[var]
            if value is None:
                if var == "dep_ratio":
                    value = float(param["mean"])
                else:
                    raise ValueError(f"{var}无法计算。")
            sd = float(param["std"])
            if sd <= 0:
                raise ValueError(f"{var}的标准差必须大于0。")
            standardized[var] = (float(value) - float(param["mean"])) / sd
        factor_inputs = {
            "risk_liquid": -standardized["liquid_month"],
            "std_debt_asset_ratio": standardized["debt_asset_ratio"],
            "std_dep_ratio": standardized["dep_ratio"],
            "risk_insure": -standardized["insure_rate"],
        }
        variables = self.factor.get("variables", list(factor_inputs.keys()))
        x = [factor_inputs[v] for v in variables]
        f1 = self.factor["factor1_score_coefficients"]
        f2 = self.factor["factor2_score_coefficients"]
        if len(x) != len(f1) or len(x) != len(f2):
            raise ValueError("因子得分系数数量与变量数量不一致。")
        factor1 = sum(a*b for a,b in zip(x, f1))
        factor2 = sum(a*b for a,b in zip(x, f2))
        w1 = float(self.factor["weight_factor1"])
        w2 = float(self.factor["weight_factor2"])
        weight_sum = w1 + w2
        if weight_sum <= 0:
            raise ValueError("两个因子权重之和必须大于0。")
        w1, w2 = w1/weight_sum, w2/weight_sum
        ffvi_raw = w1 * factor1 + w2 * factor2
        raw_min = float(self.metadata["ffvi_raw_min"])
        raw_max = float(self.metadata["ffvi_raw_max"])
        if raw_max <= raw_min:
            raise ValueError("FFVI原始分数范围无效。")
        ffvi = (ffvi_raw - raw_min) / (raw_max - raw_min) * 100
        indicators.update(factor_inputs)
        return {"input_year": self.input_year, "model_year":self.model_year,"indicators": indicators, "factor_inputs": factor_inputs, "factor1": factor1, "factor2": factor2, "FFVI_raw": ffvi_raw, "FFVI": round(max(0,min(100,ffvi)),2)}
