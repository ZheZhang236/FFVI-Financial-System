# FFVI_Financial_System

基于年度Stata FFVI模型的家庭财务健康诊断系统。

## 运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 年度模型文件

每个正式年份模型单独保存，不跨年份混用：

```
data/yearly_model/2017/
  factor.json
  scaler.json
  threshold.json
  metadata.json
```

### scaler.json
保存当年四个指标用于 `egen std_变量 = std(变量)` 的均值和标准差：

```json
{
  "liquid_month": {"mean": 8.23, "std": 5.12},
  "debt_asset_ratio": {"mean": 0.31, "std": 0.21},
  "dep_ratio": {"mean": 0.56, "std": 0.30},
  "insure_rate": {"mean": 0.84, "std": 0.19}
}
```

### factor.json
必须提供 `predict factor1 factor2` 实际使用的 scoring coefficients，而不是仅提供 rotated factor loadings：

```json
{
  "variables": ["risk_liquid", "std_debt_asset_ratio", "std_dep_ratio", "risk_insure"],
  "factor1_score_coefficients": [0.12, 0.23, 0.34, 0.45],
  "factor2_score_coefficients": [-0.12, 0.22, 0.32, -0.42],
  "weight_factor1": 0.53,
  "weight_factor2": 0.47
}
```

其中 `weight_factor1/2` 使用你Stata代码中基于两个因子方差贡献率得到的年度权重。

### threshold.json

```json
{"p30": 35.82, "p70": 68.47}
```

系统严格按当前最终Stata：最低30%=绿色，中间40%=黄色，最高30%=红色。

### metadata.json

```json
{
  "year": 2017,
  "sample_size": 5236,
  "factor_method": "pcf",
  "factor_number": 2,
  "rotation": "varimax",
  "ffvi_raw_min": -2.3815,
  "ffvi_raw_max": 2.7452,
  "model_version": "1.0"
}
```

## 新年份行为

如果用户输入的年份尚未建立模型：

- 数据仍然自动保存到 `data/user_data/user_history.csv`；
- 系统仍然计算流动月数、债务资产比、抚养比、医保覆盖率；
- 系统仍然生成流动性、消费结构和心理账户建议；
- 不借用其他年份模型计算正式FFVI或风险等级；
- 未来样本积累后，可为该年份生成独立模型目录，再正常启用FFVI与风险等级。
