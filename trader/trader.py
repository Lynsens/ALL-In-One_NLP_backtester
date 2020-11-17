import os,time
import datetime as dt
import threading
import numpy as np
import pandas as pd
import backtesting as bt

class dummystg_active(bt.Strategy):
    def init(self):
        self.runflag = True
        self.iteration_holder = threading.Lock()
        self.iteration_holder.acquire()
        print("iteration init")

    def next(self):
        if self.runflag:
            self.iteration_holder.acquire()
            print("iteration issued")

    def rc_buy(self):
        self.buy()

    def rc_sell(self):
        self.sell()

    def rc_iterate(self):
        if self.iteration_holder.locked():
            self.iteration_holder.release()
        else:
            print("Info: Iteration ended!")

class dummystg_passive(bt.Strategy):
    def init(self):
        pass

    def next(self):
        pass

"""
Workflow:
import trader as TD
t=TD.trader(time_start = "YYYY-MM-DD", time_end = "YYYY-MM-DD")
t.import_stock('AAPL') #Import as much as one want as long as the data for such symbol exists.
#optionally:
t.trade_on_close = True #So as to let trade happen on closing
t.trade_mode = 'passive' #If the passive mode is desired (and the user would then have to define the strategy callbacks by themselves)
#Then:
t.trade_init(balance = 100, preowned_stocks = {}) #Arguments are optional. Balance default to 100. Preowned_stocks are specified as a dictionary, for example: {'AAPL':10}
#Then trades:
t.trade_buy('some_symbol')
t.trade_sell('some_symbol')
t.trade_next() #When you've done all the trades and want to procede to the next timeframe
#When finishing:
t.trade_finish()
#Results are saved at:
t.results[symbol] #which is a dictionary with the symbols as the keys
#And to plot the graph for the trade:
t.result_plotters[symbol]() #which is a dictionary of callables
"""


class trader():
    def __init__(self, mode = 'active', timeframe = 86400, time_start = 0, time_end = 0, commission = 0, trade_on_close = False):
        self.time_frame = timeframe # In seconds, default to 86400 (1 day).
        self.time_start = self.time_convert(time_start) # In POSIX timestamp format
        self.time_end = self.time_convert(time_end) # In POSIX timestamp format
        self.commission = commission
        self.trade_on_close = trade_on_close
        self.features = ['name','timestamp','quote','quote_last','bidding_buy','bidding_sell','time_skip','suspension','split','merge','ownership_change']
        self.callback_init = None
        self.callback_iterate = None
        self.trade_mode = mode # Could be one of 'active', 'passive', or 'offline'. Note that offline is not real offline trading, as the tradings operations still have to be sorted by time.
        self.stock_list_raw = {}

    def time_convert(self,timestr):
        """Convert date in YYYY-MM-DD string into POSIX timestamp."""
        if isinstance(timestr,str):
            try:
                return int(dt.datetime.strptime(timestr,'%Y-%m-%d').timestamp())
            except:
                try:
                    return int(dt.datetime.strptime(timestr,'%Y-%m-%d %H:%M:%S').timestamp())
                except:
                    print("Bad starting time format!")
                    exit(0)
        else:
            return timestr

    def _timeframe_resample(self,data,target):
        resampled = []
        laststep = data[0,0]
        lastopen = data[0,1]
        lasthigh = data[0,2]
        lastlow = data[0,3]
        lastclose = data[0,4]
        lastvol = 0
        for entry in data:
            if entry[0]-laststep<target:
                lasthigh = max(lasthigh,entry[2])
                lastlow = min(lastlow,entry[3])
                lastclose = entry[4]
                lastvol = lastvol+entry[5]
            else:
                resampled.append([laststep,lastopen,lasthigh,lastlow,lastclose,lastvol])
                laststep = entry[0]
                lastopen = entry[1]
                lasthigh = entry[2]
                lastlow = entry[3]
                lastclose = entry[4]
                lastvol = entry[5]
        return np.array(resampled)
                

    def set_init_callback(self,callback_func):
        if callable(callback_func):
            self.callback_init = callback_func
        else:
            print("Uncallable init callback function!")

    def set_iterate_callback(self,callback_func):
        if callable(callback_func):
            self.callback_iterate = callback_func
        else:
            print("Uncallable iterate callback function!")

    def set_features(self,feature_list = [], feature_switch = {}):
        pass

    def prefetch_data(self):
        pass

    def import_stock(self,symbol):
        if not os.path.exists(symbol+".npy"):
            print("Stock data not exist! Please use the fetch_data module to retrieve related data first!")
            exit(0)
        with open(symbol+".npy",'rb') as f:
            rarray = np.load(f)
        self.stock_list_raw[symbol] = rarray

    def init_stockdata(self):
        if not (self.time_start and self.time_end):
            print("Please specify emulation timerange!")
            return
        self.stock_list = {}
        for stock in self.stock_list_raw:
            data = self.stock_list_raw[stock]
            timeseg = np.logical_and(data[:,0]>=self.time_start,data[:,0]<=self.time_end)
            if not np.sum(timeseg):
                print("Warning: Stock "+stock+" has no available data in the selected time range!")
            else:
                data = self._timeframe_resample(data[timeseg],self.time_frame)
                self.stock_list[stock] = pd.DataFrame({'Open':data[:,1],'High':data[:,2],'Low':data[:,3],'Close':data[:,4],'Volume':data[:,5]},index=pd.to_datetime(data[:,0],unit='s'))

    def init_stockownership(self,preowned_stocks):
        self.stock_ownership = {}
        for stock in self.stock_list_raw:
            self.stock_ownership[stock] = preowned_stocks[stock] if stock in preowned_stocks else 0

    def init_stockinstance(self):
        self.stock_dummyinst = {}
        self.stock_dummystg = {}
        self.stock_dummyinst_proc = {}
        for stock in self.stock_list_raw:
            if self.trade_mode == 'passive':
                self.stock_dummyinst[stock] = bt.Backtest(self.stock_list[stock],dummystg_passive,cash = self.balance,commission = self.commission,trade_on_close = self.trade_on_close)
                self.stock_dummystg[stock] = self.stock_dummyinst[stock]._strategy # NEED CORRECTION!!!
            else:
                self.stock_dummyinst[stock] = bt.Backtest(self.stock_list[stock],dummystg_active,cash = self.balance,commission = self.commission,trade_on_close = self.trade_on_close)
                self.stock_dummyinst_proc[stock] = threading.Thread(target = self.stock_dummyinst[stock].run)
                self.stock_dummyinst_proc[stock].start()
                time.sleep(1)
                self.stock_dummystg[stock] = self.stock_dummyinst[stock].strategy

    def end_stockinstance(self):
        if self.trade_mode == 'passive':
            print("Warning: Passive trading mode need not to be ended manually!")
            return
        for stock in self.stock_dummystg:
            self.stock_dummystg[stock].runflag = False
            self.stock_dummystg[stock].rc_iterate()
        for stock in self.stock_dummyinst_proc:
            self.stock_dummyinst_proc[stock].join()

    def trade_init(self,balance = 100,preowned_stocks = {}):
        self.init_stockdata()
        self.init_stockownership(preowned_stocks)
        self.balance = balance # Supposed to be of the same unit as the selected stock(s). Default to 0.
        self.current_time = self.time_start
        self.current_itrt = 0
        if self.trade_mode == 'passive':
            self.callback_init()
        else:
            self.init_stockinstance()

    def trade_run(self):
        if self.trade_mode != 'passive':
            print("trade_run() could only be called in passive trading mode.")
            return

    def trade_buy(self,symbol,target = -1):
        if symbol in self.stock_list:
            self.stock_dummystg[symbol].rc_buy()
        else:
            print("Warning: Symbol not exist!")

    def trade_sell(self,symbol,target = -1):
        if symbol in self.stock_list:
            self.stock_dummystg[symbol].rc_sell()
        else:
            print("Warning: Symbol not exist!")

    def trade_next(self,target_time = -1):
        if target_time == -1:
            for stock in self.stock_dummystg:
                self.stock_dummystg[stock].rc_iterate()
            self.current_time += self.time_frame
            self.current_itrt +=1
        else:
            while self.current_time<target_time:
                for stock in self.stock_dummystg:
                    self.stock_dummystg[stock].rc_iterate()
                self.current_time += self.time_frame
                self.current_itrt +=1
        print(self.current_time,self.current_itrt)

    def trade_finish(self):
        self.end_stockinstance()
        self.results = {}
        self.result_plotters = {}
        for stock in self.stock_dummyinst:
            self.results[stock] = self.stock_dummyinst[stock]._results
            self.result_plotters[stock] = self.stock_dummyinst[stock].plot
