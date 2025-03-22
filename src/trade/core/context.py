from src.service.portfolio import get_portfolio_sync
from datetime import datetime,timedelta
from .portfolio import Portfolio
from ..config import current_user_id

class Context:
    def __init__(self, current_dt: datetime = None):
        # 从数据库初始化投资组合
        portfolio_data = get_portfolio_sync(current_user_id)
        if portfolio_data:
            self.portfolio = Portfolio(portfolio_data)
        else:
            self.portfolio = Portfolio()
        
        # 设置当前时间，如果没有传入则使用当前时间
        self.current_dt = current_dt if current_dt else datetime.now()
        self.previous_date = self.current_dt - timedelta(days=1)
    
    def set_current_dt(self, current_dt: datetime):
        self.current_dt = current_dt
        self.previous_date = current_dt - timedelta(days=1)
        
    def update_portfolio(self):
        portfolio_data = get_portfolio_sync(current_user_id)
        if portfolio_data:
            self.portfolio = Portfolio(portfolio_data)
        else:
            self.portfolio = Portfolio()