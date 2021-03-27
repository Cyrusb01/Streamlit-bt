#%%
import bt
from bt.algos import RunDaily, RunMonthly, RunWeekly, run_always 

#This is the class that does the weight band rebalancing, off of a github comment with a few things edited to make it work
class RebalanceAssetThreshold(bt.Algo):
    def __init__(self, threshold=0.05):
        super(RebalanceAssetThreshold, self).__init__()
        self.threshold = threshold
        self.is_initial_rebalance = True
        
        
    def __call__(self, target):
        
        if 'weights' not in target.temp:
            return True
        
        targets = target.temp['weights']
        
        if self.is_initial_rebalance:
            print("\n", "We are in initial rebalancing.")
            
            # save value because it will change after each call to allocate. use it as base in rebalance calls
            base = target.value
            # If cash is set (it should be a value between 0-1 representing the proportion of cash to keep), 
            # calculate the new 'base'
            if 'cash' in target.temp:
                base = base * (1 - target.temp['cash'])
            for k,v in targets.items():
                target.rebalance(v, child=k, base=base, update=True)
            
            target.perm['previous_children'] = None
            target.perm["last_rebalance_date"] = target.now # Store the last rebalancing date
            
            temp_dict = {} 
            for cname in target.children:
                c = target.children[cname]
                v = c.value
                temp_dict[cname] = v
                print(f"{cname} Initial Value: {v}")
            target.perm['previous_children'] = temp_dict
            print(temp_dict)
            print("Initial Portfolio Rebalance Date: ", target.now)
            print(60*'-')
            self.is_initial_rebalance = False
            return True
        
        last_rebalance_date = target.perm["last_rebalance_date"]
        prev_children = target.perm['previous_children'] # Dict(Ticker:Value)
        
        temp_dict = {}
        # for cname in target.children:
        #     c = target.children[cname]
        #     print("Child name", c)
        #     v = c.value
        #     print("Value", v)
        #     v_prev = prev_children[cname]
        #     temp_dict[cname] = True if (v<v_prev-(v_prev*self.threshold)) or (v>v_prev+(v_prev*self.threshold)) else False

        curr_sum = 0
        for cname in target.children: #this loop gets the current value of the portfolio
            v = target.children[cname].value
            curr_sum += v
        for cname in target.children:
            v = target.children[cname].value
            if (((v/curr_sum) - targets[cname]) < -self.threshold): #this is like (.55 -.60) < -.05
                temp_dict[cname] = True
            elif (((v/curr_sum) - targets[cname]) > self.threshold): #this is like (.65 -.60) < -.05 (where .05 would be the threshold)
                temp_dict[cname] = True

        # If any Security's values deviated, then rebalance.
        if any(list(temp_dict.values())):
            print("\n", "One of children deviated. We need to rebalance.")
            print(temp_dict)
            curr_sum = 0
            for cname in target.children: #this loop gets the current value of the portfolio
                v = target.children[cname].value
                curr_sum += v

            for cname in target.children:
                v = target.children[cname].value
                print((v/curr_sum)) #this is like (.55 -.60) < -.05
            
            # save value because it will change after each call to allocate. use it as base in rebalance calls
            base = target.value
            # If cash is set (it should be a value between 0-1 representing the proportion of cash to keep), 
            # calculate the new 'base'
            if 'cash' in target.temp:
                base = base * (1 - target.temp['cash'])
            for k,v in targets.items():
                target.rebalance(v, child=k, base=base, update=True)

            temp_dict = {}
            for cname in target.children:
                c = target.children[cname]
                v = c.value
                temp_dict[cname] = v
            target.perm['previous_children'] = temp_dict
            target.perm["last_rebalance_date"] = target.now
            return True
        return True


#inputs 
stock_a = 'spy'
stock_b = 'agg'
stock_c = 'btc-usd'

percent_a = 10
percent_b = 30
percent_c = 60

start_date = '2018-01-01'

#I have to do this long way of getting the date because crypto data is everyday, while stocks are weekdays, so this combines the data in the right way 
data_a = bt.get(stock_a, start = start_date)
data_b = bt.get(stock_b, start = start_date)
data_c = bt.get(stock_c, start = start_date)

data = data_a.join(data_b, how='outer')
data = data.join(data_c, how= 'outer')
data = data.dropna()

#This is here because to get data we need 'btc-usd' for example, and then when using it in the strategy it has to be 'btcusd'
stock_a = stock_a.replace('-', '')
stock_b = stock_b.replace('-', '')
stock_c = stock_c.replace('-', '')


#dictionary of the stock and the percent allocation 
stock_dic = {stock_a: float(percent_a)/100, stock_b: float(percent_b)/100, stock_c: float(percent_c)/100}

strategy_ = bt.Strategy('Your Strategy', [
                           bt.algos.RunDaily(), 
                           bt.algos.SelectAll(), 
                           bt.algos.WeighSpecified(**stock_dic), #this is the weighting
                           RebalanceAssetThreshold(), #the rebalancing from this happens daily, (rundaily is above it)
                           bt.algos.RunMonthly(),
                           bt.algos.Rebalance() #the normal rebalance happens monthly, (runmonthly is above it)
                           ]) #Creating strategy

test = bt.Backtest(strategy_, data)
results = bt.run(test)


#this code is to export the weights into an excel file to check if rebalancing is happening properly
key = results._get_backtest(0) #Chunk of code is how to get the weights, straight from doc
filter = None
if filter is not None:
    data_w = results.backtests[key].security_weights[filter]
else:
    data_w = results.backtests[key].security_weights

data_w.to_csv('dataw.csv')



#%%
%matplotlib inline
results.plot()
results.plot_security_weights()
results.display()