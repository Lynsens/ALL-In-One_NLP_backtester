import os,time
import backtesting

class trader():
	def __init__(self):
		self.time_start = 0
		self.time_end = 0
		self.features = ['name','timestamp','quote','quote_last','bidding_buy','bidding_sell','time_skip','suspension','split','merge','ownership_change']
		self.callback_init = None
		self.callback_iterate = None
		self.active = False

	def set_init_callback(self,callback_func):
		if callable(callback_func):
			self.callback_init = callback_func
		else:
			print("Uncallable init callback function!")

	def set_iterate_callback(self,callback_func):
		if callable(callback_func):
			self.callback_iterate = callback_func
		else:
			print("Uncallable init callback function!")

	def set_features(self,feature_list = [], feature_switch = {}):
		pass

	def prefetch_data(self):
		pass

	def run(self):
		pass

	def trade(self):
		pass