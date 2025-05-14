from src.core.database import mongo_client

# 同步方法，用于策略中获取投资组合数据
def get_portfolio_sync(user_id: str):
    db = mongo_client['investment_agent']
    # 获取投资组合
    portfolio = db.portfolios.find_one({'user_id': user_id})
    if not portfolio:
        return None
        
    # 获取持仓记录
    positions = list(db.positions.find({'user_id': user_id}))
    portfolio['positions'] = positions
        
    return portfolio