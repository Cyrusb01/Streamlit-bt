from pandas._config.config import reset_option
import streamlit as st 
import pandas as pd
import numpy as np
import plotly
import matplotlib.pyplot as plt
import bt
from utils import fmtp, fmtpn
from tabulate import tabulate


st.set_page_config(layout="wide") #makes page wider 

word = "Dashboard"
st.title(word)


class WeighSpecified(bt.Algo):
# '''
# Sets temp['weights'] based on a provided dict of ticker:weights.
# Sets the weights based on pre-specified targets.
# Args:
# * weights (dict): target weights -> ticker: weight
# Sets:
# * weights
# '''
    def __init__(self, **weights):
        super(WeighSpecified, self).__init__()
        self.weights = weights

    def __call__(self, target):
        # added copy to make sure these are not overwritten
        target.temp["weights"] = self.weights.copy()
        return True





st.sidebar.write("Options")
option = st.sidebar.selectbox("Select and option", ('Chart', 'Optomized',  'Chart-Slider'))
start_date = '2017-01-01'

if ( option == 'Chart'):
    
 #beta collumns and containers 
    col1_s, col2_s = st.sidebar.beta_columns(2)
    col1, col2 = st.beta_columns((2, 1))
    col1_header = col1.beta_container()
    col2_header = col2.beta_container()
    col1_graph  = col1.beta_container()
    col2_graph  = col2.beta_container()
    col1_second = col1.beta_container()
    col2_second = col2.beta_container()
    
 #Sidebar Inputs
    stock_choice_1 = col1_s.text_input( "Enter Ticker 1", value = 'SPY', max_chars= 8) #get ticker
    percent_1 = col2_s.text_input( "% Allocation", value = 55, max_chars= 3, ) # get percent
    stock_choice_1 = stock_choice_1.lower() #bt likes lower case 
    data_1 = bt.get(stock_choice_1, start = start_date) # get the data 

    stock_choice_2 = col1_s.text_input( "Enter Ticker", value = 'AGG', max_chars= 8)
    percent_2 = col2_s.text_input( "% Allocation", value = 40, max_chars= 3)
    stock_choice_2 = stock_choice_2.lower()
    data_2 = bt.get(stock_choice_2, start = start_date)

    stock_choice_3 = col1_s.text_input( "Enter Ticker", value = 'BTC-USD', max_chars= 8)
    percent_3 = col2_s.text_input( "% Allocation", value = 5, max_chars= 3)
    stock_choice_3 = stock_choice_3.lower()
    data_3 = bt.get(stock_choice_3, start = start_date)

    #allows us to combine the datasets to account for the difference in reg vs. Crypto 
    data = data_1.join(data_2, how='outer')
    data = data.join(data_3, how= 'outer')
    data = data.dropna()
    
    #need the '-' in cryptos to get the data, but bt needs it gone to work
    stock_choice1 = stock_choice_1.replace('-', '')
    stock_choice2 = stock_choice_2.replace('-', '')
    stock_choice3 = stock_choice_3.replace('-', '')

 #Buttons
    rebalances = col1_graph.selectbox("Rebalancing Timeline", ('Daily', 'Monthly', 'Yearly', 'None'))
 #creating strategy and backtest
    stock_list = stock_choice_1 +',' + stock_choice_2 + ',' + stock_choice_3 #list of tickers to get data for 
    stock_dic = {stock_choice_1: float(percent_1)/100, stock_choice_2: float(percent_2)/100, stock_choice3: float(percent_3)/100} #dictonary for strat
    
    stock_dic_control = {stock_choice_1: float(60)/100, stock_choice_2: float(40)/100, stock_choice_3: float(0)/100}
    
    strategy_ = bt.Strategy('Your Strategy Monthly', 
                                [bt.algos.RunMonthly(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy
    
    if (rebalances == 'Daily'):
        strategy_ = bt.Strategy('Your Strategy Daily', 
                                [bt.algos.RunDaily(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy
    elif (rebalances == 'Monthly'):
        strategy_ = bt.Strategy('Your Strategy Monthly', 
                                [bt.algos.RunMonthly(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy
    elif (rebalances == 'Yearly'):
        strategy_ = bt.Strategy('Your Strategy Yearly', 
                                [bt.algos.RunYearly(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy
    elif (rebalances == 'None'):
        strategy_ = bt.Strategy('Your Strategy None', 
                                [bt.algos.RunOnce(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy
    
    strategy_control = bt.Strategy('60-40 Monthly', 
                            [bt.algos.RunMonthly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic_control),
                            bt.algos.Rebalance()]) #Creating strategy
    
    test_control = bt.Backtest(strategy_control, data)
    results_control = bt.run(test_control)
    
    test = bt.Backtest(strategy_, data)
    results = bt.run(test)

 #line chart
    ser = results._get_series(None).rebase()
    ser2 = results_control._get_series(None).rebase()
    result_final = pd.concat([ser, ser2], axis=1)
    col1_header.header("Returns Graph")
    col1_graph.line_chart(result_final)

 #pie chart
    if (rebalances == 'None'): #pie chart is wrong since no rebalances
        key = results._get_backtest(0)
        filter = None

        if filter is not None:
            data = results.backtests[key].security_weights[filter]
        else:
            data = results.backtests[key].security_weights

        percent_1 = str(round(data[stock_choice1].iloc[-1]*100)) 
        percent_2 = str(round(data[stock_choice2].iloc[-1]*100))
        percent_3 = str(round(data[stock_choice3].iloc[-1]*100)) 
        
        st.dataframe(data)
        

    labels = []
    labels.append(stock_choice_1.upper() + " " + percent_1 + "%")
    labels.append(stock_choice_2.upper() + " " + percent_2 + "%")
    labels.append(stock_choice_3.upper() + " " + percent_3 + "%")
    percentages = []
    percentages.append(percent_1)
    percentages.append(percent_2)
    percentages.append(percent_3)

    fig, ax1 = plt.subplots()
    ax1.pie(percentages,  shadow=True, startangle=90)
    plt.legend( labels, loc="best")
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    col2_header.header("Pie Chart")
    col2_header.pyplot(fig)

 #Display Results
    string_res = results.to_csv(sep=',') #This creates string of results stats 
    df = pd.DataFrame([x.split(',') for x in string_res.split('\n')]) # Takes the string and creates a dataframe 
    nan_value = float("NaN") 
    df.replace("", nan_value, inplace=True) #lot of empty collumns in dataframe, this makes the empty go to null("NaN")
    df.dropna(how='all', axis=1, inplace=True) #delete null collumns
    df = df.dropna()
    col2_second.dataframe(df)

 #Display the Monthly Returns
    key = results._get_backtest(0)
    data = [['Year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'YTD']]
    for k in results[key].return_table.index:
        r = results[key].return_table.loc[k].values
        data.append([k] + [fmtpn(x) for x in r])
    month_str = tabulate(data, headers='firstrow')
    col1_second.text(month_str)
    
elif ( option == 'Chart-Slider'):
    
    col1_s, col2_s = st.sidebar.beta_columns(2)
    col1, col2 = st.beta_columns(2)
    row1_c1 = col1.beta_container()
    row2_c1= col1.beta_container()
    
    
    #Sidebar Inputs In case want to 
    # stock_choice_1 = col1_s.text_input( "Enter Ticker 1", value = 'SPY', max_chars= 8)
    # percent_1 = col2_s.text_input( "% Allocation", value = 55, max_chars= 3, )
    # stock_choice_1 = stock_choice_1.lower()

    # stock_choice_2 = col1_s.text_input( "Enter Ticker", value = 'AGG', max_chars= 8)
    # percent_2 = col2_s.text_input( "% Allocation", value = 40, max_chars= 3)
    # stock_choice_2 = stock_choice_2.lower()

    # stock_choice_3 = col1_s.text_input( "Enter Ticker", value = 'MSFT', max_chars= 8)
    # percent_3 = col2_s.text_input( "% Allocation", value = 5, max_chars= 3)
    # stock_choice_3 = stock_choice_3.lower()

    slider_input = row2_c1.slider('percent', min_value= 0, max_value= 10, value= 5 )
    
    stock_choice_1 = 'spy'
    stock_choice_2 = 'agg'
    stock_choice_3 = 'btc-usd'
    
    percent_1 = 60-slider_input
    percent_2 = 40
    percent_3 = slider_input

    data_1 = bt.get(stock_choice_1, start = start_date)
    data_2 = bt.get(stock_choice_2, start = start_date)
    data_3 = bt.get(stock_choice_3, start = start_date)

    data = data_1.join(data_2, how='outer')
    data = data.join(data_3, how= 'outer')
    data = data.dropna()

    stock_choice_3 = stock_choice_3.replace('-', '')

    
    
    stock_list = stock_choice_1 +',' + stock_choice_2 + ',' + stock_choice_3 #list of tickers to get data for 
    stock_dic = {stock_choice_1: float(percent_1)/100, stock_choice_2: float(percent_2)/100, stock_choice_3: float(percent_3)/100} #dictonary for strat
    stock_dic_control = {stock_choice_1: float(60)/100, stock_choice_2: float(40)/100, stock_choice_3: float(0)/100}
    
    strategy_ = bt.Strategy('Strategy 1', 
                            [bt.algos.RunMonthly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic),
                            bt.algos.Rebalance()]) #Creating strategy 

    strategy_control = bt.Strategy('60-40', 
                            [bt.algos.RunMonthly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic_control),
                            bt.algos.Rebalance()]) #Creating strategy
    
    test_control = bt.Backtest(strategy_control, data)
    results_control = bt.run(test_control)
    
    test = bt.Backtest(strategy_, data)
    results = bt.run(test)

 #line chart
    ser = results._get_series(None).rebase()
    ser2 = results_control._get_series(None).rebase()
    result_final = pd.concat([ser, ser2], axis=1)
    #st.dataframe(result_final)
    row1_c1.header("Returns Graph")
    row1_c1.line_chart(result_final)

 #Pie Chart Data 
    labels = []
    labels.append(stock_choice_1.upper() + " " + str(percent_1) + "%")
    labels.append(stock_choice_2.upper() + " " + str(percent_2) + "%")
    labels.append(stock_choice_3.upper() + " " + str(percent_3) + "%")
    percentages = []
    percentages.append(percent_1)
    percentages.append(percent_2)
    percentages.append(percent_3)

 #Ploting the pie chart 
    fig, ax1 = plt.subplots()
    ax1.pie(percentages,  shadow=True, startangle=90)
    plt.legend( labels, loc="best")
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    col2.pyplot(fig)

 #Display Results
    string_res = results.to_csv(sep=',') #This creates string of results stats 
    df = pd.DataFrame([x.split(',') for x in string_res.split('\n')]) # Takes the string and creates a dataframe 
    nan_value = float("NaN") 
    df.replace("", nan_value, inplace=True) #lot of empty collumns in dataframe, this makes the empty go to null("NaN")
    df.dropna(how='all', axis=1, inplace=True) #delete null collumns
    df = df.dropna()
    st.dataframe(df)

elif (option == "Optomized"):
    
    #Get data 
    symbols = "spy,iwm,eem,efa,gld,agg,hyg"
    crypto_symbols = "btc-usd,eth-usd"
    etf_data = bt.get(symbols, start='1993-01-01')
    crypto_data = bt.get(crypto_symbols, start='2016-01-01') 

    #Merge into dataframe
    data = crypto_data.join(etf_data, how='outer')
    data = data.dropna()

    #daily optimal
    returns = data.to_log_returns().dropna()
    daily_opt = returns.calc_mean_var_weights().as_format(".2%")
    st.header("Optimal on Daily Data")
    st.dataframe(daily_opt)

    #Quarterly Optimal 
    quarterly_rets= data.asfreq("Q",method='ffill').to_log_returns().dropna()
    quart_opt = quarterly_rets.calc_mean_var_weights().as_format(".2%")
    st.header("Optimal on Quarterly Data")
    st.dataframe(quart_opt)



    
    

    





