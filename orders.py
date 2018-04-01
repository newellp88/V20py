# class to support opening and closing trades
import json
from oandapyV20 import API
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import TradeCloseRequest
from oandapyV20.exceptions import V20Error
from config import accountID, token
from account import margin_available, margin_rate
from oandapyV20.contrib.requests import (MarketOrderRequest,
                                         TakeProfitDetails,
                                         StopLossDetails,
                                         TrailingStopLossOrderRequest)

class Orders:

    def __init__(self, should_print=True):
        self.api = API(token)
        self.should_print = should_print
        self.weight = weight()
        self.order = order()
        self.trailingStop = trailingStop()
        self.close = close()
        self.closeAll = closeAll()

    def weight(self, price, allocation):
        trade_margin = float(margin_available) * self.allocation
        trade_value = trade_margin / float(margin_rate)
        w = round((trade_value/float(price)), 0)
        return w

    def order(self, instrument, weight, price):
        # calculate TP/SL, these are fixed @ .5%/.25%; change to fit your needs
        p = str(price)
        p = p.split('.')
        p = len(p[1])
        self.TP_long = round((price * 1.005), p)
        self.SL_long = round((price * 0.9975), p)
        self.TP_short = round((price * 0.995), p)
        self.SL_short = round((price * 1.0025), p) # sometimes have an issue rounding with JPY crosses

        if self.weight > 0:
            mktOrder = MarketOrderRequest(
                            instrument=instrument,
                            units=weight,
                            TakeProfitOnFill=TakeProfitDetails(price=self.TP_long).data,
                            stopLossOnFill=StopLossDetails(price=self.SL_long).data)
            r = orders.OrderCreate(accountID, data=mktOrder.data)

            try:
                rv = self.api.request(r)
                if self.should_print == True:
                    print(r.status_code)
            except V20Error as e:
                print(r.status_code, e)
            else:
                if self.should_print == True:
                    print(json.dumps(rv, indent=4))

        else:
            mktOrder = MarketOrderRequest(
                                instrument=instrument,
                                units=weight,
                                TakeProfitOnFill=TakeProfitDetails(price=self.TP_short).data,
                                stopLossOnFill=StopLossDetails(price=self.SL_short).data)
            r = orders.OrderCreate(accountId, data=mktOrder.data)

            try:
                rv = self.api.request(r)
                if self.should_print == True:
                    print(r.status_code)
            except V20Error as e:
                print(r.status_code, e)
            else:
                if self.should_print == True:
                    print(json.dumps(rv, indent=4))

        return r.response

    def trailingStop(self, tradID, distance=0.25):
        activeStop = TrailingStopLossOrderRequest(tradeID=tradeID,
                                                    distance=distance)
        r = orders.OrderCreate(accountID, tradeID, data=activeStop.data)
        self.api.request(r)
        if self.should_print == True:
            print(r.response)
        return r.response

    def close(self, tradeID):
        close_trade = TradeCloseRequest()
        r = trades.TradeClose(accountID, tradeID, data=close_trade.data)
        self.api.request(r)
        if self.should_print == True:
            print("Closing trade: ", r.response)
        return r.response

    def closeAll(self, tradeID_list):
        for trade in tradeID_list:
            close(trade)
            print(trade, "Closed")
