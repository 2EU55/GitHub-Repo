import pandas as pd
import streamlit as st

def calculate_bonus(df, total_bonus_pool, weights):
    """
    Calculate bonus based on salary and performance rating.
    """
    if df is None or df.empty:
        return df
    
    # Create a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Map weights
    df['绩效系数'] = df['绩效评分'].map(weights).fillna(0)
    
    # Calculate weighted score
    df['综合得分'] = df['当前薪资'] * df['绩效系数']
    
    # Calculate total score
    total_score = df['综合得分'].sum()
    
    if total_score == 0:
        df['预估奖金'] = 0
        df['奖金占比'] = 0
    else:
        df['预估奖金'] = (df['综合得分'] / total_score) * total_bonus_pool
        df['奖金占比'] = df['预估奖金'] / total_bonus_pool
        
    # Rounding
    df['预估奖金'] = df['预估奖金'].round(2)
    df['奖金占比'] = df['奖金占比'].round(4)
    
    return df

def check_forced_distribution(df, s_limit=0.20, sa_limit=0.40):
    """
    Check if the performance distribution meets the forced distribution requirements.
    Returns a list of warning messages.
    """
    if df is None or df.empty:
        return []
        
    total_count = len(df)
    s_count = len(df[df['绩效评分'] == 'S'])
    a_count = len(df[df['绩效评分'] == 'A'])
    
    s_ratio = s_count / total_count
    a_ratio = a_count / total_count
    
    warnings = []
    
    if s_ratio > s_limit:
        reduce_count = max(0, s_count - int(total_count * s_limit))
        warnings.append(f"⚠️ **S 级预警**: 当前占比 {s_ratio:.1%} (上限 {s_limit:.0%})，建议减少 {reduce_count} 人。")
        
    sa_ratio = s_ratio + a_ratio
    if sa_ratio > sa_limit:
        warnings.append(f"⚠️ **S+A 级预警**: 当前合计占比 {sa_ratio:.1%} (上限 {sa_limit:.0%})，高绩效比例过高。")
        
    return warnings

def check_department_budget(df, department_budgets):
    """
    Check if department bonuses exceed their budgets.
    department_budgets: dict {dept_name: budget_amount}
    """
    if df is None or df.empty or not department_budgets:
        return []
        
    dept_bonus = df.groupby('部门')['预估奖金'].sum()
    warnings = []
    
    for dept, budget in department_budgets.items():
        if dept in dept_bonus:
            actual = dept_bonus[dept]
            if budget is None:
                continue
            if budget <= 0 and actual > 0:
                warnings.append(f"💸 **部门超支**: {dept} 实际分配 ¥{actual:,.0f} > 预算 ¥0 (超支：预算为 0)")
            elif actual > budget:
                warnings.append(f"💸 **部门超支**: {dept} 实际分配 ¥{actual:,.0f} > 预算 ¥{budget:,.0f} (超支 {actual/budget - 1:.1%})")
                
    return warnings
