import websocket,requests
import datetime as dt
import numpy as np

class client_finnhub:
    def __init__(self):
        self.api = "bun5jon48v6svkfqjp10"
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
        re1 = requests.get(self.address+"profile?symbol="+symbol+"&token="+self.api)
        re2 = requests.get(self.address+"profile2?symbol="+symbol+"&token="+self.api)
        r1json = re1.json()
        r2json = re2.json()

    def fetch_MarketNews(self,symbol):
        re = requests.get(self.address+"")

    def fetch_Candles(self,symbol,start,end,res="1"):
        if isinstance(start,str):
            try:
                start = int(dt.datetime.strptime(start,'%Y-%m-%d').timestamp())
            except:
                print("Bad starting date format!")
                exit(0)
        if isinstance(end,str):
            try:
                end = int(dt.datetime.strptime(end,'%Y-%m-%d').timestamp())
            except:
                print("Bad starting date format!")
                exit(0)
        re = requests.get(self.address+"candle?symbol="+symbol+"&resolution="+str(res)+"&from="+str(start)+"&to="+str(end)+"&token="+self.api)
        rjd = re.json()
        if rjd['s']!='ok':
            print("No valid data in the given date range. Probably invalid date or limited API access?")
            exit(0)
        rarray = np.array([rjd['t'],rjd['o'],rjd['h'],rjd['l'],rjd['c'],rjd['v']]).T
        with open(symbol+'.npy','wb') as f:
            np.save(f,rarray)

