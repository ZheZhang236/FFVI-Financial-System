from recommendation.risk_rules import RISK_RULES
from recommendation.consumption_rules import consumption_recommendations
from recommendation.asset_rules import asset_recommendations

def generate_recommendations(risk: dict, liquidity: dict, consumption: dict, psychology: dict, indicators: dict) -> dict:
    level = risk.get("level")
    core = RISK_RULES.get(level, {"summary": "当前年份尚未形成正式风险等级，本次建议基于家庭自身财务结构和消费行为生成。", "actions": []})
    priority = []
    priority.extend(core["actions"][:2])
    priority.extend(asset_recommendations(liquidity, level, consumption)[:2])
    priority.extend(consumption_recommendations(consumption, liquidity, level)[:2])
    # 去重并限制网页核心建议数量
    unique = []
    for item in priority:
        if item not in unique:
            unique.append(item)
    # 心理账户提醒
    if liquidity["l1_months"] < 3:
        psychology_note = "建议将活期余额视为‘应急账户’，与日常消费账户分开管理；收入到账后优先储蓄再消费。"
    elif consumption["optional_ratio"] > 0.30:
        psychology_note = "您的享乐/形象账户可能正在挤占安全账户，建议建立清晰预算边界，让消费账户与应急账户彼此隔离。"
    else:
        psychology_note = "建议继续保持专款专用，让应急、健康、教育、安居和日常消费账户承担明确职责。"
    return {
        "summary": core["summary"],
        "priority_actions": unique[:5],
        "psychology_note": psychology_note,
        "all_asset_recommendations": asset_recommendations(liquidity, level, consumption),
        "all_consumption_recommendations": consumption_recommendations(consumption, liquidity, level),
        "accounts": psychology,
    }
