from src.service.portfolio import get_portfolio_sync
from datetime import datetime,timedelta
from .portfolio import Portfolio
from ..config import current_user_id

class Context:
    def __init__(self):
        # 从数据库初始化投资组合
        portfolio_data = get_portfolio_sync(current_user_id)
        if portfolio_data:
            self.portfolio = Portfolio(portfolio_data)
        else:
            self.portfolio = Portfolio()
        self.current_dt = datetime.now()
        self.previous_date = self.current_dt - timedelta(days=1)