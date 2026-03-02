import streamlit as st
import pandas as pd
from src.data_handler import generate_sample_data, load_data
from src.calculator import calculate_bonus, check_forced_distribution, check_department_budget
from src.visualizer import plot_department_distribution, plot_performance_distribution, plot_salary_vs_bonus
from src.ai_analysis import generate_analysis_report
from src.schema import REQUIRED_COLUMNS, suggest_mapping, build_standard_df, validate_df
from src.storage import init_db, list_scenarios, save_scenario, load_scenario, delete_scenario
from src.sales_schema import SALES_REQUIRED_COLUMNS, suggest_sales_mapping, build_sales_df, validate_sales_df
from src.sales_bonus import generate_sales_transactions, default_product_coefficients, apply_product_coefficients, summarize_sales_bonus
from src.sales_ai import generate_sales_insight

# Set page config
st.set_page_config(
    page_title="AI 奖金分析系统 (Pro)",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: #f6f7fb;
        color: #111827;
    }
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.80);
        border-bottom: 1px solid rgba(17, 24, 39, 0.10);
        backdrop-filter: blur(10px);
    }
    [data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid rgba(17, 24, 39, 0.10);
    }
    [data-testid="stSidebar"] * {
        color: #111827;
    }
    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(17, 24, 39, 0.14);
        background: #ffffff;
    }
    .stButton > button:hover {
        border-color: rgba(17, 24, 39, 0.22);
        background: rgba(17, 24, 39, 0.03);
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: rgba(17, 24, 39, 0.14) !important;
        color: #111827 !important;
    }
    .stTextArea textarea {
        background: #ffffff !important;
        border-color: rgba(17, 24, 39, 0.14) !important;
        color: #111827 !important;
    }
    .stDataFrame, [data-testid="stDataFrame"] {
        border: 1px solid rgba(17, 24, 39, 0.10);
        border-radius: 12px;
        overflow: hidden;
        background: #ffffff;
    }
    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 1.2rem;
    }
    .topbar {
        display: flex;
        gap: 12px;
        align-items: center;
    }
    .brand {
        display: flex;
        gap: 10px;
        align-items: center;
        font-weight: 700;
        letter-spacing: 0.2px;
    }
    .brand-badge {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        background: rgba(0, 122, 255, 0.12);
        border: 1px solid rgba(0, 122, 255, 0.25);
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .brand-sub {
        opacity: 0.75;
        font-size: 12px;
        font-weight: 500;
    }
    .chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(17, 24, 39, 0.03);
        border: 1px solid rgba(17, 24, 39, 0.10);
        font-size: 12px;
        opacity: 0.9;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 2px solid #ff4b4b;
    }
    .pill-ok {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        background: rgba(0, 180, 120, 0.15);
        color: rgba(0, 180, 120, 1);
        font-size: 12px;
        border: 1px solid rgba(0, 180, 120, 0.35);
    }
    .pill-warn {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        background: rgba(255, 170, 0, 0.12);
        color: rgba(255, 170, 0, 1);
        font-size: 12px;
        border: 1px solid rgba(255, 170, 0, 0.35);
    }
    .flow-card {
        border: 1px solid rgba(17, 24, 39, 0.10);
        border-radius: 12px;
        padding: 14px 14px;
        background: #ffffff;
    }
    .flow-title {
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .flow-sub {
        opacity: 0.7;
        font-size: 12px;
    }
    .asset-item {
        width: 100%;
        text-align: left;
        border-radius: 10px;
        padding: 10px 10px;
        border: 1px solid rgba(17, 24, 39, 0.10);
        background: #ffffff;
    }
    .asset-item-selected {
        border-color: rgba(0, 160, 255, 0.6);
        background: rgba(0, 160, 255, 0.08);
    }
    .asset-title {
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 2px;
    }
    .asset-sub {
        opacity: 0.75;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

def _ensure_build_state():
    if "build_mode" not in st.session_state:
        st.session_state.build_mode = {
            "step": 1,
            "goal": "",
            "rules_text": "",
            "product_coeffs": default_product_coefficients(),
            "bonus_rate": 0.08,
            "build_plan": "",
            "conclusion_columns": ["排名", "姓名", "部门", "区域", "总营收", "有效业绩", "奖金比例", "应发奖金"],
            "confirmed": {},
            "tables": {},
            "selected_table": "销售奖金结论表",
            "rule_docs": [],
        }
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "硅基流动"
    if "llm_model_choice" not in st.session_state:
        st.session_state.llm_model_choice = "Qwen/Qwen2.5-7B-Instruct"
    if "llm_model_custom" not in st.session_state:
        st.session_state.llm_model_custom = "gpt-4o-mini"
    if "llm_api_key" not in st.session_state:
        st.session_state.llm_api_key = ""


def _render_topbar():
    bm = st.session_state.get("build_mode") or {}
    step_done = min(7, int(bm.get("step", 1)) - 1) if bm else 0
    mode = st.session_state.get("mode") or "构建模式"

    top1, top2, top3, top4 = st.columns([1.25, 1.55, 1.0, 0.8])
    with top1:
        st.markdown(
            '<div class="topbar"><div class="brand"><span class="brand-badge">✦</span><div>DataLens AI<br/><span class="brand-sub">销售奖金核算</span></div></div></div>',
            unsafe_allow_html=True,
        )
    with top2:
        selected = st.radio(
            "模式",
            options=["构建模式", "解读模式"],
            horizontal=True,
            label_visibility="collapsed",
            index=0 if mode == "构建模式" else 1,
            key="mode_radio",
        )
        if selected != mode:
            st.session_state.mode = selected
            st.rerun()
    with top3:
        st.markdown(f'<span class="chip">构建进度：{step_done}/7</span>', unsafe_allow_html=True)
    with top4:
        st.markdown('<span class="chip">数据状态：已就绪</span>', unsafe_allow_html=True)

SILICONFLOW_MODEL_PRESETS = [
    ("Qwen/Qwen2.5-7B-Instruct（推荐：便宜够用）", "Qwen/Qwen2.5-7B-Instruct"),
    ("Qwen/Qwen2.5-14B-Instruct（更稳：性价比）", "Qwen/Qwen2.5-14B-Instruct"),
    ("deepseek-ai/DeepSeek-V2.5（更强：推理/写报告）", "deepseek-ai/DeepSeek-V2.5"),
    ("Qwen/Qwen2.5-32B-Instruct（更强：成本更高）", "Qwen/Qwen2.5-32B-Instruct"),
    ("自定义…", "__custom__"),
]


def _get_llm_model(provider_key, choice_key, custom_key, fallback):
    provider = (st.session_state.get(provider_key) or "").strip()
    choice = st.session_state.get(choice_key) or ""
    custom = (st.session_state.get(custom_key) or "").strip()

    if provider == "硅基流动":
        if choice == "__custom__":
            return custom or fallback
        return choice or fallback

    return custom or fallback


def _llm_suggest(system_prompt, user_prompt):
    from src.llm_client import chat_complete

    api_key = st.session_state.get("llm_api_key") or ""
    if not api_key.strip():
        return None
    provider = st.session_state.get("llm_provider") or "硅基流动"
    model = _get_llm_model("llm_provider", "llm_model_choice", "llm_model_custom", "Qwen/Qwen2.5-7B-Instruct")
    return chat_complete(
        provider=provider,
        api_key=api_key,
        model=model,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
    )


def _df_field_info(df):
    items = []
    for idx, col in enumerate(df.columns, start=1):
        dtype = str(df[col].dtype)
        non_null = int(df[col].notna().sum())
        items.append({"序号": idx, "字段": col, "类型": dtype, "非空": non_null})
    return pd.DataFrame(items)


def _render_field_panel(df):
    st.markdown("#### 字段说明")
    fields = _df_field_info(df)
    total = len(fields)
    if total > 6:
        q = st.text_input("搜索字段", key=f"field_search_{hash(tuple(df.columns))}")
        if q.strip():
            fields = fields[fields["字段"].astype(str).str.contains(q.strip(), case=False, na=False)]

    show_n = 12 if total > 12 else total
    st.caption(f"默认显示前 {show_n} 个字段，共 {total} 个")
    show_all = st.toggle("显示全部字段", value=False, key=f"field_show_all_{hash(tuple(df.columns))}")
    shown = fields if show_all else fields.head(show_n)
    st.dataframe(shown, use_container_width=True, height=320)

    if not show_all and total > show_n:
        st.caption(f"+{total - show_n} 更多字段")


def _render_table_viewer(df, title):
    st.markdown(f"## {title}")

    total_rows = len(df)
    preview_n = min(5, total_rows)
    st.caption(f"显示前 {preview_n} 行 / 共约 {total_rows:,} 行")
    st.dataframe(df.head(preview_n), use_container_width=True, height=170)

    st.markdown("---")

    col_a, col_b, col_c = st.columns([1.2, 1.2, 1.6])
    with col_a:
        page_size = st.selectbox("每页行数", [50, 100, 200], index=0, key=f"page_size_{title}")
    with col_b:
        pages = max(1, (total_rows + page_size - 1) // page_size)
        page = st.number_input("页码", min_value=1, max_value=pages, value=1, step=1, key=f"page_{title}")
    with col_c:
        st.caption(f"显示 {((page-1)*page_size)+1}-{min(page*page_size, total_rows)} 行，共 {total_rows:,} 行")

    start = (page - 1) * page_size
    end = min(start + page_size, total_rows)
    st.dataframe(df.iloc[start:end], use_container_width=True, height=520)


def _ai_add(title, content, status="待确认"):
    st.session_state.ai_messages.append(
        {"id": f"m{len(st.session_state.ai_messages)+1}", "title": title, "content": content, "status": status}
    )


def _render_ai_panel():
    bm = st.session_state.build_mode
    tables = bm.get("tables", {})
    msgs = st.session_state.ai_messages[-30:]

    st.markdown("### AI 助手")

    expand_by_default = not bool((st.session_state.get("llm_api_key") or "").strip())
    with st.expander("模型配置", expanded=expand_by_default):
        st.selectbox("提供方", ["硅基流动", "OpenAI"], key="llm_provider")
        if st.session_state.get("llm_provider") == "硅基流动":
            st.selectbox(
                "模型",
                options=[m[1] for m in SILICONFLOW_MODEL_PRESETS],
                format_func=lambda v: next((m[0] for m in SILICONFLOW_MODEL_PRESETS if m[1] == v), v),
                index=0,
                key="llm_model_choice",
            )
            if st.session_state.get("llm_model_choice") == "__custom__":
                st.text_input("自定义模型名", value="", key="llm_model_custom")
        else:
            st.text_input("模型", value=st.session_state.get("llm_model_custom", "gpt-4o-mini"), key="llm_model_custom")
        st.text_input("API Key", type="password", value=st.session_state.get("llm_api_key", ""), key="llm_api_key")
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("🔌 测试连接", use_container_width=True):
                from src.llm_client import chat_complete

                try:
                    with st.spinner("正在测试..."):
                        out = chat_complete(
                            provider=st.session_state.get("llm_provider"),
                            api_key=st.session_state.get("llm_api_key"),
                            model=_get_llm_model("llm_provider", "llm_model_choice", "llm_model_custom", "Qwen/Qwen2.5-7B-Instruct"),
                            messages=[
                                {"role": "system", "content": "你是一个测试助手。"},
                                {"role": "user", "content": "请只回复 OK"},
                            ],
                        )
                    st.success(f"连接成功：{out.strip()[:120]}")
                except Exception as e:
                    st.error(f"连接失败：{str(e)}")
        with col_b:
            st.caption("填好 Key 后，步骤 2/3/4/6 的 AI 文案会更智能。")

    if not msgs:
        if not tables:
            st.info("先在步骤 1 点击“生成示例底表”或上传文件，AI 助手才会开始产生消息。")
        else:
            st.info("已加载数据，继续执行步骤 2/3/4，AI 助手会产出建议并显示在这里。")
        return

    for i, m in enumerate(msgs[::-1]):
        with st.container(border=True):
            st.markdown(f"**{m['title']}**")
            st.markdown(m["content"])
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.caption(m.get("status", ""))
            with col2:
                if st.button("确认", key=f"ai_ok_{m['id']}", disabled=m.get("status") == "已确认"):
                    m["status"] = "已确认"
                    st.rerun()
            with col3:
                if st.button("拒绝", key=f"ai_no_{m['id']}", disabled=m.get("status") == "已拒绝"):
                    m["status"] = "已拒绝"
                    st.rerun()


def _render_assets_panel():
    bm = st.session_state.build_mode
    st.markdown("### 数据资产")
    st.caption("销售奖金核算")
    tables = bm.get("tables", {})

    with st.expander(f"数据表（{len(tables)}）", expanded=True):
        if tables:
            names = list(tables.keys())
            current = bm.get("selected_table") if bm.get("selected_table") in names else names[0]

            def fmt(n):
                df = tables[n]
                kind = "底表" if n == "销售业务明细表" else ("中间表" if n == "有效业绩折算表" else ("结论表" if n == "销售奖金结论表" else "数据表"))
                return f"{n}  ·  {kind} ·  {len(df):,} 行"

            selected = st.radio(
                "选择数据表",
                options=names,
                index=names.index(current),
                format_func=fmt,
                label_visibility="collapsed",
                key="assets_tables_radio",
            )
            bm["selected_table"] = selected
        else:
            st.caption("暂无数据表")

    st.markdown("---")
    docs = bm.get("rule_docs") or []
    with st.expander(f"规则文档（{len(docs)}）", expanded=False):
        if docs:
            for d in docs[:10]:
                title = d.get("name") or "规则文档"
                cnt = int(d.get("rules_count") or 0)
                st.markdown(f"- {title}（{cnt} 条规则）")
        else:
            st.caption("暂无规则文档")

    st.markdown("---")
    with st.expander("分析目标", expanded=False):
        if bm.get("goal", "").strip():
            st.markdown(bm["goal"])
            st.markdown("**公式**")
            st.caption("计算每个销售人员的应发奖金：奖金 = 有效业绩 × 奖金比例")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.button("有效业绩", use_container_width=True, disabled=True)
            with c2:
                st.button("奖金比例", use_container_width=True, disabled=True)
            with c3:
                st.button("应发奖金", use_container_width=True, disabled=True)
        else:
            st.caption("尚未设定")


def _render_build_center():
    bm = st.session_state.build_mode
    st.markdown("## 构建流程")
    st.caption("AI 引导的数据分析构建过程")
    st.progress(min(1.0, bm.get("step", 1) / 7.0))
    st.markdown(f"已完成 {min(7, bm.get('step', 1)-1)}/7 步")

    step = bm.get("step", 1)

    with st.container(border=True):
        st.markdown("### 步骤 1  导入底表")
        col1, col2 = st.columns([1, 1])
        with col1:
            rows = st.number_input("生成示例数据行数", min_value=100, value=5000, step=100, key="sales_rows")
        with col2:
            if st.button("生成示例底表", use_container_width=True):
                df = generate_sales_transactions(int(rows))
                bm["tables"]["销售业务明细表"] = df
                _ai_add("检测到 Excel 文件包含 7 个字段", f"记录数：{len(df):,} 行数据，涵盖 12 名销售的季度交易记录。", status="已确认")
                bm["step"] = max(bm["step"], 2)
                st.rerun()

        uploaded = st.file_uploader("或上传 CSV/Excel", type=["csv", "xlsx"])
        if uploaded is not None:
            raw = load_data(uploaded)
            if raw is not None:
                st.session_state.sales_raw = raw
                st.session_state.sales_mapping_suggestion = suggest_sales_mapping(raw.columns)

    if "sales_raw" in st.session_state and isinstance(st.session_state.sales_raw, pd.DataFrame):
        raw_df = st.session_state.sales_raw
        with st.container(border=True):
            st.markdown("### 字段映射")
            suggestion = st.session_state.get("sales_mapping_suggestion") or {}
            mapping = {}
            cols = ["(留空)"] + list(raw_df.columns)
            for target in SALES_REQUIRED_COLUMNS:
                default = suggestion.get(target)
                index = cols.index(default) if default in cols else 0
                selected = st.selectbox(f"{target} ←", cols, index=index, key=f"sales_map_{target}")
                mapping[target] = None if selected == "(留空)" else selected

            if st.button("应用映射并载入底表", use_container_width=True):
                df_sales = build_sales_df(raw_df, mapping)
                bm["tables"]["销售业务明细表"] = df_sales
                st.session_state.pop("sales_raw", None)
                _ai_add("导入完成", f"底表已载入：{len(df_sales):,} 行。", status="已确认")
                bm["step"] = max(bm["step"], 2)
                st.rerun()

    base_df = bm.get("tables", {}).get("销售业务明细表")
    if base_df is not None and not base_df.empty:
        with st.container(border=True):
            st.markdown("### 步骤 2  AI 识别数据结构")
            v = validate_sales_df(base_df)
            if v["errors"] or v["warnings"]:
                for e in v["errors"]:
                    st.error(e)
                for w in v["warnings"]:
                    st.warning(w)
            if st.button("开始识别", use_container_width=True, disabled=bool(v["errors"])):
                cols = ", ".join(SALES_REQUIRED_COLUMNS)
                content = _llm_suggest(
                    "你是一个数据分析产品的 AI 助手，负责把字段识别结果用中文输出给用户确认。",
                    f"请用一句话列出识别到的字段并说明类型：{cols}",
                ) or f"字段识别完成：{cols}"
                _ai_add("字段识别完成", content, status="已确认")
                bm["step"] = max(bm["step"], 3)
                st.rerun()

        with st.container(border=True):
            st.markdown("### 步骤 3  定义分析目标")
            with st.form("build_goal_form", clear_on_submit=False):
                st.text_area(
                    "分析目标",
                    value=bm.get("goal", ""),
                    placeholder="例如：计算销售人员的季度奖金。先按产品系数折算有效业绩，再按业绩档位确定奖金比例。",
                    height=120,
                    key="build_goal_input",
                )
                submitted = st.form_submit_button("确认目标", use_container_width=True)

            if submitted:
                goal_value = (st.session_state.get("build_goal_input") or "").strip()
                if not goal_value:
                    st.warning("请先填写分析目标")
                else:
                    bm["goal"] = st.session_state.get("build_goal_input") or ""
                    if (st.session_state.get("llm_api_key") or "").strip():
                        with st.spinner("AI 正在理解目标..."):
                            content = _llm_suggest(
                                "你是一个销售奖金核算的数据分析助手，请复述用户目标并拆解成 2-3 个关键点。",
                                bm["goal"],
                            )
                    else:
                        content = _llm_suggest(
                            "你是一个销售奖金核算的数据分析助手，请复述用户目标并拆解成 2-3 个关键点。",
                            bm["goal"],
                        )

                    _ai_add("理解你的目标", content or bm["goal"], status="已确认")
                    bm["step"] = max(bm["step"], 4)
                    st.rerun()

        with st.container(border=True):
            st.markdown("### 步骤 4  导入规则文档")
            rules_file = st.file_uploader("上传规则（txt/md）", type=["txt", "md"], key="rules_upload")
            if rules_file is not None:
                try:
                    st.session_state.build_rules_input = rules_file.getvalue().decode("utf-8", errors="ignore")
                except Exception:
                    st.session_state.build_rules_input = ""

            with st.form("build_rules_form", clear_on_submit=False):
                st.text_area(
                    "规则内容",
                    value=st.session_state.get("build_rules_input", bm.get("rules_text", "")),
                    height=150,
                    key="build_rules_input",
                )
                submitted = st.form_submit_button("提取规则", use_container_width=True)

            if submitted:
                rules_value = (st.session_state.get("build_rules_input") or "").strip()
                if not rules_value:
                    st.warning("请先填写规则内容")
                else:
                    bm["rules_text"] = st.session_state.get("build_rules_input") or ""
                    if rules_file is not None:
                        bm["rule_docs"] = [{"name": rules_file.name, "rules_count": 2}]
                    elif not bm.get("rule_docs"):
                        bm["rule_docs"] = [{"name": "2026年Q1销售奖金计算规则", "rules_count": 2}]

                    if (st.session_state.get("llm_api_key") or "").strip():
                        with st.spinner("AI 正在提取规则..."):
                            content = _llm_suggest(
                                "你是一个数据分析助手。用户给出一段规则文档，请提取为条目化规则列表，尽量简短。",
                                bm["rules_text"],
                            )
                    else:
                        content = _llm_suggest(
                            "你是一个数据分析助手。用户给出一段规则文档，请提取为条目化规则列表，尽量简短。",
                            bm["rules_text"],
                        )

                    fallback = "1. 产品系数规则（影响有效业绩计算）\n2. 奖金比例规则（影响最终奖金计算）"
                    _ai_add("已从文档中提取 2 条规则", content or fallback, status="已确认")
                    bm["step"] = max(bm["step"], 5)
                    st.rerun()

        with st.container(border=True):
            st.markdown("### 步骤 5  定义结论表结构")
            st.caption("确认结论表包含：排名、姓名、部门、区域、总营收、有效业绩、奖金比例、应发奖金")

            cols_text = "、".join(bm.get("conclusion_columns") or [])
            with st.container(border=True):
                st.markdown("**AI 建议**")
                st.markdown(
                    f"建议结论表结构：{cols_text}。\n\n"
                    "其中：总营收（聚合计算）；有效业绩（规则计算，支持下钻）；奖金比例、应发奖金（规则计算，支持下钻）。"
                )

            confirmed = bool(bm.get("confirmed", {}).get(5))
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("确认结论表结构", use_container_width=True, disabled=confirmed):
                    bm["confirmed"][5] = True
                    _ai_add("结论表结构已确认", f"结论表字段：{cols_text}", status="已确认")
                    bm["step"] = max(bm["step"], 6)
                    st.rerun()
            with col_b:
                if confirmed:
                    st.markdown('<span class="pill-ok">已确认</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="pill-warn">待确认</span>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 步骤 6  AI 生成构建计划")
            st.caption("AI 规划计算步骤：底表 → 系数折算 → 按人汇总 → 奖金计算 → 结论表")

            if not bm.get("build_plan"):
                bm["build_plan"] = (
                    "构建计划：\n"
                    "步骤1：关联产品系数，计算每笔交易的有效业绩\n"
                    "步骤2：按销售人员汇总有效业绩与总营收\n"
                    "步骤3：按奖金比例计算应发奖金\n"
                    "步骤4：生成排名与结论表"
                )

            with st.container(border=True):
                st.markdown("**AI 建议**")
                plan_text = _llm_suggest(
                    "你是一个数据分析产品的 AI 助手。请给出可执行的构建计划步骤列表，每行一个步骤。",
                    f"分析目标：{bm.get('goal','')}\n规则：{bm.get('rules_text','')}",
                ) or bm["build_plan"]
                st.markdown(plan_text)

            confirmed = bool(bm.get("confirmed", {}).get(6))
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("确认构建计划", use_container_width=True, disabled=confirmed or not bm.get("confirmed", {}).get(5)):
                    bm["confirmed"][6] = True
                    bm["build_plan"] = plan_text
                    _ai_add("构建计划已确认", plan_text, status="已确认")
                    bm["step"] = max(bm["step"], 7)
                    st.rerun()
            with col_b:
                if confirmed:
                    st.markdown('<span class="pill-ok">已确认</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="pill-warn">待确认</span>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 步骤 7  执行构建")
            st.caption("生成「有效业绩折算表」和「销售奖金结论表」")

            can_run = bool(bm.get("confirmed", {}).get(6))
            if st.button("执行构建", use_container_width=True, disabled=not can_run):
                eff = apply_product_coefficients(base_df, bm.get("product_coeffs") or {})
                summary = summarize_sales_bonus(eff, bonus_rate=float(bm.get("bonus_rate", 0.08)))
                bm["tables"]["有效业绩折算表"] = eff
                bm["tables"]["销售奖金结论表"] = summary.reset_index(drop=True)
                total_bonus = float(bm["tables"]["销售奖金结论表"]["奖金金额"].sum()) if "奖金金额" in bm["tables"]["销售奖金结论表"].columns else 0.0
                _ai_add(
                    "构建完成",
                    f"中间表「有效业绩折算表」：{len(eff):,} 行（有效业绩明细）\n"
                    f"结论表「销售奖金结论表」：{len(summary):,} 行（每人一行）\n"
                    f"奖金金额：¥{total_bonus:,.0f}",
                    status="已确认",
                )
                bm["confirmed"][7] = True
                st.rerun()

            if "销售奖金结论表" in bm.get("tables", {}):
                st.dataframe(bm["tables"]["销售奖金结论表"].head(50), use_container_width=True, height=260)

        if bm.get("tables"):
            st.markdown("---")
            st.markdown("### 数据流向")
            base_rows = len(bm["tables"].get("销售业务明细表", []))
            eff_rows = len(bm["tables"].get("有效业绩折算表", []))
            out_rows = len(bm["tables"].get("销售奖金结论表", []))

            c1, c2, c3 = st.columns([1, 0.2, 1])
            with c1:
                st.markdown(
                    f'<div class="flow-card"><div class="flow-title">销售业务明细表</div><div class="flow-sub">{base_rows:,} 行</div></div>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown("→")
            with c3:
                st.markdown(
                    f'<div class="flow-card"><div class="flow-title">有效业绩折算表</div><div class="flow-sub">{eff_rows:,} 行</div></div>',
                    unsafe_allow_html=True,
                )

            c4, c5, c6 = st.columns([1, 0.2, 1])
            with c4:
                st.markdown(" ")
            with c5:
                st.markdown("→")
            with c6:
                st.markdown(
                    f'<div class="flow-card"><div class="flow-title">销售奖金结论表</div><div class="flow-sub">{out_rows:,} 行</div></div>',
                    unsafe_allow_html=True,
                )


def _render_build_mode():
    _ensure_build_state()
    col_left, col_center, col_right = st.columns([1.1, 2.2, 1.2], gap="large")
    with col_left:
        _render_assets_panel()
    with col_center:
        _render_build_center()
    with col_right:
        _render_ai_panel()

def _render_read_mode():
    _ensure_build_state()
    bm = st.session_state.build_mode
    tables = bm.get("tables", {})
    col_left, col_center, col_right = st.columns([1.1, 2.2, 1.2], gap="large")

    with col_left:
        _render_assets_panel()

    with col_center:
        selected = bm.get("selected_table")
        df = tables.get(selected)
        if df is None or df.empty:
            st.info("请先在构建模式生成数据表")
        else:
            if {"销售人员", "奖金金额"}.issubset(set(df.columns)) and "排名" not in df.columns:
                df = df.copy()
                df.insert(0, "排名", range(1, len(df) + 1))

            header_left, header_right = st.columns([1.3, 0.7])
            with header_left:
                st.markdown(f"## {selected}")
                new_fields = max(0, len(df.columns) - 8)
                if new_fields:
                    st.caption(f"{len(df):,} 行 · {len(df.columns)} 个字段 · {new_fields} 个新字段")
                else:
                    st.caption(f"{len(df):,} 行 · {len(df.columns)} 个字段")
            with header_right:
                show_fields = st.selectbox("字段说明", ["关闭", "打开"], index=0, key="field_panel_toggle")

            if show_fields == "打开":
                with st.expander("字段说明", expanded=True):
                    _render_field_panel(df)

            _render_table_viewer(df, selected)

    with col_right:
        st.markdown("### AI 数据解读")
        st.caption("与构建模式共用同一套模型配置，切换模式无需重复填写。")
        st.selectbox("提供方", ["硅基流动", "OpenAI"], key="llm_provider")
        if st.session_state.get("llm_provider") == "硅基流动":
            st.selectbox(
                "模型",
                options=[m[1] for m in SILICONFLOW_MODEL_PRESETS],
                format_func=lambda v: next((m[0] for m in SILICONFLOW_MODEL_PRESETS if m[1] == v), v),
                index=0,
                key="llm_model_choice",
            )
            if st.session_state.get("llm_model_choice") == "__custom__":
                st.text_input("自定义模型名", value="", key="llm_model_custom")
        else:
            st.text_input("模型", value=st.session_state.get("llm_model_custom", "gpt-4o-mini"), key="llm_model_custom")

        model = _get_llm_model("llm_provider", "llm_model_choice", "llm_model_custom", "Qwen/Qwen2.5-7B-Instruct")
        api_key = st.text_input("API Key", type="password", key="llm_api_key")
        custom_prompt = st.text_area("关注重点", key="sales_ai_prompt", height=120)
        if st.button("生成解读", type="primary", use_container_width=True):
            df = tables.get(bm.get("selected_table"))
            with st.spinner("AI 正在解读数据..."):
                st.session_state.sales_insight = generate_sales_insight(
                    df,
                    api_key=api_key,
                    custom_prompt=custom_prompt,
                    model=model,
                    provider=st.session_state.get("llm_provider"),
                )

        insight = st.session_state.get("sales_insight")
        if insight:
            st.markdown(insight)
        else:
            st.caption("点击“生成解读”后显示报告")

def main():
    init_db()

    _ensure_build_state()
    st.session_state.mode = st.session_state.get("mode") or "构建模式"
    _render_topbar()

    if st.session_state.get("mode") == "构建模式":
        _render_build_mode()
        return

    if st.session_state.get("mode") == "解读模式":
        if "build_mode" not in st.session_state or not st.session_state.build_mode.get("tables") or "销售奖金结论表" not in st.session_state.build_mode.get("tables", {}):
            st.info("当前尚未生成结论表，解读模式不可用。请先在构建模式完成执行构建。")
            st.session_state.mode = "构建模式"
            st.rerun()

    if "build_mode" in st.session_state and st.session_state.build_mode.get("tables"):
        _render_read_mode()
        return

    st.title("💰 AI 奖金分析系统 (Pro)")
    st.markdown("### 🚀 企业级智能薪酬决策平台")
    
    if "load_scenario_name" in st.session_state and st.session_state.load_scenario_name:
        try:
            params, df_loaded = load_scenario(st.session_state.load_scenario_name)
            st.session_state.data = df_loaded
            st.session_state.total_bonus_pool = float(params.get("total_bonus_pool", 1000000))
            st.session_state.weight_s = float(params.get("weight_s", 2.0))
            st.session_state.weight_a = float(params.get("weight_a", 1.5))
            st.session_state.weight_b = float(params.get("weight_b", 1.0))
            st.session_state.weight_c = float(params.get("weight_c", 0.5))
            st.session_state.weight_d = float(params.get("weight_d", 0.0))
            st.session_state.limit_s = float(params.get("limit_s", 0.2))
            st.session_state.limit_sa = float(params.get("limit_sa", 0.4))
            st.session_state.enable_dept_budget = bool(params.get("enable_dept_budget", False))
            st.session_state.dept_budgets = params.get("dept_budgets", {}) or {}
        finally:
            st.session_state.load_scenario_name = None
            st.rerun()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ 全局配置")

        with st.expander("📦 方案管理", expanded=False):
            existing = ["(不选择)"] + list_scenarios()
            selected = st.selectbox("已有方案", existing, index=0)
            name = st.text_input("方案名称", key="scenario_name")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("💾 保存", use_container_width=True):
                    params = {
                        "total_bonus_pool": st.session_state.get("total_bonus_pool", 1000000),
                        "weight_s": st.session_state.get("weight_s", 2.0),
                        "weight_a": st.session_state.get("weight_a", 1.5),
                        "weight_b": st.session_state.get("weight_b", 1.0),
                        "weight_c": st.session_state.get("weight_c", 0.5),
                        "weight_d": st.session_state.get("weight_d", 0.0),
                        "limit_s": st.session_state.get("limit_s", 0.2),
                        "limit_sa": st.session_state.get("limit_sa", 0.4),
                        "enable_dept_budget": st.session_state.get("enable_dept_budget", False),
                        "dept_budgets": st.session_state.get("dept_budgets", {}) or {},
                    }
                    try:
                        save_scenario(name, params, st.session_state.data)
                    except Exception as e:
                        st.error(str(e))
                    else:
                        st.success("已保存")
                        st.rerun()
            with col_s2:
                if st.button("📂 加载", use_container_width=True, disabled=(selected == "(不选择)")):
                    st.session_state.load_scenario_name = selected
                    st.rerun()

            if st.button("🗑️ 删除", use_container_width=True, disabled=(selected == "(不选择)")):
                delete_scenario(selected)
                st.success("已删除")
                st.rerun()
        
        with st.expander("📂 数据源配置", expanded=True):
            data_source = st.radio("选择模式", ["模拟数据", "文件上传"], horizontal=True)
            if data_source == "模拟数据":
                num_employees = st.slider("员工规模", 10, 500, 50)
                if st.button("🔄 重置数据", use_container_width=True):
                    st.session_state.data = generate_sample_data(num_employees)
                    st.rerun()
            else:
                uploaded_file = st.file_uploader("拖拽上传 CSV/Excel", type=['csv', 'xlsx'])
                if uploaded_file:
                    loaded_data = load_data(uploaded_file)
                    if loaded_data is not None:
                        st.session_state.raw_data = loaded_data
                        st.session_state.mapping_suggestion = suggest_mapping(loaded_data.columns)

        with st.expander("💰 奖金池设定", expanded=True):
            total_bonus_pool = st.number_input("总奖金包 (¥)", min_value=0, step=50000, key="total_bonus_pool")
            
        with st.expander("⚖️ 绩效权重", expanded=False):
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                weight_s = st.number_input("S (卓越)", 0.0, 10.0, 2.0, 0.1, key="weight_s")
                weight_a = st.number_input("A (优秀)", 0.0, 10.0, 1.5, 0.1, key="weight_a")
                weight_b = st.number_input("B (良好)", 0.0, 10.0, 1.0, 0.1, key="weight_b")
            with col_w2:
                weight_c = st.number_input("C (合格)", 0.0, 10.0, 0.5, 0.1, key="weight_c")
                weight_d = st.number_input("D (需改进)", 0.0, 10.0, 0.0, 0.1, key="weight_d")
            weights = {'S': weight_s, 'A': weight_a, 'B': weight_b, 'C': weight_c, 'D': weight_d}

        with st.expander("🛡️ 风控规则", expanded=False):
            st.caption("强制分布预警阈值")
            limit_s = st.slider("S级 最大比例", 0.0, 1.0, key="limit_s")
            limit_sa = st.slider("S+A级 最大比例", 0.0, 1.0, key="limit_sa")
            
        with st.expander("🧠 AI 配置", expanded=False):
            api_key = st.text_input("OpenAI API Key", type="password", help="留空则使用内置规则引擎")

    # Data Initialization
    if 'data' not in st.session_state:
        st.session_state.data = generate_sample_data(50)

    if "raw_data" in st.session_state and isinstance(st.session_state.raw_data, pd.DataFrame):
        raw_df = st.session_state.raw_data
        with st.sidebar:
            with st.expander("🧭 字段映射与校验", expanded=True):
                st.caption("上传文件列名不一致时，在此映射为系统标准字段")
                suggestion = st.session_state.get("mapping_suggestion") or {}
                mapping = {}
                cols = ["(留空)"] + list(raw_df.columns)
                for target in REQUIRED_COLUMNS:
                    default = suggestion.get(target)
                    index = cols.index(default) if default in cols else 0
                    selected = st.selectbox(f"{target} ←", cols, index=index, key=f"map_{target}")
                    mapping[target] = None if selected == "(留空)" else selected

                if st.button("✅ 应用映射并载入", use_container_width=True):
                    df_standard = build_standard_df(raw_df, mapping)
                    st.session_state.data = df_standard
                    st.session_state.pop("raw_data", None)
                    st.rerun()
    
    df = st.session_state.data
    if df is None:
        st.info("👈 请在左侧加载数据")
        return

    validation = validate_df(df)
    if validation["errors"] or validation["warnings"]:
        with st.sidebar:
            with st.expander("🧪 数据质量报告", expanded=False):
                for e in validation["errors"]:
                    st.error(e)
                for w in validation["warnings"]:
                    st.warning(w)

    # Calculation
    df_calculated = calculate_bonus(df, total_bonus_pool, weights)

    edited_state = st.session_state.get("data_editor")
    if isinstance(edited_state, pd.DataFrame) and not edited_state.empty:
        df_effective = edited_state
    else:
        df_effective = df_calculated

    final_df = calculate_bonus(df_effective, total_bonus_pool, weights)

    dist_warnings = check_forced_distribution(final_df, limit_s, limit_sa)

    dept_budgets = {}
    budget_warnings = []

    with st.sidebar:
        with st.expander("🏦 部门预算", expanded=False):
            enable_dept_budget = st.checkbox("启用部门预算控制", value=False, key="enable_dept_budget")
            if enable_dept_budget:
                st.caption("默认按人头比例分配，可逐个部门调整")
                dept_counts = final_df["部门"].value_counts()
                total_headcount = len(final_df)
                st.session_state.dept_budgets = st.session_state.get("dept_budgets", {}) or {}
                for dept, count in dept_counts.items():
                    default_budget = (count / total_headcount) * total_bonus_pool
                    value = float(st.session_state.dept_budgets.get(dept, default_budget))
                    dept_budgets[dept] = st.number_input(
                        f"{dept} 预算 (¥)",
                        min_value=0.0,
                        value=value,
                        step=10000.0,
                        key=f"dept_budget_{dept}",
                    )
                st.session_state.dept_budgets = dept_budgets

    if dept_budgets:
        budget_warnings = check_department_budget(final_df, dept_budgets)

    # Dashboard Layout
    
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 员工总数", len(final_df))
    with col2:
        st.metric("💰 奖金池", f"¥{total_bonus_pool:,.0f}")
    with col3:
        actual_total = final_df["预估奖金"].sum()
        delta = total_bonus_pool - actual_total
        st.metric("💸 实际分配", f"¥{actual_total:,.0f}", delta=f"{delta:,.0f} (剩余)")
    with col4:
        avg_bonus = final_df["预估奖金"].mean()
        st.metric("📊 人均奖金", f"¥{avg_bonus:,.0f}")

    # Warning Banners
    if dist_warnings or budget_warnings:
        with st.container():
            for w in dist_warnings:
                st.warning(w, icon="⚠️")
            for w in budget_warnings:
                st.error(w, icon="💸")

    # Main Tabs
    tab1, tab2, tab3 = st.tabs(["📊 数据沙盘", "📈 深度透视", "🤖 智能顾问"])
    
    with tab1:
        st.markdown("### 🛠️ 交互式调整")
        st.caption("直接修改表格中的**绩效评分**或**当前薪资**，上方指标将实时联动。")
        
        column_config = {
            "预估奖金": st.column_config.NumberColumn(format="¥%.2f", disabled=True),
            "奖金占比": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1.0, disabled=True),
            "当前薪资": st.column_config.NumberColumn(format="¥%d"),
            "绩效评分": st.column_config.SelectboxColumn(options=['S', 'A', 'B', 'C', 'D'], required=True),
            "部门": st.column_config.SelectboxColumn(options=['研发部', '销售部', '市场部', '人力资源部', '财务部'], required=True),
            "职级": st.column_config.SelectboxColumn(options=['初级', '中级', '高级', '资深', '总监'], required=True),
        }
        
        edited_df = st.data_editor(
            final_df,
            num_rows="dynamic",
            column_config=column_config,
            use_container_width=True,
            height=500,
            key="data_editor"
        )
        
        # Recalculate if edited (handled by Streamlit's rerun on widget change, but we ensure consistency)
        # Note: In a real app, we might want to update session_state.data with edited_df

    with tab2:
        col_viz1, col_viz2 = st.columns(2)
        with col_viz1:
            plot_department_distribution(final_df)
        with col_viz2:
            plot_performance_distribution(final_df)
        st.markdown("---")
        plot_salary_vs_bonus(final_df)

    with tab3:
        st.markdown("### 🧠 AI 决策辅助")
        col_ai_input, col_ai_output = st.columns([1, 2])
        
        with col_ai_input:
            st.info("💡 **提示**: 输入您的 OpenAI API Key 可获得更深度的分析。否则将使用内置规则引擎。")
            custom_prompt = st.text_area("关注重点 (可选)", placeholder="例如：请重点分析研发部的激励情况，或者检查是否有性别薪酬差异...")
            analyze_btn = st.button("🚀 生成分析报告", type="primary", use_container_width=True)
            
        with col_ai_output:
            if analyze_btn:
                with st.spinner("🤖 AI 正在深度思考中..."):
                    report = generate_analysis_report(final_df, api_key, custom_prompt)
                    st.markdown(report)
            else:
                st.markdown("""
                > **示例洞察方向**：
                > - 部门间的公平性分析
                > - 高绩效人才的保留风险
                > - 薪酬结构的合理性建议
                """)

if __name__ == "__main__":
    main()
