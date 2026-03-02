import json
import os


def generate_sales_insight(df, api_key=None, custom_prompt=None, model=None, provider=None):
    if df is None or getattr(df, "empty", True):
        return "没有足够的数据进行解读。"

    if api_key:
        try:
            return _generate_llm(df, api_key, custom_prompt, model, provider)
        except Exception as e:
            return f"⚠️ LLM 解读失败: {str(e)}\n\n(已切换回基础规则解读)\n\n" + _generate_rule(df)

    return _generate_rule(df)


def _generate_rule(df):
    cols = set(df.columns)
    lines = ["### 🔎 AI 数据解读（基础规则）"]
    lines.append("")
    lines.append(f"- 记录数：**{len(df):,}**")

    if {"有效业绩", "奖金金额"}.issubset(cols):
        total_eff = float(df["有效业绩"].sum())
        total_bonus = float(df["奖金金额"].sum())
        avg_bonus = float(df["奖金金额"].mean())
        lines.append(f"- 总有效业绩：**¥{total_eff:,.2f}**")
        lines.append(f"- 总奖金金额：**¥{total_bonus:,.2f}**（人均 ¥{avg_bonus:,.2f}）")

        top = df.sort_values("奖金金额", ascending=False).head(3)
        items = []
        for _, r in top.iterrows():
            who = r.get("销售人员", "未知")
            bonus = float(r.get("奖金金额", 0.0))
            eff = float(r.get("有效业绩", 0.0))
            items.append(f"{who}（奖金 ¥{bonus:,.2f} / 有效业绩 ¥{eff:,.2f}）")
        if items:
            lines.append(f"- Top3：{'; '.join(items)}")

    return "\n".join(lines)


def _generate_llm(df, api_key, custom_prompt=None, model=None, provider=None):
    from src.llm_client import chat_complete
    model_name = model or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"


    cols = set(df.columns)
    summary = {"rows": len(df), "columns": list(df.columns)}

    if {"有效业绩", "奖金金额"}.issubset(cols):
        top3 = []
        for r in df.sort_values("奖金金额", ascending=False).head(3).to_dict(orient="records"):
            clean = {}
            for k, v in r.items():
                if hasattr(v, "item"):
                    try:
                        v = v.item()
                    except Exception:
                        v = str(v)
                if getattr(v, "isoformat", None) is not None and not isinstance(v, (str, int, float, bool)):
                    try:
                        v = v.isoformat()
                    except Exception:
                        v = str(v)
                if isinstance(v, float) and (v != v):
                    v = None
                clean[str(k)] = v
            top3.append(clean)

        summary.update(
            {
                "total_effective_sales": float(df["有效业绩"].sum()),
                "total_bonus": float(df["奖金金额"].sum()),
                "avg_bonus": float(df["奖金金额"].mean()),
                "top3": top3,
            }
        )

    system_prompt = (
        "你是一名企业销售激励与奖金核算的资深分析师。"
        "请根据提供的数据摘要，输出一份可给管理层阅读的解读报告，包含："
        "1) 总体规模与分布特点；2) Top/Bottom 现象；3) 异常/风险提示；4) 可执行建议。"
        "使用中文 Markdown，语气专业克制。"
    )

    user_content = f"数据摘要(JSON): {json.dumps(summary, ensure_ascii=False, default=str)}"
    if custom_prompt:
        user_content += f"\n\n用户关注点: {custom_prompt}"

    use_provider = provider or os.environ.get("LLM_PROVIDER") or "openai"
    return chat_complete(
        provider=use_provider,
        api_key=api_key,
        model=model_name,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
    )
