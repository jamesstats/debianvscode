import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. App Configuration
st.set_page_config(page_title="Portfolio Cumulative Returns", layout="wide")
st.title("💼 Custom Portfolio Cumulative Returns Tracker")
st.markdown("Input your exact holdings to calculate your true weighted portfolio returns over time.")

# 2. Sidebar: Transaction Ledger using Streamlit's Data Editor
st.sidebar.header("1. Your Portfolio Holdings")
st.sidebar.markdown("Edit the table below with your tickers, shares, and average buy price:")

# Default sample portfolio data
default_portfolio = pd.DataFrame([
    {"Ticker": "PLTR", "Shares": 1000.0, "Avg Cost Basis": 8.0},
    {"Ticker": "NVDA", "Shares": 100.0, "Avg Cost Basis": 99.0},
    {"Ticker": "HOOD", "Shares": 1500.0, "Avg Cost Basis": 15.0},
    {"Ticker": "MU", "Shares": 100.0, "Avg Cost Basis": 109.0},
    {"Ticker": "TSLA", "Shares": 100.0, "Avg Cost Basis": 164.0},
    {"Ticker": "META", "Shares": 100.0, "Avg Cost Basis": 99.0} ,
    {"Ticker": "CVNA", "Shares": 3500.0, "Avg Cost Basis": 3.0},
])

# Create an interactive, editable table in the sidebar
edited_portfolio = st.sidebar.data_editor(
    default_portfolio, 
    num_rows="dynamic", 
    use_container_width=True
)

# Clean up input data
edited_portfolio['Ticker'] = edited_portfolio['Ticker'].str.strip().str.upper()
edited_portfolio = edited_portfolio.dropna(subset=['Ticker'])
tickers = edited_portfolio['Ticker'].tolist()

# Date range picker for tracking timeline
st.sidebar.header("2. Timeline Settings")
start_date = st.sidebar.date_input("Start Date for Chart", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

# 3. Fetch Historical Data
@st.cache_data
def load_historical_data(ticker_list, start, end):
    if not ticker_list:
        return None

    raw_data = yf.download(ticker_list, start=start, end=end, progress=False)
    if raw_data is None or raw_data.empty:
        return None

    if isinstance(raw_data.columns, pd.MultiIndex):
        if 'Adj Close' in raw_data.columns.get_level_values(0):
            return raw_data.loc[:, 'Adj Close']
        if 'Close' in raw_data.columns.get_level_values(0):
            return raw_data.loc[:, 'Close']
    else:
        if 'Adj Close' in raw_data.columns:
            return raw_data['Adj Close']
        if 'Close' in raw_data.columns:
            return raw_data['Close']

    return None

if tickers:
    historical_prices = load_historical_data(tickers, start_date, end_date)
    
    if historical_prices is not None and not historical_prices.empty:
        # Normalize to DataFrame if only one ticker is present
        if isinstance(historical_prices, pd.Series):
            historical_prices = historical_prices.to_frame(name=tickers[0])
            
        historical_prices = historical_prices.dropna(how='all')

        # 4. CRITICAL MATH: Calculate Weighted Portfolio Value Over Time
        # Calculate total initial cash investment (Total Cost Basis)
        edited_portfolio['Total Cost'] = edited_portfolio['Shares'] * edited_portfolio['Avg Cost Basis']
        total_initial_investment = edited_portfolio['Total Cost'].sum()

        # Map shares to a dictionary for easy multiplication
        share_dict = dict(zip(edited_portfolio['Ticker'], edited_portfolio['Shares']))
        
        # Calculate daily portfolio dollar value: Sum of (Daily Price * Shares) for each asset
        daily_portfolio_value = pd.Series(0.0, index=historical_prices.index)
        for ticker in tickers:
            if ticker in historical_prices.columns:
                daily_portfolio_value += historical_prices[ticker] * share_dict[ticker]
        
        # Calculate portfolio cumulative return over time relative to your initial investment
        portfolio_cumulative_return = ((daily_portfolio_value / total_initial_investment) - 1) * 100
        
        # Current Metrics
        current_portfolio_value = daily_portfolio_value.iloc[-1]
        total_profit_loss = current_portfolio_value - total_initial_investment
        total_cumulative_pct = portfolio_cumulative_return.iloc[-1]

        # 5. Dashboard UI Layout
        # KPI Summary Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Investment", f"${total_initial_investment:,.2f}")
        col2.metric("Current Value", f"${current_portfolio_value:,.2f}")
        col3.metric(
            "Cumulative Return (%)", 
            f"{total_cumulative_pct:.2f}%", 
            delta=f"${total_profit_loss:,.2f} Total PnL"
        )

        st.markdown("---")

        # Layout Split: Main Chart on Left, Allocation Breakdown on Right
        chart_col, side_col = st.columns([2, 1])

        with chart_col:
            st.subheader("Total Portfolio Cumulative Return Timeline")
            
            # Prepare data for plotting
            df_plot = portfolio_cumulative_return.reset_index()
            df_plot.columns = ['Date', 'Cumulative Return (%)']
            
            fig_line = px.line(
                df_plot, 
                x='Date', 
                y='Cumulative Return (%)',
                title="Your Combined Portfolio Growth (%)",
                template="plotly_dark"
            )
            fig_line.update_layout(hovermode="x unified")
            fig_line.update_traces(line=dict(color="#00FFCC", width=3))
            st.plotly_chart(fig_line, use_container_width=True)

        with side_col:
            st.subheader("Current Portfolio Allocation")
            
            # Calculate current value distribution for the pie chart
            current_values = []
            for ticker in tickers:
                if ticker in historical_prices.columns:
                    current_values.append(historical_prices[ticker].iloc[-1] * share_dict[ticker])
                else:
                    current_values.append(0)
            
            df_alloc = pd.DataFrame({
                "Ticker": tickers,
                "Current Value": current_values
            })
            
            fig_pie = px.pie(
                df_alloc, 
                values='Current Value', 
                names='Ticker', 
                hole=0.4,
                template="plotly_dark",
                color_discrete_sequence=px.colors.sequential.Mint
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.error("Could not fetch data for those tickers. Please verify ticker spelling.")
else:
    st.info("Add some stocks in the sidebar table to see your dashboard generate!") 
        
       
           