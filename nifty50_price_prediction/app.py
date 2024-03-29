import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd

# Set date range for data retrieval
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd

# Set date range for data retrieval
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Page title and description
st.title("Nifty 50 Stocks Price Prediction App")
st.sidebar.markdown(
    """
    ## Search Stock
    Use the search bar to find and select a stock.
    """
)

# Create a list of stock symbols for auto-suggestions
stocks = ["^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "INFY.NS", "ITC.NS",
          "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "LT.NS", "KOTAKBANK.NS", "ASIANPAINT.NS", "HCLTECH.NS",
          "AXISBANK.NS", "ADANIENT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "BAJAJFINSV.NS", "ULTRACEMCO.NS",
          "ONGC.NS", "NESTLEIND.NS", "WIPRO.NS", "NTPC.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "M&M.NS", "POWERGRID.NS",
          "ADANIPORTS.NS", "LTIM.NS", "TATASTEEL.NS", "COALINDIA.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS",
          "GRASIM.NS", "BRITANNIA.NS", "TECHM.NS", "INDUSINDBK.NS", "HINDALCO.NS", "DIVISLAB.NS", "CIPLA.NS", "RDY",
          "EICHERMOT.NS", "BPCL.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "HEROMOTOCO.NS", "UPL.NS"]

# Search bar for selecting stocks with auto-suggestions in the sidebar
search_query = st.sidebar.selectbox("Search Stock", stocks, index=0)

# Load data function with caching
@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data

# Display data loading message
data_load_state = st.text("Loading data...")
data = load_data(search_query)
data_load_state.text("Loading data...done!")

# Display raw data table
st.subheader("Raw Data")
st.write(data.tail())

# Interactive plot function with MACD and Buy/Sell signals
def plot_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='Open Price', line=dict(color='royalblue')))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close Price', line=dict(color='green')))

    # Calculate MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()

    fig.add_trace(go.Scatter(x=data['Date'], y=macd, name='MACD', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data['Date'], y=signal, name='Signal', line=dict(color='red')))

    # Buy and Sell signals
    buy_signal = ((macd > signal) & (macd.shift(1) < signal.shift(1)))
    sell_signal = ((macd < signal) & (macd.shift(1) > signal.shift(1)))
    fig.add_trace(go.Scatter(x=data['Date'][buy_signal], y=data['Close'][buy_signal], 
                             mode='markers', marker=dict(color='green', size=10), name='Buy Signal'))
    fig.add_trace(go.Scatter(x=data['Date'][sell_signal], y=data['Close'][sell_signal], 
                             mode='markers', marker=dict(color='red', size=10), name='Sell Signal'))

    fig.update_layout(title="Stock Price Analysis with MACD",
                      xaxis_title="Date",
                      yaxis_title="Price",
                      xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

# Display interactive plot
st.subheader("Stock Price Analysis")
plot_data()

# Prophet forecasting
df_train = data[['Date', 'Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

n_months = st.slider("Months of Prediction", 1, 12)
period = n_months * 30

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

# Display forecast data table
st.subheader("Forecast Data")
st.write(forecast.tail())

# Plot forecast and components
st.subheader("Forecast Plots")
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

st.subheader("Forecast Components")
fig2 = m.plot_components(forecast)
st.write(fig2)

# Footer image
st.image("footer.png", use_column_width=True)

# Analysis function to suggest top 10 stocks to buy or sell
def analyze_stocks(all_stocks_data):
    analysis_results = {}
    for stock, data in all_stocks_data.items():
        close_prices = data['Close']
        if len(close_prices) >= 31:  # Minimum data required for analysis (30 days + current day)
            last_price = close_prices.iloc[-1]  # Use iloc for integer indexing
            thirty_day_avg = close_prices.iloc[-31:-1].mean()  # Exclude current day from average
            analysis_results[stock] = "Buy" if last_price > thirty_day_avg else "Sell"
        else:
            analysis_results[stock] = "Insufficient data for analysis"

    return analysis_results


# Analyze all stocks
all_stocks_data = {}
for stock_symbol in stocks:
    all_stocks_data[stock_symbol] = load_data(stock_symbol)

# Analyze and suggest top 10 stocks to buy or sell
analysis_results = analyze_stocks(all_stocks_data)
sorted_analysis = sorted(analysis_results.items(), key=lambda x: x[1], reverse=True)

top_10_stocks = dict(sorted_analysis)
df = pd.DataFrame(top_10_stocks.items(), columns=['Stock', 'Recommendation'])
buy_df = df[(df['Recommendation'] == 'Buy')]
sell_df = df[(df['Recommendation'] == 'Sell')]


buy_df = buy_df.reset_index(drop=True)
buy_df.index += 1  

sell_df = sell_df.reset_index(drop=True)
sell_df.index += 1  
# Display top 10 stocks to buy or sell in the sidebar
st.sidebar.subheader("Buy recommended Stocks")
st.sidebar.table(buy_df.head(5))


st.sidebar.subheader("Sell recommended Stocks")
st.sidebar.table(sell_df.head(5))

