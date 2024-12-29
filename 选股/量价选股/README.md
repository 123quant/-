## 问财选股数据提取

大致看了一下问财的开源的项目都没有维护比较好的，自己写了个问财的数据获取工具

## 使用方法

1. 打开  [问财](https://www.iwencai.com/unifiedwap/home/index) 输入我们的选股条件：

   比如选择条件：最近3个交易日涨幅小于15%；剔除st；沪深a股；流通市值大于50亿小于500亿；股价大于5元；最近一个月涨幅小于100%；收盘价大于5日均线

   <p align="center">
     <img src="../../assets/images/问财选股.png"/>
   </p>

   ​	可以看到我们查出有近500只股票符合条件，由于同花顺的导出数据有100条限制

    2.接下来使用我们的工具获取全部股票池

   ​	打开项目 cd 到 .\QMT-QuantLimit\选股\量价选股 目录下填写配置config.json文件

   <p align="center">
     <img src="../../assets/images/wencai_config.png"/>
   </p>

   在网页中按 F12  打开开发者模式 ，找到

    Network / 网络

   选择Fetch/XHR   找到 get_robot_data 

   点开  。如果没找到就刷新一下网页就可以了    

   <p align="center">
     <img src="../../assets/images/image-20241224213022420.png"/>
   </p>

   <p align="center">
     <img src="../../assets/images/image-20241224212913771.png"/>
   </p>

3.填写Cookie到项目的config.json文件对应的Cookie字段下

<p align="center">
  <img src="../../assets/images/image-20241224213401822.png"/>
</p>



4.同样填写question字段，点击Payload 找到question 复制到config.json文件对应的字段下即可

<p align="center">
  <img src="../../assets/images/微信图片_20241224215542.png"/>
</p>

5.填写好配置文件就直接运行代码

```
#先cd 到项目文件下 ./QMT-QuantLimit/选股/量价选股
python  问财选股.pyc
```

<p align="center">
  <img src="../../assets/images/image-20241224214010665.png"/>
</p>

等待下载完所有的数据，输出股票池

<p align="center">
  <img src="../../assets/images/image-20241224214133112.png"/>
</p>



## 大功告成

需要获取全部字段，q我

