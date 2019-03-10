
import matplotlib.pyplot as plt
import seaborn as sns
from zipline.api import symbols, order_target_percent, record
from zipline.finance import commission, slippage


sns.set()
stocks = ("BBD-B.TO","HBM.TO","IMG.TO","BTO.TO")
target = {
    u"BBD-B.TO":0.4,
    u"HBM.TO":.35,
    u"IMG.TO":0.15,
    u"BTO.TO":0.1
    }

def initialize(context):
    context.i = 0
    context.has_ordered = False
    context.stocks = symbols(*stocks)
    context.set_max_order_size(asset=context.stocks,max_notional=50000)
    context.set_commission(commission.PerTrade(cost=9.95))
    context.set_slippage(slippage.FixedSlippage(spread=0.1))

def handle_data(context, data):

    # skip first 60 days to get full windwos
    context.i += 1
    if context.i < 30:
        return

    # compute avarages and check lows and highs
    for stock in context.stocks:
        long_mavg  = data.history(stock,'price',30,"1d").mean()
        short_mavg = data.history(stock,'price',10,"1d").mean()

        #high_long  = data.history(stock,'high',10,"1d").max()
        #high_short = data.history(stock,'high',5,"1d").min()

        #low_long  = data.history(stock,'low',10,"1d").max()
        #low_short = data.history(stock,'low',5,"1d").min()

        buy_signal = short_mavg > long_mavg
        #buy_signal = buy_signal & (low_short > low_long)

        sell_signal = short_mavg < long_mavg
        #sell_signal = sell_signal & (high_short < high_long)

        if buy_signal:
            order_target_percent(stock,target[stock.symbol])

        if sell_signal:
            order_target_percent(stock,0.)

        kwargs = {
            stock.symbol:data.current(stock,"price"),
            "short_mavg":short_mavg,
            "long_mavg":long_mavg
        }
        record(**kwargs)
