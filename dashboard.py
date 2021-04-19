from logging import error
from pandas._config.config import reset_option
import streamlit as st 
import pandas as pd
import plotly
import matplotlib.pyplot as plt
import bt
import plotly.express as px
from streamlit.elements.data_frame import _get_custom_display_values
from tabulate import tabulate 
from functions import alloc_table, balance_table, line_chart, monthly_returns_table, optomize_table, optomize_table_combine, plot_pie, display_stats_combined, results_to_df, highlight_cols, scatter_plot, short_stats_table, stats_table, sum_table, monthly_table, plotly_pie

# [theme]
# primaryColor="#a90bfe"
# backgroundColor="#131c4f"
# secondaryBackgroundColor="#00eead"
# textColor="#ffffff"
# font="serif"


st.set_page_config(layout="wide") #makes page wider 

@st.cache
def get_data(dontchange):
  s_data = bt.get('spy,efa,iwm,vwo,ibb,agg,hyg,slv,tsla,aapl,msft,qqq', start = '2017-01-01') #took out gold for now because of error
  #cry_data = bt.get('btc-usd,eth-usd', start = '2017-01-01')
  btc = bt.get('btc-usd', start = '2017-01-01') #had to implement this seperatly because eth data got cut out one day on yahoo finance 
  eth = bt.get('eth-usd', start = '2017-01-01')
  data_cache = btc.join(s_data, how='outer')
  data_cache = eth.join(data_cache, how='outer')
  data_cache = data_cache.dropna()
  return data_cache

dontchange = 0
data = get_data(dontchange)

@st.cache
def calculate_controls(dontchange):
  stock_dic_control = {'spy': float(60)/100, 'agg': float(40)/100, 'vwo': float(0)/100}
  stock_dic_spy = {'spy': float(100)/100, 'agg': float(0)/100, 'vwo': float(0)/100}
  stock_dic_agg = {'spy': float(0)/100, 'agg': float(100)/100, 'vwo': float(0)/100}
                            
  strategy_control = bt.Strategy('60-40 Portfolio', 
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

  results_return = [results_control, results_spy, results_agg]

  return results_return 

returns = calculate_controls(dontchange)

results_control = returns[0]
results_spy = returns[1]
results_agg = returns[2]
  

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

c, d, e, f, g = st.sidebar.beta_columns((1,1,1,1,1))
d.image('Pictures/onramplogo.png', width = 150)

st.sidebar.write("Navigation")


option = st.sidebar.radio("Select a Dashboard", ( 'Home','Custom Strategy Dashboard' , 'BTC Portfolio Dashboard', 'Portfolio Optimizer'))
start_date = '2017-01-01'


if (option == 'Home'):
  results_list = [results_control, results_spy, results_agg]
  st.markdown("<h1 style='text-align: center; color: black;'>Home</h1>", unsafe_allow_html=True)
  st.header("This is a financial dashboard tool to simulate and backtest different portfolios of your choosing")
  #custom = st.beta_container()
  #col1, col2 = st.beta_columns((1,1))
  
    
  st.markdown('##')
  st.markdown("<h2 style='text-align: center; color: black;'>Custom Strategy Dashboard</h2>", unsafe_allow_html=True)
  col1, col2 = st.beta_columns((1,1))
  
  col1.markdown('##')
  col2.markdown('##')
  col1.markdown('* Build a custom strategy with assets and thier allocations ')
  col1.markdown('* Automatically backtest the strategy and see performance ')
  col2.markdown('* View the statistics and graphics of the strategy you built')
  col2.markdown('* View the statistics and graphics of the strategy you built')
  st.subheader('How to use the Custom Strategy Dashboard:')
  st.markdown("##")
  picture1, spacer, picture2, picture3 = st.beta_columns((3,1, 4,1))
  picture1.markdown("Create a strategy by choosing assets and their allocations. ->")
  picture1.markdown('#')
  picture1.image('Pictures/input.PNG')
  picture2.markdown("Analyze the statistics and performance of your newly created strategy")
  picture2.markdown('* Ex. Use line chart to compare returns of popular porfolios/assets to the created one')
  picture2.image("Pictures/linechart.PNG")

  #----------------------------------------------BTC Portfolio Dashboard----------------------------------------------------------------------------------------------------
  st.markdown('##')
  st.markdown("<h2 style='text-align: center; color: black;'>BTC Portfolio Dashboard</h2>", unsafe_allow_html=True)
  col1, col2 = st.beta_columns((1,1))
  
  col1.markdown('##')
  col2.markdown('##')
  col1.markdown('* Experiment with bitcoin in a traditional 60%(Stocks) 40%(Bonds) Portfolio ')
  col1.markdown('* Automatically backtest the strategy and see performance ')
  col2.markdown('* View the statistics and graphics of the strategy you built')
  col2.markdown('* View the statistics and graphics of the strategy you built')
  st.subheader('How to use the BTC Portfolio Dashboard:')
  st.markdown("##")
  picture1, spacer, picture2, picture3 = st.beta_columns((3,1, 4,1))
  picture1.markdown("Use slider to change bitcoin allocation in the portfolio ->")
  picture1.markdown('#')
  picture1.image('Pictures/btcdashboard.PNG')
  picture2.markdown("See how advantageous adding bitcoin to a portfolio can be.")
  picture2.markdown('* Ex. Use line chart to compare returns of strategy with btc to one without')
  picture2.image("Pictures/btcline.PNG")

  #----------------------------------------------Portfolio Optimizer ----------------------------------------------------------------------------------------------------
  st.markdown('##')
  st.markdown("<h2 style='text-align: center; color: black;'>Portfolio Optimizer Dashboard</h2>", unsafe_allow_html=True)
  col1, col2 = st.beta_columns((1,1))
  
  col1.markdown('##')
  col2.markdown('##')
  col1.markdown('* Optimizes portfolios based on the Efficient Fronteir')
  col1.markdown('* Focuses on optimal portfolio allocations based on chosen assets')
  col2.markdown('* Enter the stocks you are investing in, and find optimal allocations')
  col2.markdown('* View the statistics of optimized portfolios')
  st.subheader('How to use the Portfolio Optimizer Dashboard:')
  st.markdown("##")
  picture1, spacer, picture2, picture3 = st.beta_columns((3,1, 4,1))
  picture1.markdown("Enter in assets of your choice, and choose Reblance Frequency->")
  picture1.markdown('*For more information on frequency choices, read on the dashboard itself')
  picture1.markdown('#')
  picture1.image('Pictures/optimizerinput.PNG')
  picture2.markdown("Compare and analyze the perfomance and statistics of the optimized portfolio")
  picture2.markdown('* Ex. Use line chart to compare returns of optimized portfolio to equally weighted ')
  picture2.image("Pictures/optimizerline.PNG")
  




  #st.markdown("<h2 style='text-align: center; color: black;'>BTC Porfolio Dashboard</h2>", unsafe_allow_html=True)

if ( option == 'BTC Portfolio Dashboard'):
 #styling 
   st.markdown(
            f"""
   <style>
        .reportview-container .main .block-container{{
            padding-top: {0}rem;
            padding-right: {0}rem;
            padding-left: {1}rem;
            padding-bottom: {0}rem;
        }}
    </style>
    """,
            unsafe_allow_html=True,
        )
   
   st.markdown("<h1 style='text-align: center; color: black;'>Experiment with Bitcoin in your Portfolio</h1>", unsafe_allow_html=True)
 
 #Beta Columns
   col1_pie, col_spacer, col_description, spacer = st.beta_columns((5,1,8, 2))
   col1_stats, col2_scat = st.beta_columns((2, 3))
   col2_scat_t = col2_scat.beta_container()
   col2_scat_b = col2_scat.beta_container()

   col1_pie_t = col1_pie.beta_container()
   col1_pie_b = col1_pie.beta_container()

   col1_stats_t = col1_stats.beta_container()
   col1_stats_b = col1_stats.beta_container()
   col1, col2 = st.beta_columns((1, 2))
   col3, col4, col5 = st.beta_columns((1,1,3))

   col1_top = col1.beta_container()
   col1_middle = col1.beta_container()
   col1_bot = col1.beta_container()
   col2t =col2.beta_container()
   col2b =col2.beta_container()

   table = st.beta_container()

 #Creating Strategy and Backtest 
   slider_input = col1_pie_b.slider('Percent of BTC-USD in Portfolio', min_value= 0, max_value= 10, value= 5 )
    
   #hardcoding in the values since we dont have user input
   stock_choice_1 = 'spy'
   stock_choice_2 = 'agg'
   stock_choice_3 = 'btc-usd'
   stock_list_plt = [stock_choice_1, stock_choice_2, stock_choice_3]
    
   percent_1 = 60-slider_input
   percent_2 = 40
   percent_3 = slider_input
   percent_list = [percent_1, percent_2, percent_3]

   stock_choice_3 = stock_choice_3.replace('-', '') #get data with btc-usd but then bt likes btcusd

   your_strategy = stock_choice_1.upper()  + '-' +  stock_choice_2.upper() +  '-' + stock_choice_3.upper()

   stock_dic         = {stock_choice_1: float(percent_1)/100, stock_choice_2: float(percent_2)/100, stock_choice_3: float(percent_3)/100} #dictonary for strat

   strategy_ = bt.Strategy( your_strategy, 
                           [bt.algos.RunMonthly(), 
                           bt.algos.SelectAll(), 
                           bt.algos.WeighSpecified(**stock_dic),
                           bt.algos.Rebalance()]) #Creating strategy 
   
   test = bt.Backtest(strategy_, data)
   results = bt.run(test)

   results_list = [results, results_control, results_spy, results_agg]
   results_df = results_to_df(results_list) #list of the results but now in dataframe 
 
 #Text Description 
   col_description.markdown('##')
   col_description.markdown('##')
   col_description.markdown("<h2 style='text-align: center; color: black;'>Dashboard Description </h2>", unsafe_allow_html=True)
   col_description.markdown('* Traditional Portfolios usually include 60% stocks, and 40% bonds')
   col_description.markdown('* In this dashboard you are given a 60% into SPY (S&P500), and 40% into AGG (Aggregate Bond Index)')
   col_description.markdown('* Use the slider to incorporate Bitcoin into the strategy, and look at how advantagous a small allocation is')
   
 #Line Chart
   fig = line_chart(results_list)
   col2_scat_b.markdown('#')
   col2_scat_b.plotly_chart(fig)
   #col2_scat_b.markdown('Click on the legend entries to choose which datasets to display')

 #Pie Chart 
   
   fig = plotly_pie(stock_list_plt, percent_list)
   fig.update_layout(width = 500, height = 400)
   fig.update_layout(
    title={
        'text': "Portfolio Allocation",
        'y':0.87,
        'x':0.49,
        'xanchor': 'center',
        'yanchor': 'top'},
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-.3,
    xanchor="left",
    x= .15))
   #col1_top.header("Pie Chart")
   col1_pie_t.plotly_chart(fig, width = 500, height = 400)

 #Display Results
  #  results_list = [results, results_control, results_spy, results_agg] #list of results objects
  #  results_df = results_to_df(results_list) #list of the results but now in dataframe 

  #  stats = display_stats_combined(results_list)

  #  if (col2_second.button("Display Stats")):
  #     if(col2_second.button("Hide Stats")):
  #        yo = 1
  #     col2_second.dataframe(stats)

  #  col1_second.write(results.display_lookback_returns())

 #Display the Monthly Returns

   mon_table = monthly_returns_table(results_list)
   #st.dataframe(mon_table.style.apply(highlight_cols, axis = None))

 #Scatter of Risk vs Return
   fig = scatter_plot(results_df) #scatter function in functions
   fig.update_layout(width = 700, height = 500)
   col2_scat_t.plotly_chart(fig, width = 700, height =500)

 #Allocation Table
   rebalance_list = [3, 4, 5]
   fig = alloc_table(stock_list_plt, percent_list, rebalance_list)
   fig.update_layout(width = 400, height = 130)
   #col1.plotly_chart(fig, width = 400, height = 130)

 #Short Stats Table
   fig = short_stats_table(results_list)
   fig.update_layout(width = 380, height = 300)
   col1_stats_b.header("Return Statistics")
   col1_stats_b.plotly_chart(fig, width = 380, height = 300)

 #Balance Table
   fig = balance_table(results, results_control)
   fig.update_layout(width = 380, height = 75)
   col1_stats_b.plotly_chart(fig, width = 380, height = 75)

 #Monthly Table 
   my_expander = st.beta_expander("Show Monthly Returns", True)
   fig = monthly_table(results_list)
   fig.update_layout(width = 1400, height = 800)
   my_expander.plotly_chart(fig, width = 1400, height = 800)

 #Stats Table
   #stats_expander = col1.beta_expander("Click to Show Strategy Statistics")
   #col1_stats_t.markdown('##')
   #col1_stats_t.markdown('##')
   fig = stats_table(results_list)
   fig.update_layout(width = 380)
   fig.update_layout(margin = dict(l=0, r=0, t=0, b=0))
   col1_stats_t.header("Statistics")
   col1_stats_t.plotly_chart(fig, width = 380)

if ( option == 'Custom Strategy Dashboard'):
 #styling 
   st.markdown(
            f"""
   <style>
        .reportview-container .main .block-container{{
            padding-top: {0}rem;
            padding-right: {0}rem;
            padding-left: {1}rem;
            padding-bottom: {0}rem;
        }}
    </style>
    """,
            unsafe_allow_html=True,
        )
   
   st.markdown("<h1 style='text-align: center; color: black;'>Create and Backtest a Custom Strategy</h1>", unsafe_allow_html=True)
  
 #Beta Columns and Containers 
   col1_input, col2_input, col_spacer, col_description = st.beta_columns((2,2,1,8))
   col1_pie, col2_stats, col3_scat = st.beta_columns((2,2,3))

   col1, col2 = st.beta_columns((1, 2))
   col3, col4, col5 = st.beta_columns((1,1,3))
   
   col1_top = col1.beta_container()
   col1_middle = col1.beta_container()
   col1_bot = col1.beta_container()

   col3_scat_t = col3_scat.beta_container()
   col3_scat_b = col3_scat.beta_container()
   
   col2t =col2.beta_container()
   col2b =col2.beta_container()
   
   col1_header = col1.beta_container()
   col2_header = col2.beta_container()
   col1_graph  = col1.beta_container()
   col2_graph  = col2.beta_container()
   col1_second = col1.beta_container()
   col2_second = col2.beta_container()
   table = st.beta_container()

 #Text Description 
   col_description.markdown("<h2 style='text-align: center; color: black;'>Dashboard Features </h2>", unsafe_allow_html=True)
   col_description.markdown('* **Custom Strategy-** Use the boxes to the left to pick stocks and their allocations')
   col_description.markdown('* **Pie Chart-** View the allocations of the stocks chosen')
   col_description.markdown('* **Scatter Plot-** Shows the Risk(Monthly Vol) against Return(Monthly Mean)')
   col_description.markdown('* **Line Chart-** Displays the porfolio performance, starting with $100 invested')
   col_description.markdown('* **Monthly Table-** Displays month by month returns for AGG, SPY, Your Strategy, and 60-40 Portfolio')

 #Inputs
   stock_choice_1 = col1_input.selectbox( "Ticker 1", ('spy', 'efa', 'iwm', 'vwo', 'ibb', 'agg', 'hyg', 'gld', 'slv', 'tsla', 'aapl', 'msft', 'qqq', 'btc-usd', 'eth-usd')) #get ticker
   percent_1 = col2_input.text_input( "% Allocation", value = 55, max_chars= 3, ) # get percent
   stock_choice_1 = stock_choice_1.lower() #bt likes lower case 
   #data_1 = bt.get(stock_choice_1, start = start_date) # get the data 

   stock_choice_2 = col1_input.selectbox( "Ticker 2", ('agg', 'spy', 'efa', 'iwm', 'vwo', 'ibb', 'hyg', 'gld', 'slv', 'tsla', 'aapl', 'msft', 'qqq', 'btc-usd', 'eth-usd'))
   percent_2 = col2_input.text_input( "% Allocation", value = 40, max_chars= 3)
   stock_choice_2 = stock_choice_2.lower()
   #data_2 = bt.get(stock_choice_2, start = start_date)

   stock_choice_3 = col1_input.selectbox( "Ticker 3", ('btc-usd', 'spy', 'efa', 'iwm', 'vwo', 'ibb', 'agg', 'hyg', 'gld', 'slv', 'tsla', 'aapl', 'msft', 'qqq', 'eth-usd'))
   percent_3 = col2_input.text_input( "% Allocation", value = 5, max_chars= 3)
   stock_choice_3 = stock_choice_3.lower()
   #data_3 = bt.get(stock_choice_3, start = start_date)
   
   if(float(percent_1)+float(percent_2)+float(percent_3) != 100):
     st.sidebar.error("Allocation Must Equal 100")
   #allows us to combine the datasets to account for the difference in reg vs. Crypto 
  #  data = data_1.join(data_2, how='outer')
  #  data = data.join(data_3, how= 'outer')
  #  data = data.dropna()

   #data_con = bt.get('spy,agg,gme', start = start_date)
   
   #need the '-' in cryptos to get the data, but bt needs it gone to work
   stock_choice_1 = stock_choice_1.replace('-', '')
   stock_choice_2 = stock_choice_2.replace('-', '')
   stock_choice_3 = stock_choice_3.replace('-', '')

   your_strategy = stock_choice_1.upper()  + '-' +  stock_choice_2.upper() +  '-' + stock_choice_3.upper()

   #st.write(your_strategy)

 #Buttons
   #rebalances = col1_graph.selectbox("Rebalancing Timeline", ('Daily', 'Monthly', 'Yearly', 'None'))
   rebalances = 'Monthly'

 #creating Strategy and Backtest
   stock_list = stock_choice_1 +',' + stock_choice_2 + ',' + stock_choice_3 #list of tickers to get data for 
   stock_list_plt = [stock_choice_1, stock_choice_2, stock_choice_3]
   percent_list = [percent_1, percent_2, percent_3]
   stock_dic = {stock_choice_1: float(percent_1)/100, stock_choice_2: float(percent_2)/100, stock_choice_3: float(percent_3)/100} #dictonary for strat
   
 
   strategy_ = bt.Strategy(your_strategy, 
                              [bt.algos.RunMonthly(), 
                              bt.algos.SelectAll(), 
                              bt.algos.WeighSpecified(**stock_dic),
                              bt.algos.Rebalance()]) #Creating strategyj
                              
   strategy_daily = bt.Strategy('Daily', 
                              [bt.algos.RunDaily(), 
                              bt.algos.SelectAll(), 
                              bt.algos.WeighSpecified(**stock_dic),
                              bt.algos.Rebalance()]) #Creating strategy
   strategy_monthly = bt.Strategy('Monthly', 
                              [bt.algos.RunMonthly(), 
                              bt.algos.SelectAll(), 
                              bt.algos.WeighSpecified(**stock_dic),
                              bt.algos.Rebalance()]) #Creating strategy
   strategy_yearly = bt.Strategy('Yearly', 
                              [bt.algos.RunYearly(), 
                              bt.algos.SelectAll(), 
                              bt.algos.WeighSpecified(**stock_dic),
                              bt.algos.Rebalance()]) #Creating strategy
   strategy_none = bt.Strategy('No Rebalances', 
                              [bt.algos.RunOnce(), 
                              bt.algos.SelectAll(), 
                              bt.algos.WeighSpecified(**stock_dic),
                              bt.algos.Rebalance()]) #Creating strategy
 
 #old rebalances
   if (rebalances == 'Daily'):
      strategy_daily = bt.Strategy('Your Strategy Daily', 
                              [bt.algos.RunDaily(), 
                              bt.algos.SelectAll(), 
                              bt.algos.WeighSpecified(**stock_dic),
                              bt.algos.Rebalance()]) #Creating strategy

      # strategy_control = bt.Strategy('60-40 Daily', 
      #                      [bt.algos.RunDaily(), 
      #                      bt.algos.SelectAll(), 
      #                      bt.algos.WeighSpecified(**stock_dic_control),
      #                      bt.algos.Rebalance()]) #Creating strategy
   elif (rebalances == 'Monthly'):
      strategy_monthly = bt.Strategy('Monthly', 
                              [bt.algos.RunMonthly(), 
                              bt.algos.SelectAll(), 
                              bt.algos.WeighSpecified(**stock_dic),
                              bt.algos.Rebalance()]) #Creating strategy
      # strategy_control = bt.Strategy('60-40 Portfolio', 
      #                      [bt.algos.RunMonthly(), 
      #                      bt.algos.SelectAll(), 
      #                      bt.algos.WeighSpecified(**stock_dic_control),
      #                      bt.algos.Rebalance()]) #Creating strategy                        
   elif (rebalances == 'Yearly'):
      strategy_yearly = bt.Strategy('Your Strategy Yearly', 
                              [bt.algos.RunYearly(), 
                              bt.algos.SelectAll(), 
                              bt.algos.WeighSpecified(**stock_dic),
                              bt.algos.Rebalance()]) #Creating strategy

      # strategy_control = bt.Strategy('60-40 Yearly', 
      #                      [bt.algos.RunYearly(), 
      #                      bt.algos.SelectAll(), 
      #                      bt.algos.WeighSpecified(**stock_dic_control),
      #                      bt.algos.Rebalance()]) #Creating strategy
   elif (rebalances == 'None'):
      strategy_none = bt.Strategy('Your Strategy None', 
                              [bt.algos.RunOnce(), 
                              bt.algos.SelectAll(), 
                              bt.algos.WeighSpecified(**stock_dic),
                              bt.algos.Rebalance()]) #Creating strategy

      # strategy_control = bt.Strategy('60-40 None', 
      #                      [bt.algos.RunOnce(), 
      #                      bt.algos.SelectAll(), 
      #                      bt.algos.WeighSpecified(**stock_dic_control),
      #                      bt.algos.Rebalance()]) #Creating strategy


   test = bt.Backtest(strategy_, data)
   results = bt.run(test)

 #Rebalance Strategies
   test_d = bt.Backtest(strategy_daily, data)
   results_daily = bt.run(test_d)

   test_m = bt.Backtest(strategy_monthly, data)
   results_monthly = bt.run(test_m)

   test_y = bt.Backtest(strategy_yearly, data)
   results_yearly = bt.run(test_y)

   test_n = bt.Backtest(strategy_none, data)
   results_none = bt.run(test_n)
   
   results_list = [results, results_control, results_spy, results_agg] #list of results objects
   results_list_reb = [results_daily, results_monthly, results_yearly, results_none]

 #Line Chart
   fig = line_chart(results_list)
   fig.update_layout(width = 800, height = 500)

   fig2 = line_chart(results_list_reb)
   fig2.update_layout(width = 800, height = 500)
   
   figure = fig
   col3_scat_b.markdown('#')
   box = col3_scat_b.checkbox('Compare Rebalancing Options for Your Strategy')
   if box:
     figure = fig2
   col2b.markdown('#')
   col2b.plotly_chart(figure, width = 800, height = 500)
   #col3_scat_b.markdown('* Rebalancing refers to taking the current value of the portfolio and re distributing it into the allocations')
   #col3_scat_b.markdown('* Ex. Bitcoin may grow during the month and now be 10% of your portfolio, if rebalanced monthly, bitcoin will go back to 5% of your portoflio at the end of the month, and the extra money it made will be divided into the SPY and AGG so that at the start of the next month they are 55% and 40% of your portfolio')
   #col5.write("-    Click on the legend entries to choose which datasets to display")

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

   fig = plotly_pie(stock_list_plt, percent_list)
   fig.update_layout(width = 400, height = 400)
   col1_pie.plotly_chart(fig, width = 400, height = 400)

 #Display Results
    
   
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
   fig.update_layout(width = 600, height = 500)
   col3_scat_t.plotly_chart(fig, width = 600, height =500)
    
 #Allocation Table
   rebalance_list = [3, 4, 5]
   fig = alloc_table(stock_list_plt, percent_list, rebalance_list)
   fig.update_layout(width = 400, height = 130)
   #col1.plotly_chart(fig, width = 400, height = 130)

 #Balance Table
   fig = balance_table(results, results_control)
   fig.update_layout(width = 380, height = 75)
   col1_bot.plotly_chart(fig, width = 380, height = 75)

 #Short returns(stats) Table
   fig = short_stats_table(results_list)
   fig.update_layout(width = 380, height = 300)
   #col1_top.markdown("<h2 style='text-align: center; color: black;'>Return Statistics</h2>", unsafe_allow_html=True)
   col1_top.header("Return Statistics")
   col1_top.plotly_chart(fig, width = 380, height = 300)

 #Monthly Table 
   my_expander = st.beta_expander("Show Monthly Returns", True)
   fig = monthly_table(results_list)
   fig.update_layout(width = 1400, height = 800)
   my_expander.plotly_chart(fig, width = 1400, height = 800)

 #Stats Table
   fig = stats_table(results_list)
   fig.update_layout(width = 350, height = 500)
   fig.update_layout(margin = dict(l=0, r=0, t=0, b=0))
   #col2_stats.markdown("<h2 style='text-align: center; color: black;'>Return Statistics</h2>", unsafe_allow_html=True)
   col2_stats.header("Statistics")
   col2_stats.plotly_chart(fig, width = 350, height = 500)

 #optomize option 
  #  opto = col1_bot.button("Optomize Your Portfolio")
  #  if (opto):
  #    option = 'Portfolio Optimizer'

elif (option == 'Portfolio Optimizer'):
 
 #Styling
   st.markdown(
            f"""
   <style>
        .reportview-container .main .block-container{{
            padding-top: {0}rem;
            padding-right: {1}rem;
            padding-left: {1}rem;
            padding-bottom: {0}rem;
        }}
    </style>
    """,
            unsafe_allow_html=True,
        )
   st.markdown("<h1 style='text-align: center; color: black;'>Optomize Your Portfolio</h1>", unsafe_allow_html=True)

 #Beta Columns
   col1_s, col2_s = st.sidebar.beta_columns(2)
   col1_input, col2_input, spacer, col_description = st.beta_columns((4,4,1,8))
   col1, col2 = st.beta_columns((1, 2))
   col_ex, col_des = st.beta_columns((4,3))

 #Description

   col_description.markdown("<h2 style='text-align: center; color: black;'>Dashboard Features </h2>", unsafe_allow_html=True)
   col_description.markdown('**What is an optimized portfolio?**')
   col_description.markdown('An optimized portfolio maximizes the possible returns for a given unit of risk. An optimized portfolio may not generate the highest returns, but the ratio between the risk and return will be the best. This is known as the "Efficient Frontier". ')
   col_description.markdown('Read more about optimization and the Efficient Frontier here [Investopedia](https://www.investopedia.com/terms/e/efficientfrontier.asp)')
   
   col_description.markdown('* **Custom Strategy** Enter tickers to form a portfolio, then watch it be optimized')
   col_description.markdown('* **Frequency?** The data frequency is what data the optimization will look at. For example, when choosing daily, the stocks volatility and returns will be checked at the end of each day, and according to the daily data the optimization will occur. For longer term investments, a longer frequency will be more accurate. ')
   
 #Get data
   col1_input.markdown('#')
   col2_input.markdown('#')
   stock_symbols = col1_input.text_input("Enter the Stock Tickers Comma-Seperated", value = "spy,iwm,eem,efa,gld,agg,hyg" )
   crypto_symbols = col2_input.text_input("Enter Crypto Tickers Comma-Seperated", value= 'btc-usd')
   stock_symbols = stock_symbols.replace(' ', '')
   crypto_symbols = crypto_symbols.replace(' ', '')
   data_type = col1_input.selectbox("Select the Frequency the Data will be Rebalanced for Optimization", ('Daily Rebalance', 'Monthly Rebalance', 'Quarterly Rebalance', 'Yearly Rebalance', 'Compare all')) 
  #  symbols = 'spy,iwm,eem,efa,gld,agg,hyg'
  #  crypto_symbols = 'btc-usd,eth-usd'
   stock_data = bt.get(stock_symbols, start='2017-01-01')
   crypto_data = bt.get(crypto_symbols, start='2017-01-01')

 #Merge into dataframe
   data_ = crypto_data.join(stock_data, how='outer')
   data_ = data_.dropna()

 #Daily optimal
   
  #gets daily optimal data
   returns = data_.to_log_returns().dropna()
   daily_opt = returns.calc_mean_var_weights().as_format(".2%")
    
  #preparing data for charts
   stock_dic = daily_opt.to_dict()

   for key in stock_dic: #makes percents numbers 
      stock_dic[key] = float(stock_dic[key].replace('%', ''))
      stock_dic[key] = stock_dic[key]/100
    
   stock_list = list(stock_dic.keys()) #convert the dictionary into lists for plotting
   percent_list = list(stock_dic.values())

   temp = []
   temp_stock = []
   for i in range(len(percent_list)): #Takes out values of 0 
      if (percent_list[i] != 0):
        temp.append(percent_list[i])
        temp_stock.append(stock_list[i])

   stock_list = temp_stock
   percent_list= temp

   strategy_color = '#A90BFE'
   P6040_color = '#FF7052'
   spy_color = '#66F3EC'
   agg_color = '#67F9AF'
    
   strategy_op = bt.Strategy('Portolio Optomized Daily', 
                                [bt.algos.RunMonthly(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy

   strategy_port = bt.Strategy('Equally Weighted Portfolio', 
                                [bt.algos.RunMonthly(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighEqually(),
                                bt.algos.Rebalance()]) #Creating strategy

   test_op = bt.Backtest(strategy_op, data_)
   results_op_d = bt.run(test_op)

   test_port = bt.Backtest(strategy_port, data_)
   results_port = bt.run(test_port)
  

   if (data_type == "Daily Rebalance"):

  #table
    fig = optomize_table(daily_opt)
    col1.subheader("Optimized Allocations")
    fig.update_layout(width = 300, height = 450)
    col1.plotly_chart(fig, width = 300, height = 450)

  #pie chart
    results_list = [results_op_d, results_port]
    pie_colors = [strategy_color, P6040_color, spy_color, agg_color, '#7496F3', '#B7FA59', 'brown', '#EE4444', 'gold']
    fig = plotly_pie(stock_list, percent_list, pie_colors)
    #fig.set_size_inches(18.5, 18.5, forward=True) #how to change dimensions since pie is in matplotlib
    #col1.header("Optomized Portfolio")
    fig.update_layout(width = 500)
    col1.plotly_chart(fig)

  #line chart
    results_list = [results_op_d, results_port, results_spy, results_agg]
    fig = line_chart(results_list)
    fig.update_layout(width = 750, height = 400)
    #col2.header("Daily Performance")
    col2.markdown('#')
    col2.plotly_chart(fig, width = 750, height = 400)
    
  #Scatter PLot
    results_df = results_to_df(results_list)
    fig = scatter_plot(results_df) #scatter function in functions
    fig.update_layout(width = 750, height = 500)
    col2.markdown('#')
    col2.plotly_chart(fig, width = 750, height =500)
   
 #Monthly optimal
   
  #gets monthly optimal data
   returns = data_.asfreq("M",method='ffill').to_log_returns().dropna()
   mon_opt = returns.calc_mean_var_weights().as_format(".2%")
    
  #preparing data for charts
   stock_dic = mon_opt.to_dict()

   for key in stock_dic: #makes percents numbers 
      stock_dic[key] = float(stock_dic[key].replace('%', ''))
      stock_dic[key] = stock_dic[key]/100
    
   stock_list = list(stock_dic.keys()) #convert the dictionary into lists for plotting
   percent_list = list(stock_dic.values())

   temp = []
   temp_stock = []
   for i in range(len(percent_list)): #Takes out values of 0 
      if (percent_list[i] != 0):
        temp.append(percent_list[i])
        temp_stock.append(stock_list[i])

   stock_list = temp_stock
   percent_list= temp

   strategy_color = '#A90BFE'
   P6040_color = '#FF7052'
   spy_color = '#66F3EC'
   agg_color = '#67F9AF'
    
   strategy_op = bt.Strategy('Portolio Optomized Monthly', 
                                [bt.algos.RunMonthly(), 
                                bt.algos.SelectAll(), 
                                bt.algos.WeighSpecified(**stock_dic),
                                bt.algos.Rebalance()]) #Creating strategy

   test_op = bt.Backtest(strategy_op, data_)
   results_op_m = bt.run(test_op)

   if (data_type == "Monthly Rebalance"):
  
  #table
    fig = optomize_table(mon_opt)
    col1.subheader("Optimized Allocations")
    fig.update_layout(width = 300, height = 450)
    col1.plotly_chart(fig, width = 300, height = 450)

  #pie chart
    results_list = [results_op_m, results_port, results_spy, results_agg]
    pie_colors = [strategy_color, P6040_color, spy_color, agg_color, '#7496F3', '#B7FA59', 'brown', '#EE4444', 'gold']
    fig = plotly_pie(stock_list, percent_list, pie_colors)
    #fig.set_size_inches(18.5, 18.5, forward=True) #how to change dimensions since pie is in matplotlib
    #col1.header("Optomized Portfolio")
    fig.update_layout(width = 500)
    col1.plotly_chart(fig)

  #line chart
    fig = line_chart(results_list)
    fig.update_layout(width = 750, height = 400)
    col2.markdown("#")
    col2.plotly_chart(fig, width = 750, height = 400)
    
  #Scatter PLot 
    results_df = results_to_df(results_list)
    fig = scatter_plot(results_df) #scatter function in functions
    fig.update_layout(width = 750, height = 500)
    col2.markdown('#')
    col2.plotly_chart(fig, width = 750, height =500)
   
 #Quarterly Optimal 
   
  #gets quarterly optimal data   
   quarterly_rets = data_.asfreq("Q",method='ffill').to_log_returns().dropna()
   quart_opt = quarterly_rets.calc_mean_var_weights().as_format(".2%")

  #preparing data for charts
   stock_dic = quart_opt.to_dict()

   for key in stock_dic: #makes percents numbers 
      stock_dic[key] = float(stock_dic[key].replace('%', ''))
      stock_dic[key] = stock_dic[key]/100
    
   stock_list = list(stock_dic.keys()) #convert the dictionary into lists for plotting
   percent_list = list(stock_dic.values())

   temp = []
   temp_stock = []
   for i in range(len(percent_list)): #Takes out values of 0 
     if (percent_list[i] != 0):
       temp.append(percent_list[i])
       temp_stock.append(stock_list[i])

   stock_list = temp_stock
   percent_list= temp

   strategy_color = '#A90BFE'
   P6040_color = '#FF7052'
   spy_color = '#66F3EC'
   agg_color = '#67F9AF'
    
   strategy_op = bt.Strategy('Portolio Optomized Quarterly', 
                               [bt.algos.RunMonthly(), 
                               bt.algos.SelectAll(), 
                               bt.algos.WeighSpecified(**stock_dic),
                               bt.algos.Rebalance()]) #Creating strategy


   test_op = bt.Backtest(strategy_op, data_)
   results_op_q = bt.run(test_op)

   if (data_type == "Quarterly Rebalance"):
  
  #table
    fig = optomize_table(quart_opt)
    col1.subheader("Optimized Allocations")
    fig.update_layout(width = 300, height = 450)
    col1.plotly_chart(fig, width = 300, height = 450)

  #pie chart
    results_list = [results_op_q, results_port, results_spy, results_agg]
    pie_colors = [strategy_color, P6040_color, spy_color, agg_color, '#7496F3', '#B7FA59', 'brown', '#EE4444', 'gold']
    fig = plotly_pie(stock_list, percent_list, pie_colors)
    #fig.set_size_inches(18.5, 18.5, forward=True) #how to change dimensions since pie is in matplotlib
    #col1.header("Optomized Portfolio")
    fig.update_layout(width = 500)
    col1.plotly_chart(fig)

  #line chart
    fig = line_chart(results_list)
    fig.update_layout(width = 750, height = 400)
    col2.markdown('#')
    col2.plotly_chart(fig, width = 750, height = 400)
    
  #Scatter PLot 
    results_df = results_to_df(results_list)
    fig = scatter_plot(results_df) #scatter function in functions
    fig.update_layout(width = 750, height = 500)
    col2.markdown('#')
    col2.plotly_chart(fig, width = 750, height =500)

 #Yearly Optimal 
   
  #gets Yearly optimal data   
   year_rets = data_.asfreq("Y",method='ffill').to_log_returns().dropna()
   year_opt = year_rets.calc_mean_var_weights().as_format(".2%")
   
  #preparing data for charts
   stock_dic = year_opt.to_dict()

   for key in stock_dic: #makes percents numbers 
     stock_dic[key] = float(stock_dic[key].replace('%', ''))
     stock_dic[key] = stock_dic[key]/100
   
   stock_list = list(stock_dic.keys()) #convert the dictionary into lists for plotting
   percent_list = list(stock_dic.values())

   temp = []
   temp_stock = []
   for i in range(len(percent_list)): #Takes out values of 0 
     if (percent_list[i] != 0):
       temp.append(percent_list[i])
       temp_stock.append(stock_list[i])

   stock_list = temp_stock
   percent_list= temp

   strategy_color = '#A90BFE'
   P6040_color = '#FF7052'
   spy_color = '#66F3EC'
   agg_color = '#67F9AF'
   
   
   strategy_op = bt.Strategy('Portolio Optomized Yearly', 
                               [bt.algos.RunMonthly(), 
                               bt.algos.SelectAll(), 
                               bt.algos.WeighSpecified(**stock_dic),
                               bt.algos.Rebalance()]) #Creating strategy

   test_op = bt.Backtest(strategy_op, data_)
   results_op_y = bt.run(test_op)


   if (data_type == "Yearly Rebalance"):
  
  #table
    fig = optomize_table(year_opt)
    col1.header("Optimized Allocations")
    fig.update_layout(width = 300, height = 450)
    col1.plotly_chart(fig, width = 300, height = 450)

  #pie chart
    results_list = [results_op_y, results_port, results_spy, results_agg]
    pie_colors = [strategy_color, P6040_color, spy_color, agg_color, '#7496F3', '#B7FA59', 'brown', '#EE4444', 'gold']
    fig = plotly_pie(stock_list, percent_list, pie_colors)
    #fig.set_size_inches(18.5, 18.5, forward=True) #how to change dimensions since pie is in matplotlib
    #col1.header("Optomized Portfolio")
    fig.update_layout(width = 470)
    col1.plotly_chart(fig, width = 470)

  #line chart
    fig = line_chart(results_list)
    fig.update_layout(width = 750, height = 400)
    col2.markdown('#')
    col2.plotly_chart(fig, width = 750, height = 400)
    
  #Scatter PLot 
    results_df = results_to_df(results_list)
    fig = scatter_plot(results_df) #scatter function in functions
    fig.update_layout(width = 750, height = 500)
    col2.markdown('#')
    col2.plotly_chart(fig, width = 750, height =500)

 #Compare Frequencies
   if(data_type == "Compare all"):
     df = pd.DataFrame(daily_opt)
     df1 = pd.DataFrame(mon_opt)
     df2 = pd.DataFrame(quart_opt)
     df3 = pd.DataFrame(year_opt)
     df.columns = ['Daily']
     df1.columns = ['Monthly']
     df2.columns = ['Quarterly']
     df3.columns = ['Yearly']
     df = df.join(df1, how = 'outer').join(df2, how = 'outer').join(df3, how = 'outer')
    #Table 
     col1.markdown('##')
     fig = optomize_table_combine(df)
     fig.update_layout(width= 400, height = 300)
     col1.plotly_chart(fig, width = 400, height = 300)
    
    #Line Chart
     results_list = [results_op_d, results_op_m, results_op_q, results_op_y, results_port, results_spy, results_agg]
     result_final = pd.DataFrame()
    
     fig = line_chart(results_list)
     fig.update_layout(width = 750, height = 400)
     fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y= -.4,
        xanchor="right",
        x=.9
     ))
     col2.plotly_chart(fig, width = 750, height = 400)
     #col_des.write("Click the Legend items to toggle the viewing")
    
    #Scatter PLot 
     results_df = results_to_df(results_list)
     fig = scatter_plot(results_df) #scatter function in functions
     fig.update_layout(width = 750, height = 500)
     col2.markdown('#')
     col2.plotly_chart(fig, width = 750, height =500)


     
     
     