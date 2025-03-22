import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.order import order_target_value
from core.position import Position
from service.portfolio import get_portfolio_sync
from typing import Dict
from trade.config import g
from trade.core.context import Context
from trade.core.portfolio import Portfolio
from trade.trade_afternoon import trade_afternoon
from trade.weekly_adjustment import weekly_adjustment

from core.utils import fmtDate
        
#4-1 判断今天是否跳过月份
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
    # 先假设可以获取到 hold_list
    g['limitup_stocks'] = []
    if g['hold_list'] != []:
        date_str = fmtDate(context.current_dt)
        all_pre_zt_stocks = list(ak.stock_zt_pool_previous_em(date=date_str)['代码'])
        g['yesterday_HL_list'] = [stock for stock in g['hold_list'] if stock in all_pre_zt_stocks]
    else:
        g['yesterday_HL_list'] = []
    # 判断今天是否为账户资金再平衡的日期
    g['trading_signal'] = today_is_between(context)
    
def sell_stocks(context:Context):
    if g['run_stoploss']:
        current_positions = context.portfolio.positions
        if g['stoploss_strategy'] == 1 or g['stoploss_strategy'] == 3:
            for stock in current_positions.keys():
                position = current_positions[stock]
                price = current_positions[stock].price
                avg_cost = current_positions[stock].avg_cost
                # 个股盈利止盈
                if price >= avg_cost * 2:
                    order_target_value(position, 0)
                # 个股止损
                elif price < avg_cost * (1 - g['stoploss_limit']):
                    order_target_value(position, 0)
                    g['reason_to_sell'] = 'stoploss'
                    
        if g['stoploss_strategy'] == 2 or g['stoploss_strategy'] == 3:
            
            # stock_df = get_price(security=get_index_stocks('399101.XSHE'), end_date=context.previous_date, frequency='daily', fields=['close', 'open'], count=1, panel=False)
            stock_df = ak.stock_zh_a_hist(
                symbol="399101",
                period="daily",
                start_date=fmtDate(context.previous_date),
                end_date=fmtDate(context.previous_date)
            )
            # stock_down_ratio = stock_df['涨跌幅'].values[0]
            stock_open = stock_df['开盘'].values[0]
            stock_close = stock_df['收盘'].values[0]
            down_ratio = abs((stock_close / stock_open - 1).mean())
            # 市场大跌止损
            if down_ratio >= g['stoploss_market']:
                g['reason_to_sell'] = 'stoploss'
                for stock in current_positions.keys():
                    order_target_value(stock, 0)
        
    
if __name__ == "__main__":
    context = Context()
    prepare_stock_list(context)
    sell_stocks(context)
    trade_afternoon(context)
    weekly_adjustment(context)