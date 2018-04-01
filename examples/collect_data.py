from config import currencies
from pricing import Pricing
import time

windows = ['M5', 'M15', 'H1', 'H4', 'D']

def collect_data(windows, currencies):
    p = Pricing()
    n = 0
    for window in windows:
        for instr in currencies:
            p.history(instr, window, collection=True)
            n += 1
            print("% i CSVs downloaded" % n)

collect_data(windows, currencies)
