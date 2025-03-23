
from src.core.utils import logger

def print_position_info(context):
    for position in list(context.portfolio.positions.values()):
        securities=position.security
        cost=position.avg_cost
        price=position.price
        ret=100*(price/cost-1)
        value=position.value
        amount=position.total_amount    
        logger.info('代码:{}'.format(securities))
        logger.info('成本价:{}'.format(format(cost,'.2f')))
        logger.info('现价:{}'.format(price))
        logger.info('收益率:{}%'.format(format(ret,'.2f')))
        logger.info('持仓(股):{}'.format(amount))
        logger.info('市值:{}'.format(format(value,'.2f')))
    logger.info('———————————————————————————————————————分割线————————————————————————————————————————')
    