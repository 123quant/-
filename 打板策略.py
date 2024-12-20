from xtquant import xtdata
import pandas as pd
from datetime import datetime
import time
import json
import os,sys
import configparser
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant



# 获取当天日期并转换为'YYYYMMDD'格式
today_str = datetime.now().strftime('%Y%m%d')
# now_time = datetime.now().strftime("%H:%M")


print('开始读取涨停价字典')
try:
    # 读取JSON文件
    with open('./配置文件/{}-limit_up_prices.json'.format(today_str), 'r', encoding='utf-8') as f:
        loaded_dict = json.load(f)
except:
    print('没有找到涨停价字典文件,请先运行打板配置')
print('读取涨停价字典完成')

#======================================================

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
            print("打板股票池：")
            print(code_list)
except FileNotFoundError:
    print(f"文件 {file_path} 不存在，请检查文件路径。")
except Exception as e:
    print(f"发生错误：{e}")
    
    

# 定义一个类 创建类的实例 作为状态的容器
class _a():
    pass

A = _a()
A.bought_list = []

def update_bought_list():
    full_data = xtdata.get_full_tick(code_list)
    #检测如果当前价格已经等于涨停价就加入A.bought_list中
    for stock in code_list:
        if full_data[stock]['lastPrice'] == loaded_dict[stock]:
            A.bought_list.append(stock)

#======================================================

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

    return path, stock_account, buy_values  

update_bought_list_num = 0

#======================================================
def f(data):
    now = datetime.now().strftime("%H:%M")
    if update_bought_list_num == 0 and now >= '09:25':
        update_bought_list()
        update_bought_list_num = 1

    for stock  in data:
        if stock not in code_list:
            continue
        print('监控',stock,data[stock])
        cuurent_price = data[stock]['lastPrice']
        up_limit_price = loaded_dict[stock]
        factor1 = cuurent_price >= up_limit_price
        factor2 = stock not in A.bought_list
        
        if factor1  and factor2 and now <= '10:00':
            print(stock,'到达涨停')
            xtdata.download_history_data(stock_code=stock,period='tick',start_time=today_str,incrementally=True)
        
            lastPrice_array = xtdata.get_market_data_ex_ori(field_list= ['lastPrice'],period='tick',stock_list=[stock])[stock]
            
            factor3 = ((lastPrice_array[-1][0]-lastPrice_array[-25][0])/data[stock]['lastClose']) >= 0.03
            if factor3:
                stock_count = buy_values / cuurent_price
                # 取整到最接近的 100 的倍数
                buy_volume = round(stock_count / 100) * 100
        
                async_seq = xt_trader.order_stock_async(acc, stock, xtconstant.STOCK_BUY, buy_volume, xtconstant.LATEST_PRICE, up_limit_price, 'limit_up_strategy')
                A.bought_list.append(stock)

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

# def interact():
#     """执行后进入repl模式"""
#     import code
#     code.InteractiveConsole(locals=globals()).interact()





if __name__ == '__main__':
    try:
        path, stock_account, buy_values = load_config()
        print(f"qmt路径: {path}")
        print(f"账号: {stock_account}")
        print(f"每笔买多少元: {buy_values}")
    except:
        print('没有找到配置文件,请先填写配置文件')




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
    xtdata.subscribe_whole_quote(code_list, callback=f)
    xt_trader.run_forever()

