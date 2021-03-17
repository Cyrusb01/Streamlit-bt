from pandas._config.config import reset_option
import streamlit as st 
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import bt
from tabulate import tabulate
import plotly.graph_objects as go

def line_chart(results_list):
    ser = results_list[0]._get_series(None).rebase() #gets all the daily balances as a series 
    ser2 = results_list[1]._get_series(None).rebase()
   
    result_final = pd.concat([ser, ser2], axis=1) #makes dataframe for both series
    result_final.columns = ["Your Strategy Monthly", "60-40 Monthly"] 
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
    return fig

def plot_pie(stock_list, percent_list):
    labels = []
    percents = []
    pie_colors = ['#66F3EC', '#67F9AF', '#F9C515']

    for x, y in zip(stock_list, percent_list): #labels show the percent in the legend 
        labels.append(x.upper())
        percents.append(y)
    
    fig, ax1 = plt.subplots()
    ax1.pie(percents,
            shadow=True, 
            startangle=90,
            colors = pie_colors,
            wedgeprops={"edgecolor":"white",'linewidth': 1, 'linestyle': 'solid', 'antialiased': True},
            autopct='%1.0f%%' )
    plt.legend( labels, bbox_to_anchor=(0.5, -0.05), framealpha=0, ncol = 3, loc="upper center")
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
    
    df_list = results_to_df(results_list) #The results arent dataframes, so need to make them dataframes
    
    stats_combined = pd.concat([df_list[0], df_list[1]], axis=1) #this combines them 
    stats_combined.columns = ['Stats', 'Strategy 1', 'Drop', "Strategy 2"]
    stats_combined = stats_combined.drop(['Drop'], axis =1 )

    return stats_combined

def monthly_returns_table(results_list):
    
    key = results_list[0]._get_backtest(0)
    res_mon = results_list[0][key].return_table
    return res_mon
    keyc = results_list[1]._get_backtest(0)
    res_con = results_list[1][keyc].return_table

    something = pd.concat([res_mon, res_con], axis =0) #making the collumns go jan jan feb feb
    # something.columns = ['Jan', 'Feb',  'Mar',  'Apr',  'May',  'Jun',  'Jul',  'Aug',  'Sep', 'Oct',  'Nov', 'Dec', 'YTD', 'Jan2', 'Feb2',  'Mar2',  'Apr2',  'May2',  'Jun2',  'Jul2',  'Aug2',  'Sep2', 'Oct2',  'Nov2', 'Dec2', 'YTD2']
    # column_names = ['Jan', 'Jan2', 'Feb', 'Feb2', 'Mar', 'Mar2', 'Apr', 'Apr2', 'May', 'May2', 'Jun', 'Jun2', 'Jul', 'Jul2', 'Aug', 'Aug2', 'Sep', 'Sep2', 'Oct', 'Oct2', 'Nov', 'Nov2', 'Dec', 'Dec2', 'YTD', 'YTD2']
    # something = something.reindex(columns = column_names)
    # something.columns = ['Jan', 'Jan ', 'Feb', 'Feb ', 'Mar', 'Mar ', 'Apr', 'Apr ', 'May', 'May ', 'Jun', 'Jun ', 'Jul', 'Jul ', 'Aug', 'Aug ', 'Sep', 'Sep ', 'Oct', 'Oct ', 'Nov', 'Nov ', 'Dec', 'Dec ', 'YTD', 'YTD '] 
    
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
    labels_ = ['Your Strategy', '60-40', 'SPY', 'AGG'] 
    color=['tab:orange','tab:blue','tab:red', 'tab:green']

    # #creating the plot 
    # fig, ax = plt.subplots()
    # for x, y, c, lb in zip(xaxis_vol, yaxis_return, color, labels_):
    #   ax.scatter(x, y, color=c, label = lb)

    # ax.set_title('Risk Vs. Return')
    # ax.set_ylabel("Monthly Mean (ann.) %")
    # ax.set_xlabel("Monthly Vol (ann.) %")
    # ax.legend()

    fig = px.scatter( x= xaxis_vol, y= yaxis_return, size = [4, 4, 4, 4], color = ["Your Strategy", "60-40 Portfolio", "SPY", "AGG"],
                            color_discrete_sequence=['#66F3EC', '#67F9AF', '#F9C515', '#ac77f2'],
                            labels={
                            "x": "Monthly Vol (ann.) %",
                            "y": "Monthly Mean (ann.) %",
                            "color" : ""
                            },
                            title="Risk Vs. Return")
    fig.update_layout(
    title={
        'text': "Risk Vs. Return",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-.3,
    xanchor="left",
    x=0.1
    
    ))
    fig.update_layout(margin = dict(l=30, r=0, t=80, b=80))



    return fig
    
def alloc_table(stock_list, percent_list, rebalance_trigger_list):
    for i in range(len(stock_list)):
        stock_list[i]= stock_list[i].upper()

    headerColor = 'black'
    fig = go.Figure(data=[go.Table(
                                header=dict(values=['', 'Target Allocation', 'Rebalance'],
                                            line_color= 'white',
                                            fill_color=headerColor,
                                            align=['left','center'],
                                            font=dict(color='white', size=12)),
                                cells=dict(values=[stock_list, percent_list, rebalance_trigger_list],
                                            line_color = 'white',
                                            font = dict(color = 'black'),
                                            fill = dict(color=['white', '#a2a4a8', 'white']))) ])
    fig.update_layout(margin = dict(l=0, r=20, t=20, b=0))
    return fig

def sum_table(rebalance_type, weight_band):
    axis = ["Initial Investment", "Rebalance", "Weight Band"]
    fig = go.Figure(data=go.Table(
                            cells = dict(values = [axis, ["$100.00", rebalance_type, weight_band]],
                            line_color = 'black',
                            font = dict(color = 'black'),
                            fill_color = 'white')))
    return fig

def balance_table(results, results_con):
    labels = ['Strategy', 'Initial Investment', 'Final Balance']
    series_res = results._get_series(None).rebase()
    series_con = results_con._get_series(None).rebase()
    final_res = round(series_res.iloc[-1])
    final_con = round(series_con.iloc[-1])
    fig = go.Figure(data=[go.Table(
                                header=dict(values= labels,
                                            line_color= 'black',
                                            fill_color= '#a2a4a8',
                                            align=['center','center'],
                                            font=dict(color='white', size=10)),
                                cells=dict(values=[['60-40 Portfolio', 'Your Strategy'], ["$100", "$100"], [final_con, final_res]],
                                            line_color = 'white',
                                            font = dict(color = 'black'),
                                            fill_color = '#dbdbdb' )) ])
    fig.update_layout(margin = dict(l=0, r=20, t=0, b=0))
    
    return fig

def short_stats_table(results_list):
    stats_0 = results_list[0].display_lookback_returns() #these objects are the dataframes we want, just need to combine them and-
    stats_1 = results_list[1].display_lookback_returns()   #make them into a nice table 
    labels= ["Stats", "Your Strategy", "60-40 Portfolio"]


    #combining 
    stats_combined = pd.concat([stats_0, stats_1], axis=1) 
    stats_combined.columns = ['Your_Strategy', "Portfolio6040"]
    stats_combined = stats_combined.dropna()
    

    fig = go.Figure(data=[go.Table(
                            header=dict(values= labels,
                                        line_color= 'black',
                                        fill_color= '#a2a4a8',
                                        align=['center','center'],
                                        font=dict(color='white', size=10)),
                            cells=dict(values=[stats_combined.index, stats_combined.Your_Strategy, stats_combined.Portfolio6040],
                                        line_color = 'white',
                                        height = 30,
                                        font = dict(color = 'black'),
                                        fill_color = '#dbdbdb' )) ])
    fig.update_layout(margin = dict(l=0, r=0, t=0, b=0))
    return fig

def monthly_table(results_list):
    
    key = results_list[0]._get_backtest(0) #syntax for getting the monthly returns data frame 
    res_mon = results_list[0][key].return_table
    df_r = pd.DataFrame(res_mon)

    keyc = results_list[1]._get_backtest(0)  
    res_con = results_list[1][keyc].return_table
    df_c = pd.DataFrame(res_con)

    #hard part of this is combining
    index = res_mon.index
    index = index.tolist()
    
    
    year_rows =[] #create a list of the rows of year month month YTD
    for i in range(len(res_mon.index)):
        temp = []
        temp.append(index[i])
        temp.append("Jan")
        temp.append("Feb")
        temp.append("Mar")
        temp.append("Apr")
        temp.append("May")
        temp.append("Jun")
        temp.append("Jul")
        temp.append("Aug")
        temp.append("Sep")
        temp.append("Oct")
        temp.append("Nov")
        temp.append("Dec")
        temp.append("YTD")
        year_rows.append(temp)

    res_rows = [] #this creates the list of the "Your Strategy" then all the numbers
    for i in range(len(res_mon.index)):
        temp = []
        temp += ["Your Strategy"]
        for j in range(len(res_mon.columns)):
            temp += [str(round(df_r.iloc[i][j]*100, 2)) + '%']
        res_rows.append(temp)
    
    con_rows = [] #this creates the list of the "60-40 Portfolio " then all the numbers
    for i in range(len(res_mon.index)):
        temp = []
        temp += ["60-40 Portfolio"]
        for j in range(len(res_con.columns)):
            temp += [str((round(df_c.iloc[i][j] *100, 2))) + '%'] #this takes the value in, round to 2 decimal places, and adds the percent sign
        con_rows.append(temp)

    length = len(year_rows)
    
    list_4_df = [] #appends the rows in the correct order
    for i in range(length):
        list_4_df.append(year_rows[(length-1)-i])
        list_4_df.append(res_rows[(length-1)-i])
        list_4_df.append(con_rows[(length-1)-i])
    
    label_row = year_rows[length-1] #grabs the label row
    for i in range (len(year_rows)): # this loop is to make all the labels bold
        for j in range(len(year_rows[0])):
            label_row[j] = str(label_row[j])
            label_row[j] = '<b>' + label_row[j] + '<b>'

            year_rows[i][j] = str(year_rows[i][j])
            year_rows[i][j] = '<b>' + year_rows[i][j] + '<b>'

    for i in range (len(res_rows)): # this loop is to make all the strategy titles bold 

        res_rows[i][0] = str(res_rows[i][0])
        res_rows[i][0] = '<b>' + res_rows[i][0] + '<b>'  

        con_rows[i][0] = str(con_rows[i][0])
        con_rows[i][0] = '<b>' + con_rows[i][0] + '<b>'   

    df = pd.DataFrame(list_4_df) #creates a dataframe of the lists
    df = df.drop(df.index[0]) #drops the label row, this is for creating a plotly table better 
        
    df.columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']
    #making the table 
    date_color = '#131c4f'
    fig = go.Figure(data=[go.Table(
                            #columnorder = [1,2,1,1,1,1,1,1,1,1,1,1,1,1],
                            columnwidth = [200, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
                            header=dict(values= label_row,
                                        line_color= '#dbdbdb',
                                        height = 30,
                                        fill_color= '#131c4f',
                                        align=['center','center'],
                                        font=dict(color='white', size=12)),
                            cells=dict(values=[df.a, df.b, df.c, df.d, df.e, df.f, df.g, df.h, df.i, df.j, df.k, df.l, df.m, df.n],
                                        line_color = '#dbdbdb',
                                        height = 30,
                                        font = dict(color = [['black', 'black', 'white', 'black','black', 'white', 'black', 'black', 'white', 'black', 'black', 'white', 'black', 'black']*14]),
                                        fill_color = [['#00EEAD', '#00EEAD', date_color, '#00EEAD','#00EEAD', date_color, '#00EEAD', '#00EEAD', date_color, '#00EEAD', '#00EEAD', date_color, '#00EEAD', '#00EEAD']*14] )) ])
    fig.update_layout(margin = dict(l=0, r=0, t=0, b=0))


    return fig

def optomize_table(df):
    df = pd.DataFrame(df)
    #combining 
    labels = ['<b>Tickers<b>', '<b>Allocation<b>']

    df.columns = ["Allocation"]
    df = df.dropna()
    
    fig = go.Figure(data=[go.Table(
                            header=dict(values= labels,
                                        line_color= 'black',
                                        fill_color= '#a2a4a8',
                                        align=['center','center'],
                                        font=dict(color='white', size=10)),
                            cells=dict(values=[df.index, df.Allocation],
                                        line_color = 'white',
                                        height = 30,
                                        font = dict(color = 'black'),
                                        fill_color = '#dbdbdb' )) ])
    fig.update_layout(margin = dict(l=0, r=0, t=0, b=0))
    return fig






