from src.core.position import Position
from typing import Dict


class Portfolio:
    positions: Dict[str, Position]
    def __init__(self, portfolio_data=None):
        if portfolio_data:
            self.cash = portfolio_data['cash']
            self.total_value = portfolio_data['total_value']
            self.positions:Dict[str,Position] = {}
            # 初始化持仓
            for pos_data in portfolio_data['positions']:
                position = Position(pos_data['code'])
                position.total_amount = pos_data['shares']
                position.avg_cost = pos_data['cost_price']
                position.price = pos_data['current_price']
                position.init_time = pos_data['buy_date']
                position.transact_time = pos_data['updated_at']
                self.positions[pos_data['code']] = position
        else:
            self.positions:Dict[str,Position] = {}
            self.cash = 1e6  # 初始资金
            self.total_value = self.cash
    
    def get_position(self, code):
        return self.positions.get(code)