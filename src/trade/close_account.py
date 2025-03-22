from .core.context import Context
from .config import g
from src.core.order import order_target_value


def close_account(context:Context):
    if g['trading_signal'] == False:
        if len(g['hold_list']) != 0 and g['hold_list'] != [g['etf']]:
            for stock in g['hold_list']:
                position = context.portfolio.positions[stock]
                order_target_value(position, 0)
                log.info("卖出[%s]" % (stock))