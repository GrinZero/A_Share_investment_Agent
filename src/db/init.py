from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
import os

# 获取MongoDB连接URI
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://root:example@localhost:27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'investment_agent')

def init_database():
    """初始化数据库，创建集合和索引"""
    try:
        # 连接MongoDB
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        
        # 创建投资组合集合并设置索引
        portfolios = db.portfolios
        portfolios.create_index([('user_id', ASCENDING)])
        portfolios.create_index([('created_at', DESCENDING)])
        
        # 创建持仓记录集合并设置索引
        positions = db.positions
        positions.create_index([('portfolio_id', ASCENDING)])
        positions.create_index([('code', ASCENDING)])
        positions.create_index([('created_at', DESCENDING)])
        
        # 创建交易记录集合并设置索引
        transactions = db.transactions
        transactions.create_index([('portfolio_id', ASCENDING)])
        transactions.create_index([('code', ASCENDING)])
        transactions.create_index([('date', DESCENDING)])
        
        print(f"数据库 {MONGODB_DATABASE} 初始化成功")
        
        # 创建示例投资组合
        create_example_portfolio(db)
        
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
    finally:
        client.close()

def create_example_portfolio(db):
    """创建示例投资组合数据"""
    try:
        # 创建示例投资组合
        portfolio = {
            'user_id': 'example_user',
            'name': '示例A股组合',
            'cash': 100000,  # 10万初始资金
            'total_value': 0, # 初始总市值
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        portfolio_id = db.portfolios.insert_one(portfolio).inserted_id
        
        # 创建示例持仓记录
        position = {
            'portfolio_id': portfolio_id,
            'code': '600519',
            'name': '贵州茅台',
            'shares': 100,
            'cost_price': 1800.0,
            'current_price': 1850.0,
            'market_value': 185000.0,
            'profit': 5000.0,
            'profit_pct': 2.78,
            'hold_days': 30,
            'buy_date': datetime.utcnow(),
            'highest_price': 1900.0,
            'stoploss_price': 1700.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # 但是不要插入
        # db.positions.insert_one(position)
        
        # 创建示例交易记录
        transaction = {
            'portfolio_id': portfolio_id,
            'code': '600519',
            'name': '贵州茅台',
            'type': 'buy',
            'date': datetime.utcnow(),
            'price': 1800.0,
            'shares': 100,
            'amount': 180000.0,
            'fee': 180.0,
            'reason': '示例买入',
            'created_at': datetime.utcnow()
        }
        
        # 但是不要插入
        # db.transactions.insert_one(transaction)
        
        print("示例数据创建成功")
        
    except Exception as e:
        print(f"示例数据创建失败: {str(e)}")

if __name__ == '__main__':
    init_database()