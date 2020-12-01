#正则表达式
import os
import re
import urllib.request

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlwt
from bs4 import BeautifulSoup as bs

#利用正则表达式过滤
#影片链接
findlink = re.compile(r'<a href="(.*?)">')
#电影图片链接
findimgsrc = re.compile(r'<img.*src="(.*?)"',re.S)#让换行符包含在字符中

#片名
findtitle = re.compile(r'<span class="title">(.*)</span>')
#影片的评分
findrating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#评价人数
findcont =re.compile(r'<span>(\d*)人评价</span>')
#影片概述
findinq = re.compile(r'<span class="inq">(.*)</span>',re.S)

#影片的相关内容
finddb = re.compile(r'<p class="">(.*?)</p>',re.S)


#爬取网页

def askURL(url):
    '''
    爬取网页，获得网页的全部内容
    ：param url:爬取网站
    '''
#注意：****修改为自己电脑的用户代理*****
    head = {
       "User-Agent": " 	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0"#用引号括起来
          }
#用户代理：告诉浏览器自己的浏览器类型
    req = urllib.request.Request(url,headers=head)
    try:
        resp = urllib.request.urlopen(req)
        html = resp.read().decode('utf-8')
        #print(html)
    except urllib.error.HTTPError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html  



#获取数据，解析得到数据列表
def get_data(baseurl):
    '''
    使用正则表达式约束，得到想要爬取的内容
    ：param baseurl:基本网址
    '''

    datalist = []
    for i in range(0,10):
        url = baseurl+str(i*25)  #网页自动翻页
        html=askURL(url)  #保存获取到的数据
        
        #解析内容
        soup = bs(html,"html.parser")
        for item in soup.find_all('div',class_="item"):
            
            data = [] #每个影片的数据
            item = str(item)
            
            #影片链接
            link = re.findall(findlink,item)[0]
            data.append(link)
            
            #image link
            imsrc = re.findall(findimgsrc,item)[0]
            data.append(imsrc)
            
            #title
            tt = re.findall(findtitle,item)
            if(2==len(tt)):
                ctt = tt[0]   #中文名
                data.append(ctt)#add chinese title
                
                #ett外文名
                ett = re.sub('/','',tt[1])#remove /
                ett = re.sub('\xa0','',ett)#remove \xa0
                data.append(ett)   #add other title
            else:
                data.append(tt[0])
                data.append(" ")
            #影片评分
            rating = re.findall(findrating,item)[0]
            data.append(rating)
            #参评人数
            cont = re.findall(findcont,item)[0]
            data.append(cont)
            '''
            #影片概述
            inq= re.findall(findinq,item)[0]
            inq = re.sub("<br(/s+)?/>(/s+)?"," ",inq)#remove <br>
            inq = re.sub('/'," ",inq) #去除/
            inq = inq.strip()  #去掉前后的空格
            inq = inq.replace('\xa0','')#去除\xa0
            data.append(inq)
            '''
            #related info
            inf = re.findall(finddb,item)[0]
            inf = re.sub("<br(/s+)?/>(/s+)?"," ",inf)#remove <br>
            inf = re.sub('/'," ",inf) #去除/
            inf = inf.strip()  #去掉前后的空格
            inf = inf.replace('\xa0','')#去除\xa0
            data.append(inf)

            datalist.append(data) #将数据存入datalist
    #print(datalist)#测试
    return datalist



#整理文档
def list2xlwt(url):
    '''
    将列表中的数保存至csv文件中
    :param url:网站链接
    '''
    li = get_data(url)#爬取得到的数据
    columns = ["影片链接", "图片链接","中文片名","其他片名","影片评分","参评人数","影片相关内容"]#栏目名
    dt = pd.DataFrame(li, columns=columns)
    
    #注意：****必须自定义文件路径****
    path = "豆瓣top250.csv"
    if  not os.path.exists(path):  #传入绝对路径
        dt.to_csv(path,index=0)#保存文件
    else:
        print('文件已存在！')
    return path


#下载进度条
def progress_bar(a,b,c):
    '''
    显示下载进度
    :param a:已经下载的数据块
    :param b:数据块的大小
    :param c：远程文件的大小
    '''
    per = a * b*100.0 /c
    if per>100:
        per=100
    print("\rdownloading:%5.1f%%"% per,end='\t')


#批量下载图片
def download_img(path):
    '''
    下载图片并且保存在文件夹中
    ：param path:文件下载路径
    '''
    df = pd.DataFrame(pd.read_csv(path,header=0))
    x = df['图片链接'].values  #图片链接一栏
    y=df['中文片名'].values    #影片中文名
    for i in range(250):
        #注意：****自定义路径****
        #判断文件是否存在，如果不存在就下载
        strn = 'image/'+str(i)+y[i]+'.jpg'#image name 
        if not os.path.isfile(strn):
            urllib.request.urlretrieve(x[i],strn,progress_bar)  #爬取图片
            print('download finished!')
        else:
            print('文件已存在！')


def further_process(path):
    '''
    进一步处理，绘制电影的top250的评分柱状图
    ：param path:文件下载路径
    '''
    df = pd.DataFrame(pd.read_csv(path,header=0))
    x = df['影片评分'].values  #影片的评分一栏
    y = df['参评人数'].values  #参评人数一栏
    
    #评分绘图
    plt.figure(figsize=(14, 10), dpi=80)
    idx = np.arange(1,len(x)+1)
    plt.plot(idx,x,color='red')
    p2 = plt.bar(idx, x,label="score", color="#87CEFA")
    plt.xlabel('top250')
    plt.ylabel('Movie scores')
    plt.ylim([0,12])
    plt.title('Movie ratings')
    plt.legend(loc="upper right")
    plt.show()

#评分绘图
    plt.figure(figsize=(14, 10), dpi=80)
    idx = np.arange(1,1+len(x))
    plt.plot(idx,y,color='red')
    p2 = plt.bar(idx, y,label="contestant number", color="#87CEFA")
    plt.xlabel('top250')
    plt.ylabel('contestant numbers')
    #plt.ylim([0,12])
    plt.title('The contestant number')
    plt.legend(loc="upper right")
    plt.show()


def main():
    #url = "https://movie.douban.com/top250?start="  #网址
    #path=list2xlwt(url)  #保存至csv文件
    #download_img('豆瓣top250.csv')   #爬取图片
     #输入你所存储的表格的位置
    path = "豆瓣top250.csv"
    further_process(path)
    
if __name__=="__main__":
    main()
