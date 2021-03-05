#%%
import bt 
import pandas as pd
import os
from pathlib import Path
import ffn
import matplotlib.pyplot as plt
os.environ["DISPLAY"] = ""
try:
    cwd = Path(__file__).parents[0]
except:
    cwd = Path.cwd()
class WeighEqually(bt.Algo):

# """
# Sets temp['weights'] by calculating equal weights for all items in
# selected.
# Equal weight Algo. Sets the 'weights' to 1/n for each item in 'selected'.
# Sets:
# * weights
# Requires:
# * selected
# """

    def __init__(self):
        super(WeighEqually, self).__init__()
    def __call__(self, target):
        selected = target.temp["selected"]
        n = len(selected)
        if n == 0:
            target.temp["weights"] = {}
        else:
            w = 1.0 / n
        target.temp["weights"] = {x: w for x in selected}
        return True

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
symbols = 'spy,agg,aapl'
crypto_symbols = 'btc-usd,eth-usd'
stock_data = bt.get(symbols, start= '2020-01-01')
crypto_data = bt.get(crypto_symbols, start = '2020-01-01')

data = bt.get(symbols, start = '2020-01-01')
# if data.index.tzinfo == None:
#     data.index = pd.to_datetime(data.index).tz_localize("UTC")
data = bt.get(crypto_symbols, start ='2020-01-01', existing = data,)
print(stock_data)
print(crypto_data)

stock_dic = {'spy': .45, 'agg': .05, 'btcusd': .50}

#%%
strategy_test = bt.Strategy('s1', 
                            [bt.algos.RunMonthly(), 
                            bt.algos.SelectAll(), 
                            bt.algos.WeighSpecified(**stock_dic),
                            bt.algos.Rebalance()])

test = bt.Backtest(strategy_test, data)
res = bt.run(test)
#%%
#bt.algos.WeighSpecified(**stock_dic),
#%matplotlib inline
res.plot()
#plt.show()
res.plot_security_weights()
res.display()
print("end of file")

