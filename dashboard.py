from pandas._config.config import reset_option
import streamlit as st 
import pandas as pd
import plotly
import matplotlib.pyplot as plt
import bt
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
    
    stock_dic_control = {'spy': float(60)/100, 'agg': float(40)/100, stock_choice_3: float(0)/100}
    stock_dic_spy = {'spy': float(100)/100, 'agg': float(0)/100, stock_choice_3: float(0)/100}
    stock_dic_agg = {'spy': float(0)/100, 'agg': float(100)/100, stock_choice_3: float(0)/100}
    
    strategy_ = bt.Strategy('Your Strategy Monthly', 
                                [bt.algos.RunMonthly(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy
    strategy_control = bt.Strategy('60-40', 
                            [bt.algos.RunMonthly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic_control),
                            bt.algos.Rebalance()]) #Creating strategy
    strategy_spy = bt.Strategy('SPY', 
                            [bt.algos.RunMonthly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic_spy),
                            bt.algos.Rebalance()]) #Creating strategy
    strategy_agg = bt.Strategy('AGG', 
                            [bt.algos.RunMonthly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic_agg),
                            bt.algos.Rebalance()]) #Creating strategy
    
    if (rebalances == 'Daily'):
        strategy_ = bt.Strategy('Your Strategy Daily', 
                                [bt.algos.RunDaily(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy

        strategy_control = bt.Strategy('60-40 Daily', 
                            [bt.algos.RunDaily(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic_control),
                            bt.algos.Rebalance()]) #Creating strategy
    elif (rebalances == 'Monthly'):
        strategy_ = bt.Strategy('Your Strategy Monthly', 
                                [bt.algos.RunMonthly(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy
        strategy_control = bt.Strategy('60-40 Monthly', 
                            [bt.algos.RunMonthly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic_control),
                            bt.algos.Rebalance()]) #Creating strategy                        
    elif (rebalances == 'Yearly'):
        strategy_ = bt.Strategy('Your Strategy Yearly', 
                                [bt.algos.RunYearly(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy

        strategy_control = bt.Strategy('60-40 Yearly', 
                            [bt.algos.RunYearly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic_control),
                            bt.algos.Rebalance()]) #Creating strategy
    elif (rebalances == 'None'):
        strategy_ = bt.Strategy('Your Strategy None', 
                                [bt.algos.RunOnce(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy

        strategy_control = bt.Strategy('60-40 None', 
                            [bt.algos.RunOnce(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic_control),
                            bt.algos.Rebalance()]) #Creating strategy
    
    
    test_control = bt.Backtest(strategy_control, data)
    results_control = bt.run(test_control)
    
    test_spy = bt.Backtest(strategy_spy, data)
    results_spy = bt.run(test_spy)
    
    test_agg = bt.Backtest(strategy_agg, data)
    results_agg = bt.run(test_agg)

    
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
        
        #st.dataframe(data)
        

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

    string_con = results_control.to_csv(sep=',') #This creates string of results_control stats 
    df_control = pd.DataFrame([x.split(',') for x in string_con.split('\n')]) # Takes the string and creates a dataframe 
    nan_value = float("NaN") 
    df_control.replace("", nan_value, inplace=True) #lot of empty collumns in dataframe, this makes the empty go to null("NaN")
    df_control.dropna(how='all', axis=1, inplace=True) #delete null collumns
    df_control = df_control.dropna()

    #combining the stats
    stats_combined = pd.concat([df, df_control], axis=1)
    stats_combined.columns = ['Stats', 'Strategy 1', 'Drop', "Strategy 2"]
    stats_combined = stats_combined.drop(['Drop'], axis =1 )
    if (col2_second.button("Display Stats")):
        if(col2_second.button("Hide Stats")):
            yo = 1
        col2_second.dataframe(stats_combined)
   
    col1_second.write(results.display_lookback_returns())


 #Display the Monthly Returns
    #Monthly Returns for Chosen Strat
    key = results._get_backtest(0)
    res_mon = results[key].return_table

    keyc = results_control._get_backtest(0)
    res_con = results_control[keyc].return_table

    something = pd.concat([res_mon, res_con], axis =1)
    something.columns = ['Jan', 'Feb',  'Mar',  'Apr',  'May',  'Jun',  'Jul',  'Aug',  'Sep', 'Oct',  'Nov', 'Dec', 'YTD', 'Jan2', 'Feb2',  'Mar2',  'Apr2',  'May2',  'Jun2',  'Jul2',  'Aug2',  'Sep2', 'Oct2',  'Nov2', 'Dec2', 'YTD2']
    column_names = ['Jan', 'Jan2', 'Feb', 'Feb2', 'Mar', 'Mar2', 'Apr', 'Apr2', 'May', 'May2', 'Jun', 'Jun2', 'Jul', 'Jul2', 'Aug', 'Aug2', 'Sep', 'Sep2', 'Oct', 'Oct2', 'Nov', 'Nov2', 'Dec', 'Dec2', 'YTD', 'YTD2']
    something = something.reindex(columns = column_names)
    something.columns = ['Jan', 'Jan ', 'Feb', 'Feb ', 'Mar', 'Mar ', 'Apr', 'Apr ', 'May', 'May ', 'Jun', 'Jun ', 'Jul', 'Jul ', 'Aug', 'Aug ', 'Sep', 'Sep ', 'Oct', 'Oct ', 'Nov', 'Nov ', 'Dec', 'Dec ', 'YTD', 'YTD '] 
    
    def highlight_cols(x): 
        # copy df to new - original data is not changed 
        df = x.copy() 
        
        # select all values to blue color 
        df.loc[:, :] = 'background-color: blue'
        
        # overwrite values grey color 
        df[['Jan', 'Feb',  'Mar',  'Apr',  'May',  'Jun',  'Jul',  'Aug',  'Sep', 'Oct',  'Nov', 'Dec', 'YTD']] = 'background-color: orange'
        
        # return color df 
        return df  

    st.dataframe(something.style.apply(highlight_cols, axis = None))
   
 #Scatter of Risk vs Return
    #get stats for the spy
    string_spy = results_spy.to_csv(sep=',') #This creates string of results stats 
    df_spy = pd.DataFrame([x.split(',') for x in string_spy.split('\n')]) # Takes the string and creates a dataframe 
    nan_value = float("NaN") 
    df_spy.replace("", nan_value, inplace=True) #lot of empty collumns in dataframe, this makes the empty go to null("NaN")
    df_spy.dropna(how='all', axis=1, inplace=True) #delete null collumns
    df_spy = df_spy.dropna()
   
    #get stats for the agg
    string_agg = results_agg.to_csv(sep=',') #This creates string of results stats 
    df_agg = pd.DataFrame([x.split(',') for x in string_agg.split('\n')]) # Takes the string and creates a dataframe 
    nan_value = float("NaN") 
    df_agg.replace("", nan_value, inplace=True) #lot of empty collumns in dataframe, this makes the empty go to null("NaN")
    df_agg.dropna(how='all', axis=1, inplace=True) #delete null collumns
    df_agg = df_agg.dropna()
    
    #create x axis list()
    xaxis_vol = []
    xaxis_vol.append(float(df.iloc[30][1].replace('%', '')))
    xaxis_vol.append(float(df_control.iloc[30][1].replace('%', '')))
    xaxis_vol.append(float(df_spy.iloc[30][1].replace('%', '')))
    xaxis_vol.append(float(df_agg.iloc[30][1].replace('%', '')))
    
    yaxis_return = []
    yaxis_return.append(float(df.iloc[29][1].replace('%', '')))
    yaxis_return.append(float(df_control.iloc[29][1].replace('%', '')))
    yaxis_return.append(float(df_spy.iloc[29][1].replace('%', '')))
    yaxis_return.append(float(df_agg.iloc[29][1].replace('%', '')))


    labels_ = ['Your Strategy', '60-40', 'Spy', 'Agg']
    color=['tab:orange','tab:blue','tab:red', 'tab:green']
    fig, ax = plt.subplots()
    for x, y, c, lb in zip(xaxis_vol, yaxis_return, color, labels_):
      ax.scatter(x, y, color=c, label = lb)
    ax.set_title('Risk Vs. Return')
    ax.set_ylabel("Monthly Mean (ann.) %")
    ax.set_xlabel("Monthly Vol (ann.) %")
    ax.legend()
    col2_second.pyplot(fig)
    

    

    
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
    st.write(df.iloc[7])
    st.dataframe(df.iloc[0])
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



    
    

    





