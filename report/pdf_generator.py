from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from config.settings import PDF_REPORT_DIR

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))


def build_pdf_report(report: dict, output_path: Path | None = None) -> Path:
    if output_path is None:
        output_path = PDF_REPORT_DIR / f"家庭财务诊断_{report['hhid']}.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleCN", parent=styles["Title"], fontName="STSong-Light", fontSize=20, leading=26, alignment=TA_CENTER, spaceAfter=12)
    h1 = ParagraphStyle("H1CN", parent=styles["Heading1"], fontName="STSong-Light", fontSize=14, leading=20, spaceBefore=10, spaceAfter=7)
    body = ParagraphStyle("BodyCN", parent=styles["BodyText"], fontName="STSong-Light", fontSize=10.5, leading=17)
    small = ParagraphStyle("SmallCN", parent=body, fontSize=9)
    story = []
    story.append(Paragraph("家庭财务健康诊断报告", title))
    story.append(Spacer(1, 20))
    privacy_text = """
              本报告基于用户主动填写的信息生成。
              相关数据仅用于模型计算和未来模型优化，
              不会用于其他用途。
              """
    story.append(Paragraph(privacy_text,styles["Normal"]))
    story.append(Paragraph(f"""家庭ID：{report['hhid']}<br/>用户填写年份：{report['year']}<br/>
    参考模型年份：{report['ffvi'].get('model_year', '当前年份')}""",body))
    story.append(Paragraph("""说明：系统优先采用用户填写年份模型。若当前年份训练样本不足，系统自动调用距离最近年份模型。您的数据已保存至对应年份数据库，未来将用于模型优化。""",body))
    story.append(Paragraph(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}", small))
    story.append(Spacer(1, 8))
    story.append(Paragraph("一、核心结果", h1))
    if report["risk"]["available"]:
        result_rows = [["指标", "结果"], ["FFVI", f"{report['ffvi']['FFVI']:.2f}"], ["风险等级", report["risk"]["level"]], ["年度参考样本", str(report['risk'].get('sample_size') or '未提供')], ["结果可信度提示", report['risk'].get('confidence', '未提供')]]
    else:
        result_rows = [["项目", "结果"], ["FFVI", "当前年份尚无正式模型"], ["风险等级", "当前年份尚无正式年度分级"], ["说明", "本报告依据家庭自身财务结构、流动性和消费行为生成建议。"]]
    t = Table(result_rows, colWidths=[50*mm, 120*mm])
    t.setStyle(TableStyle([("FONTNAME", (0,0), (-1,-1), "STSong-Light"), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EAF2FF")), ("GRID", (0,0), (-1,-1), 0.4, colors.grey), ("VALIGN", (0,0), (-1,-1), "TOP"), ("FONTSIZE", (0,0), (-1,-1), 9.5), ("LEADING", (0,0), (-1,-1), 14)]))
    story.append(t)
    story.append(Paragraph("二、四维财务指标", h1))
    ind = report["indicators"]
    rows = [["指标", "结果"], ["流动性覆盖月数", f"{ind['liquid_month']:.2f}个月"], ["债务资产比", f"{ind['debt_asset_ratio']:.2%}"], ["抚养比", "无法计算" if ind['dep_ratio'] is None else f"{ind['dep_ratio']:.2f}"], ["医保覆盖率", f"{ind['insure_rate']:.2%}"]]
    t = Table(rows, colWidths=[60*mm, 110*mm])
    t.setStyle(TableStyle([("FONTNAME", (0,0), (-1,-1), "STSong-Light"), ("GRID", (0,0), (-1,-1), 0.4, colors.grey), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#F1F7F3"))]))
    story.append(t)
    story.append(Paragraph("三、流动性结构", h1))
    liq = report["liquidity"]
    for text in [f"L1（活期）覆盖：{liq['l1_months']:.2f}个月；{liq['l1_status']}。", f"L2占流动资产：{liq['l2_share']:.2%}；{liq['l2_status']}。", f"L1+L2折算后覆盖：{liq['l1_l2_months']:.2f}个月；{liq['l3_status']}。"]:
        story.append(Paragraph(text, body))
    story.append(Paragraph("四、消费结构与心理账户", h1))
    con = report["consumption"]
    story.append(Paragraph(f"必需消费占比：{con['necessary_ratio']:.2%}；可选消费占比：{con['optional_ratio']:.2%}；发展消费占比：{con['development_ratio']:.2%}。", body))
    psy = report["psychology"]
    account_rows = [["心理账户", "金额（元/月或余额）"]] + [[name, f"{v['value']:.2f}"] for name, v in psy.items()]
    t = Table(account_rows, colWidths=[80*mm, 90*mm])
    t.setStyle(TableStyle([("FONTNAME", (0,0), (-1,-1), "STSong-Light"), ("GRID", (0,0), (-1,-1), 0.4, colors.grey), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#FFF7E8"))]))
    story.append(t)
    story.append(Paragraph("五、个性化建议", h1))
    for i, rec in enumerate(report["recommendation"]["priority_actions"], 1):
        story.append(Paragraph(f"{i}. {rec}", body))
    story.append(Paragraph("六、详细建议", h1))
    for rec in report["recommendation"]["all_asset_recommendations"]:
        story.append(Paragraph("资产端：" + rec, body))
    for rec in report["recommendation"]["all_consumption_recommendations"]:
        story.append(Paragraph("消费端：" + rec, body))
    story.append(PageBreak())
    story.append(Paragraph("七、心理账户管理建议", h1))
    for name, item in psy.items():
        story.append(Paragraph(f"{name}：{item['description']}", body))
    story.append(Paragraph("八、说明", h1))
    story.append(Paragraph("本系统以用户输入的家庭财务结构和对应年份模型为基础。若输入年份尚未建立年度模型，系统不会用其他年份模型替代正式年度模型；此时仅进行指标、流动性、消费结构和心理账户分析，并提示等待该年份模型更新。", body))
    doc.build(story)
    return output_path
