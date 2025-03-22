from .core.context import Context
from .config import g
from datetime import datetime, timedelta
import akshare as ak
from src.core.utils import fmtDate
import pandas as pd
from core.order import buy_security,order_target_value
from .core.stock import get_stock_list

def adjust_stock_num(context: Context):
    ma_para = 10  # 设置MA参数
    today = context.previous_date
    start_date = today - timedelta(days = ma_para*2)
    index_df = ak.stock_zh_a_hist(
        symbol="399101",
        start_date=fmtDate(start_date),
        end_date=fmtDate(today),
        period="daily",
    )
    close_prices = list(index_df['收盘'].values)
    # 用 pandas 计算MA
    index_df['ma'] = pd.Series(close_prices).rolling(window=ma_para).mean()
    last_row = index_df.iloc[-1]
    diff = last_row['收盘'] - last_row['ma']
    result = 3 if diff >= 500 else \
             3 if 200 <= diff < 500 else \
             4 if -200 <= diff < 200 else \
             5 if -500 <= diff < -200 else \
             6
    return result
    
def weekly_adjustment(context: Context):
    """
    每周调仓
    """
    # 判断今天是否为账户资金再平衡的日期
    if g['trading_signal'] and g['adjust_num']:
        new_num = adjust_stock_num(context)
        print(new_num)
        if new_num == 0:
            buy_security(context, [g['etf']])
            print('MA指示指数大跌，持有%s' % g['etf'])
        else:
            if g['stock_num'] != new_num:
                g['stock_num'] = new_num
                print('调整股票数量为：%d' % new_num)
            g['target_list'] = get_stock_list(context)[:g['stock_num']]
            # 注意买的时候要确保购买价格 last_prices <= g['highest']
            print(str(g.target_list))
            
            sell_list = [stock for stock in g['hold_list'] if stock not in g['target_list'] and stock not in g['yesterday_HL_list']]
            hold_list = [stock for stock in g['hold_list'] if stock in g['target_list'] or stock in g['yesterday_HL_list']]
            print("已持有[%s]" % (str(hold_list)))
            print("卖出[%s]" % (str(sell_list)))
            
            sell_positions = [context.portfolio.positions[stock] for stock in sell_list]
            for position in sell_positions:
                order_target_value(position, 0)
                
            buy_security(context, g['target_list'])
    else:
        buy_security(context, [g['etf']])
        print('该月份为空仓月份，持有银华日利ETF')