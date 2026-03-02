import pandas as pd
import numpy as np
import streamlit as st

def generate_sample_data(num_employees=50):
    """Generate sample employee data."""
    departments = ['研发部', '销售部', '市场部', '人力资源部', '财务部']
    levels = ['初级', '中级', '高级', '资深', '总监']
    performance_ratings = ['S', 'A', 'B', 'C', 'D']
    
    data = []
    for i in range(num_employees):
        dept = np.random.choice(departments)
        level = np.random.choice(levels, p=[0.3, 0.4, 0.2, 0.08, 0.02])
        rating = np.random.choice(performance_ratings, p=[0.1, 0.2, 0.5, 0.15, 0.05])
        
        # Base salary logic
        base_salary_map = {
            '初级': (8000, 15000),
            '中级': (15000, 25000),
            '高级': (25000, 40000),
            '资深': (40000, 60000),
            '总监': (60000, 100000)
        }
        min_s, max_s = base_salary_map[level]
        salary = np.random.randint(min_s, max_s)
        
        data.append({
            '员工ID': f'E{1000+i}',
            '姓名': f'员工_{i+1}',
            '部门': dept,
            '职级': level,
            '当前薪资': salary,
            '绩效评分': rating
        })
        
    return pd.DataFrame(data)

def load_data(uploaded_file):
    """Load data from CSV or Excel."""
    if uploaded_file is None:
        return None
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None
