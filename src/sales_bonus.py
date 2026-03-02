from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def generate_sales_transactions(rows=5000, seed=7):
    rng = np.random.default_rng(seed)
    sellers = ["张三", "李四", "王五", "赵六", "孙七", "周八", "吴九", "郑十", "钱十一", "冯十二", "杨四四", "黄三三"]
    dept_map = {
        "张三": "华东区",
        "李四": "华北区",
        "王五": "华南区",
        "赵六": "华东区",
        "孙七": "西南区",
        "周八": "华北区",
        "吴九": "华南区",
        "郑十": "西北区",
        "钱十一": "东北区",
        "冯十二": "华中区",
        "杨四四": "华东区",
        "黄三三": "华南区",
    }
    regions = ["上海", "北京", "深圳", "杭州", "成都", "广州", "天津", "南京", "大连", "苏州", "厦门", "西安"]
    products = ["产品A", "产品B", "产品C", "产品D", "产品E"]
    customers = [f"客户{idx:03d}" for idx in range(1, 401)]

    start = datetime.now() - timedelta(days=120)
    dates = [start + timedelta(days=int(x)) for x in rng.integers(0, 120, size=rows)]

    seller_choices = rng.choice(sellers, size=rows, replace=True)
    dept_choices = [dept_map.get(s, "未知") for s in seller_choices]
    region_choices = rng.choice(regions, size=rows, replace=True)
    customer_choices = rng.choice(customers, size=rows, replace=True)
    product_choices = rng.choice(products, size=rows, replace=True, p=[0.28, 0.25, 0.2, 0.15, 0.12])

    amount = rng.gamma(shape=3.0, scale=8000.0, size=rows)
    amount = np.maximum(500.0, amount)
    amount = np.round(amount, 2)

    df = pd.DataFrame(
        {
            "销售人员": seller_choices,
            "部门": dept_choices,
            "区域": region_choices,
            "客户名称": customer_choices,
            "产品名称": product_choices,
            "消费金额": amount,
            "交易日期": pd.to_datetime(dates),
        }
    )
    return df


def default_product_coefficients():
    return {"产品A": 1.0, "产品B": 0.9, "产品C": 0.8, "产品D": 0.7, "产品E": 0.6}


def apply_product_coefficients(df, product_coeffs):
    coeff = df["产品名称"].map(product_coeffs).fillna(1.0).astype(float)
    out = df.copy()
    out["产品系数"] = coeff
    out["有效业绩"] = (out["消费金额"].astype(float) * out["产品系数"]).round(2)
    return out


def summarize_sales_bonus(df_effective, bonus_rate=0.08):
    g = (
        df_effective.groupby(["销售人员", "部门", "区域"], as_index=False)
        .agg(总营收=("消费金额", "sum"), 有效业绩=("有效业绩", "sum"))
        .sort_values("有效业绩", ascending=False)
    )
    g["奖金比例"] = float(bonus_rate)
    g["奖金金额"] = (g["有效业绩"] * g["奖金比例"]).round(2)
    return g
