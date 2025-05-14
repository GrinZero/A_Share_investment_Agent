from .core.context import Context
from .config import g
from src.core.order import order_target_value
from src.core.utils import fmtDate
import akshare as ak
from src.core.utils import logger

def today_is_between(context:Context):
    # 根据g.pass_month跳过指定月份
    today = context.current_dt
    month = today.month
    if month in g['pass_months']:
        return False
    else:
        return True

def prepare_stock_list(context:Context):
    g['hold_list']= [] # str[]
    for position in list(context.portfolio.positions.values()):
        stock = position.security
        g['hold_list'].append(stock)
    logger.info('持仓列表: %s', g['hold_list'])
    g['limitup_stocks'] = []
    if g['hold_list'] != []:
        date_str = fmtDate(context.current_dt)
        all_pre_zt_stocks = list(ak.stock_zt_pool_previous_em(date=date_str)['代码'])
        g['yesterday_HL_list'] = [stock for stock in g['hold_list'] if stock in all_pre_zt_stocks]
    else:
        g['yesterday_HL_list'] = []
    logger.info('昨日涨停列表: %s', g['yesterday_HL_list'])
    # 判断今天是否为账户资金再平衡的日期
    g['trading_signal'] = today_is_between(context)
    logger.info('账户资金再平衡: %s', g['trading_signal'])
   