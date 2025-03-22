from .core.context import Context
from .config import g
import akshare as ak
from datetime import datetime, timedelta
from core.order import order_target_value,buy_security

def check_limit_up(context:Context):
    """
    检查当天涨停情况
    """
    now_time = context.current_dt
    if g['yesterday_HL_list'] != []:
        for stock in g['yesterday_HL_list']:
            # stock_zh_a_minute ｜ stock_zh_a_hist_min_em
            # now
            if g['in_history']:
                current_data = ak.stock_zh_a_hist_min_em(
                    symbol=stock, 
                    period="1", 
                    # start_date=(now_time - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    # end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                    start_date='2025-03-20 13:59:02',
                    end_date='2025-03-20 14:00:03', 
                    adjust=""
                )
                current_price = current_data['收盘'][0]
                # TODO 检查是否涨停
                # high_limit_price = 
                
            else:
                current_data = ak.stock_bid_ask_em(symbol=stock)
                current_price = current_data['value'][10]
                high_limit_price = current_data['value'][32]

            if current_price >= high_limit_price:
                print('[%s]涨停，继续持有' % (stock))
            else:
                print('[%s]未涨停，卖出' % (stock))
                print('context.portfolio.positions',context.portfolio.positions)
                position = context.portfolio.positions[stock]
                order_target_value(position, 0) #TODO 警惕失败
                g['reason_to_sell'] ='limitup'
                g['limitup_stocks'].append(stock)
                
    
def check_remain_amount(context:Context):
    """
    检查当天剩余资金是否足够
    """
    if g['reason_to_sell'] is 'limitup':
        g['hold_list'] = []
        for position in list(context.portfolio.positions.values()):
            stock = position.security
            g['hold_list'].append(stock)
        if len(g['hold_list']) < g['stock_num']:
            # 计算需要买入的股票数量
            num_stocks_to_buy = min(len(g['limitup_stocks']), g['stock_num'] - len(context.portfolio.positions))
            target_list = [stock for stock in g['target_list'] if stock not in g['limitup_stocks']][:num_stocks_to_buy]
            log.info('有余额可用'+str(round((context.portfolio.cash),2))+'元。买入'+ str(target_list))
            # buy_security(context,target_list)
        g['reason_to_sell'] = ''
    elif g['reason_to_sell'] is 'stoploss':
        print('有余额可用'+str(round((context.portfolio.cash),2))+'元。买入'+ str(g['etf']))
        buy_security(context,[g['etf']])
        g['reason_to_sell'] = ''
        
def trade_afternoon(context:Context):
    if g['trading_signal'] == True:
        check_limit_up(context)
        check_remain_amount(context)