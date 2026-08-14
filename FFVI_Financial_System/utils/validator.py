from typing import Mapping, Any
from config.variables import INPUT_VARIABLES

NUMERIC_INPUTS = [k for k in INPUT_VARIABLES if k != "year"]

def validate_user_input(data: Mapping[str, Any]) -> None:
    missing = [k for k in INPUT_VARIABLES if k not in data or data[k] is None]
    if missing:
        names = [INPUT_VARIABLES[k]["name"] for k in missing]
        raise ValueError("以下项目不能为空：" + "、".join(names))
    try:
        year = int(data["year"])
    except (TypeError, ValueError) as exc:
        raise ValueError("年份必须是整数。") from exc
    if not 1900 <= year <= 2100:
        raise ValueError("年份必须在1900到2100之间。")
    for key in NUMERIC_INPUTS:
        try:
            value = float(data[key])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{INPUT_VARIABLES[key]['name']}必须是数字。") from exc
        if value < 0:
            raise ValueError(f"{INPUT_VARIABLES[key]['name']}不能为负数。")
    family_count = int(data["num_labor"]) + int(data["num_child"]) + int(data["num_elder"])
    if family_count <= 0:
        raise ValueError("家庭成员人数不能为0。")
    if int(data["num_medicare"]) > family_count:
        raise ValueError("医保人数不能超过家庭总人数。")
