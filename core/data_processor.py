from typing import Mapping, Any
from config.settings import MAX_LIQUID_MONTH

def calculate_month_cost(data: Mapping[str, Any]) -> float:
    keys = ["food","alcohol","housing","daily","service","transport","communication","entertainment","clothing","repair","education","travel","medical"]
    return sum(float(data[k]) for k in keys)

def calculate_liquid_assets(data: Mapping[str, Any]) -> float:
    return float(data["cash"]) + 0.7 * (float(data["stock_total"]) + float(data["fund_total"]) + float(data["bond_total"]))

def calculate_liquid_month(data: Mapping[str, Any]) -> float:
    month_cost = calculate_month_cost(data)
    if month_cost <= 0:
        raise ValueError("月均总消费必须大于0。")
    value = calculate_liquid_assets(data) / month_cost
    if value < 0 or value > MAX_LIQUID_MONTH:
        raise ValueError(f"流动月数为 {value:.2f}，超出当前模型适用范围0-{MAX_LIQUID_MONTH:.0f}个月。")
    return value

def calculate_debt_asset_ratio(data: Mapping[str, Any]) -> float:
    total_asset = calculate_liquid_assets(data) + float(data["house_asset"])
    if total_asset <= 0:
        raise ValueError("家庭总资产必须大于0，才能计算资产负债率。")
    return max(0.0, min(1.0, float(data["debt_total"]) / total_asset))

def calculate_dep_ratio(data: Mapping[str, Any]) -> float | None:
    labor = int(data["num_labor"])
    dep_total = int(data["num_child"]) + int(data["num_elder"])
    if labor == 0:
        return None
    return dep_total / labor

def calculate_insure_rate(data: Mapping[str, Any]) -> float:
    family_size = int(data["num_labor"]) + int(data["num_child"]) + int(data["num_elder"])
    if family_size <= 0:
        raise ValueError("家庭总人数必须大于0。")
    return max(0.0, min(1.0, int(data["num_medicare"]) / family_size))

def calculate_indicators(data: Mapping[str, Any]) -> dict[str, float | None]:
    return {
        "liquid_month": calculate_liquid_month(data),
        "debt_asset_ratio": calculate_debt_asset_ratio(data),
        "dep_ratio": calculate_dep_ratio(data),
        "insure_rate": calculate_insure_rate(data)}

