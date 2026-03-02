# AI 奖金分析系统 (Pro)

这是一个基于 Python + Streamlit 的“奖金分配沙盘”应用，用一天时间做出的可交付 MVP，支持数据导入/编辑、奖金分配模拟、风控预警与 AI 报告。

## ✅ 已实现能力

- 数据输入：模拟数据生成、CSV/Excel 上传、在线编辑
- 奖金分配：按 (薪资 × 绩效系数) 加权分配，实时重算
- 可视化：部门奖金分布、绩效分布（人数/金额）、薪资-奖金散点
- 风控规则：
  - 强制分布预警（S 上限、S+A 上限）
  - 部门预算控制（按人头默认分配，可逐部门调整，超支预警）
- AI 报告：
  - 未填 Key：内置规则报告
  - 填入 OpenAI Key：基于脱敏统计摘要生成更专业的报告（模型可通过 `OPENAI_MODEL` 配置）

## 🚀 本地运行

```bash
pip install -r requirements.txt
streamlit run main.py
```

默认访问：`http://localhost:8501`（如果端口占用，Streamlit 会自动改用 8502/8503…）。

## 🐳 Docker 部署

```bash
docker compose up -d --build
```

默认访问：`http://<服务器IP>:8501`。

## 📂 关键代码位置

- 主入口：main.py
- 奖金与风控：src/calculator.py
- AI 报告：src/ai_analysis.py
- 可视化：src/visualizer.py
