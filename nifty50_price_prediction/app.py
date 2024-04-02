import streamlit as st
from datetime import date

import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd


START = "2019-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

import streamlit as st

import streamlit as st

# Define the HTML/CSS code for the full-screen timed image display
timed_image_html = """
<style>
    body {
        margin: 0;
        padding: 0;
        overflow: hidden;
        background-color: #f2f2f2; /* Set background color */
    }
    #timed-image {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        /* Use a blurred version of your image as background */
        background-image: url('https://stockmarkets.co.in/wp-content/webp-express/webp-images/uploads/2023/12/Navigating-Through-Bull-and-Bear-Markets-in-India-scaled.jpg.webp');
        filter: blur(3px) brightness(50%); /* Apply blur effect */
        background-size: cover;
        background-position: center;
    }
    #main-content {
        display: none; /* Hide main content initially */
    }
</style>
<div id="timed-image"></div>
<div id="main-content">
    <!-- Your main content goes here -->
    <h1>Welcome to My Streamlit App!</h1>
    <p>This is the main content of the app.</p>
</div>
<script>
    setTimeout(function() {
        document.getElementById('timed-image').style.display = 'none';
        document.getElementById('main-content').style.display = 'block';
    }, 20000);  // 20 seconds timeout
</script>
"""

# Display the full-screen timed image
st.markdown(timed_image_html, unsafe_allow_html=True)
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
st.sidebar.image("nifty_50.png", width= 350)
# selected_stock = st.sidebar.selectbox("Select the stock for prediction", stocks)
selected_stock = st.sidebar.selectbox("Search Stock", stocks, index=0)

n_months = st.slider("Months of prediction:", 1,12)
period = n_months * 30

if n_months == 1:
    month = "month"
else:
    month = "months"

@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    data['Symbol'] = ticker  #update
    return data


# data_load_state = st.text("load data...")
data = load_data(selected_stock)
# data_load_state.text("Loading data...done!")

# st.subheader("Raw data")
# st.write(data.tail())

def get_company_fundamentals(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info
        company_name = info.get('longName', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        net_profit = info.get('netIncomeToCommon', 'N/A')
        dividend_yield = info.get('dividendYield', 'N/A')

        # Convert market cap to crores (divide by 10^7) and format to 2 decimal places
        market_cap_cr = '{:.2f}'.format(market_cap / 10 ** 7) if market_cap != 'N/A' else 'N/A'

        # Convert net profit to crores (divide by 10^7) and format to 2 decimal places
        net_profit_cr = '{:.2f}'.format(net_profit / 10 ** 7) if net_profit != 'N/A' else 'N/A'

        # Convert dividend yield to percentage and format to 2 decimal places
        dividend_yield = '{:.2f}'.format(dividend_yield * 100) if dividend_yield != 'N/A' else 'N/A'

        return company_name, market_cap_cr, net_profit_cr, dividend_yield
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None, None, None


company_name, market_cap_cr, net_profit_cr, dividend_yield = get_company_fundamentals(selected_stock)

# Display company fundamental data in a table
st.subheader("Company Fundamental Data")
if company_name:
    fundamental_data = {
        "Attribute": ["Company Name", "Market Cap (Cr)", "Net Profit (Cr)", "Dividend Yield (%)"],
        "Value": [company_name, market_cap_cr, net_profit_cr, dividend_yield]
    }
    df = pd.DataFrame(fundamental_data)
    st.table(df.set_index('Attribute', drop=True))


def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
    st.subheader("Time Series Data")
    fig.layout.update(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


plot_raw_data()

def ma_data():
    mafig = go.Figure()
    ma100 = data.Close.rolling(50).mean()
    ma50 = data.Close.rolling(200).mean()
    mafig.add_trace(go.Scatter(x=data['Date'], y=ma100, name='50 Days MA'))
    mafig.add_trace(go.Scatter(x=data['Date'], y=ma50, name='200 Days MA'))
    mafig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
    st.subheader("Moving Average Crossover Strategy")
    mafig.layout.update(xaxis_rangeslider_visible=True)
    st.plotly_chart(mafig)


ma_data()

df_train = data[['Date', 'Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

# st.subheader("Forecast data")
# st.write(forecast.tail())


if forecast['trend'].iloc[-1] > data['Close'].iloc[-1]:
    positive_return = round(((forecast["trend"].iloc[-1] - data['Close'].iloc[-1])/ data["Close"].iloc[-1]) * 100, 2)
    st.write(f"<h1 style='color: green;'>Buy +{positive_return}%</h1>", unsafe_allow_html=True)
    st.subheader(f"You can Buy this stock for {n_months} {month} {stock_market_emoji}")
    trend = "Bullish"
else:
    negative_return = round(((forecast["trend"].iloc[-1] - data['Close'].iloc[-1])/ data["Close"].iloc[-1]) * 100, 2)
    st.write(f"<h1 style='color: red;'>Sell {negative_return}%</h1>", unsafe_allow_html=True)
    st.subheader(f"Ignore this stock or sell the stock")
    trend = "Bearish"

upper_range = round(forecast['yhat_upper'].iloc[-1])
lower_range = round(forecast["yhat_lower"].iloc[-1])
target = round(forecast['yhat'].iloc[-1])

st.write(f"The {selected_stock} Looks {trend} according to our prediction model for {n_months} {month}. The range of "
         f"this stock for {n_months} {month} will be {upper_range} to {lower_range}. The predicted target of the selected stock will be {target}.")

st.subheader("Forecast data")
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)


st.write("Forecast components")
fig2 = m.plot_components(forecast)
st.write(fig2)

# st.write("<iframe src='https://shreedhar-parge.github.io/stock-price-prediction-footer/' width='100%' height='400'></iframe>", unsafe_allow_html=True)
st.image("footer.png")

days = 180

@st.cache_data
def predict_and_rank_stocks(data):
    all_stock_forecasts = []
    for symbol in stocks:
        df = data[data["Symbol"] == symbol]
        if not df.empty:
            df = df.rename(columns={"Date": "ds", "Close": "y"})  # Rename columns to match Prophet requirements
            m = Prophet()
            m.fit(df)
            future = m.make_future_dataframe(periods=days)
            forecast = m.predict(future)
            future_prices = forecast.loc[forecast['ds'] == forecast['ds'].max(), 'yhat'].values[0]
            current_price = df['y'].iloc[-1]  # Using 'y' column for current price
            Expected_Returns = ((future_prices / current_price) - 1) * 100
            
            all_stock_forecasts.append({'Symbol': symbol, 'Expected_Returns': Expected_Returns})

    # Convert the forecasts into a DataFrame
    forecast_df = pd.DataFrame(all_stock_forecasts)

    # Rank the stocks based on expected percentage returns
    top_5_stocks_buying = forecast_df.sort_values(by='Expected_Returns', ascending=False).head(5)
    top_5_stocks_selling = forecast_df.sort_values(by='Expected_Returns', ascending=True).head(5)

    # Reset the index and drop the index column
    top_5_stocks_buying.reset_index(drop=True, inplace=True)
    top_5_stocks_selling.reset_index(drop=True, inplace=True)

    # Format the expected percentage returns
    top_5_stocks_buying['Expected_Returns'] = top_5_stocks_buying['Expected_Returns'].apply(lambda x: f"{int(x)}%")
    top_5_stocks_selling['Expected_Returns'] = top_5_stocks_selling['Expected_Returns'].apply(lambda x: f"{int(x)}%")

    return top_5_stocks_buying, top_5_stocks_selling

all_data = pd.concat([load_data(symbol) for symbol in stocks], ignore_index=True)

# Get the top 5 buying and selling stocks
top_5_buying_stocks, top_5_selling_stocks = predict_and_rank_stocks(all_data)

# Reset index and add 1 to start from 1
top_5_buying_stocks.index = top_5_buying_stocks.index + 1
top_5_selling_stocks.index = top_5_selling_stocks.index + 1

st.sidebar.subheader("Top 5 Buying Stocks")
buying_stocks_table = top_5_buying_stocks.style.apply(lambda x: ['color: green' if '%' in str(cell) else '' for cell in x])
buying_stocks_table = buying_stocks_table.set_table_styles([{
    'selector': 'th',
    'props': [('color', 'green')]
}])
st.sidebar.write(buying_stocks_table)

# Display the top 5 selling stocks in the sidebar
st.sidebar.subheader("Top 5 Selling Stocks")
selling_stocks_table = top_5_selling_stocks.style.apply(lambda x: ['color: red' if '%' in str(cell) else '' for cell in x])
selling_stocks_table = selling_stocks_table.set_table_styles([{
    'selector': 'th',
    'props': [('color', 'red')]
}])
st.sidebar.write(selling_stocks_table)
# 2-apr
# import streamlit as st
# from datetime import date
# import yfinance as yf
# from prophet import Prophet
# from prophet.plot import plot_plotly
# from plotly import graph_objs as go
# import pandas as pd

# # Set date range for data retrieval
# START = "2015-01-01"
# TODAY = date.today().strftime("%Y-%m-%d")


# # Define the HTML/CSS code for the full-screen timed image display
# timed_image_html = """
# <style>
#     body {
#         margin: 0;
#         padding: 0;
#         overflow: hidden;
#     }
#     #timed-image {
#         position: fixed;
#         top: 0;
#         left: 0;
#         width: 100vw;
#         height: 100vh;
#         background-image: url('https://stockmarkets.co.in/wp-content/webp-express/webp-images/uploads/2023/12/Navigating-Through-Bull-and-Bear-Markets-in-India-scaled.jpg.webp'); /* Replace with your image URL */
#         background-size: cover;
#         background-position: center;
#         animation: fadeOut 20s ease forwards;
#     }
#     @keyframes fadeOut {
#         0% { opacity: 1; }
#         100% { opacity: 0; }
#     }
# </style>
# <div id="timed-image"></div>
# <script>
#     setTimeout(function() {
#         document.getElementById('timed-image').style.display = 'none';
#         document.getElementById('main-content').style.display = 'block';
#     }, 20000);  // 20 seconds timeout
# </script>
# """

# # Display the full-screen timed image
# st.markdown(timed_image_html, unsafe_allow_html=True)


# sidebar_bg = st.sidebar.image('https://nsearchives.nseindia.com/products/resources/images/nifty_50.jpg', use_column_width=True)




# # Page title and description
# st.title("Nifty 50 Stocks Price Prediction App")
# st.sidebar.markdown(
#     """
#     ## Search Stock
#     Use the search bar to find and select a stock.
#     """
# )

# # Create a list of stock symbols for auto-suggestions
# stocks = ["^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "INFY.NS", "ITC.NS",
#           "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "LT.NS", "KOTAKBANK.NS", "ASIANPAINT.NS", "HCLTECH.NS",
#           "AXISBANK.NS", "ADANIENT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "BAJAJFINSV.NS", "ULTRACEMCO.NS",
#           "ONGC.NS", "NESTLEIND.NS", "WIPRO.NS", "NTPC.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "M&M.NS", "POWERGRID.NS",
#           "ADANIPORTS.NS", "LTIM.NS", "TATASTEEL.NS", "COALINDIA.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS",
#           "GRASIM.NS", "BRITANNIA.NS", "TECHM.NS", "INDUSINDBK.NS", "HINDALCO.NS", "DIVISLAB.NS", "CIPLA.NS", "RDY",
#           "EICHERMOT.NS", "BPCL.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "HEROMOTOCO.NS", "UPL.NS"]

# # Search bar for selecting stocks with auto-suggestions in the sidebar
# search_query = st.sidebar.selectbox("Search Stock", stocks, index=0)

# # Load data function with caching
# @st.cache_data
# def load_data(ticker):
#     data = yf.download(ticker, START, TODAY)
#     data.reset_index(inplace=True)
#     return data

# # Display data loading message
# data_load_state = st.text("Loading data...")
# data = load_data(search_query)
# data_load_state.text("Loading data...done!")

# # Display raw data table
# st.subheader("Raw Data")
# st.write(data.tail())

# # Interactive plot function with MACD and Buy/Sell signals
# def plot_data():
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='Open Price', line=dict(color='royalblue')))
#     fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close Price', line=dict(color='green')))

#     # Calculate MACD
#     exp1 = data['Close'].ewm(span=12, adjust=False).mean()
#     exp2 = data['Close'].ewm(span=26, adjust=False).mean()
#     macd = exp1 - exp2
#     signal = macd.ewm(span=9, adjust=False).mean()

#     fig.add_trace(go.Scatter(x=data['Date'], y=macd, name='MACD', line=dict(color='blue')))
#     fig.add_trace(go.Scatter(x=data['Date'], y=signal, name='Signal', line=dict(color='red')))

#     # Buy and Sell signals
#     buy_signal = ((macd > signal) & (macd.shift(1) < signal.shift(1)))
#     sell_signal = ((macd < signal) & (macd.shift(1) > signal.shift(1)))
#     fig.add_trace(go.Scatter(x=data['Date'][buy_signal], y=data['Close'][buy_signal], 
#                              mode='markers', marker=dict(color='green', size=10), name='Buy Signal'))
#     fig.add_trace(go.Scatter(x=data['Date'][sell_signal], y=data['Close'][sell_signal], 
#                              mode='markers', marker=dict(color='red', size=10), name='Sell Signal'))

#     fig.update_layout(title="Stock Price Analysis with MACD",
#                       xaxis_title="Date",
#                       yaxis_title="Price",
#                       xaxis_rangeslider_visible=True)
#     st.plotly_chart(fig)

# # Display interactive plot
# st.subheader("Stock Price Analysis")
# plot_data()

# # Prophet forecasting
# df_train = data[['Date', 'Close']]
# df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

# n_months = st.slider("Months of Prediction", 1, 12)
# period = n_months * 30

# m = Prophet()
# m.fit(df_train)
# future = m.make_future_dataframe(periods=period)
# forecast = m.predict(future)

# # Display forecast data table
# st.subheader("Forecast Data")
# st.write(forecast.tail())

# # Plot forecast and components
# st.subheader("Forecast Plots")
# fig1 = plot_plotly(m, forecast)
# st.plotly_chart(fig1)

# st.subheader("Forecast Components")
# fig2 = m.plot_components(forecast)
# st.write(fig2)

# # Footer image
# st.image("footer.png", use_column_width=True)

# # Analysis function to suggest top 10 stocks to buy or sell
# def analyze_stocks(all_stocks_data, forecast_data, period):
#     analysis_results = {}
#     for stock, data in all_stocks_data.items():
#         close_prices = data['Close']
#         if len(close_prices) >= 31:  # Minimum data required for analysis (30 days + current day)
#             last_price = close_prices.iloc[-1]  # Use iloc for integer indexing
#             thirty_day_avg = close_prices.iloc[-31:-1].mean()  # Exclude current day from average

#             # Calculate return based on buying at last closing price and selling at predicted future price
#             if last_price > thirty_day_avg:
#                 predicted_price = forecast_data.loc[forecast_data['ds'] == forecast_data['ds'].max(), 'yhat'].values[0]
#                 return_percentage = ((predicted_price - last_price) / last_price) * 100
#                 analysis_results[stock] = {"Recommendation": "Buy", "Return (%)": round(return_percentage, 2)}
#             else:
#                 analysis_results[stock] = {"Recommendation": "Sell", "Return (%)": 0}  # Set return percentage to 0 for sell recommendation
#         else:
#             analysis_results[stock] = {"Recommendation": "Insufficient data for analysis", "Return (%)": 0}  # Set return percentage to 0 for insufficient data

#     return analysis_results


# # Analyze all stocks
# all_stocks_data = {}
# for stock_symbol in stocks:
#     all_stocks_data[stock_symbol] = load_data(stock_symbol)

# # Analyze and suggest top 10 stocks to buy or sell
# analysis_results = analyze_stocks(all_stocks_data, forecast, period)
# sorted_analysis = sorted(analysis_results.items(), key=lambda x: x[1]['Return (%)'] if x[1]['Return (%)'] is not None else -float('inf'), reverse=True)

# top_10_stocks = dict(sorted_analysis[:10])
# df = pd.DataFrame(top_10_stocks.values(), index=top_10_stocks.keys(), columns=['Recommendation', 'Return (%)'])

# # Display top 10 stocks to buy or sell in the sidebar
# st.sidebar.subheader("Top 10 recommended Stocks")
# st.sidebar.table(df)

# # Display buy and sell recommendations separately
# buy_df = df[df['Recommendation'] == 'Buy']
# sell_df = df[df['Recommendation'] == 'Sell']

# st.sidebar.subheader("Buy recommended Stocks")
# st.sidebar.table(buy_df)

# st.sidebar.subheader("Sell recommended Stocks")
# st.sidebar.table(sell_df)


# # date 29-march-2024
# # import streamlit as st
# # from datetime import date
# # import yfinance as yf
# # from prophet import Prophet
# # from prophet.plot import plot_plotly
# # from plotly import graph_objs as go
# # import pandas as pd

# # # Set date range for data retrieval
# # START = "2015-01-01"
# # TODAY = date.today().strftime("%Y-%m-%d")

# # import streamlit as st
# # from datetime import date
# # import yfinance as yf
# # from prophet import Prophet
# # from prophet.plot import plot_plotly
# # from plotly import graph_objs as go
# # import pandas as pd

# # # Set date range for data retrieval
# # START = "2015-01-01"
# # TODAY = date.today().strftime("%Y-%m-%d")

# # # Page title and description
# # st.title("Nifty 50 Stocks Price Prediction App")
# # st.sidebar.markdown(
# #     """
# #     ## Search Stock
# #     Use the search bar to find and select a stock.
# #     """
# # )

# # # Create a list of stock symbols for auto-suggestions
# # stocks = ["^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "INFY.NS", "ITC.NS",
# #           "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "LT.NS", "KOTAKBANK.NS", "ASIANPAINT.NS", "HCLTECH.NS",
# #           "AXISBANK.NS", "ADANIENT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "BAJAJFINSV.NS", "ULTRACEMCO.NS",
# #           "ONGC.NS", "NESTLEIND.NS", "WIPRO.NS", "NTPC.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "M&M.NS", "POWERGRID.NS",
# #           "ADANIPORTS.NS", "LTIM.NS", "TATASTEEL.NS", "COALINDIA.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS",
# #           "GRASIM.NS", "BRITANNIA.NS", "TECHM.NS", "INDUSINDBK.NS", "HINDALCO.NS", "DIVISLAB.NS", "CIPLA.NS", "RDY",
# #           "EICHERMOT.NS", "BPCL.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "HEROMOTOCO.NS", "UPL.NS"]

# # # Search bar for selecting stocks with auto-suggestions in the sidebar
# # search_query = st.sidebar.selectbox("Search Stock", stocks, index=0)

# # # Load data function with caching
# # @st.cache_data
# # def load_data(ticker):
# #     data = yf.download(ticker, START, TODAY)
# #     data.reset_index(inplace=True)
# #     return data

# # # Display data loading message
# # data_load_state = st.text("Loading data...")
# # data = load_data(search_query)
# # data_load_state.text("Loading data...done!")

# # # Display raw data table
# # st.subheader("Raw Data")
# # st.write(data.tail())

# # # Interactive plot function with MACD and Buy/Sell signals
# # def plot_data():
# #     fig = go.Figure()
# #     fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='Open Price', line=dict(color='royalblue')))
# #     fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close Price', line=dict(color='green')))

# #     # Calculate MACD
# #     exp1 = data['Close'].ewm(span=12, adjust=False).mean()
# #     exp2 = data['Close'].ewm(span=26, adjust=False).mean()
# #     macd = exp1 - exp2
# #     signal = macd.ewm(span=9, adjust=False).mean()

# #     fig.add_trace(go.Scatter(x=data['Date'], y=macd, name='MACD', line=dict(color='blue')))
# #     fig.add_trace(go.Scatter(x=data['Date'], y=signal, name='Signal', line=dict(color='red')))

# #     # Buy and Sell signals
# #     buy_signal = ((macd > signal) & (macd.shift(1) < signal.shift(1)))
# #     sell_signal = ((macd < signal) & (macd.shift(1) > signal.shift(1)))
# #     fig.add_trace(go.Scatter(x=data['Date'][buy_signal], y=data['Close'][buy_signal], 
# #                              mode='markers', marker=dict(color='green', size=10), name='Buy Signal'))
# #     fig.add_trace(go.Scatter(x=data['Date'][sell_signal], y=data['Close'][sell_signal], 
# #                              mode='markers', marker=dict(color='red', size=10), name='Sell Signal'))

# #     fig.update_layout(title="Stock Price Analysis with MACD",
# #                       xaxis_title="Date",
# #                       yaxis_title="Price",
# #                       xaxis_rangeslider_visible=True)
# #     st.plotly_chart(fig)

# # # Display interactive plot
# # st.subheader("Stock Price Analysis")
# # plot_data()

# # # Prophet forecasting
# # df_train = data[['Date', 'Close']]
# # df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

# # n_months = st.slider("Months of Prediction", 1, 12)
# # period = n_months * 30

# # m = Prophet()
# # m.fit(df_train)
# # future = m.make_future_dataframe(periods=period)
# # forecast = m.predict(future)

# # # Display forecast data table
# # st.subheader("Forecast Data")
# # st.write(forecast.tail())

# # # Plot forecast and components
# # st.subheader("Forecast Plots")
# # fig1 = plot_plotly(m, forecast)
# # st.plotly_chart(fig1)

# # st.subheader("Forecast Components")
# # fig2 = m.plot_components(forecast)
# # st.write(fig2)

# # # Footer image
# # st.image("footer.png", use_column_width=True)

# # # Analysis function to suggest top 10 stocks to buy or sell
# # def analyze_stocks(all_stocks_data):
# #     analysis_results = {}
# #     for stock, data in all_stocks_data.items():
# #         close_prices = data['Close']
# #         if len(close_prices) >= 31:  # Minimum data required for analysis (30 days + current day)
# #             last_price = close_prices.iloc[-1]  # Use iloc for integer indexing
# #             thirty_day_avg = close_prices.iloc[-31:-1].mean()  # Exclude current day from average
# #             analysis_results[stock] = "Buy" if last_price > thirty_day_avg else "Sell"
# #         else:
# #             analysis_results[stock] = "Insufficient data for analysis"

# #     return analysis_results


# # # Analyze all stocks
# # all_stocks_data = {}
# # for stock_symbol in stocks:
# #     all_stocks_data[stock_symbol] = load_data(stock_symbol)

# # # Analyze and suggest top 10 stocks to buy or sell
# # analysis_results = analyze_stocks(all_stocks_data)
# # sorted_analysis = sorted(analysis_results.items(), key=lambda x: x[1], reverse=True)

# # top_10_stocks = dict(sorted_analysis)
# # df = pd.DataFrame(top_10_stocks.items(), columns=['Stock', 'Recommendation'])
# # buy_df = df[(df['Recommendation'] == 'Buy')]
# # sell_df = df[(df['Recommendation'] == 'Sell')]


# # buy_df = buy_df.reset_index(drop=True)
# # buy_df.index += 1  

# # sell_df = sell_df.reset_index(drop=True)
# # sell_df.index += 1  
# # # Display top 10 stocks to buy or sell in the sidebar
# # st.sidebar.subheader("Buy recommended Stocks")
# # st.sidebar.table(buy_df.head(5))


# # st.sidebar.subheader("Sell recommended Stocks")
# # st.sidebar.table(sell_df.head(5))

