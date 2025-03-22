from datetime import datetime, timedelta
from .position import Position
from .database import mongo_client
from src.trade.core.context import Context
from src.trade.config import g,current_user_id
from .utils import fmtDateTime
import akshare as ak
from src.trade.core.stock import get_market_code_by_code
from .recorder import record
from src.core.utils import logger

def order_target_value(context: Context, stock:Position | str, target_count):
    if isinstance(stock, str):
        stock = context.portfolio.get_position(stock) 
    logger.info(f"股票代码: {stock.security}, 交易变化: 从 {stock.total_amount} 股调整到 {target_count} 股")
    
    try:
        db = mongo_client['investment_agent']
        
        # 计算交易数量和方向
        trade_shares = target_count - stock.total_amount
        trade_type = 'buy' if trade_shares > 0 else 'sell'
        trade_shares = abs(trade_shares)
        
        if trade_shares > 0:
            # 获取当前价格
            if g['in_history']:
                ad = ak.stock_zh_a_minute(
                    symbol = get_market_code_by_code(stock.security,style="lower"),
                    period="1",
                )
                ad.set_index('day', inplace=True)
                day = context.current_dt
                day = day.replace(second=0)
                day = fmtDateTime(day)
                price = float(ad.loc[day]['close'])
            else:
                ad = ak.stock_bid_ask_em(symbol=stock.security)
                price = float(ad['value'][8] if trade_type == 'buy' else ad['value'][10])
            
            logger.info('买入/卖出价格: %s' % price)
            logger.info('交易数量: %s' % trade_shares)
            logger.info('交易类型: %s' % trade_type)
            logger.info('交易金额: %s' % (trade_shares * price))
            logger.info('交易手续费: %s' % (trade_shares * price * 0.001))
            logger.info('交易时间: %s' % context.current_dt)
            global order_record
            record['order_record'].append({
                'code': stock.security,
                'name': stock.security,
                'shares': trade_shares,
                'price': price,
                'amount': trade_shares * price,
                'fee': trade_shares * price * 0.001,
                'type': trade_type,
                'date': context.current_dt
            })
            
            # 更新 Position 对象
            stock.update_price(price)
            if trade_type == 'buy':
                stock.buy(trade_shares, price, trade_shares * price * 0.001)
            else:
                stock.sell(trade_shares, price, trade_shares * price * 0.001)
            
            # 更新持仓记录
            position_update = {
                'code': stock.security,
                'name': stock.security,
                'shares': stock.total_amount,
                'cost_price': stock.avg_cost,
                'current_price': stock.price,
                'market_value': stock.value,
                'profit': stock.floating_pnl,
                'profit_pct': (stock.floating_pnl / (stock.avg_cost * stock.total_amount)) * 100 if stock.total_amount > 0 else 0,
                'hold_days': (context.current_dt - stock.init_time).days if stock.init_time else 0,
                'buy_date': stock.init_time or context.current_dt,
                'highest_price': max(price, stock.highest_price if hasattr(stock, 'highest_price') else price),
                'stoploss_price': stock.avg_cost * 0.9,
                'updated_at': context.current_dt,
                'user_id': current_user_id
            }
            
            # 数据库操作
            if stock.total_amount > 0:
                db.positions.update_one(
                    {'code': stock.security, 'user_id': current_user_id},
                    {'$set': position_update},
                    upsert=True
                )
            else:
                db.positions.delete_one({'code': stock.security, 'user_id': current_user_id})
            
            # 创建交易记录
            transaction = {
                'code': stock.security,
                'type': trade_type,
                'date': context.current_dt,
                'price': price,
                'shares': trade_shares,
                'amount': trade_shares * price,
                'fee': trade_shares * price * 0.001,
                'created_at': context.current_dt,
                'user_id': current_user_id
            }
            db.transactions.insert_one(transaction)
            
            # 更新投资组合
            trade_amount = trade_shares * price * (1 if trade_type == 'sell' else -1)
            db.portfolios.update_one(
                {'user_id': current_user_id},
                {'$inc': {
                    'cash': trade_amount - transaction['fee'],
                    'total_value': -trade_amount
                }}
            )
            
            # 更新内存中的 portfolio
            if trade_type == 'buy':
                context.portfolio.positions[stock.security] = stock
                context.portfolio.cash -= (trade_amount + transaction['fee'])
                context.portfolio.total_value -= trade_amount
            else:
                if stock.total_amount == 0:
                    del context.portfolio.positions[stock.security]
                else:
                    context.portfolio.positions[stock.security] = stock
                context.portfolio.cash += (trade_amount - transaction['fee'])
                context.portfolio.total_value += trade_amount
            
    except Exception as e:
        logger.info(f"交易执行失败: {str(e)}")
        raise e
    
def buy_security(context:Context, target_list):
    position_count = len(context.portfolio.positions)
    target_num = len(target_list)
    if target_num > position_count:
        value = context.portfolio.cash / (target_num - position_count)
        for stock in target_list:
            position = context.portfolio.get_position(stock)
            if position == None or position.total_amount == 0:
                logger.info("买入[%s]（%s元）" % (stock,value))
                order_target_value(context,stock, value)
                
def close_position(context:Context, stock:Position):
    logger.info("卖出[%s]" % (stock.security))
    order_target_value(context,stock, 0)
    
if __name__ == "__main__":
    context = Context()
    context.set_current_dt(
        datetime(2025, 3, 21, 14, 30)
    )
    g['in_history'] = True
    order_target_value(context, '000001', 1000)

