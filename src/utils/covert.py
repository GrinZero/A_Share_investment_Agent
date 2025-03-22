def convert_chinese_number(amount_str):
    """将中文金额字符串转换为浮点数
    Args:
        amount_str: 包含中文单位的金额字符串，如"324.99万"、"2亿"、"3千万"等
    Returns:
        float: 转换后的数值（单位：元）
    """
    # 移除所有空格
    amount_str = amount_str.strip().replace(' ', '')
    
    # 单位转换表（转换到万为基础单位）
    unit_dict = {
        '千': 0.1,    # 千 = 0.1万
        '百': 0.01,   # 百 = 0.01万
        '十': 0.001,  # 十 = 0.001万
        '万': 1,      # 万 = 1万
        '亿': 10000   # 亿 = 10000万
    }
    
    # 提取数字部分
    number = ''
    unit = '万'  # 默认单位为万
    
    for char in amount_str:
        if char.isdigit() or char == '.' or char == '-':
            number += char
        elif char in unit_dict:
            unit = char
            
    # 转换为浮点数
    try:
        value = float(number)
        # 应用单位转换
        value = value * unit_dict.get(unit, 1)
        # 转换为元
        value = value * 10000  # 万转元
        return value
    except ValueError:
        print(f"无法转换金额: {amount_str}")
        return 0.0

# 使用示例：
# stock_net_profit = convert_chinese_number(financial_data['*净利润'].values[0])
# operating_revenue = convert_chinese_number(financial_data['*营业总收入'].values[-1])