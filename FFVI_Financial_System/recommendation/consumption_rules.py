
def consumption_recommendations(consumption: dict, liquidity: dict, risk_level: str | None) -> list[str]:
    recs = []
    n, o, d = consumption["necessary_ratio"], consumption["optional_ratio"], consumption["development_ratio"]
    if o > 0.30:
        if risk_level == "红色-高脆弱风险":
            recs.append("您的可选消费占比较高，建议优先压缩酒水、娱乐、旅游、衣物、家政和修缮等弹性支出，将释放的资金用于补足应急储备。")
        else:
            recs.append("您的可选消费占比超过30%，建议设置月度预算上限，逐步将可选消费控制在更可持续的水平。")
    elif 0.15 <= o <= 0.25:
        recs.append("您的可选消费比例处于建议区间，可继续保持预算纪律。")
    if d > 0.15:
        recs.append("教育培训支出占比较高，建议将其作为独立的人力资本投资账户管理，并结合家庭流动性水平设置预算上限。")
    if n >= 0.70:
        recs.append("您的必需消费占比较高，当前重点不是简单压缩生活必需支出，而是优化食品、通信和医疗等项目的使用效率。")
    if consumption["balanced"]:
        recs.append("您的必需、可选和发展消费结构较为均衡，建议继续维持，并将后续优化重点放在资产端。")
    if liquidity["l1_months"] < 3 and o > 0.20:
        recs.append("当前活期储备不足3个月，同时可选消费偏高，建议优先调整可选消费与储蓄顺序。")
    return recs
