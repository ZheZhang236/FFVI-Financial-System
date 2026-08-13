def asset_recommendations(liquidity: dict, risk_level: str | None, consumption: dict) -> list[str]:
    recs = []
    l1 = liquidity["l1_months"]
    l2_share = liquidity["l2_share"]
    l1_l2 = liquidity["l1_l2_months"]
    if l1 < 3:
        recs.append("活期资金目前不足以覆盖3个月刚性支出，建议优先建立独立应急账户，并将储蓄前置。")
    elif l1 < 6:
        recs.append("活期资金可以覆盖3个月以上但尚未达到6个月，建议逐步补足安全垫。")
    elif l1 > 12:
        recs.append("活期资金超过12个月支出，可评估是否存在安全账户过厚的问题；在不影响应急安全的前提下，再考虑长期增值配置。")
    if l2_share > 0.70 and l1 < 3:
        recs.append("股票、基金和债券占流动资产比例较高，但L1又不足3个月，建议优先恢复L1安全底线，避免流动性错配。")
    if l1_l2 < 6 and liquidity["l3_share"] > 0.70:
        recs.append("房产等低流动性资产占比较高，而L1+L2覆盖不足6个月，建议提前制定必要时的资产变现预案。")
    if l1 >= 6 and l2_share <= 0.70 and liquidity["l3_share"] <= 0.70:
        recs.append("当前L1、L2与房产资产的流动性结构相对均衡，建议保持分账户管理。")
    return recs
