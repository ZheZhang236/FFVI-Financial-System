from typing import Mapping

def analyze_consumption_structure(data: Mapping[str, float]) -> dict:
    necessary = sum(float(data[k]) for k in ["food","housing","daily","transport","communication","medical"])
    optional = sum(float(data[k]) for k in ["alcohol","entertainment","travel","clothing","service","repair"])
    development = float(data["education"])
    total = necessary + optional + development
    if total <= 0:
        raise ValueError("月均总消费必须大于0。")
    n_ratio, o_ratio, d_ratio = necessary/total, optional/total, development/total
    return {
        "total": total,
        "necessary": necessary,
        "optional": optional,
        "development": development,
        "necessary_ratio": n_ratio,
        "optional_ratio": o_ratio,
        "development_ratio": d_ratio,
        "necessary_status": "必需消费基准型" if n_ratio >= 0.70 else "必需消费占比低于70%",
        "optional_status": "可选消费膨胀型" if o_ratio > 0.30 else "可选消费处于可控范围",
        "development_status": "发展消费焦虑型" if d_ratio > 0.15 else "发展消费占比适中",
        "balanced": 0.60 <= n_ratio <= 0.70 and 0.15 <= o_ratio <= 0.25 and 0.05 <= d_ratio <= 0.15,
    }
