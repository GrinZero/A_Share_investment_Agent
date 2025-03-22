from .context import Context
import akshare as ak
import pandas as pd
from datetime import datetime,timedelta
from ..config import g
from src.utils.covert import convert_chinese_number
from .audit import filter_audit

def is_paused(stock_data):
    """判断股票是否停牌
    Args:
        stock_data: DataFrame的一行数据，包含股票的交易信息
    Returns:
        bool: True表示停牌，False表示正常交易
    """
    # 检查关键指标是否为NaN
    key_fields = ['成交量', '最新价', '成交额', '今开']
    for field in key_fields:
        if pd.isna(stock_data[field]) or stock_data[field] == 0:
            return True
    return False

def is_st(stock_data):
    """判断是否为ST股票
    Args:
        stock_data: DataFrame的一行数据，包含股票的交易信息
    Returns:
        bool: True表示是ST股票，False表示不是
    """
    name = stock_data['名称']
    st_keywords = ['ST', '*ST', 'S*ST', 'SST', 'S', '*S']
    return any(keyword in name for keyword in st_keywords)

def is_out(stock_data):
    name = stock_data['名称']
    out_keywords = ['退', '退市', '*退', 'X', 'XD', 'XR']
    return any(keyword in name for keyword in out_keywords)

def is_limit(stock_data):
    """判断股票是否涨停或跌停
    Args:
        stock_data: DataFrame的一行数据，包含股票的交易信息
    Returns:
        tuple: (is_up_limit, is_down_limit) 分别表示是否涨停和跌停
    """
    code = stock_data.name  # 获取股票代码
    price = stock_data['最新价']
    pre_close = stock_data['昨收']
    
    # 判断涨跌幅限制
    if code.startswith(('30', '68')):  # 创业板、科创板 20%
        limit_rate = 0.20
    elif code.startswith(('000', '001', '002', '600', '601', '603')):  # 主板、中小板 10%
        limit_rate = 0.10
    elif code.startswith('ST'):  # ST股票 5%
        limit_rate = 0.05
    else:
        limit_rate = 0.10  # 默认使用10%
    
    # 计算涨跌停价格
    up_limit = round(pre_close * (1 + limit_rate), 2)
    down_limit = round(pre_close * (1 - limit_rate), 2)
    
    # 判断是否涨跌停（考虑价格误差）
    is_up_limit = abs(price - up_limit) < 0.01
    is_down_limit = abs(price - down_limit) < 0.01
    
    return is_up_limit, is_down_limit

stock_info_a_sh_code_name_df = None
def get_market_code(stock_name, stock_code, variant='start'):
    """
    根据股票代码和名称判断所属市场
    :param stock_code: 股票代码
    :param name: 股票名称
    :param variant: 匹配方式，'start'，如 SZ000001，'end' 如 000001.SZ
    :return: 所属市场代码
    :return: SZ000001
    """
    global stock_info_a_sh_code_name_df
    
    if stock_code.startswith('9') or stock_code.startswith('8') or stock_code.startswith('4'):
        if variant == 'start':
            return "BJ" + stock_code
        else:
            return stock_code + ".BJ"
    
    if stock_info_a_sh_code_name_df is None:
        stock_info_a_sh_code_name_df = ak.stock_info_sh_name_code()
        stock_info_a_sh_code_name_df.set_index('证券简称', inplace=True)
        
    if stock_name in stock_info_a_sh_code_name_df.index:
        market_code = stock_info_a_sh_code_name_df.loc[stock_name, '证券代码']
        if variant =='start':
            return "SH" + market_code
        else:
            return market_code + ".SH"
    else:
        if variant =='start':
            return "SZ" + stock_code
        else:
            return stock_code + ".SZ"
    

def get_market_code_by_code(code, variant='start', style='upper'):
    """
    根据股票代码判断所属市场
    :param stock_code: 股票代码
    :param variant: 匹配方式，'start'，如 SZ000001，'end' 如 000001.SZ
    :param style: 股票代码风格，'upper'，如 SH000001，'lower' 如 sh000001
    :return: 所属市场代码
    """
    fix = ''
    if code.startswith('9') or code.startswith('8') or code.startswith('4'):
        fix = "BJ"
    
    if (code.startswith('000') or code.startswith('001') or code.startswith('002') 
        or code.startswith('003') or code.startswith('004') or code.startswith('005') 
        or code.startswith("300") or code.startswith("301") or code.startswith("302")):
        fix = "SZ"
        
    if code.startswith('600') or code.startswith('601') or code.startswith('603') or code.startswith('605') or code.startswith('688'):
        fix = "SH"
    
    if style == 'lower':
        code = code.lower()

    if variant =='start':
        return fix + code
    else:
        return code + "." + fix



#2 过滤各种股票
def filter_stocks(context:Context, stock_list):
    print('批量筛选股票中')
    current_data = ak.stock_zh_a_spot_em() #! 重要，想办法换成回测的分钟级数据
    current_data.set_index('代码', inplace=True)
    # print('current_data',current_data)
    # 涨跌停和最近价格的判断
    # last_prices = history(1, unit='1m', field='close', security_list=stock_list)
    
    filtered_stocks = []
    for stock in stock_list:
        stock_data = current_data.loc[stock]
        if is_paused(stock_data):  # 停牌
            continue
        if is_st(stock_data):  # ST
            continue
        if is_out(stock_data):  # 退市
            continue
        if stock.startswith('30') or stock.startswith('68') or stock.startswith('8') or stock.startswith('4'):  # 市场类型
            continue
        if not (stock in context.portfolio.positions or any(is_limit(stock_data))):  # 涨停跌停
            continue
        # 次新股过滤
        astock_info_data = ak.stock_individual_info_em(symbol=stock)
        astock_info_data.set_index('item', inplace=True)
        start_date_str = str(astock_info_data.loc['上市时间'].value)
        start_date = datetime.strptime(start_date_str, '%Y%m%d')  # 将字符串转换为datetime对象
        if context.previous_date - start_date < timedelta(days=375):
            continue
        filtered_stocks.append(stock)
        
    return filtered_stocks

def query_market_codes(context:Context, initial_list):
    now = context.current_dt
    filtered_stocks = []
    print('批量筛选股票财务数据中，该过程耗时可能长')
    for stock in initial_list:
        try:
            # 获取财务指标
            stock_info = ak.stock_individual_info_em(symbol=stock)
            stock_info.set_index('item', inplace=True)
            
            # 获取市值数据
            stock_mv = stock_info.loc['总市值']
            total_mv = (float(stock_mv.iloc[0]) / 1e8)
            # 检查市值范围
            if not (g['min_mv'] <= total_mv <= g['max_mv']):
                continue
            
            financial_data = ak.stock_financial_benefit_ths(symbol=stock, indicator="按报告期")
            # 获取最新一期财务数据
            np_parent_company_owners = convert_chinese_number(financial_data['归属于母公司股东的综合收益总额'].values[0])  # 归属于母公司股东的综合收益总额
            net_profit = convert_chinese_number(financial_data['*净利润'].values[0])
            operating_revenue = convert_chinese_number(financial_data['*营业总收入'].values[-1])  # 营业收入
            last_year = str(now.year - 1)
            financial_analysis_indicator_df = ak.stock_financial_analysis_indicator(
                symbol=stock,
                start_year=last_year
            )
            roe = financial_analysis_indicator_df['净资产收益率(%)'].values[-1]   # ROE
            roa = financial_analysis_indicator_df['总资产利润率(%)'].values[-1]   # ROA（近似）
            
            # 应用筛选条件
            if (net_profit > 0 and 
                operating_revenue > 1e8 and 
                roe > 0 and 
                roa > 0):
                filtered_stocks.append((stock,total_mv))
                
            if len(filtered_stocks) >= g['stock_num'] * g['stock_pool_mult']:
                break
                
        except Exception as e:
            print(f"处理股票 {stock} 时出错: {str(e)}")
            continue
    
    sorted_stocks = sorted(filtered_stocks, key=lambda x: x[1])
    # 按照 total_mv 正排
    return [stock[0] for stock in sorted_stocks]
    


#1-2 选股模块
def get_stock_list(context:Context):
    final_list = []
    MKT_index = '399101'
    index_stock_df = ak.index_stock_cons(symbol=MKT_index)
    index_stock_df.set_index('品种代码', inplace=True)
    index_stock_list = list(
        set(index_stock_df.index)
    )
    
    initial_list = filter_stocks(context, index_stock_list)
    
    # 国九更新：过滤近一年净利润为负且营业收入小于1亿的
    # 国九更新：过滤近一年期末净资产为负的 (经查询没有为负数的，所以直接pass这条)
    # 国九更新：过滤近一年审计建议无法出具或者为负面建议的 (经过净利润等筛选，审计意见几乎不会存在异常)
    data = query_market_codes(context, initial_list)[:int(g['stock_num'] * g['stock_pool_mult'])]

    final_list = list(data)
    
    # 过滤审计意见
    if g['filter_audit']:
        # 获取股票名称列表，处理重复数据
        stock_name_list = []
        for stock in initial_list:
            name = index_stock_df.loc[stock, '品种名称']
            if isinstance(name, pd.Series):
                # 如果返回的是Series（重复数据），取第一个值
                name = name.iloc[0]
            stock_name_list.append(name)
        # 构建带市场代码的股票代码列表
        market_stock_list = [get_market_code(name, code) for name, code in zip(stock_name_list, initial_list)]
        final_list = filter_audit(context, market_stock_list)
    
    # TODO：过滤红利股
    # if g['filter_bonus']:
    #     final_list = bonus_filter(context,final_list)
        
    if len(final_list) == 0:
        # 由于有时候选股条件苛刻，所以会没有股票入选，这时买入银华日利ETF
        log.info('无适合股票，买入ETF')
        return [g['etf']]
    else:
        # 注意买的时候要确保购买价格 last_prices <= g['highest']
        current_data = ak.stock_zh_a_spot_em()
        current_data.set_index('代码', inplace=True)
        return [stock for stock in final_list if stock in g['hold_list'] or current_data.loc[stock, '最新价'] <= g['highest']]
