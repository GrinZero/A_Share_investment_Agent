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
from trade.close_account import close_account
from trade.prepare_stock_list import prepare_stock_list
from trade.sell_stocks import sell_stocks
from src.core.scheduler import run_scheduler,run_daily,run_weekly
from core.utils import fmtDate
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    run_daily(prepare_stock_list, '9:05')
    run_daily(trade_afternoon, time='14:00') #检查持仓中的涨停股是否需要卖出
    run_daily(sell_stocks, time='10:00') # 止损函数
    run_daily(close_account, '14:50')
    run_weekly(weekly_adjustment,3,'09:45')
    
    run_scheduler()