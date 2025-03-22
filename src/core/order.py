from datetime import datetime, timedelta
from .position import Position
from .database import mongo_client
from src.trade.core.context import Context
from src.trade.config import g,current_user_id
from .utils import fmtDateTime
import akshare as ak
from src.trade.core.stock import get_market_code_by_code

def order_target_value(context: Context, stock:Position | str, target_count):
    if isinstance(stock, str):
        stock = Position(stock)
    print(f"股票代码: {stock.security}, 交易变化: 从 {stock.total_amount} 股调整到 {target_count} 股")
    
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
            
            # 获取股票名称
            stock_name = stock.security
            
            # 计算持仓成本和收益
            if trade_type == 'buy':
                if stock.total_amount == 0:  # 新建仓位
                    cost_price = price
                    buy_date = context.current_dt
                    hold_days = 0
                else:  # 加仓，计算平均成本
                    total_cost = stock.total_amount * stock.cost_price + trade_shares * price
                    cost_price = total_cost / target_count
                    buy_date = stock.buy_date
                    hold_days = (context.current_dt - buy_date).days
            else:  # 卖出，保持原有成本价
                cost_price = stock.cost_price
                buy_date = stock.buy_date
                hold_days = (context.current_dt - buy_date).days
            
            market_value = target_count * price
            profit = market_value - (target_count * cost_price)
            profit_pct = (profit / (target_count * cost_price)) * 100 if target_count > 0 else 0
            
            # 更新持仓记录
            position_update = {
                'code': stock.security,
                'name': stock_name,
                'shares': target_count,
                'cost_price': cost_price,
                'current_price': price,
                'market_value': market_value,
                'profit': profit,
                'profit_pct': profit_pct,
                'hold_days': hold_days,
                'buy_date': buy_date,
                'highest_price': max(price, stock.highest_price if hasattr(stock, 'highest_price') else price),
                'stoploss_price': cost_price * 0.9,  # 设置止损价为成本价的90%
                'updated_at': context.current_dt,
                'user_id': current_user_id
            }
            
            if target_count > 0:  # 有持仓才更新或创建
                db.positions.update_one(
                    {'code': stock.security, 'user_id': current_user_id},
                    {'$set': position_update},
                    upsert=True
                )
            else:  # 清仓则删除持仓记录
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
                    'cash': trade_amount,
                    'total_value': -trade_amount
                }}
            )
            
            # 更新内存中的 portfolio
            if trade_type == 'buy':
                stock.update_from_dict(position_update)
                context.portfolio.positions[stock.security] = stock
                context.portfolio.cash -= trade_amount
                context.portfolio.total_value -= trade_amount
            else:
                if target_count == 0:
                    del context.portfolio.positions[stock.security]
                else:
                    stock.update_from_dict(position_update)
                    context.portfolio.positions[stock.security] = stock
                context.portfolio.cash += trade_amount
                context.portfolio.total_value += trade_amount
            
    except Exception as e:
        print(f"交易执行失败: {str(e)}")
        raise e
    
def buy_security(context:Context, target_list):
    position_count = len(context.portfolio.positions)
    target_num = len(target_list)
    if target_num > position_count:
        value = context.portfolio.cash / (target_num - position_count)
        for stock in target_list:
            position = context.portfolio.get_position(stock)
            if position == None or position.total_amount == 0:
                print("买入[%s]（%s元）" % (stock,value))
                order_target_value(context,stock, value)
                
def close_position(context:Context, stock:Position):
    print("卖出[%s]" % (stock.security))
    order_target_value(context,stock, 0)
    
if __name__ == "__main__":
    context = Context()
    context.set_current_dt(
        datetime(2025, 3, 21, 14, 30)
    )
    # g['in_history'] = True
    order_target_value(context, '000001', 10000)

