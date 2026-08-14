from pathlib import Path
from typing import Mapping, Any
from config.settings import YEARLY_MODEL_DIR, FACTOR_FILE, SCALER_FILE, METADATA_FILE
from utils.file_manager import read_json
from core.data_processor import calculate_indicators

class FFVIModel:
    def __init__(self, year: int):
        self.year = int(year)
        self.model_dir = YEARLY_MODEL_DIR / str(self.year)
        if not self.model_dir.exists():
            raise FileNotFoundError(f"当前年份 {self.year} 尚未建立FFVI模型。")
        self.factor = read_json(self.model_dir / FACTOR_FILE)
        self.scaler = read_json(self.model_dir / SCALER_FILE)
        self.metadata = read_json(self.model_dir / METADATA_FILE)

    def calculate(self, data: Mapping[str, Any]) -> dict[str, Any]:
        indicators = calculate_indicators(data)
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
        return {"year": self.year, "indicators": indicators, "factor_inputs": factor_inputs, "factor1": factor1, "factor2": factor2, "FFVI_raw": ffvi_raw, "FFVI": round(max(0,min(100,ffvi)),2)}
