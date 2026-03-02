import pandas as pd


REQUIRED_COLUMNS = ["员工ID", "姓名", "部门", "职级", "当前薪资", "绩效评分"]
PERFORMANCE_VALUES = ["S", "A", "B", "C", "D"]


def normalize_performance(value):
    if pd.isna(value):
        return None
    v = str(value).strip().upper()
    mapping = {
        "优秀": "A",
        "良好": "B",
        "合格": "C",
        "需改进": "D",
        "卓越": "S",
    }
    v = mapping.get(v, v)
    if v in PERFORMANCE_VALUES:
        return v
    return None


def build_standard_df(raw_df, mapping):
    df = pd.DataFrame()
    for target_col in REQUIRED_COLUMNS:
        source_col = mapping.get(target_col)
        if source_col and source_col in raw_df.columns:
            df[target_col] = raw_df[source_col]
        else:
            df[target_col] = None

    if df["员工ID"].isna().all():
        df["员工ID"] = [f"E{1000+i}" for i in range(len(df))]
    else:
        df["员工ID"] = df["员工ID"].astype(str)
        mask = df["员工ID"].isna() | (df["员工ID"].str.strip() == "")
        if mask.any():
            df.loc[mask, "员工ID"] = [f"E{1000+i}" for i in range(mask.sum())]

    if df["姓名"].isna().all():
        df["姓名"] = df["员工ID"]
    else:
        df["姓名"] = df["姓名"].fillna(df["员工ID"]).astype(str)

    df["部门"] = df["部门"].fillna("未知").astype(str)
    df["职级"] = df["职级"].fillna("未知").astype(str)

    df["当前薪资"] = pd.to_numeric(df["当前薪资"], errors="coerce").fillna(0).astype(float)
    df["绩效评分"] = df["绩效评分"].apply(normalize_performance).fillna("B")

    return df


def validate_df(df):
    errors = []
    warnings = []

    if df is None or df.empty:
        errors.append("数据为空")
        return {"errors": errors, "warnings": warnings}

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            errors.append(f"缺少必填列：{col}")

    if errors:
        return {"errors": errors, "warnings": warnings}

    if df["员工ID"].isna().any():
        errors.append("员工ID 存在空值")

    dup = df["员工ID"].astype(str).duplicated()
    if dup.any():
        warnings.append(f"员工ID 存在重复：{dup.sum()} 条")

    invalid_salary = pd.to_numeric(df["当前薪资"], errors="coerce").isna()
    if invalid_salary.any():
        warnings.append(f"当前薪资存在无法解析为数字：{invalid_salary.sum()} 条")

    invalid_perf = ~df["绩效评分"].astype(str).str.upper().isin(PERFORMANCE_VALUES)
    if invalid_perf.any():
        warnings.append(f"绩效评分存在非 S/A/B/C/D：{invalid_perf.sum()} 条")

    if (pd.to_numeric(df["当前薪资"], errors="coerce").fillna(0) < 0).any():
        warnings.append("当前薪资存在负数")

    return {"errors": errors, "warnings": warnings}


def suggest_mapping(columns):
    cols = list(columns)
    lower = {c: str(c).lower() for c in cols}

    def pick(*needles):
        for c in cols:
            if any(n in lower[c] for n in needles):
                return c
        return None

    return {
        "员工ID": pick("员工id", "id", "工号"),
        "姓名": pick("姓名", "name"),
        "部门": pick("部门", "dept", "department"),
        "职级": pick("职级", "级别", "level", "title"),
        "当前薪资": pick("薪资", "工资", "salary", "base"),
        "绩效评分": pick("绩效", "评分", "rating", "perf"),
    }
