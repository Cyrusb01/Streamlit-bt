from pandas._config.config import reset_option
import streamlit as st 
import pandas as pd
import plotly
import matplotlib.pyplot as plt
import bt
from tabulate import tabulate

def plot_pie(stock_list, percent_list):
    labels = []
    percents = []

    for x, y in zip(stock_list, percent_list): #labels show the percent in the legend 
        labels.append(x.upper() + " " + str(y) + "%")
        percents.append(y)
    
    fig, ax1 = plt.subplots()
    ax1.pie(percents,  shadow=True, startangle=90)
    plt.legend( labels, loc="best")
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    return fig

def results_to_df(results_list):
    df_list = [] #list of completed dataframes
    
    for x in results_list:
        string_res = x.to_csv(sep=',') #This creates string of results stats 
        df = pd.DataFrame([x.split(',') for x in string_res.split('\n')]) # Takes the string and creates a dataframe 
        nan_value = float("NaN") 
        df.replace("", nan_value, inplace=True) #lot of empty collumns in dataframe, this makes the empty go to null("NaN")
        df.dropna(how='all', axis=1, inplace=True) #delete null collumns
        df = df.dropna()

        df_list.append(df)
    
    return df_list

def display_stats_combined(results_list): #works for list of two results df 
    
    df_list = results_to_df(results_list) 
    
    stats_combined = pd.concat([df_list[0], df_list[1]], axis=1)
    stats_combined.columns = ['Stats', 'Strategy 1', 'Drop', "Strategy 2"]
    stats_combined = stats_combined.drop(['Drop'], axis =1 )

    return stats_combined

def monthly_returns_table(results_list):
    
    key = results_list[0]._get_backtest(0)
    res_mon = results_list[0][key].return_table

    keyc = results_list[1]._get_backtest(0)
    res_con = results_list[1][keyc].return_table

    something = pd.concat([res_mon, res_con], axis =1) #making the collumns go jan jan feb feb
    something.columns = ['Jan', 'Feb',  'Mar',  'Apr',  'May',  'Jun',  'Jul',  'Aug',  'Sep', 'Oct',  'Nov', 'Dec', 'YTD', 'Jan2', 'Feb2',  'Mar2',  'Apr2',  'May2',  'Jun2',  'Jul2',  'Aug2',  'Sep2', 'Oct2',  'Nov2', 'Dec2', 'YTD2']
    column_names = ['Jan', 'Jan2', 'Feb', 'Feb2', 'Mar', 'Mar2', 'Apr', 'Apr2', 'May', 'May2', 'Jun', 'Jun2', 'Jul', 'Jul2', 'Aug', 'Aug2', 'Sep', 'Sep2', 'Oct', 'Oct2', 'Nov', 'Nov2', 'Dec', 'Dec2', 'YTD', 'YTD2']
    something = something.reindex(columns = column_names)
    something.columns = ['Jan', 'Jan ', 'Feb', 'Feb ', 'Mar', 'Mar ', 'Apr', 'Apr ', 'May', 'May ', 'Jun', 'Jun ', 'Jul', 'Jul ', 'Aug', 'Aug ', 'Sep', 'Sep ', 'Oct', 'Oct ', 'Nov', 'Nov ', 'Dec', 'Dec ', 'YTD', 'YTD '] 

    return something
    
    
def highlight_cols(x): #highlights collumns in pandas / straight off stack overflow
    # copy df to new - original data is not changed 
    df = x.copy() 
    # select all values to blue color 
    df.loc[:, :] = 'background-color: blue'
    # overwrite values grey color 
    df[['Jan', 'Feb',  'Mar',  'Apr',  'May',  'Jun',  'Jul',  'Aug',  'Sep', 'Oct',  'Nov', 'Dec', 'YTD']] = 'background-color: orange'
    # return color df 
    return df  

def scatter_plot(results_df):
    xaxis_vol = []
    yaxis_return = []
    for x in results_df: #fill in two lists with the vol and return %s 
        xaxis_vol.append(float(x.iloc[30][1].replace('%', '')))
        yaxis_return.append(float(x.iloc[29][1].replace('%', '')))

    #probably should make these dynamic
    labels_ = ['Your Strategy', '60-40', 'Spy', 'Agg'] 
    color=['tab:orange','tab:blue','tab:red', 'tab:green']

    #creating the plot 
    fig, ax = plt.subplots()
    for x, y, c, lb in zip(xaxis_vol, yaxis_return, color, labels_):
      ax.scatter(x, y, color=c, label = lb)
    ax.set_title('Risk Vs. Return')
    ax.set_ylabel("Monthly Mean (ann.) %")
    ax.set_xlabel("Monthly Vol (ann.) %")
    ax.legend()

    return fig
    
    

