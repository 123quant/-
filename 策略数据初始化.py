
from xtquant import xtdata
import pandas as pd
from datetime import datetime
import ray

xtdata.enable_hello = False



# 获取当前时间
current_time = datetime.now().strftime('%H:%M')

current_time


sector_list = xtdata.get_sector_list()
if not sector_list:
    xtdata.download_sector_data()

import os
import glob

# 指定文件夹路径
folder_path = './配置文件'

# 获取所有以 limit_up_prices.json 结尾的文件
files_to_delete = glob.glob(os.path.join(folder_path, '*limit_up_prices.json'))

# 删除文件
for file in files_to_delete:
    try:
        os.remove(file)
        print(f'已删除文件: {file}')
    except Exception as e:
        print(f'删除文件 {file} 时出错: {e}')


stock_list = xtdata.get_stock_list_in_sector('沪深A股')

# 获取当天日期并转换为'YYYYMMDD'格式
today_str = datetime.now().strftime('%Y%m%d')
today_str


print('开始下载数据,需要花费5分钟')


data_000001 = xtdata.get_local_data(field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
                           stock_list=['000001.SZ'],
                           count=2,
                           period='1d')['000001.SZ']
new_data_time = data_000001.index[-1]

if "15:00">  current_time > "09:15":
    trader_data = data_000001.index[0]
else:
    trader_data = data_000001.index[-1]

if new_data_time == today_str:
    print('数据已更新')
else:
    # 初始化Ray（如果还没初始化）
    if not ray.is_initialized():
        ray.init()

    @ray.remote
    def download_stock_data(stock):
        return xtdata.download_history_data(stock, period='1d', start_time='', end_time=today_str, incrementally=True)

    # 创建所有远程任务
    futures = [download_stock_data.remote(stock) for stock in stock_list]
    ray.get(futures)
    print('数据下载完成')


# 获取所有A股股票代码列表
stock_list = xtdata.get_stock_list_in_sector('沪深A股')

# 获取所有股票的日线数据
stock_dict = xtdata.get_local_data(field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
                           stock_list=stock_list,
                           start_time=trader_data,
                           end_time=trader_data,
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

print('计算涨停价完成')


import json

# 将DataFrame的两列转换为字典
limit_up_dict = dict(zip(result_df['code'], result_df['limit_up_price']))


import json

# 将DataFrame的两列转换为字典
limit_up_dict = dict(zip(result_df['code'], result_df['limit_up_price']))
# 保存为JSON文件
with open('./配置文件/{}-limit_up_prices.json'.format(trader_data), 'w', encoding='utf-8') as f:
    json.dump(limit_up_dict, f, indent=4)


print('涨停价字典文件已保存,可以运行打板策略')
