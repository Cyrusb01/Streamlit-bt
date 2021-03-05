import streamlit as st 
import pandas as pd
import numpy as np
import plotly
import bt

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
option = st.sidebar.selectbox("Select and option", ('Chart', 'Chart-Slider', 'etc'))

if ( option == 'Chart'):
    col1, col2 = st.sidebar.beta_columns(2)
    #Sidebar Inputs
    #st.sidebar.write("Keep total percentage equal to 100 for accurate results")

    stock_choice_1 = col1.text_input( "Enter Ticker 1", value = 'SPY', max_chars= 8)
    percent_1 = col2.text_input( "% Allocation", value = 55, max_chars= 3, )

    stock_choice_2 = col1.text_input( "Enter Ticker", value = 'AGG', max_chars= 8)
    percent_2 = col2.text_input( "% Allocation", value = 40, max_chars= 3)
    
    stock_choice_3 = col1.text_input( "Enter Ticker", value = 'MSFT', max_chars= 8)
    percent_3 = col2.text_input( "% Allocation", value = 5, max_chars= 3)
    
    stock_list = stock_choice_1 +',' + stock_choice_2 + ',' + stock_choice_3 #list of tickers to get data for 

    stock_dic = {'spy': float(percent_1)/100, 'agg': float(percent_2)/100, 'msft': float(percent_3)/100}


    

    
    data = bt.get('spy,agg,msft', start= '2020-01-01') #get data
    
    strategy_ = bt.Strategy('s1', 
                            [bt.algos.RunMonthly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic),
                            bt.algos.Rebalance()]) #Creating strategy 
    
    test = bt.Backtest(strategy_, data)
    results = bt.run(test)
    
    fig = results.plot()
    st.plotly_chart(fig)
    
    st.header("Returns Graph")

    st.text(results.display())

if ( option == 'Chart-slider'):

    #Sidebar Inputs 
    stock_choice_1 = st.sidebar.text_input( "Enter Ticker 1", value = 'SPY', max_chars= 8)
    percent_1 = st.sidebar.text_input( "Enter Ticker 1 Percent", value = 55, max_chars= 3)

    stock_choice_2 = st.sidebar.text_input( "Enter Ticker", value = 'AGG', max_chars= 8)
    percent_2 = st.sidebar.text_input( "Enter Ticker 2 Percent", value = 40, max_chars= 3)
    
    stock_choice_3 = st.sidebar.text_input( "Enter Ticker", value = 'BTC-USD', max_chars= 8)
    percent_3 = st.sidebar.text_input( "Enter Ticker 3 Percent", value = 5, max_chars= 3)
    
    st.header("Returns Graph")
    
    data = bt.get(stock_choice_1, start= '2020-01-01') #get data 
    
    st.line_chart(data) #plot data 
    option2 = st.slider('percent', min_value= 0, max_value= 10, value= 5 )
    #st.dataframe(data)


    
    

    





