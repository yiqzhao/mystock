import streamlit as st
import pandas as pd
import akshare as ak
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="股票行情数据",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加股票选择功能
st.sidebar.subheader("股票选择")

# 股票类型选择
stock_type = st.sidebar.radio(
    "选择股票类型",
    ["指数", ""]
)

# 股票代码输入
stock_code = st.sidebar.text_input(
    "输入股票代码",
    value="sh000001" if stock_type == "指数" else "sz000001",
    placeholder="如: sh000001 或 sz000001"
)

# 添加快捷选择按钮
st.sidebar.subheader("快捷选择")
col1, col2 = st.sidebar.columns(2)
if stock_type == "指数":
    if col1.button("上证指数"):
        stock_code = "sh000001"
    if col2.button("深证成指"):
        stock_code = "sz399001"
    if col1.button("创业板指"):
        stock_code = "sz399006"
    if col2.button("科创板指"):
        stock_code = "sh000688"
else:
    if col1.button("平安银行"):
        stock_code = "sz000001"
    if col2.button("贵州茅台"):
        stock_code = "sh600519"
    if col1.button("腾讯控股"):
        stock_code = "hk00700"
    if col2.button("阿里巴巴"):
        stock_code = "usBABA"

# 添加标题和说明
st.title(f"{stock_code} 历史行情数据")
st.markdown("本应用展示股票的历史行情数据，包括开盘价、收盘价、最高价、最低价和成交量等信息")

# 获取股票的历史行情数据
try:
    with st.spinner("正在获取数据..."):
        if stock_type == "指数":
            stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol=stock_code)
        else:
            stock_zh_index_daily_df = ak.stock_zh_a_hist(symbol=stock_code, adjust="qfq")
    
    # 数据预处理
    if not stock_zh_index_daily_df.empty:
        # 检查是否需要处理列名
        if 'open' in stock_zh_index_daily_df.columns:
            # 重命名列名以便更好地理解
            stock_zh_index_daily_df = stock_zh_index_daily_df.rename(columns={
                'open': '开盘价',
                'close': '收盘价',
                'high': '最高价',
                'low': '最低价',
                'volume': '成交量'
            })
        
        # 检查是否已经有date列
        if 'date' not in stock_zh_index_daily_df.columns:
            # 处理日期索引 - 检查并转换为datetime类型
            if not pd.api.types.is_datetime64_any_dtype(stock_zh_index_daily_df.index):
                try:
                    # 尝试将索引转换为datetime类型
                    stock_zh_index_daily_df.index = pd.to_datetime(stock_zh_index_daily_df.index, format='%Y%m%d')
                except Exception as e:
                    st.warning(f"无法将索引转换为日期格式: {e}")
                    # 如果转换失败，我们仍然可以继续使用原始索引
            
            # 将日期索引转换为数据列
            stock_zh_index_daily_df = stock_zh_index_daily_df.reset_index()
            stock_zh_index_daily_df.rename(columns={'index': 'date'}, inplace=True)
        else:
            # 确保date列是datetime类型
            try:
                stock_zh_index_daily_df['date'] = pd.to_datetime(stock_zh_index_daily_df['date'])
            except Exception as e:
                st.warning(f"无法将date列转换为日期格式: {e}")
        
        # 显示数据基本信息
        st.subheader("数据基本信息")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("数据总量", len(stock_zh_index_daily_df))
        
        # 安全地从date列获取起始和结束日期
        try:
            start_date = stock_zh_index_daily_df['date'].min().strftime("%Y-%m-%d")
        except AttributeError:
            start_date = str(stock_zh_index_daily_df['date'].min())
            
        try:
            end_date = stock_zh_index_daily_df['date'].max().strftime("%Y-%m-%d")
        except AttributeError:
            end_date = str(stock_zh_index_daily_df['date'].max())
        
        col2.metric("起始日期", start_date)
        col3.metric("结束日期", end_date)
        col4.metric("最新收盘价", f"{stock_zh_index_daily_df['收盘价'].iloc[-1]:.2f}")
        
        # 显示数据表格
        st.subheader("历史行情数据")
        st.dataframe(stock_zh_index_daily_df, use_container_width=True)
        
        # 显示数据统计信息
        st.subheader("数据统计摘要")
        st.dataframe(stock_zh_index_daily_df.describe(), use_container_width=True)
        
        # 绘制价格走势图 (Plotly交互式图表)
        st.subheader("价格走势")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=stock_zh_index_daily_df['date'], y=stock_zh_index_daily_df['收盘价'], 
                               name='收盘价', line=dict(color='blue'), mode='lines'))
        fig1.add_trace(go.Scatter(x=stock_zh_index_daily_df['date'], y=stock_zh_index_daily_df['开盘价'], 
                               name='开盘价', line=dict(color='green', width=1), mode='lines'))
        fig1.update_layout(title=f'{stock_code} 价格走势',
                          xaxis_title='日期',
                          yaxis_title='价格',
                          xaxis_rangeslider_visible=True,
                          hovermode='x unified',
                          legend=dict(x=0, y=1),
                          height=600)
        st.plotly_chart(fig1, use_container_width=True)
        
        # 绘制成交量图 (Plotly交互式图表)
        st.subheader("成交量变化")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=stock_zh_index_daily_df['date'], y=stock_zh_index_daily_df['成交量'], 
                            name='成交量', marker=dict(color='orange')))
        fig2.update_layout(title=f'{stock_code} 成交量变化',
                          xaxis_title='日期',
                          yaxis_title='成交量',
                          xaxis_rangeslider_visible=True,
                          hovermode='x unified',
                          legend=dict(x=0, y=1),
                          height=600)
        st.plotly_chart(fig2, use_container_width=True)
        
        # 绘制价格范围图 (Plotly交互式图表)
        st.subheader("价格范围")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=stock_zh_index_daily_df['date'], y=stock_zh_index_daily_df['最高价'], 
                               name='最高价', line=dict(color='red', width=1), mode='lines'))
        fig3.add_trace(go.Scatter(x=stock_zh_index_daily_df['date'], y=stock_zh_index_daily_df['最低价'], 
                               name='最低价', line=dict(color='blue', width=1), mode='lines'))
        fig3.add_trace(go.Scatter(x=stock_zh_index_daily_df['date'], y=stock_zh_index_daily_df['收盘价'], 
                               name='收盘价', line=dict(color='green', width=2), mode='lines'))
        fig3.update_layout(title=f'{stock_code} 价格范围',
                          xaxis_title='日期',
                          yaxis_title='价格',
                          xaxis_rangeslider_visible=True,
                          hovermode='x unified',
                          legend=dict(x=0, y=1),
                          height=600)
        st.plotly_chart(fig3, use_container_width=True)
        
        # 数据下载功能
        st.subheader("数据下载")
        # 使用utf-8-sig编码解决中文乱码问题，Excel可正确识别
        csv = stock_zh_index_daily_df.to_csv(encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="下载CSV文件",
            data=csv,
            file_name=f"{stock_code}_历史数据_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
    else:
        st.error("未能获取到数据，请检查网络连接或稍后重试")
        
except Exception as e:
    st.error(f"获取数据时发生错误: {e}")
    st.info("如果遇到限流问题，可能需要添加重试机制或等待一段时间后再次尝试")
    st.info("请检查AKShare库是否正确安装: pip install akshare -U")
    st.info("请确保输入的股票代码格式正确，例如：sh000001 或 sz000001")

# 更新使用说明
with st.sidebar:
    st.markdown("---")
    st.subheader("使用说明")
    st.markdown("- 本应用使用AKShare库获取股票历史数据")
    st.markdown("- 支持指数和A股股票查询")
    st.markdown("- 可手动输入股票代码或使用快捷选择")
    st.markdown("- 数据包括开盘价、收盘价、最高价、最低价和成交量")
    st.markdown("- 可通过图表直观查看价格走势和成交量变化")
    st.markdown("- 图表支持鼠标悬停显示数据、缩放和平移功能")
    st.markdown("- 支持将数据下载为CSV文件")
    st.markdown("---")
    st.markdown("**更新时间:**")
    st.markdown(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))