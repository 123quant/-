## **[QuantLimit](https://github.com/123quant/QuantLimit)**

该项目实现了一种**量化打板策略**，用于A股股票交易，涨停板制度只存在于A股市场,

旨在识别并利用市场中潜在的涨停机会。该策略通过技术指标、历史价格数据和成交量分析，股吧数据分析获取可能达到涨停的股票池，并在股票涨停瞬间买入以获取隔日高溢价。

## 安装步骤

克隆仓库：

```
bash

复制代码
git clone  https://github.com/123quant/QMT-QuantLimit.git
```

安装所需依赖：

```
复制代码
pip install -r requirements.txt
```

## 使用方法

1.配置参数

打开 配置文件->config.ini

![image-20241219085031486](C:\Users\yfH\AppData\Roaming\Typora\typora-user-images\image-20241219085031486.png)

本策略通过miniqmt实现，需要配置三个参数

- qmt_path ：qmt软件的安装路径
- stock_account ：股票账号
- buy_values ：每只票买入金额

2.填好配置文件，第二步上传股票池

打开 配置文件->股票池.txt

![image-20241219085524214](C:\Users\yfH\AppData\Roaming\Typora\typora-user-images\image-20241219085524214.png)

把需要监控的股票填进股票池，也可以使用同花顺、通达信导出的股票池。

3.在每日打板策略运行前，需要先初始化涨停板数据

直接运行    策略数据初始化.py

```
#先进入当前目录
python 策略数据初始化.py
```

![image-20241219085756431](C:\Users\yfH\AppData\Roaming\Typora\typora-user-images\image-20241219085756431.png)

运行结束后在配置文件价下有一个json数据，记录今日沪深A股的涨停价

![image-20241219085910444](C:\Users\yfH\AppData\Roaming\Typora\typora-user-images\image-20241219085910444.png)

4.最后直接运行策略，开始打板

```
#先进入文件目录
python ./打板策略.py
```

![image-20241219090049748](C:\Users\yfH\AppData\Roaming\Typora\typora-user-images\image-20241219090049748.png)