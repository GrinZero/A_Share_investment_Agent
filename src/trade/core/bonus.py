from .context import Context
from src.core.utils import logger

#2.2 #获取红利列表
def bonus_filter(context:Context, stock_list):
    #logger.info(f'进入红利筛选前,共{len(stock_list)}只股票')
    year=context.previous_date.year
    start_date=datetime.date(year, 1, 1)
    end_date=context.previous_date
    if end_date.month in g['Expected_bonus']:
        q = query(finance.STK_XR_XD.code,finance.STK_XR_XD.company_name, finance.STK_XR_XD.board_plan_pub_date,finance.STK_XR_XD.bonus_amount_rmb,finance.STK_XR_XD.bonus_ratio_rmb
            ).filter(               
                #finance.STK_XR_XD.bonus_type !='年度分红',
                finance.STK_XR_XD.board_plan_pub_date>start_date,
                finance.STK_XR_XD.implementation_pub_date<=end_date,
                #finance.STK_XR_XD.a_xr_date < context.previous_date,
                finance.STK_XR_XD.bonus_ratio_rmb>0,
                finance.STK_XR_XD.code.in_(stock_list))
        Expected_bonus_df = finance.run_query(q)
        
        if len(Expected_bonus_df)>0:
            bonus_list=Expected_bonus_df['code'].unique().tolist()
            price_df=history(1, unit='1d', field='close', security_list=bonus_list, df=True, skip_paused=False, fq='pre')
            price_df=price_df.T
            price_df.rename(columns={price_df.columns[0]:'Close_now'},inplace=True)
            price_df['code']=price_df.index
            Expected_bonus_df=pd.merge(Expected_bonus_df,price_df,on=('code'),how='left')
            Expected_bonus_df['bonus_ratio']=(Expected_bonus_df['bonus_ratio_rmb'])/Expected_bonus_df['Close_now']
            Expected_bonus_df=Expected_bonus_df.sort_values(by='bonus_ratio',ascending=True)
            bonus_list=Expected_bonus_df['code'].unique().tolist()
        else:
            bonus_list=[]
    else:
        reprot_date = datetime.date(year-1, 12, 31)
        q = query(finance.STK_XR_XD.code,finance.STK_XR_XD.company_name,finance.STK_XR_XD.a_registration_date, finance.STK_XR_XD.bonus_amount_rmb,finance.STK_XR_XD.bonus_ratio_rmb
            ).filter(
                finance.STK_XR_XD.report_date ==reprot_date,         
                finance.STK_XR_XD.bonus_type=='年度分红' ,
                finance.STK_XR_XD.implementation_pub_date<=end_date,
                finance.STK_XR_XD.board_plan_bonusnote=='不分配不转增',
                finance.STK_XR_XD.code.in_(stock_list))
    
        no_year_bonus = finance.run_query(q)
        no_year_bonus_list=no_year_bonus['code'].unique().tolist()
        #排除今年不分红的股票
        bonus_list=[code for code in stock_list if code not in no_year_bonus_list]
        bonus_list=short_by_market_cap(context,bonus_list)
       
    logger.info(f'进行实际红利筛选后,原有{len(stock_list)}只股票，筛选后剩余{len(bonus_list)}只股票')
    
    if len(bonus_list)< g.stock_num:
        bonus_list.extend([x for x in short_by_market_cap(context,stock_list) if x not in bonus_list ][:g.stock_num-len(bonus_list)])
    return bonus_list
