# price history or stream functions

from config import token, accountID, env
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20.endpoints.pricing import PricingStream
import pandas as pd
import time

class Pricing:

    def __init__(self):
        self.api = API(token)
        #self.history = history()
        #self.stream = stream()

    # returns the last 500 OHLCV candles for an instrument
    # maximum count is 500
    # window: M1, M5, M15, H, H4, D, etc.
    def history(self, instrument, window, collection=False):
        instrument = instrument
        data = list()
        client = API(token)
        params = {"count":500, "granularity":window}
        r = InstrumentsCandles(instrument, params)
        client.request(r)
        resp = r.response
        for candle in resp.get('candles'):
            Open   = candle['mid']['o']
            High   = candle['mid']['h']
            Low    = candle['mid']['l']
            Close  = candle['mid']['c']
            Volume = candle['volume']

            update = [Open, High, Low, Close, Volume]
            data.append(update)
        df = pd.DataFrame(data, columns=['Open','High','Low','Close','Volume'])
        # collect data, useful for research and weekends/holidays when the market isn't open
        if collection == True:
            title = 'data/%s_%s_history.csv' % (instrument, window)
            df.to_csv(title)

    # creates a pricing stream,
    def stream(self, instrument, window):
        request_params = {"timeout":100}
        params = {"instruments":instrument, "granularity":window}
        self.api = API(access_token=token,environment=env, request_params=request_params)
        r = PricingStream(accountID=accountID, params=params)

        while True:
            try:
                api.request(r)
                for R in r.response:
                    data = {"time":R['time'],
                            "closeoutAsk":R['closeoutAsk'],
                            "closeoutBid":R['closeoutBid'],
                            "status":R['status'],
                            "instrument":R['instrument'],
                            "ask":R['ask'],
                            "bid":R['bid']}

                    print(data)
            except Exception as e:
                print(e)
                continue
