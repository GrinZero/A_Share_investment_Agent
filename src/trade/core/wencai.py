from datetime import datetime

wencai = [{"score":0,"node_type":"op","chunkedResult":"总市值大于等于10亿元,_&_归属于母公司股东的综合收益总额大于零,_&_净利润大于零,_&_roe大于零,_&_roa大于零,_&_营业总收入大于1亿,_&_主板股票,_&_非 st,_&_非新股与次新股,_&_未涨停,_&_未跌停,_&_中小综指股票,_&_未停牌,_&_近三年审计意见只包含标准无保留意见,_&_股价不超过50","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":33,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"总市值","indexProperties":["nodate 1","交易日期 20250506","(=1000000000"],"source":"new_parser","type":"index","indexPropertiesMap":{"交易日期":"20250506","(=":"1000000000","nodate":"1"},"reportType":"TRADE_DAILY","score":0,"node_type":"index","dateType":"交易日期","domain":"abs_股票领域","uiText":"总市值>=10亿元","valueType":"_浮点型数值(元|港元|美元|英镑)","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":31,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"归属于母公司股东的综合收益总额:合并报表","indexProperties":["nodate 1","交易日期 20250331","(0"],"source":"new_parser","type":"index","indexPropertiesMap":{"交易日期":"20250331","(":"0","nodate":"1"},"reportType":"QUARTER","score":0,"node_type":"index","dateType":"报告期","domain":"abs_股票领域","uiText":"归属于母公司股东的综合收益总额>0元","valueType":"_浮点型数值(元)","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":29,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"归属于母公司所有者的净利润","indexProperties":["nodate 1","交易日期 20250331","(0"],"source":"new_parser","type":"index","indexPropertiesMap":{"交易日期":"20250331","(":"0","nodate":"1"},"reportType":"QUARTER","score":0,"node_type":"index","dateType":"报告期","domain":"abs_股票领域","uiText":"归属于母公司所有者的净利润>0元","valueType":"_浮点型数值(元)","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":27,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"净资产收益率roe(加权,公布值)","indexProperties":["nodate 1","交易日期 20250331","(0"],"source":"new_parser","type":"index","indexPropertiesMap":{"交易日期":"20250331","(":"0","nodate":"1"},"reportType":"QUARTER","score":0,"node_type":"index","dateType":"报告期","domain":"abs_股票领域","uiText":"净资产收益率roe(加权,公布值)>0%","valueType":"_浮点型数值(%)","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":25,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"总资产报酬率roa","indexProperties":["nodate 1","交易日期 20250331","(0"],"source":"new_parser","type":"index","indexPropertiesMap":{"交易日期":"20250331","(":"0","nodate":"1"},"reportType":"QUARTER","score":0,"node_type":"index","dateType":"报告期","domain":"abs_股票领域","uiText":"总资产报酬率roa>0%","valueType":"_浮点型数值(%)","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":23,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"营业总收入","indexProperties":["nodate 1","交易日期 20250331","(100000000"],"source":"new_parser","type":"index","indexPropertiesMap":{"交易日期":"20250331","(":"100000000","nodate":"1"},"reportType":"QUARTER","score":0,"node_type":"index","dateType":"报告期","domain":"abs_股票领域","uiText":"营业总收入>1亿元","valueType":"_浮点型数值(元)","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":21,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"上市板块","indexProperties":["包含主板"],"source":"new_parser","type":"index","indexPropertiesMap":{"包含":"主板"},"reportType":"null","score":0,"node_type":"index","domain":"abs_股票领域","uiText":"上市板块是主板","valueType":"_上市板块","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":19,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"股票简称","indexProperties":["不包含st"],"source":"new_parser","type":"index","indexPropertiesMap":{"不包含":"st"},"reportType":"null","score":0,"node_type":"index","domain":"abs_股票领域","uiText":"股票简称不包含st","valueType":"_股票简称","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":17,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"所属概念","indexProperties":["概念id 300870","不包含新股与次新股"],"source":"new_parser","type":"index","indexPropertiesMap":{"概念id":"300870","不包含":"新股与次新股"},"reportType":"null","score":0,"node_type":"index","domain":"abs_股票领域","uiText":"所属概念不包含新股与次新股","valueType":"_所属概念","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":15,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"非涨停","indexProperties":["nodate 1","交易日期 20250506"],"source":"new_parser","type":"tech","indexPropertiesMap":{"交易日期":"20250506","nodate":"1"},"reportType":"TRADE_DAILY","score":0,"node_type":"index","dateType":"交易日期","domain":"abs_股票领域","uiText":"非涨停","valueType":"","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":13,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"非跌停","indexProperties":["nodate 1","交易日期 20250506"],"source":"new_parser","type":"tech","indexPropertiesMap":{"交易日期":"20250506","nodate":"1"},"reportType":"TRADE_DAILY","score":0,"node_type":"index","dateType":"交易日期","domain":"abs_股票领域","uiText":"非跌停","valueType":"","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":11,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"所属指数类","indexProperties":["包含中小综指"],"source":"new_parser","type":"index","indexPropertiesMap":{"包含":"中小综指"},"reportType":"null","score":0,"node_type":"index","domain":"abs_股票领域","uiText":"所属指数类是中小综指","valueType":"_所属指数类","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":9,"opPropertyMap":{},"source":"new_parser"},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","uiText":"2025年05月06日交易状态包含交易>-<新股上市,2025年05月06日交易状态不包含停牌>-<暂停上市","sonSize":2,"opPropertyMap":{},"source":"new_parser"},{"dateText":"","ci":False,"indexName":"交易状态","indexProperties":["交易日期 20250506","包含交易>-<新股上市"],"source":"new_parser","type":"index","indexPropertiesMap":{"交易日期":"20250506","包含":"交易>-<新股上市"},"reportType":"TRADE_DAILY","score":0,"node_type":"index","dateType":"交易日期","domain":"abs_股票领域","valueType":"_交易状态","sonSize":0},{"dateText":"","ci":False,"indexName":"交易状态","indexProperties":["交易日期 20250506","不包含停牌>-<暂停上市"],"source":"new_parser","type":"index","indexPropertiesMap":{"交易日期":"20250506","不包含":"停牌>-<暂停上市"},"reportType":"TRADE_DAILY","score":0,"node_type":"index","dateType":"交易日期","domain":"abs_股票领域","valueType":"_交易状态","sonSize":0},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","sonSize":5,"opPropertyMap":{},"source":"new_parser"},{"score":0,"node_type":"op","children":[],"opName":"and","ci":False,"opPropertiesMap":{},"opProperty":"","uiText":"近3年的审计意见类别包含标准无保留意见","sonSize":3,"opPropertyMap":{},"source":"new_parser"},{"dateText":"近3年","ci":False,"indexName":"审计意见类别","indexProperties":["EQUAL 标准无保留意见","起始交易日期 20221231","截止交易日期 20221231"],"dateUnit":"年","source":"new_parser","type":"index","indexPropertiesMap":{"EQUAL":"标准无保留意见","起始交易日期":"20221231","截止交易日期":"20221231"},"reportType":"QUARTER","score":0,"node_type":"index","dateType":"报告期","domain":"abs_股票领域","valueType":"_审计意见类别","sonSize":0},{"dateText":"近3年","ci":False,"indexName":"审计意见类别","indexProperties":["EQUAL 标准无保留意见","起始交易日期 20231231","截止交易日期 20231231"],"dateUnit":"年","source":"new_parser","type":"index","indexPropertiesMap":{"EQUAL":"标准无保留意见","起始交易日期":"20231231","截止交易日期":"20231231"},"reportType":"QUARTER","score":0,"node_type":"index","dateType":"报告期","domain":"abs_股票领域","valueType":"_审计意见类别","sonSize":0},{"dateText":"近3年","ci":False,"indexName":"审计意见类别","indexProperties":["EQUAL 标准无保留意见","起始交易日期 20241231","截止交易日期 20241231"],"dateUnit":"年","source":"new_parser","type":"index","indexPropertiesMap":{"EQUAL":"标准无保留意见","起始交易日期":"20241231","截止交易日期":"20241231"},"reportType":"QUARTER","score":0,"node_type":"index","dateType":"报告期","domain":"abs_股票领域","valueType":"_审计意见类别","sonSize":0},{"dateText":"","ci":False,"indexName":"收盘价:不复权","indexProperties":["nodate 1","交易日期 20250506","<=50"],"source":"new_parser","type":"index","indexPropertiesMap":{"<=":"50","交易日期":"20250506","nodate":"1"},"reportType":"TRADE_DAILY","score":0,"node_type":"index","dateType":"交易日期","domain":"abs_股票领域","uiText":"收盘价<=50元","valueType":"_浮点型数值(元|港元|美元|英镑)","sonSize":0}]


def get_last_report_date(date):
    """
    获取最近的报告日期
    :param date: 20250506
    :return: 20250331
    """
    date = datetime.strptime(date, "%Y%m%d")
    if date.month == 1 or date.month == 2 or date.month == 3:
        return (date.replace(year=date.year - 1, month=12, day=31)).strftime("%Y%m%d")
    elif date.month == 4 or date.month == 5 or date.month == 6:
        return (date.replace(year=date.year, month=3, day=31)).strftime("%Y%m%d")
    elif date.month == 7 or date.month == 8 or date.month == 9:
        return (date.replace(year=date.year, month=6, day=30)).strftime("%Y%m%d")
    elif date.month == 10 or date.month == 11 or date.month == 12:
        return (date.replace(year=date.year, month=9, day=30)).strftime("%Y%m%d")


def get_conditions():
    import copy
    global wencai
    data = copy.deepcopy(wencai)
    today = datetime.today()
    current_trade_date = today.strftime("%Y%m%d")
    last_report_date = get_last_report_date(current_trade_date)

    def calculate_past_year_end(years_ago):
        return datetime(today.year - years_ago, 12, 31).strftime("%Y%m%d")

    updated_data = copy.deepcopy(data)

    audit_opinion_count = 0

    for node in updated_data:
        if node.get("node_type") != "index":
            continue

        index_props_map = node.get("indexPropertiesMap", {})
        index_name = node.get("indexName", "")
        ui_text = node.get("uiText", "")
        new_index_properties = []

        # 判断是否为审计意见类
        is_audit_opinion = "审计意见" in index_name or "审计意见" in ui_text

        # 普通 nodate=1 的每日指标
        if index_props_map.get("nodate") == "1":
            if "交易日期" in index_props_map:
                if node.get("dateType") == "报告期":
                    index_props_map["交易日期"] = last_report_date
                else:
                    index_props_map["交易日期"] = current_trade_date
            for item in node.get("indexProperties", []):
                if item.startswith("交易日期 "):
                    if node.get("dateType") == "报告期":
                        new_index_properties.append(f"交易日期 {last_report_date}")
                    else:
                        new_index_properties.append(f"交易日期 {current_trade_date}")
                else:
                    new_index_properties.append(item)

        # 处理审计意见的日期，递增设置为：近1年、2年、3年
        elif is_audit_opinion and "起始交易日期" in index_props_map and "截止交易日期" in index_props_map:
            start_date = calculate_past_year_end(3 - audit_opinion_count)
            end_date = calculate_past_year_end(3 - audit_opinion_count)
            index_props_map["起始交易日期"] = start_date
            index_props_map["截止交易日期"] = end_date
            for item in node.get("indexProperties", []):
                if item.startswith("起始交易日期 "):
                    new_index_properties.append(f"起始交易日期 {start_date}")
                elif item.startswith("截止交易日期 "):
                    new_index_properties.append(f"截止交易日期 {end_date}")
                else:
                    new_index_properties.append(item)
            audit_opinion_count += 1

        # 处理近3年范围的其他日期节点
        elif node.get("dateText") == "近3年" and "起始交易日期" in index_props_map and "截止交易日期" in index_props_map:
            index_props_map["起始交易日期"] = calculate_past_year_end(2)
            index_props_map["截止交易日期"] = calculate_past_year_end(0)
            for item in node.get("indexProperties", []):
                if item.startswith("起始交易日期 "):
                    new_index_properties.append(f"起始交易日期 {calculate_past_year_end(2)}")
                elif item.startswith("截止交易日期 "):
                    new_index_properties.append(f"截止交易日期 {calculate_past_year_end(0)}")
                else:
                    new_index_properties.append(item)
        else:
            new_index_properties = node.get("indexProperties", [])

        # 更新最终结果
        node["indexProperties"] = new_index_properties

    return updated_data
