import pandas as pd


SALES_REQUIRED_COLUMNS = [
    "销售人员",
    "部门",
    "区域",
    "客户名称",
    "产品名称",
    "消费金额",
    "交易日期",
]


def _normalize_text(v, default=None):
    if pd.isna(v):
        return default
    s = str(v).strip()
    return s if s else default


def _to_amount(v):
    if pd.isna(v):
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "")
    s = s.replace("¥", "").replace("￥", "")
    x = pd.to_numeric(s, errors="coerce")
    if pd.isna(x):
        return 0.0
    return float(x)


def _to_date(v):
    dt = pd.to_datetime(v, errors="coerce")
    return dt


def suggest_sales_mapping(columns):
    cols = list(columns)
    lower = {c: str(c).lower() for c in cols}

    def pick(*needles):
        for c in cols:
            if any(n in lower[c] for n in needles):
                return c
        return None

    return {
        "销售人员": pick("销售", "seller", "salesperson", "owner", "人员"),
        "部门": pick("部门", "dept", "department"),
        "区域": pick("区域", "region", "area", "城市"),
        "客户名称": pick("客户", "customer", "client"),
        "产品名称": pick("产品", "product", "sku"),
        "消费金额": pick("金额", "消费", "营收", "revenue", "amount", "gmv"),
        "交易日期": pick("日期", "时间", "date", "time"),
    }


def build_sales_df(raw_df, mapping):
    df = pd.DataFrame()
    for target in SALES_REQUIRED_COLUMNS:
        source = mapping.get(target)
        if source and source in raw_df.columns:
            df[target] = raw_df[source]
        else:
            df[target] = None

    df["销售人员"] = df["销售人员"].apply(lambda x: _normalize_text(x, "未知销售"))
    df["部门"] = df["部门"].apply(lambda x: _normalize_text(x, "未知部门"))
    df["区域"] = df["区域"].apply(lambda x: _normalize_text(x, "未知区域"))
    df["客户名称"] = df["客户名称"].apply(lambda x: _normalize_text(x, "未知客户"))
    df["产品名称"] = df["产品名称"].apply(lambda x: _normalize_text(x, "未知产品"))
    df["消费金额"] = df["消费金额"].apply(_to_amount).astype(float)
    df["交易日期"] = df["交易日期"].apply(_to_date)
    return df


def validate_sales_df(df):
    errors = []
    warnings = []

    if df is None or df.empty:
        errors.append("数据为空")
        return {"errors": errors, "warnings": warnings}

    for col in SALES_REQUIRED_COLUMNS:
        if col not in df.columns:
            errors.append(f"缺少必填列：{col}")

    if errors:
        return {"errors": errors, "warnings": warnings}

    if df["交易日期"].isna().any():
        warnings.append(f"交易日期存在无法解析：{df['交易日期'].isna().sum()} 条")

    if (df["消费金额"] < 0).any():
        warnings.append("消费金额存在负数")

    if (df["消费金额"] == 0).any():
        warnings.append(f"消费金额为 0 的记录：{(df['消费金额'] == 0).sum()} 条")

    return {"errors": errors, "warnings": warnings}
