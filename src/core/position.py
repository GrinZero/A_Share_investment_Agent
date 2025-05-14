import datetime
from src.core.utils import logger
import akshare as ak

class Position:
    def __init__(self, security, name = None, multiplier=1, side='long', pindex=0):
        # 基础信息
        self.security = security          # 标的代码
        self.name = name or security      # 标的名称
        if not name or name == security:
            try:
                d = ak.stock_individual_info_em(symbol=security)
                self.name = d['value'][2]
            except Exception as e:
                print(f'获取股票名称失败: {e}')
                self.name = security
        
        self.multiplier = multiplier      # 合约乘数(股票为1)
        self.side = side                  # 仓位方向
        self.pindex = pindex              # 子账户索引
        
        # 持仓状态
        self.total_amount = 0             # 总持仓量(不含冻结)
        self.locked_amount = 0            # 冻结数量
        self.today_amount = 0             # 当日新增持仓
        self.init_time = None             # 首次建仓时间
        self.transact_time = None         # 最后交易时间
        
        # 成本相关
        self.acc_avg_cost = 0.0           # 累计平均成本(含历史盈亏)
        self.avg_cost = 0.0               # 当前持仓成本(仅买入更新)
        self.hold_cost = 0.0              # 当日持仓成本
        
        # 市场数据
        self.price = 0.0                  # 最新行情价格
        
    def update_from_dict(self, data):
        for key, value in data.items():
            setattr(self, key, value)    
        
    @property
    def closeable_amount(self):
        """可平仓数量(示例按T+1规则，需根据具体市场规则实现)"""
        return self.total_amount - self.today_amount - self.locked_amount
    
    @property
    def value(self):
        """当前持仓市值"""
        return self.price * self.total_amount * self.multiplier
    
    @property
    def floating_pnl(self):
        """浮动盈亏"""
        return (self.price - self.avg_cost) * self.total_amount * self.multiplier
    
    def update_price(self, new_price):
        """更新市场价格"""
        self.price = new_price
    
    def buy(self, trade_amount, trade_price, commission=0):
        """买入开仓/加仓"""
        # 计算交易金额
        trade_value = trade_amount * trade_price
        
        # 更新累计成本(考虑历史盈亏)
        total_cost = self.acc_avg_cost * self.total_amount + trade_value + commission
        new_total_amount = self.total_amount + trade_amount
        self.acc_avg_cost = total_cost / new_total_amount if new_total_amount !=0 else 0
        
        # 更新当前持仓成本(不考虑历史盈亏)
        current_value = self.avg_cost * self.total_amount
        new_avg_cost = (current_value + trade_value + commission) / new_total_amount
        
        # 更新持仓数量
        self.avg_cost = new_avg_cost
        self.total_amount += trade_amount
        self.today_amount += trade_amount
        
        # 更新持仓成本(当日)
        self._update_hold_cost(trade_amount, trade_price, is_buy=True)
        
        # 更新时间戳
        self._update_timestamps()
    
    def sell(self, trade_amount, trade_price, commission=0):
        """卖出平仓/减仓"""
        if trade_amount > self.closeable_amount:
            raise ValueError("可平仓数量不足")
        
        # 计算交易金额
        trade_value = trade_amount * trade_price
        
        # 更新累计成本(卖出时保留小数避免除零)
        total_cost = self.acc_avg_cost * self.total_amount - trade_value + commission
        new_total_amount = self.total_amount - trade_amount
        self.acc_avg_cost = total_cost / new_total_amount if new_total_amount !=0 else 0
        
        # 当前持仓成本不变
        # 更新持仓数量
        self.total_amount -= trade_amount
        self._update_hold_cost(trade_amount, trade_price, is_buy=False)
        
        # 更新时间戳
        self._update_timestamps()
    
    def _update_hold_cost(self, trade_amount, trade_price, is_buy):
        """更新当日持仓成本"""
        if is_buy:
            total = self.hold_cost * (self.total_amount - trade_amount) + trade_price * trade_amount
            self.hold_cost = total / self.total_amount
        else:
            remaining_amount = self.total_amount
            if remaining_amount > 0:
                self.hold_cost = (self.hold_cost * (remaining_amount + trade_amount) - trade_price * trade_amount) / remaining_amount
    
    def _update_timestamps(self):
        """更新时间戳"""
        now = datetime.datetime.now()
        if self.total_amount > 0 and self.init_time is None:
            self.init_time = now
        self.transact_time = now
    
    def daily_settlement(self, settlement_price):
        """每日结算"""
        self.hold_cost = settlement_price  # 重置为前收价
        self.today_amount = 0              # 重置当日开仓
        self.locked_amount = 0              # 清空冻结量(假设未成交单作废)
    
    def __repr__(self):
        return (f"<Position {self.security} | "
                f"Amount: {self.total_amount} | "
                f"AvgCost: {self.avg_cost:.2f} | "
                f"Value: {self.value:.2f}>")

# 测试用例
if __name__ == "__main__":
    # 测试1: 初始建仓
    p = Position('600000')
    p.update_price(10.0)
    p.buy(1000, 10.0, commission=5)  # 买入1000股，价格10元，手续费5元
    
    logger.info(p)  # <Position 600000 | Amount: 1000 | AvgCost: 10.01 | Value: 10000.00>
    logger.info(f"累计成本: {p.acc_avg_cost:.4f}")  # (1000 * 10 +5)/1000 = 10.005
    
    # 测试2: 加仓操作
    p.update_price(12.0)
    p.buy(500, 12.5, commission=5)  # 加仓500股，价格12.5
    
    logger.info(p)  # <Position 600000 | Amount: 1500 | AvgCost: 11.01 | Value: 18000.00>
    logger.info(f"累计成本: {p.acc_avg_cost:.4f}")  # (1000 * 10.005 + 500 * 12.5 +5)/1500 ≈ 11.0033
    
    # 测试3: 部分卖出
    p.update_price(15.0)
    p.sell(800, 15.0, commission=5)  # 卖出800股
    
    logger.info(p)  # <Position 600000 | Amount: 700 | AvgCost: 11.01 | Value: 10500.00>
    logger.info(f"累计成本: {p.acc_avg_cost:.4f}")  # (1500 * 11.0033 - 800 * 15 +5)/700 ≈ 4.288
    
    # 测试4: 每日结算
    p.daily_settlement(14.0)
    logger.info(f"结算后持仓成本: {p.hold_cost}")  # 14.0