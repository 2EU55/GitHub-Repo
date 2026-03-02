# AI 奖金分析系统 (Pro)

一个可直接演示的 Streamlit 应用，覆盖“奖金核算构建流 + 奖金分配沙盘”两条路径：

- 销售奖金核算（DataLens 风格）：导入/映射 → 目标/规则 → 中间表 → 结论表 → AI 解读
- 奖金分配沙盘：上传/生成员工数据 → 权重分配 → 风控预警 → 可视化 → AI 报告 → 方案保存

> 说明：本仓库仅维护代码与示例数据；你的公网演示链接已部署完成，无需在仓库中配置密钥。

## ✅ 功能概览

### 1) 销售奖金核算（构建/解读模式）
- 构建模式（7 步）：导入底表/字段映射/结构识别/定义目标/导入规则/生成构建计划/执行构建
- 数据资产面板：底表/中间表/结论表 + 行数展示
- 解读模式：结果表分页/字段说明面板/AI 数据解读报告

### 2) 奖金分配沙盘
- 数据输入：模拟数据生成、CSV/Excel 上传、在线编辑
- 分配逻辑：按 (薪资 × 绩效系数) 加权分配，实时重算
- 可视化：部门奖金分布、绩效分布（人数/金额）、薪资-奖金散点
- 风控规则：强制分布预警（S 上限、S+A 上限）、部门预算超支预警
- AI 报告：未填 Key 时基础规则报告；填 Key 时基于脱敏统计摘要生成更专业报告

## 🚀 快速开始（本地）

```bash
pip install -r requirements.txt
streamlit run main.py
```

默认访问：`http://localhost:8501`（端口占用时 Streamlit 会自动改用 8502/8503…）。

## 🧪 演示数据（推荐给 HR 演示）

示例文件都在 `examples/`：
- `examples/sales_sample.csv`：销售明细样例
- `examples/analysis_goal.md`：分析目标样例
- `examples/rules.md`：规则文档样例

建议演示流程：
1. 构建模式 → 步骤 1 上传 `examples/sales_sample.csv`（或直接生成示例底表）
2. 步骤 3 粘贴 `examples/analysis_goal.md`
3. 步骤 4 粘贴 `examples/rules.md`
4. 执行构建 → 切到解读模式 → 生成解读

## 🔑 LLM 配置（可选）

应用默认支持两种提供方：硅基流动 / OpenAI。

- 最简单：在页面右侧“模型配置”里选择提供方、模型，并填入 API Key
- 高级：通过环境变量控制 base_url、超时与重试（参考 `.env.example`）

目前支持的环境变量：
- `SILICONFLOW_BASE_URL`：硅基流动 OpenAI 兼容地址（默认 `https://api.siliconflow.cn/v1`）
- `OPENAI_BASE_URL`：OpenAI 兼容地址（可选）
- `LLM_TIMEOUT_SECONDS`：请求超时秒数（默认 30）
- `LLM_MAX_RETRIES`：失败重试次数（默认 1）

## 🐳 Docker（可选）

```bash
docker compose up -d --build
```

默认访问：`http://<服务器IP>:8501`。

## 🔒 数据与隐私

- 应用包含“方案保存”能力，会将数据写入本地 `analyst.db`（SQLite）。
- 演示环境建议使用示例数据或脱敏数据，避免将真实员工/薪资明细落盘。
- `analyst.db` 已被加入 `.gitignore`，不会提交到仓库。

## 📁 代码结构

- `main.py`：Streamlit 入口与页面路由/状态管理
- `src/sales_schema.py`：销售底表字段标准化与校验
- `src/sales_bonus.py`：销售奖金构建逻辑（中间表/结论表）
- `src/sales_ai.py`：销售结果 AI 解读
- `src/data_handler.py`：通用沙盘数据导入/示例生成
- `src/calculator.py`：通用沙盘奖金计算与风控
- `src/ai_analysis.py`：通用沙盘 AI 分析报告
- `src/visualizer.py`：图表可视化
- `src/storage.py`：方案保存/加载（SQLite）
- `src/llm_client.py`：统一 LLM 调用（OpenAI SDK，支持硅基流动）

## 📄 License

MIT License，详见 [LICENSE](LICENSE)。
