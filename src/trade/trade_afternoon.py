from .core.context import Context
from .config import g
import akshare as ak
from datetime import datetime, timedelta
from src.core.order import order_target_value,buy_security
from src.core.utils import logger

def check_limit_up(context:Context):
    """
    检查当天涨停情况
    """
    now_time = context.current_dt
    logger.info("检查涨停情况: %s",g['yesterday_HL_list'])
    if g['yesterday_HL_list'] != []:
        for stock in g['yesterday_HL_list']:
            # stock_zh_a_minute ｜ stock_zh_a_hist_min_em
            # now
            if g['in_history']:
                current_data = ak.stock_zh_a_hist_min_em(
                    symbol=stock, 
                    period="1", 
                    start_date=(now_time - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    end_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
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
                logger.info('[%s]涨停，继续持有' % (stock))
            else:
                logger.info('[%s]未涨停，卖出' % (stock))
                logger.info('context.portfolio.positions',context.portfolio.positions)
                position = context.portfolio.get_position(stock)
                if position == None or position.total_amount == 0:
                    logger.info('position is None',position)
                order_target_value(context,position, 0) #TODO 警惕失败
                g['reason_to_sell'] ='limitup'
                g['limitup_stocks'].append(stock)
                
    
def check_remain_amount(context:Context):
    """
    检查当天剩余资金是否足够
    """
    logger.info("检查剩余资金: %s",g['reason_to_sell'])
    if g['reason_to_sell'] == 'limitup':
        g['hold_list'] = []
        for position in list(context.portfolio.positions.values()):
            stock = position.security
            g['hold_list'].append(stock)
        if len(g['hold_list']) < g['stock_num']:
            # 计算需要买入的股票数量
            num_stocks_to_buy = min(len(g['limitup_stocks']), g['stock_num'] - len(context.portfolio.positions))
            target_list = [stock for stock in g['target_list'] if stock not in g['limitup_stocks']][:num_stocks_to_buy]
            logger.info('有余额可用'+str(round((context.portfolio.cash),2))+'元。买入'+ str(target_list))
            buy_security(context,target_list)
        g['reason_to_sell'] = ''
    elif g['reason_to_sell'] == 'stoploss':
        logger.info('有余额可用'+str(round((context.portfolio.cash),2))+'元。买入'+ str(g['etf']))
        buy_security(context,[g['etf']])
        g['reason_to_sell'] = ''
        
def trade_afternoon(context:Context):
    logger.info('下午交易开始')
    if g['trading_signal'] == True:
        logger.info('下午交易信号为 True, 检查是否需要存在涨停股以及存量资金')
        check_limit_up(context)
        check_remain_amount(context)