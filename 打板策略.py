import pandas as pd
from datetime import datetime
import json
import os
import configparser
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
import collections
import sys
import time
xtdata.enable_hello = False

# 获取当天日期并转换为'YYYYMMDD'格式
today_str = datetime.now().strftime('%Y%m%d')
print('开始获取涨停价数据')
from xtquant import xtdata
stock_list = xtdata.get_stock_list_in_sector('沪深A股') 
loaded_dict = {}
for code in stock_list:
    UpStopPrice = xtdata.get_instrument_detail(code)['UpStopPrice']
    loaded_dict[code] = UpStopPrice
print('读取涨停价字典完成')
#————————————————————————————————————————————————————————————

print('开始读取股票池')
# 读取股票池
file_path = './配置文件/股票池.txt'

# 尝试读取文件
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        # 读取文件内容
        code_list = file.read().splitlines() # .strip() 去除两端的空白字符
        
        # 判断文件是否为空
        if not code_list:
            print("股票池为空，请填写股票池")
        else:
            print('读取股票池完成',code_list)
except FileNotFoundError:
    print(f"文件 {file_path} 不存在，请检查文件路径。")
except Exception as e:
    print(f"发生错误：{e}")



#___________________________________________________________
def load_config():
    # 定义配置文件路径
    config_file = './配置文件/config.ini'

    # 创建配置解析器对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config.read(config_file, encoding='utf-8')

    # 获取配置项
    path = r'{}'.format(config.get('Path', 'qmt_path'))
    stock_account = config.get('Account', 'stock_account')
    buy_values = config.getint('Trading', 'buy_values')
    trade_time_periods = config.get('Trading', 'trade_time_and_ratio')
    return path, stock_account, buy_values,trade_time_periods  
try:
    path, stock_account, buy_values,trade_time_periods = load_config()
    print(f"qmt路径: {path}")
    print(f"账号: {stock_account}")
    print(f"每笔买多少元: {buy_values}")
    print(f"交易时间与对应买入比例: {trade_time_periods}")
    print('读取配置文件完成')
except:
    print('没有找到配置文件,请先填写配置文件')
#___________________________________________________________
from datetime import datetime
import ast
# 获取当前时间
current_time = datetime.now().strftime('%H:%M')
trade_time_periods_dict = ast.literal_eval(trade_time_periods)
# 判断当前时间是否处于某个时间段，并输出买入比例
def get_buying_ratio(current_time, time_periods):
    for period, ratio in time_periods.items():
        start_time, end_time = period.split('~')
        
        # 比较当前时间是否在某个时间段内
        if start_time <= current_time <= end_time:
            return ratio
    return None  # 如果不在任何时间段内

#___________________________________________________________
# 定义一个类 创建类的实例 作为状态的容器
class _a():
    pass


A = _a()
A.bought_list = []
A.data_cache = {}
A.update_bought_list_num = 0
#___________________________________________________________
def update_bought_list():
    full_data = xtdata.get_full_tick(code_list)
    #检测如果当前价格已经等于涨停价就加入A.bought_list中
    for stock in code_list:
        if full_data[stock]['lastPrice'] >= loaded_dict[stock]:
            A.bought_list.append(stock)



# code_list = xtdata.get_stock_list_in_sector('沪深A股')

# 数据缓存：存储每个股票的最近40个数据
def update_cache(stock, new_data):
    if stock not in A.data_cache:
        # 如果股票没有数据缓存，初始化一个空的队列
        A.data_cache[stock] = collections.deque(maxlen=40)  # 保留最近40条数据
    
    # 添加新的数据记录
    A.data_cache[stock].append(new_data)

# 因子计算
def calculate_factors(stock):
    '''
    计算因子
    '''
    # 如果缓存中没有数据，跳过计算
    if stock not in A.data_cache:
        return False  # 如果缓存中没有数据，跳过计算
    data = A.data_cache[stock]
    if len(data) < 25:
        Start_price  = data[-1]['lastPrice']
    else:
        Start_price  = data[-25]['lastPrice']

    last_price = data[-1]['lastPrice']
    lastclose = data[-1]['lastClose']
    #计算因子3:该因子计算的是股票的在股价达到涨停前涨幅，如果涨幅大于3%，则返回True，否则返回False
    factor3 = ((last_price-Start_price)/lastclose) >= 0.03 
    
    #计算因子4:该因子计算的是股票价格到达涨停价时挂单和最近3tick成交额的总金额大于3000万
    # last_price = data[-1]['lastPrice']
    sum_ask_amount = sum(data[-1]['askVol']*100)*last_price
    pre_3tick_amount = data[-1]['amount'] - data[-3]['amount']
    all_amount = sum_ask_amount + pre_3tick_amount
    factor4 = all_amount >= 30000000

    #计算因子5:该因子计算的是股票在股价到达涨停前20个tick中大单比例大于40%，大单>200万
    pre_amt = 0
    big_order_amt = 0
    for amt in data[-21:]:
        if pre_amt == 0:
            amt=0
        else:
            amt = amt-pre_amt
        if amt > 2000000:
            big_order_amt = amt+big_order_amt
        pre_amt = amt['amount']
    sum_amt = data[-1]['amount']-data[-21]['amount']
    big_order_ratio = big_order_amt/sum_amt
    factor5 = big_order_ratio >= 0.7
    return factor3 and factor4 and factor5




def on_tick(data):
    print(data)
    now = datetime.now().strftime("%H:%M")
    #每次运行剔除已经涨停的票
    if A.update_bought_list_num == 0 and now >= '09:25':
        update_bought_list()
        A.update_bought_list_num = 1

    for stock, stock_data in data.items():
        if (stock not in code_list )or (stock in A.bought_list):
            continue
        # 更新缓存数据以便计算因子
        update_cache(stock, stock_data)
        # print(stock,stock_data)

        lastprice = stock_data['lastPrice']

        up_limit_price = loaded_dict[stock]

        factor1 = lastprice >= up_limit_price
        if factor1:
            factor = calculate_factors(stock)
            if factor:
                stock_count = buy_values / lastprice
                # 取整到最接近的 100 的倍数
                buy_volume = round(stock_count / 100) * 100
        
                async_seq = xt_trader.order_stock_async(acc, stock, xtconstant.STOCK_BUY, buy_volume, xtconstant.LATEST_PRICE, up_limit_price, '打板策略')
                A.bought_list.append(stock)
        # 更新缓存
        update_cache(stock, stock_data)



class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        """
        连接断开
        :return:
        """
        print(datetime.datetime.now(), '连接断开回调')

    def on_stock_order(self, order):
        """
        委托回报推送
        :param order: XtOrder对象
        :return:
        """
        print(datetime.datetime.now(), '委托回调', order.order_remark)

    def on_stock_trade(self, trade):
        """
        成交变动推送
        :param trade: XtTrade对象
        :return:
        """
        print(datetime.datetime.now(), '成交回调', trade.order_remark)

    def on_order_error(self, order_error):
        """
        委托失败推送
        :param order_error:XtOrderError 对象
        :return:
        """
        # print("on order_error callback")
        # print(order_error.order_id, order_error.error_id, order_error.error_msg)
        print(f"委托报错回调 {order_error.order_remark} {order_error.error_msg}")

    def on_cancel_error(self, cancel_error):
        """
        撤单失败推送
        :param cancel_error: XtCancelError 对象
        :return:
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)

    def on_order_stock_async_response(self, response):
        """
        异步下单回报推送
        :param response: XtOrderResponse 对象
        :return:
        """
        print(f"异步委托回调 {response.order_remark}")

    def on_cancel_order_stock_async_response(self, response):
        """
        :param response: XtCancelOrderResponse 对象
        :return:
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)

    def on_account_status(self, status):
        """
        :param response: XtAccountStatus 对象
        :return:
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)

def interact():
    """执行后进入repl模式"""
    import code
    code.InteractiveConsole(locals=globals()).interact()




if __name__ == '__main__':
    xtdata.enable_hello = False

    print("start")
    # 指定客户端所在路径, 券商端指定到 userdata_mini文件夹
    # 注意：如果是连接投研端进行交易，文件目录需要指定到f"{安装目录}\userdata"
    path = path
    # 生成session id 整数类型 同时运行的策略不能重复
    session_id = int(time.time())
    xt_trader = XtQuantTrader(path, session_id)
    # 开启主动请求接口的专用线程 开启后在on_stock_xxx回调函数里调用XtQuantTrader.query_xxx函数不会卡住回调线程，但是查询和推送的数据在时序上会变得不确定
    # 详见: http://docs.thinktrader.net/vip/pages/ee0e9b/#开启主动请求接口的专用线程
    # xt_trader.set_relaxed_response_order_enabled(True)

    # 创建资金账号为 800068 的证券账号对象 股票账号为STOCK 信用CREDIT 期货FUTURE
    acc = StockAccount(stock_account, 'STOCK')
    # 创建交易回调类对象，并声明接收回调
    callback = MyXtQuantTraderCallback()
    xt_trader.register_callback(callback)
    # 启动交易线程
    xt_trader.start()
    # 建立交易连接，返回0表示连接成功
    connect_result = xt_trader.connect()
    print('建立交易连接，返回0表示连接成功', connect_result)
    # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
    subscribe_result = xt_trader.subscribe(acc)
    print('对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功', subscribe_result)
    # xtdata.subscribe_whole_quote(code_list, callback=on_tick)
    xtdata.subscribe_quote('000066.SZ', period='tick', callback=on_tick)
    xt_trader.run_forever()

