import streamlit as st
from datetime import date

import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

stock_market_emoji = "\U0001F4C8"
st.header(f"Nifty 50 Stocks Price Prediction App {stock_market_emoji}")
st.image("stock_market.png", width=700)
stocks = ("^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "INFY.NS", "ITC.NS", "SBIN.NS",
          "BHARTIARTL.NS", "BAJFINANCE.NS", "LT.NS", "KOTAKBANK.NS", "ASIANPAINT.NS", "HCLTECH.NS", "AXISBANK.NS",
          "ADANIENT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "BAJAJFINSV.NS", "ULTRACEMCO.NS", "ONGC.NS",
          "NESTLEIND.NS", "WIPRO.NS", "NTPC.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "M&M.NS", "POWERGRID.NS", "ADANIPORTS.NS",
          "LTIM.NS", "TATASTEEL.NS", "COALINDIA.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS", "GRASIM.NS",
          "BRITANNIA.NS", "TECHM.NS", "INDUSINDBK.NS", "HINDALCO.NS", "DIVISLAB.NS", "CIPLA.NS", "RDY", "EICHERMOT.NS",
          "BPCL.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "HEROMOTOCO.NS", "UPL.NS")
st.sidebar.image("nifty_50.png")
selected_stock = st.sidebar.selectbox("Select dataset for prediction", stocks)

n_months = st.slider("Months of prediction:", 1,12)
period = n_months * 30


@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data


data_load_state = st.text("load data...")
data = load_data(selected_stock)
data_load_state.text("Loading data...done!")

st.subheader("Raw data")
st.write(data.tail())


def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
    fig.layout.update(title_text = "Time Series Data", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


plot_raw_data()

def ma_data():
    mafig = go.Figure()
    ma100 = data.Close.rolling(50).mean()
    ma50 = data.Close.rolling(200).mean()
    mafig.add_trace(go.Scatter(x=data['Date'], y=ma100, name='50 Days MA'))
    mafig.add_trace(go.Scatter(x=data['Date'], y=ma50, name='200 Days MA'))
    mafig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
    mafig.layout.update(title_text = "Moving Average Crossover Strategy", xaxis_rangeslider_visible=True)
    st.plotly_chart(mafig)


ma_data()

df_train = data[['Date', 'Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

st.subheader("Forecast data")
st.write(forecast.tail())

st.subheader("Forecast data")
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

st.write("Forecast components")
fig2 = m.plot_components(forecast)
st.write(fig2)


st.image("footer.png")