import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def plot_department_distribution(df):
    """Pie chart of bonus distribution by department."""
    dept_bonus = df.groupby('部门')['预估奖金'].sum().reset_index()
    fig = px.pie(dept_bonus, values='预估奖金', names='部门', title='各部门奖金分布')
    st.plotly_chart(fig, use_container_width=True)

def plot_performance_distribution(df):
    """Bar chart of employee count and bonus by performance rating."""
    perf_stats = df.groupby('绩效评分').agg({'员工ID': 'count', '预估奖金': 'sum'}).reset_index()
    perf_stats.columns = ['绩效评分', '人数', '奖金总额']
    
    # Order S, A, B, C, D
    order = ['S', 'A', 'B', 'C', 'D']
    # Filter order to only include present ratings
    present_order = [x for x in order if x in perf_stats['绩效评分'].unique()]
    
    perf_stats['绩效评分'] = pd.Categorical(perf_stats['绩效评分'], categories=present_order, ordered=True)
    perf_stats = perf_stats.sort_values('绩效评分')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=perf_stats['绩效评分'], y=perf_stats['人数'], name='人数', yaxis='y'))
    fig.add_trace(go.Scatter(x=perf_stats['绩效评分'], y=perf_stats['奖金总额'], name='奖金总额', yaxis='y2', mode='lines+markers'))
    
    fig.update_layout(
        title='绩效等级分布 (人数 vs 奖金)',
        yaxis=dict(title='人数'),
        yaxis2=dict(title='奖金总额', overlaying='y', side='right'),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_salary_vs_bonus(df):
    """Scatter plot."""
    fig = px.scatter(df, x='当前薪资', y='预估奖金', color='绩效评分', 
                     hover_data=['姓名', '部门', '职级'],
                     title='薪资 vs 奖金散点图')
    st.plotly_chart(fig, use_container_width=True)
