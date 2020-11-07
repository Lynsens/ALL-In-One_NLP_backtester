import websocket,requests,json

class client_finnhub:
	def __init__(self):
		self.api = ""
		self.cookies = None
		self.address = "https://finnhub.io/api/v1/stock/"

	def on_message(self,ws,message):
		"""Saves data to local storage."""
		pass

	def on_error(self,ws,message):
		pass

	def on_open(self,ws,message):
		pass

	def realtime_fetching(self):
		websocket.enableTrace(True)
		fh = websocket.WebSocketApp("wss://ws.finnhub.io?token="+self.api,on_message = self.on_message,on_error = self.on_error,on_open = self.on_open)
		fh.run_forever()

	def fetch_CompanyProfile(self,symbol):
		re = requests.get(self.address+"profile?symbol="+symbol+"&token="+self.api)
		rjson = re.json()

	def fetch_MarketNews(self,symbol):
		