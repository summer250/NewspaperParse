# 报纸数据分析：
通过scrapy-redis爬取报纸网站：
  1. 浙江日报（http://zjrb.zjol.com.cn/html/2022-04/01/node_18.htm）
  2. 光明日报（https://epaper.gmw.cn/gmrb/html/2022-04/17/nbs.D110000gmrb_01.htm）
  3. 新快报（https://epaper.xkb.com.cn/）
  4. 上海青年报（http://www.why.com.cn/epaper/webpc/qnb/html/2021-04/19/node_1.html）

并通过Flink 进行数据分析

![88042db53249e5316f9171ee18bf9d6](https://user-images.githubusercontent.com/56312206/164392685-1ebc9a27-6ec1-4abf-83f6-3503d915832b.png)
 
 具体词汇的话如图所示，文章中出现红线上方的词汇则是需要寻找的目标文章，此外在基础上统计目标文章中出现红线下方词汇的文章数。
