import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd

# Define the HTML/CSS code for the full-screen timed image display.
image_html = """
<style>
    body {
        margin: 0;
        padding: 0;
        overflow: hidden;
        background-color: #f2f2f2; /* Set background color */
    }
    #image {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        /* Use a blurred version of your image as background */
        background-image: url('https://img.freepik.com/free-vector/gradient-stock-market-concept_23-2149166929.jpg?size=626&ext=jpg&ga=GA1.1.2008272138.1712016000&semt=ais');
        filter: blur(15px) brightness(100%); /* Apply blur effect */
        background-size: cover;
        background-position: center;
    }
</style>
<div id="image"></div>
"""

# Display the full-screen timed image
st.markdown(image_html, unsafe_allow_html=True)
# st.sidebar.markdown(image_html, unsafe_allow_html=True)

START = "2019-01-01"
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

st.sidebar.image("nifty_50.png", width= 320)
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
    data['Symbol'] = ticker  
    return data


data = load_data(selected_stock)

def get_company_fundamentals(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info
        company_name = info.get('longName', 'N/A')
        current_pr = company.history(period="1d")["Close"].iloc[-1] if 'N/A' not in company_name else 'N/A'
        market_cap = info.get('marketCap', 'N/A')
        net_profit = info.get('netIncomeToCommon', 'N/A')
        dividend_yield = info.get('dividendYield', 'N/A')

        # Format current price to 2 decimal places
        current_pr = '{:.2f}'.format(current_pr) if current_pr != 'N/A' else 'N/A'

        # Convert market cap to crores (divide by 10^7) and format to 2 decimal places
        market_cap_cr = '{:.2f}'.format(market_cap / 10 ** 7) if market_cap != 'N/A' else 'N/A'

        # Convert net profit to crores (divide by 10^7) and format to 2 decimal places
        net_profit_cr = '{:.2f}'.format(net_profit / 10 ** 7) if net_profit != 'N/A' else 'N/A'

        # Convert dividend yield to percentage and format to 2 decimal places
        dividend_yield = '{:.2f}'.format(dividend_yield * 100) if dividend_yield != 'N/A' else 'N/A'

        return company_name, current_pr, market_cap_cr, net_profit_cr, dividend_yield
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None, None, None


company_name, current_pr, market_cap_cr, net_profit_cr, dividend_yield = get_company_fundamentals(selected_stock)

# Display company fundamental data in a table
st.subheader("Company Details")
if company_name:
    fundamental_data = {
        "Attribute": ["Company Name", "Current Market Price", "Market Cap (Cr)", "Net Profit (Cr)", "Dividend Yield (%)"],
        "Value": [company_name, current_pr, market_cap_cr, net_profit_cr, dividend_yield]
    }
    df = pd.DataFrame(fundamental_data)
    df_styled = df.set_index('Attribute', drop=True).style.set_table_styles([{'selector': 'th','props': [('color', 'black')]}])
    st.table(df_styled)

# st.write(data.head())

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

st.write(f"The {company_name} Looks {trend} according to our prediction model for {n_months} {month}. The range of "
         f"this stock for {n_months} {month} will be {upper_range} to {lower_range}. The  target that is predicted of the selected stock will be {target}.")

st.subheader("Forecast data")
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)


st.write("Forecast components")
fig2 = m.plot_components(forecast)
st.write(fig2)

st.image("footer.png")

def predict_and_rank_stocks(data):
    all_stock_forecasts = []
    for symbol in stocks:
        df = data[data["Symbol"] == symbol]
        if not df.empty:
            df = df.rename(columns={"Date": "ds", "Close": "y"})  # Rename columns to match Prophet requirements
            m = Prophet()
            m.fit(df)
            future = m.make_future_dataframe(periods=period)
            forecast = m.predict(future)
            if forecast['trend'].iloc[-1] > df['y'].iloc[-1]:
                Expected_Returns = round(((forecast["trend"].iloc[-1] - df['y'].iloc[-1])/ df["y"].iloc[-1]) * 100, 2)
            else:
                Expected_Returns = round(((forecast["trend"].iloc[-1] - df['y'].iloc[-1])/ df["y"].iloc[-1]) * 100, 2)
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

st.sidebar.subheader(f"Top 5 Buying Stocks for next {n_months} {month}")
buying_stocks_table = top_5_buying_stocks.style.apply(lambda x: ['color: green' if '%' in str(cell) else '' for cell in x])
buying_stocks_table = buying_stocks_table.set_table_styles([{
    'selector': 'th',
    'props': [('color', 'green')]
}])
st.sidebar.write(buying_stocks_table)

# Display the top 5 selling stocks in the sidebar
st.sidebar.subheader(f"Top 5 Selling Stocks for next {n_months} {month}")
selling_stocks_table = top_5_selling_stocks.style.apply(lambda x: ['color: red' if '%' in str(cell) else '' for cell in x])
selling_stocks_table = selling_stocks_table.set_table_styles([{
    'selector': 'th',
    'props': [('color', 'red')]
}])
st.sidebar.write(selling_stocks_table)

# import streamlit as st
# from datetime import date
# import yfinance as yf
# from prophet import Prophet
# from prophet.plot import plot_plotly
# from plotly import graph_objs as go
# import pandas as pd

# # Define the HTML/CSS code for the full-screen timed image display
# timed_image_html = """
# <style>
#     body {
#         margin: 0;
#         padding: 0;
#         overflow: hidden;
#         background-color: #f2f2f2; /* Set background color */
#     }
#     #timed-image {
#         position: fixed;
#         top: 0;
#         left: 0;
#         width: 100vw;
#         height: 100vh;
#         /* Use a blurred version of your image as background */
#         background-image: url('https://img.freepik.com/free-vector/gradient-stock-market-concept_23-2149166929.jpg?size=626&ext=jpg&ga=GA1.1.2008272138.1712016000&semt=ais');
#         filter: blur(10px) brightness(100%); /* Apply blur effect */
#         background-size: cover;
#         background-position: center;
#     }
#     #main-content {
#         display: none; /* Hide main content initially */
#     }
# </style>
# <div id="timed-image"></div>
# <div id="main-content">
#     <!-- Your main content goes here -->
#     <h1>Welcome to My Streamlit App!</h1>
#     <p>This is the main content of the app.</p>
# </div>
# <script>
#     setTimeout(function() {
#         document.getElementById('timed-image').style.display = 'none';
#         document.getElementById('main-content').style.display = 'block';
#     }, 20000);  // 20 seconds timeout
# </script>
# """

# # Display the full-screen timed image
# st.markdown(timed_image_html, unsafe_allow_html=True)
# # st.sidebar.markdown(timed_image_html, unsafe_allow_html=True)

# START = "2019-01-01"
# TODAY = date.today().strftime("%Y-%m-%d")

# stock_market_emoji = "\U0001F4C8"
# st.header(f"Nifty 50 Stocks Price Prediction App {stock_market_emoji}")
# st.image("stock_market.png", width=700)
#added all the stocks statically
# stocks = ("^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "INFY.NS", "ITC.NS", "SBIN.NS",
#           "BHARTIARTL.NS", "BAJFINANCE.NS", "LT.NS", "KOTAKBANK.NS", "ASIANPAINT.NS", "HCLTECH.NS", "AXISBANK.NS",
#           "ADANIENT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "BAJAJFINSV.NS", "ULTRACEMCO.NS", "ONGC.NS",
#           "NESTLEIND.NS", "WIPRO.NS", "NTPC.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "M&M.NS", "POWERGRID.NS", "ADANIPORTS.NS",
#           "LTIM.NS", "TATASTEEL.NS", "COALINDIA.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS", "GRASIM.NS",
#           "BRITANNIA.NS", "TECHM.NS", "INDUSINDBK.NS", "HINDALCO.NS", "DIVISLAB.NS", "CIPLA.NS", "RDY", "EICHERMOT.NS",
#           "BPCL.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "HEROMOTOCO.NS", "UPL.NS")

# st.sidebar.image("nifty_50.png", width= 320)
# selected_stock = st.sidebar.selectbox("Search Stock", stocks, index=0)

# n_months = st.slider("Months of prediction:", 1,12)
# period = n_months * 30

# if n_months == 1:
#     month = "month"
# else:
#     month = "months"

# @st.cache_data
# def load_data(ticker):
#     data = yf.download(ticker, START, TODAY)
#     data.reset_index(inplace=True)
#     data['Symbol'] = ticker  #update
#     return data


# data = load_data(selected_stock)

# def get_company_fundamentals(ticker):
#     try:
#         company = yf.Ticker(ticker)
#         info = company.info
#         company_name = info.get('longName', 'N/A')
#         current_pr = company.history(period="1d")["Close"].iloc[-1] if 'N/A' not in company_name else 'N/A'
#         market_cap = info.get('marketCap', 'N/A')
#         net_profit = info.get('netIncomeToCommon', 'N/A')
#         dividend_yield = info.get('dividendYield', 'N/A')

#         # Format current price to 2 decimal places
#         current_pr = '{:.2f}'.format(current_pr) if current_pr != 'N/A' else 'N/A'

#         # Convert market cap to crores (divide by 10^7) and format to 2 decimal places
#         market_cap_cr = '{:.2f}'.format(market_cap / 10 ** 7) if market_cap != 'N/A' else 'N/A'

#         # Convert net profit to crores (divide by 10^7) and format to 2 decimal places
#         net_profit_cr = '{:.2f}'.format(net_profit / 10 ** 7) if net_profit != 'N/A' else 'N/A'

#         # Convert dividend yield to percentage and format to 2 decimal places
#         dividend_yield = '{:.2f}'.format(dividend_yield * 100) if dividend_yield != 'N/A' else 'N/A'

#         return company_name, current_pr, market_cap_cr, net_profit_cr, dividend_yield
#     except Exception as e:
#         st.error(f"Error fetching data: {e}")
#         return None, None, None, None


# company_name, current_pr, market_cap_cr, net_profit_cr, dividend_yield = get_company_fundamentals(selected_stock)

# # Display company fundamental data in a table
# st.subheader("Company Details")
# if company_name:
#     fundamental_data = {
#         "Attribute": ["Company Name", "Current Market Price", "Market Cap (Cr)", "Net Profit (Cr)", "Dividend Yield (%)"],
#         "Value": [company_name, current_pr, market_cap_cr, net_profit_cr, dividend_yield]
#     }
#     df = pd.DataFrame(fundamental_data)
#     st.table(df.set_index('Attribute', drop=True))


# def plot_raw_data():
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open', line=dict(color='red', width=2)))
#     fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
#     st.subheader("Time Series Data")
#     fig.layout.update(xaxis_rangeslider_visible=True)
#     st.plotly_chart(fig)


# plot_raw_data()

# def ma_data():
#     mafig = go.Figure()
#     ma100 = data.Close.rolling(50).mean()
#     ma50 = data.Close.rolling(200).mean()
#     mafig.add_trace(go.Scatter(x=data['Date'], y=ma100, name='50 Days MA'))
#     mafig.add_trace(go.Scatter(x=data['Date'], y=ma50, name='200 Days MA'))
#     mafig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
#     st.subheader("Moving Average Crossover Strategy")
#     mafig.layout.update(xaxis_rangeslider_visible=True)
#     st.plotly_chart(mafig)


# ma_data()

# df_train = data[['Date', 'Close']]
# df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

# m = Prophet()
# m.fit(df_train)
# future = m.make_future_dataframe(periods=period)
# forecast = m.predict(future)

# # st.subheader("Forecast data")
# # st.write(forecast.tail())


# if forecast['trend'].iloc[-1] > data['Close'].iloc[-1]:
#     positive_return = round(((forecast["trend"].iloc[-1] - data['Close'].iloc[-1])/ data["Close"].iloc[-1]) * 100, 2)
#     st.write(f"<h1 style='color: green;'>Buy +{positive_return}%</h1>", unsafe_allow_html=True)
#     st.subheader(f"You can Buy this stock for {n_months} {month} {stock_market_emoji}")
#     trend = "Bullish"
# else:
#     negative_return = round(((forecast["trend"].iloc[-1] - data['Close'].iloc[-1])/ data["Close"].iloc[-1]) * 100, 2)
#     st.write(f"<h1 style='color: red;'>Sell {negative_return}%</h1>", unsafe_allow_html=True)
#     st.subheader(f"Ignore this stock or sell the stock")
#     trend = "Bearish"

# upper_range = round(forecast['yhat_upper'].iloc[-1])
# lower_range = round(forecast["yhat_lower"].iloc[-1])
# target = round(forecast['yhat'].iloc[-1])

# st.write(f"The {company_name} Looks {trend} according to our prediction model for {n_months} {month}. The range of "
#          f"this stock for {n_months} {month} will be {upper_range} to {lower_range}. The predicted target of the selected stock will be {target}.")

# st.subheader("Forecast data")
# fig1 = plot_plotly(m, forecast)
# st.plotly_chart(fig1)


# st.write("Forecast components")
# fig2 = m.plot_components(forecast)
# st.write(fig2)

# st.image("footer.png")

# # days = 180

# # @st.cache_data
# def predict_and_rank_stocks(data):
#     all_stock_forecasts = []
#     for symbol in stocks:
#         df = data[data["Symbol"] == symbol]
#         if not df.empty:
#             df = df.rename(columns={"Date": "ds", "Close": "y"})  # Rename columns to match Prophet requirements
#             m = Prophet()
#             m.fit(df)
#             future = m.make_future_dataframe(periods=period)
#             forecast = m.predict(future)
#             future_prices = forecast.loc[forecast['ds'] == forecast['ds'].max(), 'yhat'].values[0]
#             current_price = df['y'].iloc[-1]  # Using 'y' column for current price
#             Expected_Returns = ((future_prices / current_price) - 1) * 100
#             all_stock_forecasts.append({'Symbol': symbol, 'Expected_Returns': Expected_Returns})

#     # Convert the forecasts into a DataFrame
#     forecast_df = pd.DataFrame(all_stock_forecasts)

#     # Rank the stocks based on expected percentage returns
#     top_5_stocks_buying = forecast_df.sort_values(by='Expected_Returns', ascending=False).head(5)
#     top_5_stocks_selling = forecast_df.sort_values(by='Expected_Returns', ascending=True).head(5)

#     # Reset the index and drop the index column
#     top_5_stocks_buying.reset_index(drop=True, inplace=True)
#     top_5_stocks_selling.reset_index(drop=True, inplace=True)

#     # Format the expected percentage returns
#     top_5_stocks_buying['Expected_Returns'] = top_5_stocks_buying['Expected_Returns'].apply(lambda x: f"{int(x)}%")
#     top_5_stocks_selling['Expected_Returns'] = top_5_stocks_selling['Expected_Returns'].apply(lambda x: f"{int(x)}%")

#     return top_5_stocks_buying, top_5_stocks_selling

# all_data = pd.concat([load_data(symbol) for symbol in stocks], ignore_index=True)

# # Get the top 5 buying and selling stocks
# top_5_buying_stocks, top_5_selling_stocks = predict_and_rank_stocks(all_data)

# # Reset index and add 1 to start from 1
# top_5_buying_stocks.index = top_5_buying_stocks.index + 1
# top_5_selling_stocks.index = top_5_selling_stocks.index + 1

# st.sidebar.subheader(f"Top 5 Buying Stocks for next {n_months} {month}")
# buying_stocks_table = top_5_buying_stocks.style.apply(lambda x: ['color: green' if '%' in str(cell) else '' for cell in x])
# buying_stocks_table = buying_stocks_table.set_table_styles([{
#     'selector': 'th',
#     'props': [('color', 'green')]
# }])
# st.sidebar.write(buying_stocks_table)

# # Display the top 5 selling stocks in the sidebar
# st.sidebar.subheader(f"Top 5 Selling Stocks for next {n_months} {month}")
# selling_stocks_table = top_5_selling_stocks.style.apply(lambda x: ['color: red' if '%' in str(cell) else '' for cell in x])
# selling_stocks_table = selling_stocks_table.set_table_styles([{
#     'selector': 'th',
#     'props': [('color', 'red')]
# }])
# st.sidebar.write(selling_stocks_table)

# # import streamlit as st
# # from datetime import date
# # import yfinance as yf
# # from prophet import Prophet
# # from prophet.plot import plot_plotly
# # from plotly import graph_objs as go
# # import pandas as pd

# # # Define the HTML/CSS code for the full-screen timed image display
# # timed_image_html = """
# # <style>
# #     body {
# #         margin: 0;
# #         padding: 0;
# #         overflow: hidden;
# #         background-color: #f2f2f2; /* Set background color */
# #     }
# #     #timed-image {
# #         position: fixed;
# #         top: 0;
# #         left: 0;
# #         width: 100vw;
# #         height: 100vh;
# #         /* Use a blurred version of your image as background */
# #         background-image: url('https://img.freepik.com/free-vector/gradient-stock-market-concept_23-2149166929.jpg?size=626&ext=jpg&ga=GA1.1.2008272138.1712016000&semt=ais');
# #         filter: blur(10px) brightness(100%); /* Apply blur effect */
# #         background-size: cover;
# #         background-position: center;
# #     }
# #     #main-content {
# #         display: none; /* Hide main content initially */
# #     }
# # </style>
# # <div id="timed-image"></div>
# # <div id="main-content">
# #     <!-- Your main content goes here -->
# #     <h1>Welcome to My Streamlit App!</h1>
# #     <p>This is the main content of the app.</p>
# # </div>
# # <script>
# #     setTimeout(function() {
# #         document.getElementById('timed-image').style.display = 'none';
# #         document.getElementById('main-content').style.display = 'block';
# #     }, 20000);  // 20 seconds timeout
# # </script>
# # """

# # # Display the full-screen timed image
# # st.markdown(timed_image_html, unsafe_allow_html=True)
# # # st.sidebar.markdown(timed_image_html, unsafe_allow_html=True)

# # START = "2019-01-01"
# # TODAY = date.today().strftime("%Y-%m-%d")

# # stock_market_emoji = "\U0001F4C8"
# # st.header(f"Nifty 50 Stocks Price Prediction App {stock_market_emoji}")
# # st.image("stock_market.png", width=700)

# # stocks = ("^NSEI", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "INFY.NS", "ITC.NS", "SBIN.NS",
# #           "BHARTIARTL.NS", "BAJFINANCE.NS", "LT.NS", "KOTAKBANK.NS", "ASIANPAINT.NS", "HCLTECH.NS", "AXISBANK.NS",
# #           "ADANIENT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "BAJAJFINSV.NS", "ULTRACEMCO.NS", "ONGC.NS",
# #           "NESTLEIND.NS", "WIPRO.NS", "NTPC.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "M&M.NS", "POWERGRID.NS", "ADANIPORTS.NS",
# #           "LTIM.NS", "TATASTEEL.NS", "COALINDIA.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS", "GRASIM.NS",
# #           "BRITANNIA.NS", "TECHM.NS", "INDUSINDBK.NS", "HINDALCO.NS", "DIVISLAB.NS", "CIPLA.NS", "RDY", "EICHERMOT.NS",
# #           "BPCL.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "HEROMOTOCO.NS", "UPL.NS")

# # st.sidebar.image("nifty_50.png", width= 320)
# # selected_stock = st.sidebar.selectbox("Search Stock", stocks, index=0)

# # n_months = st.slider("Months of prediction:", 1,12)
# # period = n_months * 30

# # if n_months == 1:
# #     month = "month"
# # else:
# #     month = "months"

# # @st.cache_data
# # def load_data(ticker):
# #     data = yf.download(ticker, START, TODAY)
# #     data.reset_index(inplace=True)
# #     data['Symbol'] = ticker  #update
# #     return data


# # data = load_data(selected_stock)

# # def get_company_fundamentals(ticker):
# #     try:
# #         company = yf.Ticker(ticker)
# #         info = company.info
# #         company_name = info.get('longName', 'N/A')
# #         current_pr = company.history(period="1d")["Close"].iloc[-1] if 'N/A' not in company_name else 'N/A'
# #         market_cap = info.get('marketCap', 'N/A')
# #         net_profit = info.get('netIncomeToCommon', 'N/A')
# #         dividend_yield = info.get('dividendYield', 'N/A')

# #         # Format current price to 2 decimal places
# #         current_pr = '{:.2f}'.format(current_pr) if current_pr != 'N/A' else 'N/A'

# #         # Convert market cap to crores (divide by 10^7) and format to 2 decimal places
# #         market_cap_cr = '{:.2f}'.format(market_cap / 10 ** 7) if market_cap != 'N/A' else 'N/A'

# #         # Convert net profit to crores (divide by 10^7) and format to 2 decimal places
# #         net_profit_cr = '{:.2f}'.format(net_profit / 10 ** 7) if net_profit != 'N/A' else 'N/A'

# #         # Convert dividend yield to percentage and format to 2 decimal places
# #         dividend_yield = '{:.2f}'.format(dividend_yield * 100) if dividend_yield != 'N/A' else 'N/A'

# #         return company_name, current_pr, market_cap_cr, net_profit_cr, dividend_yield
# #     except Exception as e:
# #         st.error(f"Error fetching data: {e}")
# #         return None, None, None, None


# # company_name, current_pr, market_cap_cr, net_profit_cr, dividend_yield = get_company_fundamentals(selected_stock)

# # # Display company fundamental data in a table
# # st.subheader("Company Details")
# # if company_name:
# #     fundamental_data = {
# #         "Attribute": ["Company Name", "Current Market Price", "Market Cap (Cr)", "Net Profit (Cr)", "Dividend Yield (%)"],
# #         "Value": [company_name, current_pr, market_cap_cr, net_profit_cr, dividend_yield]
# #     }
# #     df = pd.DataFrame(fundamental_data)
# #     st.table(df.set_index('Attribute', drop=True))


# # def plot_raw_data():
# #     fig = go.Figure()
# #     fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open', line=dict(color='red', width=2)))
# #     fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
# #     st.subheader("Time Series Data")
# #     fig.layout.update(xaxis_rangeslider_visible=True)
# #     st.plotly_chart(fig)


# # plot_raw_data()

# # def ma_data():
# #     mafig = go.Figure()
# #     ma100 = data.Close.rolling(50).mean()
# #     ma50 = data.Close.rolling(200).mean()
# #     mafig.add_trace(go.Scatter(x=data['Date'], y=ma100, name='50 Days MA'))
# #     mafig.add_trace(go.Scatter(x=data['Date'], y=ma50, name='200 Days MA'))
# #     mafig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
# #     st.subheader("Moving Average Crossover Strategy")
# #     mafig.layout.update(xaxis_rangeslider_visible=True)
# #     st.plotly_chart(mafig)


# # ma_data()

# # df_train = data[['Date', 'Close']]
# # df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

# # m = Prophet()
# # m.fit(df_train)
# # future = m.make_future_dataframe(periods=period)
# # forecast = m.predict(future)

# # # st.subheader("Forecast data")
# # # st.write(forecast.tail())


# # if forecast['trend'].iloc[-1] > data['Close'].iloc[-1]:
# #     positive_return = round(((forecast["trend"].iloc[-1] - data['Close'].iloc[-1])/ data["Close"].iloc[-1]) * 100, 2)
# #     st.write(f"<h1 style='color: green;'>Buy +{positive_return}%</h1>", unsafe_allow_html=True)
# #     st.subheader(f"You can Buy this stock for {n_months} {month} {stock_market_emoji}")
# #     trend = "Bullish"
# # else:
# #     negative_return = round(((forecast["trend"].iloc[-1] - data['Close'].iloc[-1])/ data["Close"].iloc[-1]) * 100, 2)
# #     st.write(f"<h1 style='color: red;'>Sell {negative_return}%</h1>", unsafe_allow_html=True)
# #     st.subheader(f"Ignore this stock or sell the stock")
# #     trend = "Bearish"

# # upper_range = round(forecast['yhat_upper'].iloc[-1])
# # lower_range = round(forecast["yhat_lower"].iloc[-1])
# # target = round(forecast['yhat'].iloc[-1])

# # st.write(f"The {company_name} Looks {trend} according to our prediction model for {n_months} {month}. The range of "
# #          f"this stock for {n_months} {month} will be {upper_range} to {lower_range}. The predicted target of the selected stock will be {target}.")

# # st.subheader("Forecast data")
# # fig1 = plot_plotly(m, forecast)
# # st.plotly_chart(fig1)


# # st.write("Forecast components")
# # fig2 = m.plot_components(forecast)
# # st.write(fig2)

# # st.image("footer.png")

# # # days = 180

# # # @st.cache_data
# # def predict_and_rank_stocks(data):
# #     all_stock_forecasts = []
# #     for symbol in stocks:
# #         df = data[data["Symbol"] == symbol]
# #         if not df.empty:
# #             df = df.rename(columns={"Date": "ds", "Close": "y"})  # Rename columns to match Prophet requirements
# #             m = Prophet()
# #             m.fit(df)
# #             future = m.make_future_dataframe(periods=period)
# #             forecast = m.predict(future)
# #             future_prices = forecast.loc[forecast['ds'] == forecast['ds'].max(), 'yhat'].values[0]
# #             current_price = df['y'].iloc[-1]  # Using 'y' column for current price
# #             Expected_Returns = ((future_prices / current_price) - 1) * 100
# #             all_stock_forecasts.append({'Symbol': symbol, 'Expected_Returns': Expected_Returns})

# #     # Convert the forecasts into a DataFrame
# #     forecast_df = pd.DataFrame(all_stock_forecasts)

# #     # Rank the stocks based on expected percentage returns
# #     top_5_stocks_buying = forecast_df.sort_values(by='Expected_Returns', ascending=False).head(5)
# #     top_5_stocks_selling = forecast_df.sort_values(by='Expected_Returns', ascending=True).head(5)

# #     # Reset the index and drop the index column
# #     top_5_stocks_buying.reset_index(drop=True, inplace=True)
# #     top_5_stocks_selling.reset_index(drop=True, inplace=True)

# #     # Format the expected percentage returns
# #     top_5_stocks_buying['Expected_Returns'] = top_5_stocks_buying['Expected_Returns'].apply(lambda x: f"{int(x)}%")
# #     top_5_stocks_selling['Expected_Returns'] = top_5_stocks_selling['Expected_Returns'].apply(lambda x: f"{int(x)}%")

# #     return top_5_stocks_buying, top_5_stocks_selling

# # all_data = pd.concat([load_data(symbol) for symbol in stocks], ignore_index=True)

# # # Get the top 5 buying and selling stocks
# # top_5_buying_stocks, top_5_selling_stocks = predict_and_rank_stocks(all_data)

# # # Reset index and add 1 to start from 1
# # top_5_buying_stocks.index = top_5_buying_stocks.index + 1
# # top_5_selling_stocks.index = top_5_selling_stocks.index + 1

# # st.sidebar.subheader(f"Top 5 Buying Stocks for next {n_months} {month}")
# # buying_stocks_table = top_5_buying_stocks.style.apply(lambda x: ['color: green' if '%' in str(cell) else '' for cell in x])
# # buying_stocks_table = buying_stocks_table.set_table_styles([{
# #     'selector': 'th',
# #     'props': [('color', 'green')]
# # }])
# # st.sidebar.write(buying_stocks_table)

# # # Display the top 5 selling stocks in the sidebar
# # st.sidebar.subheader(f"Top 5 Selling Stocks for next {n_months} {month}")
# # selling_stocks_table = top_5_selling_stocks.style.apply(lambda x: ['color: red' if '%' in str(cell) else '' for cell in x])
# # selling_stocks_table = selling_stocks_table.set_table_styles([{
# #     'selector': 'th',
# #     'props': [('color', 'red')]
# # }])
# # st.sidebar.write(selling_stocks_table)
