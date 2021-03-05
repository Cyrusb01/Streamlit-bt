
import bt

stock_choice_1 ='spy'
stock_choice_2 ='agg'
stock_choice_3 ='msft'


stock_list = stock_choice_1 +',' + stock_choice_2 + ',' + stock_choice_3

data = bt.get(stock_list, start = '2020-01-01')

stock_dic = {'spy': float(50)/100, 'agg': float(45)/100, 'msft': float(5)/100}


    

    
data = bt.get('spy,agg,msft', start= '2020-01-01') #get data
    
strategy_ = bt.Strategy('s1', 
                        [bt.algos.RunMonthly(), 
                        bt.algos.SelectAll(), 
                        bt.algos.WeighSpecified(**stock_dic),
                        bt.algos.Rebalance()]) #Creating strategy 
    
test = bt.Backtest(strategy_, data)
results = bt.run(test)

#results.display()
print(results.display())
#print(stock_list)
#print(data)