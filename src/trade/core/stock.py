from .context import Context
import akshare as ak
import pandas as pd
from datetime import datetime,timedelta
from ..config import g
from src.utils.covert import convert_chinese_number
from .audit import filter_audit
from src.core.utils import logger



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

def get_market_code(stock_name, stock_code, variant='start'):
    """
    根据股票代码和名称判断所属市场
    :param stock_code: 股票代码
    :param name: 股票名称
    :param variant: 匹配方式，'start'，如 SZ000001，'end' 如 000001.SZ
    :return: 所属市场代码
    :return: SZ000001
    """
    return get_market_code_by_code(code=stock_code, variant=variant)


#2 过滤各种股票
def filter_stocks(context:Context, stock_list):
    logger.info('批量筛选股票中')
    current_data = ak.stock_zh_a_spot_em() #! 重要，想办法换成回测的分钟级数据
    current_data.set_index('代码', inplace=True)
    # logger.info('current_data',current_data)
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
        if not (stock in context.portfolio.positions) and any(is_limit(stock_data)):  # 涨停跌停
            continue

        stock_mv = stock_data['总市值']
        total_mv = (float(stock_mv) / 1e8)
        if not (g['min_mv'] <= total_mv <= g['max_mv']):
            continue
        
        # 次新股过滤
        # astock_info_data = ak.stock_individual_info_em(symbol=stock)
        # astock_info_data.set_index('item', inplace=True)
        # start_date_str = str(astock_info_data.loc['上市时间'].value)
        # start_date = datetime.strptime(start_date_str, '%Y%m%d')  # 将字符串转换为datetime对象
        # if context.previous_date - start_date < timedelta(days=375):
        #     continue
        filtered_stocks.append((stock,total_mv))

    sorted_stocks = sorted(filtered_stocks, key=lambda x: x[1])
        
    return [stock[0] for stock in sorted_stocks]


def filter_wencai(context:Context):
    import json
    import requests
    from .wencai import get_conditions
    from urllib.parse import urlencode

    url = "https://www.iwencai.com/gateway/urp/v7/landing/getDataList"

    condition = get_conditions()
    condition_str = json.dumps(condition, ensure_ascii=False)

    sort_key = "总市值[" + str(datetime.now().strftime('%Y%m%d')) + "]"

    form = {
        # "query": "总市值大于等于10亿元,归属于母公司股东的综合收益总额大于零,净利润大于零,roe大于零,roa大于零,营业总收入大于1亿,主板股票,非 ST,非新股与次新股,未涨停,未跌停,中小综指股票,未停牌,近三年审计意见只包含标准无保留意见,股价不超过50",
        "urp_sort_way": "asc",
        "urp_sort_index": sort_key,
        "page": 1,
        "perpage": 100,
        # "addheaderindexes": "",
        "condition": condition_str,
        # "codelist": "",
        # "indexnamelimit": "",
        "logid": "c13d2ba6bf45e44a7b57f709726189f6",
        "ret": "json_all",
        "sessionid": "c13d2ba6bf45e44a7b57f709726189f6",
        "source": "Ths_iwencai_Xuangu",
        # "date_range[0]": 20221231,
        # "date_range[1]": 20250506,
        # "iwc_token": "0ac9ebeb17465382910985970",
        "urp_use_sort": 1,
        # "user_id": 513617837,
        # "uuids[0]": 24087,
        "query_type": "stock",
        "comp_id": 6836372,
        "business_cat": "soniu",
        "uuid": 24087
    }

    data = urlencode(form)

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded",
        # "hexin-v": "A6n3hMEY5dABMtlkwNvZ6Hpmvl4BdrXGB3fK0kq8IU7OG8eAk8ateJe60cnY",
        "pragma": "no-cache",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "cid=94deb62674692cb0adea032b308010251742012109; other_uid=Ths_iwencai_Xuangu_kksyr6d5gidi38zt64jqzoh1cymjhb70; ta_random_userid=0e1hebfxrk; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=VDCmGgaj3Kvm%2BGEIKSPpy8GgLdea1pXgyV5gcwqMa3MUlAuju3jjxZFDZJeM9m7%2FHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=057F2207A97A4DBA9A97AA8AAFABAF54; u_ttype=WEB; user=MDrUtNDEy%2Fg6Ok5vbmU6NTAwOjUyMzYxNzgzNzo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoyNDo6OjUxMzYxNzgzNzoxNzQ2NTMwNTc0Ojo6MTU4MzU4MzM2MDoyNjc4NDAwOjA6MTllOGE5M2VjN2QxYjU0YTQyOTc2NjU2OGJjZmQ0ZjBhOmRlZmF1bHRfNDox; userid=513617837; u_name=%D4%B4%D0%C4%CB%F8; escapename=%25u6e90%25u5fc3%25u9501; ticket=4a2c2267fc758a223cb74c019201ca64; user_status=0; utk=06b32c65d662059c0f51d184eb0572ca;",
        "Referer": "https://www.iwencai.com/unifiedwap/result",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    response = requests.post(url, headers=headers, data=data).json()
    print('response', json.dumps(response, ensure_ascii=False))
    datas = response['answer']['components'][0]['data']['datas']
    codes = map(lambda x: x['code'], datas)
    return list(codes)


def filter_wencai_api(context:Context):
    import pywencai
    try:
        cookie = 'cid=94deb62674692cb0adea032b308010251742012109; other_uid=Ths_iwencai_Xuangu_kksyr6d5gidi38zt64jqzoh1cymjhb70; ta_random_userid=0e1hebfxrk; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=VDCmGgaj3Kvm%2BGEIKSPpy8GgLdea1pXgyV5gcwqMa3MUlAuju3jjxZFDZJeM9m7%2FHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=057F2207A97A4DBA9A97AA8AAFABAF54; u_ttype=WEB; user=MDrUtNDEy%2Fg6Ok5vbmU6NTAwOjUyMzYxNzgzNzo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoyNDo6OjUxMzYxNzgzNzoxNzQ2NTMwNTc0Ojo6MTU4MzU4MzM2MDoyNjc4NDAwOjA6MTllOGE5M2VjN2QxYjU0YTQyOTc2NjU2OGJjZmQ0ZjBhOmRlZmF1bHRfNDox; userid=513617837; u_name=%D4%B4%D0%C4%CB%F8; escapename=%25u6e90%25u5fc3%25u9501; ticket=4a2c2267fc758a223cb74c019201ca64; user_status=0; utk=06b32c65d662059c0f51d184eb0572ca; v=AzNt5v-mX8BUrRMU_C0zKjywxDxYaMcTgfwLReXQj9KJ5F0ibThXepHMm7X2'
        query = "总市值大于等于10亿元,归属于母公司股东的综合收益总额大于零,净利润大于零,roe大于零,roa大于零,营业总收入大于1亿,主板股票,非 ST,非新股与次新股,未涨停,未跌停,中小综指股票,未停牌,近三年审计意见只包含标准无保留意见,股价不超过50"

        sort_key = "总市值[" + str(context.current_dt.strftime('%Y%m%d')) + "]"
        res = pywencai.get(query=query,page=1,perpage=100, sort_key=sort_key, sort_order='asc', cookie=cookie)
        return list(res['code'])
    except Exception as e:
        logger.info(f"获取问财数据失败: {str(e)}")
        return []


def query_market_codes(context:Context, initial_list):
    now = context.current_dt
    filtered_stocks = []
    logger.info('批量筛选股票财务数据中，该过程耗时可能长')
    # print('len(initial_list)', len(initial_list))
    # filter_wencai(context)
    for stock in initial_list:
        try:
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
                np_parent_company_owners > 0 and
                roe > 0 and 
                roa > 0):
                filtered_stocks.append(stock)
                
            if len(filtered_stocks) >= g['stock_num'] * g['stock_pool_mult']:
                break
                
        except Exception as e:
            logger.info(f"处理股票 {stock} 时出错: {str(e)}")
            continue
    
    return filtered_stocks
    


#1-2 选股模块
def get_stock_list(context:Context):
    stock_list = filter_wencai_api(context)
    if len(stock_list) != 0:
        current_data = ak.stock_zh_a_spot_em()
        current_data.set_index('代码', inplace=True)
        return [stock for stock in stock_list if stock in g['hold_list'] or current_data.loc[stock, '最新价'] <= g['highest']]

    final_list = []
    MKT_index = '399101'
    index_stock_df = ak.index_stock_cons(symbol=MKT_index)
    index_stock_df.set_index('品种代码', inplace=True)
    index_stock_list = list(
        set(index_stock_df.index)
    )
    index_stock_list.sort()
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
        logger.info('无适合股票，买入ETF')
        return [g['etf']]
    else:
        # 注意买的时候要确保购买价格 last_prices <= g['highest']
        current_data = ak.stock_zh_a_spot_em()
        current_data.set_index('代码', inplace=True)
        return [stock for stock in final_list if stock in g['hold_list'] or current_data.loc[stock, '最新价'] <= g['highest']]

if __name__ == "__main__":
    context = Context()
    wencai = filter_wencai_api(context)
    print(wencai)