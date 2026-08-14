import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

from config.settings import USER_HISTORY_FILE
from config.variables import INPUT_VARIABLES
from core.id_generator import generate_hhid
from core.data_processor import calculate_indicators
from core.liquidity_analysis import analyze_liquidity
from core.structure_analysis import analyze_consumption_structure
from core.psychological_account import analyze_psychological_accounts
from core.ffvi_model import FFVIModel
from core.risk_classifier import assess_risk
from recommendation.recommendation_engine import generate_recommendations
from utils.file_manager import append_user_record, read_user_history, get_year_user_file
from utils.validator import validate_user_input
from report.pdf_generator import build_pdf_report

def check_demo_password():
    """演示版访问密码验证"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # 已经验证过
    if st.session_state.authenticated:
        return True

    st.set_page_config(
        page_title="家庭财务健康诊断系统",
        page_icon="🏠",
        layout="wide")

    st.title("🏠 家庭财务健康诊断系统")
    st.info(
        """
        感谢您的信任与参与。
    
        您填写的信息仅用于本次家庭财务健康分析，
        不会用于商业用途，也不会向第三方提供。
    
        为持续优化家庭财务健康评估模型，
        系统会保存您填写的数据至用户数据数据库，
        用于未来模型更新和模型准确性提升。
    
        您的信息仅用于模型研究与计算分析。
        """
    )
    st.subheader("系统访问验证")

    st.write("请输入访问密码后进入系统。")

    password = st.text_input(
        type="password")

    if st.button("进入系统",use_container_width=True):

        correct_password = st.secrets.get("DEMO_PASSWORD","")

        if not correct_password:
            st.error("系统尚未配置演示密码，请联系管理员。")
            st.stop()

        if password == correct_password:

            st.session_state.authenticated = True
            st.rerun()

        else:

            st.error("密码错误，请重新输入。")

    return False


if not check_demo_password():
    st.stop()


# =========================================================
# 从这里开始，才是你原来的 FFVI 软件主体
# =========================================================

st.set_page_config(page_title="家庭财务健康诊断系统", page_icon="🏠", layout="wide")

st.markdown("""
<style>
.main {background: #F6F8FC;}
.block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1200px;}
.hero {padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(135deg,#102A43,#2B6CB0); color: white; margin-bottom: 1.2rem;}
.hero h1 {font-size: 2rem; margin-bottom: .3rem;}
.hero p {opacity: .9; margin: 0;}
.card {padding: 1rem 1.1rem; border-radius: 14px; background: white; border: 1px solid #E6EAF0; box-shadow: 0 4px 16px rgba(27,42,65,.05);}
.metric-title {font-size: .85rem; color: #6B7280; margin-bottom: .2rem;}
.metric-value {font-size: 1.7rem; font-weight: 700; color: #102A43;}
.small-note {font-size: .85rem; color: #667085;}
</style>
""", unsafe_allow_html=True)


def input_money(label: str, help_text: str = ""):
    return st.number_input(label, min_value=0.0, value=None, step=100.0, format="%.2f", help=help_text)


def input_people(label: str):
    return st.number_input(label, min_value=0, value=None, step=1, format="%d")


st.markdown("""
<div class="hero">
    <h1>🏠 家庭财务健康诊断系统</h1>
    <p>基于年度FFVI模型、流动性结构与消费心理账户的家庭财务健康分析</p>
</div>
""", unsafe_allow_html=True)

st.info("""
系统优先使用用户填写年份对应模型。
若该年份尚未形成稳定模型，
系统将自动调用距离最近年份模型进行分析。
""")

# Family ID / year are tied together.
year = st.number_input("填写年份", min_value=1900, max_value=2200, value=None, step=1, format="%d")
if year is not None:
    hhid = generate_hhid(int(year), USER_HISTORY_FILE)
else:
    hhid = "提交后自动生成"
st.markdown(f"**家庭ID：** `{hhid}` 　<span class='small-note'>系统自动生成，用户不可修改</span>", unsafe_allow_html=True)

st.divider()

with st.expander("💰 月均消费信息", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        food = input_money("月均伙食费（元）")
        alcohol = input_money("月均酒水花费（元）")
        housing = input_money("月均水/电/燃料/物管费用（元）")
        daily = input_money("月均日用品花费（元）")
        service = input_money("月均家政服务费（元）")
    with c2:
        transport = input_money("月均本地交通费（元）")
        communication = input_money("月均通信网络费（元）")
        entertainment = input_money("月均文化娱乐费（元）")
        clothing = input_money("月均衣物支出（元）")
    with c3:
        repair = input_money("住房修缮花费（元）")
        education = input_money("教育培训费用（元）")
        travel = input_money("旅游花费（元）")
        medical = input_money("医疗费用（元）")

with st.expander("🏦 家庭资产负债信息", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        cash = input_money("活期账户余额（元）")
        stock_total = input_money("股票资产（元）")
    with c2:
        fund_total = input_money("基金资产（元）")
        bond_total = input_money("债券资产（元）")
    with c3:
        debt_total = input_money("负债总额（元）")
        house_asset = input_money("房产资产（元）")

with st.expander("👨‍👩‍👧‍👦 家庭结构信息", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        num_labor = input_people("家庭劳动力人数")
    with c2:
        num_child = input_people("儿童人数")
    with c3:
        num_elder = input_people("老人数量")
    with c4:
        num_medicare = input_people("医保人数")

st.divider()

submit = st.button("🚀 开始家庭财务诊断", type="primary", use_container_width=True)

if submit:
    data = {
        "year": year,
        "food": food,
        "alcohol": alcohol,
        "housing": housing,
        "daily": daily,
        "service": service,
        "transport": transport,
        "communication": communication,
        "entertainment": entertainment,
        "clothing": clothing,
        "repair": repair,
        "education": education,
        "travel": travel,
        "medical": medical,
        "cash": cash,
        "stock_total": stock_total,
        "fund_total": fund_total,
        "bond_total": bond_total,
        "debt_total": debt_total,
        "house_asset": house_asset,
        "num_labor": num_labor,
        "num_child": num_child,
        "num_elder": num_elder,
        "num_medicare": num_medicare,
    }

    try:
        validate_user_input(data)
        data["hhid"] = generate_hhid(int(year), USER_HISTORY_FILE)

        indicators = calculate_indicators(data)
        data_for_analysis = {**data, **indicators}
        liquidity = analyze_liquidity(data_for_analysis)
        consumption = analyze_consumption_structure(data_for_analysis)
        psychology = analyze_psychological_accounts(data_for_analysis)

        # Strict annual separation: no cross-year model borrowing.
        model_dir = Path(__file__).resolve().parent / "data" / "yearly_model" / str(int(year))
        ffvi_result = None
        if model_dir.exists():
            model = FFVIModel(int(year))
            ffvi_result = model.calculate(data_for_analysis)

        if ffvi_result is not None:
            risk = assess_risk(int(year), ffvi_result["FFVI"])
        else:
            risk = assess_risk(int(year), 0.0)

        recommendation = generate_recommendations(risk, liquidity, consumption, psychology, indicators)

        record = dict(data)
        record.update(indicators)
        if ffvi_result is not None:
            record.update({"FFVI_raw": ffvi_result["FFVI_raw"], "FFVI": ffvi_result["FFVI"]})
        else:
            record.update({"FFVI_raw": None, "FFVI": None})
        record["risk_level"] = risk.get("level")
        if ffvi_result is not None:
            record["model_year_used"] = ffvi_result["model_year"]
            record["is_reference_model"] = (int(year) != int(ffvi_result["model_year"]))
        else:
            record["model_year_used"] = None
            record["is_reference_model"] = None
        record["created_at"] = datetime.now().isoformat(timespec="seconds")
        user_file = get_year_user_file(year)
        append_user_record(user_file,record)

        report = {
            "hhid": data["hhid"],
            "year": int(year),
            "ffvi": ffvi_result,
            "risk": risk,
            "indicators": indicators,
            "liquidity": liquidity,
            "consumption": consumption,
            "psychology": psychology,
            "recommendation": recommendation,
        }

        st.session_state["latest_report"] = report
        st.success("本次数据已保存。")

    except Exception as exc:
        st.error(f"无法完成诊断：{exc}")


if "latest_report" in st.session_state:
    report = st.session_state["latest_report"]
    st.divider()
    st.header("📊 诊断结果")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><div class="metric-title">家庭ID</div><div class="metric-value">{}</div></div>'.format(report["hhid"]), unsafe_allow_html=True)
    with c2:
        if report["ffvi"]:
            st.markdown('<div class="card"><div class="metric-title">家庭财务健康指数 FFVI</div><div class="metric-value">{:.2f}</div></div>'.format(report["ffvi"]["FFVI"]), unsafe_allow_html=True)
        else:
            st.markdown('<div class="card"><div class="metric-title">家庭财务健康指数 FFVI</div><div class="metric-value">暂不可用</div></div>', unsafe_allow_html=True)
    with c3:
        level = report["risk"].get("level") or "暂无年度风险等级"
        st.markdown('<div class="card"><div class="metric-title">风险等级</div><div class="metric-value" style="font-size:1.2rem">{}</div></div>'.format(level), unsafe_allow_html=True)

    if not report["ffvi"]:
        st.warning("当前年份尚无独立训练模型。为避免跨年份混用，系统没有借用其他年份模型计算正式FFVI和风险等级；下面仍提供基于本家庭实际数据的财务结构、消费结构和心理账户建议。")
    else:
        risk = report["risk"]
        st.info(f"年度参考样本：{risk.get('sample_size', '未提供')}；结果可信度提示：{risk.get('confidence', '未提供')}。该可信度提示不改变Stata风险等级，只用于帮助用户理解结果稳定程度。")

    if report["ffvi"]:
        gauge = go.Figure(go.Indicator(mode="gauge+number", value=report["ffvi"]["FFVI"], title={"text": "FFVI"}, gauge={"axis": {"range": [0, 100]}}))
        gauge.update_layout(height=280, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(gauge, use_container_width=True)

    st.subheader("🔎 核心分析")
    a = report["indicators"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("流动性覆盖月数", f"{a['liquid_month']:.2f}个月")
    c2.metric("债务资产比", f"{a['debt_asset_ratio']:.2%}")
    c3.metric("抚养比", "无法计算" if a["dep_ratio"] is None else f"{a['dep_ratio']:.2f}")
    c4.metric("医保覆盖率", f"{a['insure_rate']:.2%}")

    st.subheader("💡 核心建议")
    st.write(report["recommendation"]["summary"])
    for i, rec in enumerate(report["recommendation"]["priority_actions"], 1):
        st.markdown(f"**{i}.** {rec}")

    st.subheader("🧠 消费与心理账户")
    con = report["consumption"]
    c1, c2, c3 = st.columns(3)
    c1.metric("必需消费", f"{con['necessary_ratio']:.1%}")
    c2.metric("可选消费", f"{con['optional_ratio']:.1%}")
    c3.metric("发展消费", f"{con['development_ratio']:.1%}")
    st.caption(report["recommendation"]["psychology_note"])

    st.subheader("🏦 流动性结构")
    liq = report["liquidity"]
    st.write(f"L1覆盖：{liq['l1_months']:.2f}个月；{liq['l1_status']}。")
    st.write(f"L2占流动资产：{liq['l2_share']:.1%}；{liq['l2_status']}。")
    st.write(f"L1+L2折算覆盖：{liq['l1_l2_months']:.2f}个月；{liq['l3_status']}。")

    st.subheader("📄 生成详细PDF报告")
    if st.button("生成PDF报告"):
        pdf_path = build_pdf_report(report)
        with open(pdf_path, "rb") as f:
            st.download_button("下载详细PDF报告", f, file_name=pdf_path.name, mime="application/pdf")

    # 历史趋势，仅展示同一家庭ID的记录
    history = read_user_history(USER_HISTORY_FILE)
    if not history.empty and "hhid" in history.columns:
        same = history[history["hhid"].astype(str) == str(report["hhid"])].copy()
        if len(same) >= 2 and "FFVI" in same.columns:
            same = same.dropna(subset=["FFVI"]).sort_values("year")
            if not same.empty:
                st.subheader("📈 家庭历史FFVI记录")
                st.line_chart(same.set_index("year")["FFVI"])
