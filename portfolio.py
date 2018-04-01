# basic functions for managing open trades
# TODO: active exposure and trade/asset correlations functions

from config import accountID, token
from orders import closeAll, trailingStop, close
from account import balance
from oandapyV20 import API
from oandapyV20.endpoints.positions import OpenPositions
from oandapyV20.exceptions import V20Error
import time

class Portfolio:

    def __init__(self):
        self.api = API(token)
        self.openOrders = openOrders()
        self.killTrades = killTrades()
        self.statistics = statistics()
        self.monitor = monitor()
        self.applyTS = applyTS()

    # returns a dictionary of open orders, with IDs, long/short bias, and averagePrice of open trades for an asset
    def openOrders(self, instrument_list):
        OP = OpenPositions(accountID)
        self.api.request(OP)
        op = OP.response['positions']
        open_orders = dict()
        # collect all open tradeIDs
        for pair in instrument_list:
            # search op to find all positions for an asset
            positions = list(filter(lambda position: position['instrument'] == pair, op))
            if positions:
                if int(positions[0]['long']['units']) > 0:
                    longIDs = positions[0]['long']['tradeIDs']
                    avgPrice = positions[0]['long']['averagePrice']
                    open_orders[pair] = {'IDs': longIDs,
                                        'Bias': 'long', "AvgPrice": avgPrice}
                elif int(positions[0]['short']['units']) > 0:
                    shortIDs = positions[0]['short']['tradeIDs']
                    avgPrice = positions[0]['short']['averagePrice']
                    open_orders[pair] = {'IDs': shortIDs,
                                        'Bias':'short', 'AvgPrice':avgPrice}
        return open_orders

    # closes all open trades
    def killTrades(self, instrument_list):
        oo = self.openOrders(instrument_list)
        for i in oo:
            open_trades = oo[i]['IDs']
            closeAll(open_trades)

    # get per trade statistics
    def statistics(self, instrument):
        OP = OpenPositions(accountID)
        self.api.request(OP)
        op = OP.response['positions']
        pos = list(filter(lambda position: position['instrument'] == instrument, op))
        try:
            if int(pos[0]['long']['units']) > 0:
                trade = pos[0]['long']
                open_pnl = trade['unrealizedPL']
                carry = pos[0]['financing']
                margin_used = pos[0]['marginUsed']
                return open_pnl, carry, margin_used
            elif int(pos[0]['short']['units']) < 0:
                trade = pos[0]['short']
                open_pnl = trade['unrealizedPL']
                carry = trade['financing']
                margin_used = pos[0]['marginUsed']
                return open_pnl, carry, margin_used
        except:
            pass

    # monitors the health of all open trades,redundant use of openOrders because
    # trades/instruments sometimes get missed for one reason or another.
    def monitor(self, instrument_list):
        oo = openOrders(instrument_list)
        print("Monitoring trades...")
        for instr in instrument_list:
            if instr in oo:
                stats = self.statistics(instr)
                open_pnl = float(stats[0])
                print("%s current pnl: %s" % (instr, open_pnl))
            # other functions can be put here to close or add to positions, store data, etc.

    # mo --> market order response, ts --> distance for trailingStop
    def applyTS(self, mo, ts):
        tradeID = mo['orderFillTransaction']['id']
        price = float(mo['orderFillTransaction']['price'])

        p = str(price)
        p = p.split('.')
        p0 = len(p[0])
        p1 = len(p[1])

        # filter for gold, some fx, and indicies with larger front values but shorter floating points
        if p0 < 4:
            n = float(ts / 100000)
            r = round((price * n), p1)
        else:
            n = ts / 10000
            r = round((price * n), p1)

        try:
            trailingStop(tradeID, r)

        except V20Error as e:
            print(e)
            n = float(ts / 10000)
            try:
                trailingStop(tradeID, r)
            except:
                close(tradeID)
