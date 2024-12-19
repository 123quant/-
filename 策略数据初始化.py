
from xtquant import xtdata
import pandas as pd
from datetime import datetime

xtdata.enable_hello = False



# 获取当前时间
current_time = datetime.now()
# 获取当前小时
current_hour = current_time.hour


sector_list = xtdata.get_sector_list()
if not sector_list:
    xtdata.download_sector_data()


stock_list = xtdata.get_stock_list_in_sector('沪深A股')

# 获取当天日期并转换为'YYYYMMDD'格式
today_str = datetime.now().strftime('%Y%m%d')
today_str

def on_progress(data):
	print(data)
xtdata.download_history_data2(stock_list=stock_list, period='1d',end_time=today_str,callback=on_progress,incrementally = True)


# 获取所有A股股票代码列表
stock_list = xtdata.get_stock_list_in_sector('沪深A股')

# 获取所有股票的日线数据
stock_dict = xtdata.get_local_data(field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
                           stock_list=stock_list,
                           start_time=today_str,
                           end_time=today_str,
                           period='1d')
result_df = pd.concat([df.assign(code=code) for code, df in stock_dict.items()], axis=0).reset_index()
# 创建涨停价计算函数
def calc_limit_up_price(close_price, stock_code):
    # 科创板和创业板涨幅限制为20%
    if stock_code.startswith('688') or stock_code.startswith('30'):
        limit_up_rate = 0.20
    # 其他股票涨幅限制为10%
    else:
        limit_up_rate = 0.10
    
    # 计算涨停价并四舍五入到分
    limit_up_price = round(close_price * (1 + limit_up_rate), 2)
    return limit_up_price

# 计算每只股票的涨停价
result_df['limit_up_price'] = result_df.apply(lambda x: calc_limit_up_price(x['close'], x['code']), axis=1)
result_df

import json

# 将DataFrame的两列转换为字典
limit_up_dict = dict(zip(result_df['code'], result_df['limit_up_price']))


# 检查是否是交易时间
if 15 > current_hour >= 9:
    print("当前时间是交易时间，不可更新涨停数据配置文件")
else:    
    # 保存为JSON文件
    with open('./配置文件/{}-limit_up_prices.json'.format(today_str), 'w', encoding='utf-8') as f:
        json.dump(limit_up_dict, f, indent=4)
    print('涨停价字典文件已保存,可以运行打板策略')
