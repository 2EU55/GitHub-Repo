import os
import json

def generate_analysis_report(df, api_key=None, custom_prompt=None, model=None, provider=None):
    """
    Generate analysis report. 
    If api_key is provided, use LLM. Otherwise, use rule-based template.
    """
    if df is None or df.empty:
        return "没有足够的数据进行分析。"
    
    # Check if we should use LLM
    if api_key:
        try:
            return generate_llm_report(df, api_key, custom_prompt, model, provider)
        except Exception as e:
            return f"⚠️ LLM 分析失败: {str(e)}\n\n(已切换回基础规则分析)\n\n" + generate_rule_based_report(df)
    else:
        return generate_rule_based_report(df)

def generate_rule_based_report(df):
    """Original rule-based logic."""
    total_bonus = df['预估奖金'].sum()
    avg_bonus = df['预估奖金'].mean()
    top_performer = df.loc[df['预估奖金'].idxmax()]
    
    dept_stats = df.groupby('部门')['预估奖金'].mean().sort_values(ascending=False)
    highest_dept = dept_stats.index[0]
    lowest_dept = dept_stats.index[-1]
    
    s_count = len(df[df['绩效评分'] == 'S'])
    d_count = len(df[df['绩效评分'] == 'D'])
    
    report = f"""
### 🤖 基础规则洞察报告

#### 1. 总体概况
本次奖金分配共覆盖 **{len(df)}** 名员工，奖金池总额 **¥{total_bonus:,.2f}**，人均奖金 **¥{avg_bonus:,.2f}**。

#### 2. 部门分析
- **{highest_dept}** 的人均奖金最高，显示该部门整体绩效表现或薪资基数较高。
- **{lowest_dept}** 的人均奖金最低，建议关注该部门的激励机制是否充足。

#### 3. 绩效结构
- 获得 **S** 级评价的员工有 **{s_count}** 人，属于核心骨干，建议重点保留。
- 获得 **D** 级评价的员工有 **{d_count}** 人，建议制定绩效改进计划 (PIP)。

#### 4. 异常检测与建议
- **最高奖金获得者**：{top_performer['姓名']} ({top_performer['部门']} - {top_performer['职级']})，奖金金额 ¥{top_performer['预估奖金']:,.2f}。
"""
    return report

def generate_llm_report(df, api_key, custom_prompt=None, model=None, provider=None):
    from src.llm_client import chat_complete
    
    # Prepare summary data for LLM (avoid sending PII)
    dept_agg = (
        df.groupby("部门", dropna=False)
        .agg(bonus_sum=("预估奖金", "sum"), bonus_mean=("预估奖金", "mean"), employee_count=("员工ID", "count"))
        .reset_index()
    )
    dept_stats = []
    for r in dept_agg.to_dict(orient="records"):
        dept_stats.append(
            {
                "部门": str(r.get("部门")),
                "奖金合计": float(r.get("bonus_sum") or 0.0),
                "奖金均值": float(r.get("bonus_mean") or 0.0),
                "人数": int(r.get("employee_count") or 0),
            }
        )

    top_performers = []
    top_df = df.nlargest(3, "预估奖金")[["部门", "职级", "绩效评分", "预估奖金"]]
    for r in top_df.to_dict("records"):
        top_performers.append(
            {
                "部门": str(r.get("部门")),
                "职级": str(r.get("职级")),
                "绩效评分": str(r.get("绩效评分")),
                "预估奖金": float(r.get("预估奖金") or 0.0),
            }
        )

    summary = {
        "total_employees": len(df),
        "total_bonus": float(df["预估奖金"].sum()),
        "avg_bonus": float(df["预估奖金"].mean()),
        "dept_stats": dept_stats,
        "performance_dist": {str(k): int(v) for k, v in df["绩效评分"].value_counts().to_dict().items()},
        "top_performers": top_performers,
    }
    
    system_prompt = """
    你是一个专业的人力资源数据分析师。根据提供的奖金分配数据摘要，生成一份专业的分析报告。
    报告应包含：
    1. 总体评价（资金使用效率、覆盖面）
    2. 部门间公平性分析
    3. 绩效激励效果评估
    4. 具体的管理建议（如某些部门是否被低估，高绩效比例是否合理）
    
    请使用 Markdown 格式，语气专业、客观。
    """
    
    model_name = model or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
    user_content = f"数据摘要(JSON): {json.dumps(summary, ensure_ascii=False, default=str)}"
    if custom_prompt:
        user_content += f"\n\n用户额外关注点: {custom_prompt}"

    use_provider = provider or os.environ.get("LLM_PROVIDER") or "openai"
    return chat_complete(
        provider=use_provider,
        api_key=api_key,
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
