import os


def chat_complete(provider, api_key, model, messages):
    from openai import OpenAI

    if not api_key:
        raise ValueError("API Key 不能为空")

    p = (provider or "").strip().lower()
    if p in ("硅基流动", "siliconflow", "sf"):
        base_url = os.environ.get("SILICONFLOW_BASE_URL") or "https://api.siliconflow.cn/v1"
    else:
        base_url = os.environ.get("OPENAI_BASE_URL") or None

    timeout_s = float(os.environ.get("LLM_TIMEOUT_SECONDS") or 30.0)
    max_retries = int(os.environ.get("LLM_MAX_RETRIES") or 1)
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_s, max_retries=max_retries)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
    )
    return resp.choices[0].message.content
