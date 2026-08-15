from typing import Mapping

def analyze_liquidity(data: Mapping[str, float]) -> dict:
    cash = float(data["cash"])
    l2_asset = float(data["stock_total"]) + float(data["fund_total"]) + float(data["bond_total"])
    house_asset = float(data["house_asset"])
    month_cost = float(data["month_cost"])
    cash = data.get("cash", 0)
    stock_fund_bond = ( data.get("stock_total", 0) + data.get("fund_total", 0) + data.get("bond_total", 0))
    real_liquid_total = cash + stock_fund_bond * 0.7
    l1_months = cash / month_cost if month_cost > 0 else 0.0
    l2_share = l2_asset / real_liquid_total if real_liquid_total > 0 else 0.0
    l1_l2_asset = cash + 0.7 * l2_asset
    l1_l2_months = l1_l2_asset / month_cost if month_cost > 0 else 0.0
    total_asset = real_liquid_total + house_asset
    l3_share = house_asset / total_asset if total_asset > 0 else 0.0
    if l1_months < 3:
        l1_status = "L1资产严重短缺型"
    elif l1_months < 6:
        l1_status = "L1储备一般"
    elif l1_months <= 12:
        l1_status = "L1储备充足"
    else:
        l1_status = "L1可能存在闲置"
    l2_status = "L2资产过度集中型" if l2_share > 0.70 and l1_months < 3 else "L2配置未触发集中风险"
    l3_status = "L3资产固化风险需要关注" if l1_l2_months < 6 else "L3流动性风险较低"
    return {"l1_asset": cash, "l2_asset": l2_asset, "l3_asset": house_asset, "l1_months": l1_months, "l1_l2_months": l1_l2_months, "l2_share": l2_share, "l3_share": l3_share, "l1_status": l1_status, "l2_status": l2_status, "l3_status": l3_status}
