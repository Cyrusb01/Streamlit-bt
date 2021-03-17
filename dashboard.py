from pandas._config.config import reset_option
import streamlit as st 
import pandas as pd
import plotly
import matplotlib.pyplot as plt
import bt
import plotly.express as px
from tabulate import tabulate 
from functions import alloc_table, balance_table, monthly_returns_table, plot_pie, display_stats_combined, results_to_df, highlight_cols, scatter_plot, short_stats_table, sum_table, monthly_table



st.set_page_config(layout="wide") #makes page wider 

# st.markdown(
#   """
#   <style>
#   .main {
#   background-color: #478f7c;
#   }
#   </style>
#   """,
#   unsafe_allow_html=True
# )


word = "Dashboard"
#st.title(word)


class WeighSpecified(bt.Algo):

   def __init__(self, **weights):
      super(WeighSpecified, self).__init__()
      self.weights = weights

   def __call__(self, target):
      # added copy to make sure these are not overwritten
      target.temp["weights"] = self.weights.copy()
      return True

st.sidebar.write("Options")
option = st.sidebar.selectbox("Select and option", ('Chart-work', 'Chart', 'Optomized',  'Chart-Slider'))
start_date = '2017-01-01'


if ( option == 'Chart'):
 #Beta Columns and Containers 
   col1_s, col2_s = st.sidebar.beta_columns(2)
   col1, col2 = st.beta_columns((2, 1))
   col1_header = col1.beta_container()
   col2_header = col2.beta_container()
   col1_graph  = col1.beta_container()
   col2_graph  = col2.beta_container()
   col1_second = col1.beta_container()
   col2_second = col2.beta_container()
    
 #Sidebar Inputs
   stock_choice_1 = col1_s.selectbox( "Ticker 1", ('spy', 'efa', 'iwm', 'vwo', 'ibb', 'agg', 'hyg', 'gld', 'slv', 'tsla', 'aapl', 'msft', 'qqq', 'btc-usd', 'eth-usd')) #get ticker
   percent_1 = col2_s.text_input( "% Allocation", value = 55, max_chars= 3, ) # get percent
   stock_choice_1 = stock_choice_1.lower() #bt likes lower case 
   data_1 = bt.get(stock_choice_1, start = start_date) # get the data 

   stock_choice_2 = col1_s.selectbox( "Ticker 2", ('agg', 'spy', 'efa', 'iwm', 'vwo', 'ibb', 'hyg', 'gld', 'slv', 'tsla', 'aapl', 'msft', 'qqq', 'btc-usd', 'eth-usd'))
   percent_2 = col2_s.text_input( "% Allocation", value = 40, max_chars= 3)
   stock_choice_2 = stock_choice_2.lower()
   data_2 = bt.get(stock_choice_2, start = start_date)

   stock_choice_3 = col1_s.selectbox( "Ticker 3", ('btc-usd', 'spy', 'efa', 'iwm', 'vwo', 'ibb', 'agg', 'hyg', 'gld', 'slv', 'tsla', 'aapl', 'msft', 'qqq', 'eth-usd'))
   percent_3 = col2_s.text_input( "% Allocation", value = 5, max_chars= 3)
   stock_choice_3 = stock_choice_3.lower()
   data_3 = bt.get(stock_choice_3, start = start_date)

   #allows us to combine the datasets to account for the difference in reg vs. Crypto 
   data = data_1.join(data_2, how='outer')
   data = data.join(data_3, how= 'outer')
   data = data.dropna()
   
   #need the '-' in cryptos to get the data, but bt needs it gone to work
   stock_choice_1 = stock_choice_1.replace('-', '')
   stock_choice_2 = stock_choice_2.replace('-', '')
   stock_choice_3 = stock_choice_3.replace('-', '')

 #Buttons
   rebalances = col1_graph.selectbox("Rebalancing Timeline", ('Daily', 'Monthly', 'Yearly', 'None'))

 #creating Strategy and Backtest
   stock_list = stock_choice_1 +',' + stock_choice_2 + ',' + stock_choice_3 #list of tickers to get data for 
   stock_list_plt = [stock_choice_1, stock_choice_2, stock_choice_3]
   percent_list = [percent_1, percent_2, percent_3]
   stock_dic = {stock_choice_1: float(percent_1)/100, stock_choice_2: float(percent_2)/100, stock_choice_3: float(percent_3)/100} #dictonary for strat
   
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

 #Line Chart
   ser = results._get_series(None).rebase() #gets all the daily balances as a series 
   ser2 = results_control._get_series(None).rebase()

   result_final = pd.concat([ser, ser2], axis=1) #makes dataframe for both series 
   
   col1_header.header("Returns Graph")
   col1_graph.line_chart(result_final)

 #Pie Chart
   if (rebalances == 'None'): #pie chart is wrong since no rebalances
   
      key = results._get_backtest(0) #Chunk of code is how to get the weights, straight from doc
      filter = None
      if filter is not None:
         data = results.backtests[key].security_weights[filter]
      else:
         data = results.backtests[key].security_weights
         
      for i in range(len(percent_list)): #puts all the right values into the percent list 
         percent_list[i] = str(round(data[stock_list_plt[i]].iloc[-1]*100))

   fig = plot_pie(stock_list_plt, percent_list)
   col2_header.header("Pie Chart")
   col2_header.pyplot(fig)

 #Display Results
    
   results_list = [results, results_control, results_spy, results_agg] #list of results objects
   results_df = results_to_df(results_list) #list of the results but now in dataframe 

   stats = display_stats_combined(results_list)
   
   if (col2_second.button("Display Stats")):#button logic 
      if(col2_second.button("Hide Stats")):
         do_nothing = 0 #literally do nothing
      col2_second.dataframe(stats)

   col1_second.write(results.display_lookback_returns()) # displays the shortened stats

 #Display the Monthly Returns

   mon_table = monthly_returns_table(results_list)
   st.dataframe(mon_table)
   
 #Scatter of Risk vs Return

   fig = scatter_plot(results_df) #scatter function in functions
   col2_second.plotly_chart(fig)
    
 #Allocation Table
   rebalance_list = [3, 4, 5]
   fig = alloc_table(stock_list_plt, percent_list, rebalance_list)
   col2.plotly_chart(fig)

elif ( option == 'Chart-Slider'):
    
 #Beta Columns

   col1_s, col2_s = st.sidebar.beta_columns(2)
   col1, col2 = st.beta_columns((2, 1))
   
   col1_header = col1.beta_container()
   col2_header = col2.beta_container()

   row1_c1 = col1.beta_container()
   row2_c1= col1.beta_container()

   col1_graph  = col1.beta_container()
   col2_graph  = col2.beta_container()

   col1_second = col1.beta_container()
   col2_second = col2.beta_container()

 #Creating Strategy and Backtest 
   slider_input = row2_c1.slider('Percent of BTC-USD in Portfolio', min_value= 0, max_value= 10, value= 5 )
    
   #hardcoding in the values since we dont have user input
   stock_choice_1 = 'spy'
   stock_choice_2 = 'agg'
   stock_choice_3 = 'btc-usd'
   stock_list_plt = [stock_choice_1, stock_choice_2, stock_choice_3]
    
   percent_1 = 60-slider_input
   percent_2 = 40
   percent_3 = slider_input
   percent_list = [percent_1, percent_2, percent_3]

   #get data seperatly because crypto and reg data dont work together 
   data_1 = bt.get(stock_choice_1, start = start_date)
   data_2 = bt.get(stock_choice_2, start = start_date)
   data_3 = bt.get(stock_choice_3, start = start_date)
   
   #Allows for crypto and stock to be in a dataframe
   data = data_1.join(data_2, how='outer')
   data = data.join(data_3, how= 'outer')
   data = data.dropna()

   stock_choice_3 = stock_choice_3.replace('-', '') #get data with btc-usd but then bt likes btcusd

    
    
   stock_dic         = {stock_choice_1: float(percent_1)/100, stock_choice_2: float(percent_2)/100, stock_choice_3: float(percent_3)/100} #dictonary for strat
   stock_dic_control = {stock_choice_1: float(60)/100, stock_choice_2: float(40)/100, stock_choice_3: float(0)/100} #60-40
   stock_dic_spy     = {'spy': float(100)/100, 'agg': float(0)/100, stock_choice_3: float(0)/100} #all spy
   stock_dic_agg     = {'spy': float(0)/100, 'agg': float(100)/100, stock_choice_3: float(0)/100} #all agg
   
   
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
   
   test_control = bt.Backtest(strategy_control, data)
   results_control = bt.run(test_control)

   test_spy = bt.Backtest(strategy_spy, data)
   results_spy = bt.run(test_spy)
   
   test_agg = bt.Backtest(strategy_agg, data)
   results_agg = bt.run(test_agg)
   
   test = bt.Backtest(strategy_, data)
   results = bt.run(test)

 #Line Chart

   ser = results._get_series(None).rebase()
   ser2 = results_control._get_series(None).rebase()
   result_final = pd.concat([ser, ser2], axis=1)
   col1_header.header("Returns Graph")
   col1_header.line_chart(result_final)

 #Pie Chart 
   
   fig = plot_pie(stock_list_plt, percent_list)
   col2_header.header("Pie Chart")
   col2_header.pyplot(fig)

 #Display Results
   results_list = [results, results_control, results_spy, results_agg] #list of results objects
   results_df = results_to_df(results_list) #list of the results but now in dataframe 

   stats = display_stats_combined(results_list)

   if (col2_second.button("Display Stats")):
      if(col2_second.button("Hide Stats")):
         yo = 1
      col2_second.dataframe(stats)

   col1_second.write(results.display_lookback_returns())

 #Display the Monthly Returns

   mon_table = monthly_returns_table(results_list)
   st.dataframe(mon_table.style.apply(highlight_cols, axis = None))

 #Scatter of Risk vs Return
   fig = scatter_plot(results_df) #scatter function in functions
   col2_second.pyplot(fig)

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



if ( option == 'Chart-work'):
 #Beta Columns and Containers 
   col1_s, col2_s = st.sidebar.beta_columns(2)
   col1, col2 = st.beta_columns((1, 2))
   col1_top = col1.beta_container()
   col1_middle = col1.beta_container()
   col1_bot = col1.beta_container()
   col2t =col2.beta_container()
   col2b =col2.beta_container()
   
   col1_header = col1.beta_container()
   col2_header = col2.beta_container()
   col1_graph  = col1.beta_container()
   col2_graph  = col2.beta_container()
   col1_second = col1.beta_container()
   col2_second = col2.beta_container()
   table = st.beta_container()
    
 #Sidebar Inputs
   stock_choice_1 = col1_s.selectbox( "Ticker 1", ('spy', 'efa', 'iwm', 'vwo', 'ibb', 'agg', 'hyg', 'gld', 'slv', 'tsla', 'aapl', 'msft', 'qqq', 'btc-usd', 'eth-usd')) #get ticker
   percent_1 = col2_s.text_input( "% Allocation", value = 55, max_chars= 3, ) # get percent
   stock_choice_1 = stock_choice_1.lower() #bt likes lower case 
   data_1 = bt.get(stock_choice_1, start = start_date) # get the data 

   stock_choice_2 = col1_s.selectbox( "Ticker 2", ('agg', 'spy', 'efa', 'iwm', 'vwo', 'ibb', 'hyg', 'gld', 'slv', 'tsla', 'aapl', 'msft', 'qqq', 'btc-usd', 'eth-usd'))
   percent_2 = col2_s.text_input( "% Allocation", value = 40, max_chars= 3)
   stock_choice_2 = stock_choice_2.lower()
   data_2 = bt.get(stock_choice_2, start = start_date)

   stock_choice_3 = col1_s.selectbox( "Ticker 3", ('btc-usd', 'spy', 'efa', 'iwm', 'vwo', 'ibb', 'agg', 'hyg', 'gld', 'slv', 'tsla', 'aapl', 'msft', 'qqq', 'eth-usd'))
   percent_3 = col2_s.text_input( "% Allocation", value = 5, max_chars= 3)
   stock_choice_3 = stock_choice_3.lower()
   data_3 = bt.get(stock_choice_3, start = start_date)

   #allows us to combine the datasets to account for the difference in reg vs. Crypto 
   data = data_1.join(data_2, how='outer')
   data = data.join(data_3, how= 'outer')
   data = data.dropna()

   data_con = bt.get('spy,agg,gme', start = start_date)
   
   #need the '-' in cryptos to get the data, but bt needs it gone to work
   stock_choice_1 = stock_choice_1.replace('-', '')
   stock_choice_2 = stock_choice_2.replace('-', '')
   stock_choice_3 = stock_choice_3.replace('-', '')

 #Buttons
   #rebalances = col1_graph.selectbox("Rebalancing Timeline", ('Daily', 'Monthly', 'Yearly', 'None'))
   rebalances = 'Monthly'

 #creating Strategy and Backtest
   stock_list = stock_choice_1 +',' + stock_choice_2 + ',' + stock_choice_3 #list of tickers to get data for 
   stock_list_plt = [stock_choice_1, stock_choice_2, stock_choice_3]
   percent_list = [percent_1, percent_2, percent_3]
   stock_dic = {stock_choice_1: float(percent_1)/100, stock_choice_2: float(percent_2)/100, stock_choice_3: float(percent_3)/100} #dictonary for strat
   
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
   
   
   test_control = bt.Backtest(strategy_control, data_con)
   results_control = bt.run(test_control)
   
   test_spy = bt.Backtest(strategy_spy, data_con)
   results_spy = bt.run(test_spy)
   
   test_agg = bt.Backtest(strategy_agg, data_con)
   results_agg = bt.run(test_agg)

   
   test = bt.Backtest(strategy_, data)
   results = bt.run(test)

 #Line Chart
   ser = results._get_series(None).rebase() #gets all the daily balances as a series 
   ser2 = results_control._get_series(None).rebase()
   
   result_final = pd.concat([ser, ser2], axis=1) #makes dataframe for both series 
   #df = px.data.ser
   fig = px.line(result_final, labels=dict(index="", value="", variable=""),
                  title="Portfolio Performance",
                  color_discrete_map={ # replaces default color mapping by value
                      "Your Strategy Monthly": '#66F3EC', "60-40 Monthly": '#67F9AF'
                  },
                  template="simple_white"
                  )
   fig.update_yaxes( # the y-axis is in dollars
    tickprefix="$", showgrid=True
   )
   fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y= -.25,
    xanchor="right",
    x=.82
   ),
   title={
        'text': "Portfolio Performance",
        'y':.99,
        'x':0.6,
        'xanchor': 'center',
        'yanchor': 'top'},)
   #fig.update_layout(height = 500)
   fig.update_layout(margin = dict(l=0, r=0, t=20, b=10))
   fig.update_layout(width = 700)
   col2b.plotly_chart(fig)

  
   
   #col1_header.header("Returns Graph")
   #col1_graph.line_chart(result_final)

 #Pie Chart
   if (rebalances == 'None'): #pie chart is wrong since no rebalances
   
      key = results._get_backtest(0) #Chunk of code is how to get the weights, straight from doc
      filter = None
      if filter is not None:
         data = results.backtests[key].security_weights[filter]
      else:
         data = results.backtests[key].security_weights
         
      for i in range(len(percent_list)): #puts all the right values into the percent list 
         percent_list[i] = str(round(data[stock_list_plt[i]].iloc[-1]*100))

   fig = plot_pie(stock_list_plt, percent_list)
   fig.set_facecolor('#fafafa')
   col1_top.header("PORTFOLIO ALLOCATION")
   col1_top.pyplot(fig)

 #Display Results
    
   results_list = [results, results_control, results_spy, results_agg] #list of results objects
   results_df = results_to_df(results_list) #list of the results but now in dataframe 

   stats = display_stats_combined(results_list)
   
  #  if (col2_second.button("Display Stats")):#button logic 
  #     if(col2_second.button("Hide Stats")):
  #        do_nothing = 0 #literally do nothing
      #col2_second.dataframe(stats)

   #col1_second.write(results.display_lookback_returns()) # displays the shortened stats

 #Display the Monthly Returns

   mon_table = monthly_returns_table(results_list)
   #st.dataframe(mon_table.style.apply(highlight_cols, axis = None))
   
 #Scatter of Risk vs Return

   fig = scatter_plot(results_df) #scatter function in functions
   fig.update_layout(width = 750, height = 500)
   col2t.plotly_chart(fig, width = 750, height =500)
    
 #Allocation Table
   rebalance_list = [3, 4, 5]
   fig = alloc_table(stock_list_plt, percent_list, rebalance_list)
   fig.update_layout(width = 400, height = 130)
   #col1.plotly_chart(fig, width = 400, height = 130)

 #Balance Table
   fig = balance_table(results, results_control)
   fig.update_layout(width = 400, height = 75)
   col1.plotly_chart(fig, width = 400, height = 75)

 #Short Stats Table
   fig = short_stats_table(results_list)
   fig.update_layout(width = 380, height = 300)
   col1.header("Return Statistics")
   col1.plotly_chart(fig, width = 380, height = 300)

 #Monthly Table 
   my_expander = st.beta_expander("Show Monthly Returns")
   fig = monthly_table(results_list)
   fig.update_layout(width = 1100)
   my_expander.plotly_chart(fig, width = 1100)




