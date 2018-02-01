from bs4 import BeautifulSoup
import requests
import os
from enum import Enum
from program import config
import pandas as pd



pd.set_option('expand_frame_repr', False)  # 列太多不换行

class FindJobWebType(Enum):
    _51job = '_51job'  # 51job
    zhilian = 'zhilian'  # 智联
    all = 3  # 所有

#全局变量  记录爬虫次数
SPIDER_REQUIRE_COUNT = 0

#获取51job地址编号对应地名
def get_51job_area_code():
    dic = {}
    for i in range(1, 37):
        url = 'http://search.51job.com/list/{}0000,000000,0000,00,9,99,ios,2,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=1&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='.format('%02d' % i)
        r = requests.get(url, headers=config.http_headers).content.decode('gbk')
        area_name = BeautifulSoup(r, 'lxml').find(id="work_position_input")['value']
        print(area_name, i)
        dic[area_name] = i
    file_path = os.path.join(config.job_data_dir, '51job_area_code.txt')
    print('51job地区编号文件获取成功')
    with open(file_path, "w+", encoding="utf-8") as f:
        f.write(str(dic))
        f.close()


#  检查本地是否有51job地区编号 没有的话就自动获取
def check_area_name():
    file_path = os.path.join(config.job_data_dir, '51job_area_code.txt')
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            if f:
                result = f.read()
                dic = eval(result)
                f.close()
    else:
        print('51job缺少地区编号文件,获取中')
        get_51job_area_code()
        check_area_name()





def fetch_data( web_type=FindJobWebType.all, keywords=['iOS'], page_count=5, area='深圳'):
    if os.path.exists(config.jobs_data_path):
        os.remove(config.jobs_data_path)
        print('删除之前爬的数据')

    if web_type == FindJobWebType._51job:
        _fetch_data(web_type, keywords, page_count, area)
    elif web_type == FindJobWebType.zhilian:
        _fetch_data(web_type, keywords, page_count, area)
    elif web_type == FindJobWebType.all:
        for type in list(FindJobWebType)[0: -1]:
            _fetch_data(type, keywords, page_count, area)

def _fetch_data(web_type, keywords, page_count, area):
    df = fetch_job_introduce(web_type, keywords, page_count, area)
    df = fetch_job_detail(df)
    df.fillna(value='', inplace=True)

    if os.path.exists(config.jobs_data_path):
        df_existed = pd.read_csv(config.jobs_data_path, encoding='utf-8', index_col=0)
        df = df.append(df_existed, ignore_index=True)

    df.sort_values(by=['地区'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.to_csv(config.jobs_data_path, mode='w', encoding='utf-8')


    #去除简介 方便查看
    df_no_require = df.drop(['要求'], axis=1)
    df_no_require['薪酬'] = df_no_require['薪酬'].apply(lambda x: x.ljust(12))
    df_no_require['地区'] = df_no_require['地区'].apply(lambda x:x.ljust(12))
    df_no_require['详细地址'] = df_no_require['详细地址'].apply(lambda x: x.ljust(30))
    df_no_require['链接'] = df_no_require['链接'].apply(lambda x: x.ljust(50))
    df_no_require.to_csv(config.jobs_data_introduce_path, mode='w', encoding='utf-8')


# 获取工作简介
def fetch_job_introduce(web_type, keywords, page_count, area):
    url = ""
    decode_type = ""
    #根据不同网络设置不同的地址格式
    area_need = ""
    if web_type == FindJobWebType._51job:
        url = "http://search.51job.com/list/{}0000,000000" \
              ",0000,00,9,99,{},2,{}.html? lang=c&stype=1&postchannel=0000&workyear=99&" \
              "cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0" \
              "&confirmdate=9&fromType=1&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
        decode_type = 'gbk'
        file_path = os.path.join(config.job_data_dir, '51job_area_code.txt')
        with open(file_path, mode='r', encoding='utf-8') as f:
            result = f.read()
            dic = eval(result)
            area_need = '%02d' % dic[area]
    elif web_type == FindJobWebType.zhilian:
        url = "http://sou.zhaopin.com/jobs/searchresult.ashx?jl={}&kw={}&isadv=0&sg=7e9e61449fd14593a5604fff81aec46a&p={}"
        decode_type = "utf-8"
    # 实际页数从1开始，所以+1
    urls = [url.format(area_need,' '.join(keywords), p+1) for p in range(0, page_count)]
    df = fetch_companies(urls, decode_type, web_type)
    return df




def fetch_companies(urls, decode_type, web_type):
    df = pd.DataFrame(columns=['薪酬', '地区', '详细地址', '链接', '工作', '公司', '来源', '要求'])

    # 要页数从0开始
    for url in urls:
        r = requests.get(url, headers=config.http_headers).content.decode(decode_type)
        if web_type == FindJobWebType._51job:
            bs = BeautifulSoup(r, 'lxml').find("div", class_="dw_table").find_all("div", class_="el")
            for b in bs:
                try:
                    href, job_name = b.find('a')['href'], b.find('a')['title']
                    company_name = b.find('span', class_='t2').text
                    locate = b.find('span', class_='t3').text
                    salary = b.find('span', class_='t4').text

                    dic = {'工作': company_name,
                           '地区': locate,
                           '详细地址': '',
                           '薪酬': salary,
                           '公司': job_name,
                           '链接': href,
                           '来源': web_type.value,
                           '要求': ''}
                    index = df.shape[0]
                    df.loc[index] = dic
                    # print(df)
                except Exception:
                    print("简介解析错误")
                    pass
        elif web_type == FindJobWebType.zhilian:
            bs = BeautifulSoup(r, 'lxml').find(id="newlist_list_content_table").find_all("table",class_="newlist")
            for b in bs:
                try:
                    # 第一个标签没有信息
                    href = b.find("td", class_="zwmc").find("div").find("a")["href"]
                    company_name = b.find("td", class_="zwmc").find("div").find("a").text
                    job_name = b.find("td", class_='gsmc').find("a").text
                    locate = b.find("td", class_="gzdd").text
                    salary = b.find("td", class_="zwyx").text
                    dic = {'工作': company_name,
                           '地区': locate,
                           '详细地址': '',
                           '薪酬': salary,
                           '公司': job_name,
                           '链接': href,
                           '来源': web_type.value,
                           '要求': ''}
                    index = df.shape[0]
                    df.loc[index] = dic
                    # print(df)
                except:
                    print("简介解析错误")
                    pass
    return df

# 获取工作详情
def fetch_job_detail(df):

    for i in  range(0, df.shape[0]):
        introduce = df.loc[i]
        location, require = _fetch_location_and_require_from_detail(introduce)
        df.loc[i, '详细地址'] = location
        df.loc[i, '要求'] = require

    return df

# 获取详细地址与工作要求详情
def _fetch_location_and_require_from_detail(introduce):
    global SPIDER_REQUIRE_COUNT
    web_type = introduce['来源']
    href = introduce['链接']
    company_name = introduce['公司']
    if web_type == FindJobWebType._51job.value:
        SPIDER_REQUIRE_COUNT += 1
        print("正在爬第{}个公司{}的要求\n{}".format(SPIDER_REQUIRE_COUNT, company_name, href))
        try:
            r = requests.get(href, headers=config.http_headers).content.decode("gbk")
            location_detail = _fetch_location_from_detail(r, introduce)
            bs = BeautifulSoup(r, 'lxml').find('div', class_="bmsg job_msg inbox")
            useless_bs1 = bs.find('p', class_='fp')
            useless_bs2 = bs.find('div', class_='share')
            require = bs.text.replace(useless_bs1.text, '').replace(useless_bs2.text, '')\
                .replace("\t", "").replace("\n", "").replace("\r", "")
            return location_detail, require
        except:
            print("工作要求解析错误")
            return "", ""
            pass

    elif web_type == FindJobWebType.zhilian.value:
        SPIDER_REQUIRE_COUNT += 1
        print("正在爬第{}个公司{}的要求\n{}".format(SPIDER_REQUIRE_COUNT, company_name, href))

        try:
            r = requests.get(href, headers=config.http_headers).content.decode("utf-8")
            location_detail = _fetch_location_from_detail(r, introduce)
            bs = BeautifulSoup(r, 'lxml').find('div', class_="tab-inner-cont")
            useless_bs1 = bs.find('b')
            useless_bs2 = bs.find('h2')
            useless_bs3 = bs.find(id='applyVacButton1')
            require = bs.text.replace(useless_bs1.text, '').replace(useless_bs2.text, '').replace(useless_bs3.text, '')\
                .replace("\t", "").replace("\n", "").replace("\r", "")
            return location_detail, require
        except:
            print("工作要求解析错误")
            return "", ""
            pass

#获取详细地址
def _fetch_location_from_detail(h5_content, introduce):

    """获取公司详细地址"""
    web_type = introduce['来源']
    if web_type == FindJobWebType._51job.value:
        bs = BeautifulSoup(h5_content, 'lxml').find_all('p', class_="fp")
        for b in bs:
            try:
                location = b.text
                if "上班地址" in location:
                    location = location.replace("上班地址：", "").replace("\t", "").replace("\n", "")
                    return location
            except:
                print('上班地址解析错误')
                return introduce['地区']
                pass
    elif web_type == FindJobWebType.zhilian.value:

        bs = BeautifulSoup(h5_content, 'lxml').find('div', class_="tab-inner-cont")

        try:
            location = bs.find("h2").text
            location = location.replace("\t", "").replace("\n", "").replace("\r", "").replace(" ", "").replace("查看职位地图", "")
            return location

        except:
            print('上班地址解析错误')
            return introduce['地区']
            pass




