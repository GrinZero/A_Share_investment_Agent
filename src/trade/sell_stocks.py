from .config import g
from .core.context import Context
from src.core.order import order_target_value
from src.core.utils import fmtDate
from src.trade.core.stock import get_market_code
import akshare as ak
from datetime import timedelta
from src.core.tushare import tspro
from src.core.utils import logger

def get_down_ratio(context:Context):
    # 获取中证1000成分股列表
    index_stocks = ak.index_stock_cons(
        symbol="399101"
    )
    
    # 转换成 market_code
    market_code_list = []
    for _, row in index_stocks.iterrows():
        code = row['品种代码']
        name = row['品种名称']
        market_code = get_market_code(name, code, variant='end')
        if market_code:
            market_code_list.append(market_code)
    
    market_code_str = ','.join(market_code_list)
    stock_df = tspro.daily(
        ts_code=market_code_str,
        trade_date=fmtDate(context.previous_date)
    )
    down_ratio = abs((stock_df['close'] / stock_df['open'] - 1).mean())
    return down_ratio

def sell_stocks(context:Context):
    if g['run_stoploss']:
        current_positions = context.portfolio.positions
        if g['stoploss_strategy'] == 1 or g['stoploss_strategy'] == 3:
            for stock in current_positions.keys():
                position = context.portfolio.get_position(stock)
                if not position:
                    continue
                price = position.price
                avg_cost = position.avg_cost
                # 个股盈利止盈
                if price >= avg_cost * 2:
                    order_target_value(context,position, 0)
                # 个股止损
                elif price < avg_cost * (1 - g['stoploss_limit']):
                    order_target_value(context,position, 0)
                    g['reason_to_sell'] = 'stoploss'
                    
        if g['stoploss_strategy'] == 2 or g['stoploss_strategy'] == 3:
            down_ratio = get_down_ratio(context=context)
            # 市场大跌止损
            if down_ratio >= g['stoploss_market']:
                g['reason_to_sell'] = 'stoploss'
                for stock in current_positions.keys():
                    order_target_value(context.portfolio.get_position(stock), 0)
        
if __name__ == '__main__':
    context = Context()
    logger.info(get_down_ratio(context=context))