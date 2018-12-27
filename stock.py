# coding: utf-8
import re, time,datetime
import urllib.request
import urllib.error
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import mpl_finance as mpf
import matplotlib.dates as mpd
import matplotlib.ticker as mpt
import tkinter as Tk
import tkinter.messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

mpl.use('TkAgg')

# 全局变量
t = time.localtime()
year = range(t[0], t[0]-1 , -1)
season = range(4, 0, -1)
quotes_date2 = []


# 获取股票交易信息
def getData(url):
    try:
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        content = response.read()
    except urllib.error.HTTPError as e:
        Tk.messagebox.showinfo('提示', '无法获取该股票信息，请重新输入')
        return

    pattern = re.compile('</thead[\s\S]*</tr>    </table>')
    ta = re.findall(pattern, str(content))
    pattern1 = re.compile('<td(.*?)>')
    #pattern2 = re.compile('class=\'cRed\'')
    pattern3 = re.compile(",")
    tab1 = re.sub(pattern1, "<td>", str(ta))
    #tab2 = re.sub(pattern2, "", str(tab1))
    tab = re.sub(pattern3, "", str(tab1))

    if len(tab) == 0:
        data = []
    else:
        pattern3 = re.compile('<td>(.*?)</td>')
        data = re.findall(pattern3, str(tab))

    for d in data:
        if d == '':
            data.remove('')

    return data


# 解析股票代码信息地址
def get_stock_price():
    try: code = int(inputEntry.get())
    except:
            code = 600036
    url1 = "http://quotes.money.163.com/trade/lsjysj_"
    url2 = ".html?year="
    url3 = "&season="
    urllist = []
    for k in year:
        for v in season:
            urllist.append(url1 + str(code) + url2 + str(k) + url3 + str(v))

    price = []
    for url in urllist:
        price.extend(getData(url))

    return price


# 获取股票名
def get_stock_name():
    try: code = int(inputEntry.get())
    except:
            code = 600036
    url1 = "http://quotes.money.163.com/trade/lsjysj_"
    url2 = ".html"
    url = url1 + str(code) + url2

    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    content = response.read()
    content = content.decode("utf-8")

    pattern = re.compile('<h1 class=[\s\S]*</h1>')
    ta = re.findall(pattern, str(content))
    pattern1 = re.compile('<a href=(.*?)>')
    tab1 = re.sub(pattern1, "<a>", str(ta))
    if len(tab1) == 0:
        name = ""
    else:
        pattern2 = re.compile('<a>(.*?)</a>')
        name = re.findall(pattern2, str(tab1))

    return name


# # get the number for date by date2num
# def Date_no(strdate):
#     t = time.strptime(strdate, "%Y-%m-%d")
#     y, m, d = t[0:3]
#     d = datetime.date(y, m, d)
#     n = mpd.date2num(d)
#
#     return n


# 平滑加权
def moving_average(l, N):
    sum = 0
    result = list(0 for x in l)

    for i in range(0, N):
        sum = sum + l[i]
        result[i] = sum / (i + 1)

    for i in range(N, len(l)):
        sum = sum - l[i - N] + l[i]
        result[i] = sum / N

    return result


# 根据数据顺序更换日期
def format_date(x,pos=None):
    # 由于前面股票数据在 date 这个位置传入的都是int
    # 因此 x=0,1,2,...
    # date_tickers 是所有日期的字符串形式列表
    if x < 0 or x > len(quotes_date2)-1:
        return ''
    return quotes_date2[int(len(quotes_date2)-x)]


# 主要函数，负责画K线图
def draw_stock_Kline(Ktime = 128):
    price = get_stock_price()
    theLow = float(price[3])
    thei = 0

    # out = open("stock.csv", 'w')
    # writer = csv.writer(out)
    # writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    # pr = []
    # for i in range(0, len(price), 11):
    #     pr.extend([[price[i], price[i + 1], price[i + 2], price[i + 3], price[i + 4], price[i + 8]]])
    #
    # for prl in pr:
    #     writer.writerow(prl)

    # 获取交易信息
    pr = []
    for i in range(0, len(price), 11):
        pr.extend([[
            # Date_no(price[i])
            (len(price) - i) / 11
            , float(price[i + 1])
            , float(price[i + 2])
            , float(price[i + 3])
            , float(price[i + 4])
            , float(price[i + 8])]]
        )
        temp=float(price[i+3])
        if temp<theLow:
            theLow=float(price[i+3])
            thei=int(i)

    # print(thei)

    quotes = pr[0:Ktime]  # 改
    # print(quotes)

    # 收盘价数组
    quotes_close = [x[4] for x in quotes]
    # 日期数组
    quotes_date = [x[0] for x in quotes]
    for i in range(0, len(price), 11):
        quotes_date2.append(price[i])
    # 成交量数组
    quotes_volume = [x[5] for x in quotes]

    # 清除图像
    fig.clf()

    # 添加图像
    ax = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, facecolor='#07000d')
    mpf.candlestick_ohlc(ax, quotes, width=0.6, colorup='r', colordown='g')     # 蜡烛图

    # 添加10日线与30日线
    av10 = moving_average(quotes_close,10)
    ax.plot(quotes_date, av10, '#e1edf9', label='10 SMA', linewidth=1.5)
    if (Ktime>30):
        av30 = moving_average(quotes_close,30)
        ax.plot(quotes_date, av30, '#4ee6fd', label='30 SMA', linewidth=1.5)

    plt.legend(loc=0,ncol=2)

    # 设置界面布局
    ax.grid(True,color='w')
    ax.xaxis.set_major_locator(mpt.MaxNLocator(10))
    #ax.xaxis.set_major_formatter(mpd.DateFormatter('%Y-%m-%d'))
    #ax.set_xticklabels(quotes_date2)
    ax.xaxis.set_major_formatter(mpt.FuncFormatter(format_date))
    ax.yaxis.label.set_color("w")
    #ax.xaxis_date()
    ax.spines['bottom'].set_color("#5998ff")
    ax.spines['top'].set_color("#5998ff")
    ax.spines['left'].set_color("#5998ff")
    ax.spines['right'].set_color("#5998ff")
    ax.tick_params(axis='y', colors='w')
    plt.gca().yaxis.set_major_locator(mpt.MaxNLocator(prune='upper'))
    ax.tick_params(axis='x', colors='w')
    plt.ylabel('Stock price and Volume')
    #ax.autoscale_view()
    #plt.setp(plt.gca().get_xticklabels(), rotation=30)

    # 添加每日成交量图显示在主图上
    volumeMin = 0
    ax1v = ax.twinx()
    ax1v.fill_between(quotes_date, volumeMin,quotes_volume, facecolor='#00ffe8', alpha=.4)
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    # y轴设置为最大成交量的3倍，不然会太大
    ax1v.set_ylim(0, 3 * max(quotes_volume))

    ax1v.spines['bottom'].set_color("#5998ff")
    ax1v.spines['top'].set_color("#5998ff")
    ax1v.spines['left'].set_color("#5998ff")
    ax1v.spines['right'].set_color("#5998ff")
    ax1v.tick_params(axis='x', colors='w')
    ax1v.tick_params(axis='y', colors='w')

    # 获取股票名并设为窗体标题
    name = get_stock_name()
    root.title(name[0]+'('+name[1]+')')

    # 收集图中收盘价最低的一天信息显示在表格上
    plt.table(cellText=[[str(price[thei]), str(price[thei+1]), str(price[thei+2]), str(price[thei+3]), str(price[thei+4]), str(price[thei+8])]],
              cellLoc='center',
              rowLabels=[""],
              colLabels=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'],
              loc='top',
              )

    canvas.draw()


def _quit():
    #结束事件主循环，并销毁应用程序窗口
    root.quit()
    root.destroy()


if __name__ == '__main__':

    root=Tk.Tk()

    fig = plt.figure(facecolor='#07000d', figsize=(12,8))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget()
    canvas._tkcanvas.grid(row=1,column=0,columnspan=7, rowspan=2,)

    #放置标签、文本框和按钮等部件，并设置文本框的默认值和按钮的事件函数
    label = Tk.Label(root, text='请输入股票代码：').grid(row=0,column=0)

    inputEntry = Tk.Entry(root)
    inputEntry.insert(0, '600036')
    inputEntry.grid(row=0,column=1)

    button1 = Tk.Button(root, text='GO', command=draw_stock_Kline).grid(row=0,column=2)

    monthK = Tk.Button(root, text='monthK', command=lambda : draw_stock_Kline(20)).grid(row=0,column=3)
    seasonK = Tk.Button(root, text='seasonK', command=lambda : draw_stock_Kline(75)).grid(row=0,column=4)
    halfyearK = Tk.Button(root, text='halfyearK', command=lambda : draw_stock_Kline(128)).grid(row=0,column=5)

    button2 = Tk.Button(master=root, text='Quit', command=_quit).grid(row=0,column=6)


    # 启动事件循环
    root.mainloop()
