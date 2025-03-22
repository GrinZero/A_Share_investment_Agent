from datetime import datetime, timedelta
import akshare as ak
from .context import Context
import pandas as pd

'''
审计意见类型编码
类型编码 审计意见类型
1 	     标准无保留意见 ✅
2 	     带解释性说明的无保留意见 ✅
3        保留意见 ❌
4        无法表示意见 ❌
5        否定意见 ❌
6 	     未经审计 ✅
7 	     保留带解释性说明 ❌
8        带强调事项段的无保留意见 ✅
9        拒绝表示意见 ❌
10 	     经审计（不确定具体意见类型）
11       无保留带持续经营重大不确定性
'''
def filter_audit(context:Context, market_stock_list):
    # 获取审计意见，近三年内如果有不合格的审计意见则返回False，否则返回True
    UNSAFE_AUDIT = [
        "保留意见",
        "无法表示意见",
        "否定意见",
        "保留带解释性说明",
        "拒绝表示意见",
    ]
    final_list = []
    expection_Audit_list = []
    for stock in market_stock_list:
        lstd = context.previous_date
        last_year = (lstd.replace(year=lstd.year - 3, month=1, day=1)).strftime('%Y-%m-%d')
        report_list = ak.stock_profit_sheet_by_yearly_em(symbol=stock)
        report_list['REPORT_DATE'] = pd.to_datetime(report_list['REPORT_DATE'])
        # print("报表列名:", report_list.columns.tolist())
        # print("数据预览:\n", report_list.head())
        
        # 筛选 REPORT_DATE 列中大于等于 last_year 的行，小于等于 context.current_dt 的行
        filtered_df = report_list[(report_list['REPORT_DATE'] >= last_year) & (report_list['REPORT_DATE'] <= context.current_dt)]
        # 提取 OPINION_TYPE 列的值
        opinion_types = list(filtered_df['OPINION_TYPE'].values)
        # 检查 opinion_types 中是否包含 UNSAFE_AUDIT 中的任何一个元素
        if any(opinion_type in UNSAFE_AUDIT for opinion_type in opinion_types):
            expection_Audit_list.append(stock)
        else:
            final_list.append(stock)
    return final_list

if __name__ == '__main__':
    context = Context()
    context.previous_date = datetime(2025, 3, 21)
    context.current_dt = datetime(2025, 3, 22)
    
    market_stock_list = ['SH' + code for code in ak.stock_info_sh_name_code()['证券代码']]
    s = set()
    for stock in market_stock_list:
        asd = ak.stock_profit_sheet_by_yearly_em(symbol=stock)
        v = list(asd['OPINION_TYPE'].values)
        for i in v:
            s.add(i)
        print(s)
    print(s)
        