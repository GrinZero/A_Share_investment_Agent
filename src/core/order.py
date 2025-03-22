from datetime import datetime
from .position import Position
from .database import mongo_client
from src.trade.core.context import Context

def order_target_value(stock:Position, target_count):
    current_count = stock.total_amount
    print(f"股票代码: {stock.security}, 交易变化: 从 {current_count} 股调整到 {target_count} 股")
    
    try:
        db = mongo_client['investment_agent']
        
        # 计算交易数量和方向
        trade_shares = target_count - current_count
        trade_type = 'buy' if trade_shares > 0 else 'sell'
        trade_shares = abs(trade_shares)
        
        if trade_shares > 0:
            # 更新持仓记录
            db.positions.update_one(
                {'code': stock.security},
                {'$set': {
                    'shares': target_count,
                    'market_value': target_count * stock.price,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            # 创建交易记录
            transaction = {
                'code': stock.security,
                'type': trade_type,
                'date': datetime.utcnow(),
                'price': stock.price,
                'shares': trade_shares,
                'amount': trade_shares * stock.price,
                'fee': trade_shares * stock.price * 0.001,  # 假设手续费为0.1%
                'created_at': datetime.utcnow()
            }
            db.transactions.insert_one(transaction)
            
            # 更新投资组合的现金和总市值
            trade_amount = trade_shares * stock.price * (1 if trade_type == 'sell' else -1)
            db.portfolios.update_many(
                {},
                {'$inc': {
                    'cash': trade_amount,
                    'total_value': -trade_amount
                }}
            )
            
    except Exception as e:
        print(f"数据库操作失败: {str(e)}")
    
def buy_security(context:Context, target_list):
    position_count = len(context.portfolio.positions)
    target_num = len(target_list)
    if target_num > position_count:
        value = context.portfolio.cash / (target_num - position_count)
        for stock in target_list:
            if context.portfolio.positions[stock].total_amount == 0:
                print("买入[%s]（%s元）" % (stock,value))
                order_target_value(stock, value)
                
def close_position(stock:Position):
    print("卖出[%s]" % (stock.security))
    order_target_value(stock, 0)
    