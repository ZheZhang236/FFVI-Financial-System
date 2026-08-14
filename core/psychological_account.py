from typing import Mapping

def analyze_psychological_accounts(data: Mapping[str, float]) -> dict:
    return {
        "应急账户": {"value": float(data["cash"]), "description": "对应活期余额，非生死关头不动用。"},
        "健康保障账户": {"value": float(data["medical"]), "description": "医疗支出与保障投入应统筹管理。"},
        "子女教育账户": {"value": float(data["education"]), "description": "教育培训支出，建议专款专用。"},
        "安居账户": {"value": float(data["housing"]) + float(data["repair"]), "description": "水电物业与住房修缮统一管理。"},
        "日常消费账户": {"value": sum(float(data[k]) for k in ["food","daily","transport","communication"]), "description": "维持日常生活的必要消费。"},
        "享乐账户": {"value": sum(float(data[k]) for k in ["alcohol","entertainment","travel"]), "description": "酒水、娱乐、旅游等即时满足型支出。"},
        "形象账户": {"value": float(data["clothing"]) + float(data["service"]), "description": "衣物与家政等形象/生活品质支出。"},
    }
