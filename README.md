#找工作啊找工作
年关将至，相信很多小伙伴在寻思着发展方向。不知有没小伙伴跟笔者找工作时狂刷简历，为的是找出离家近点的公司，但是有很多公司的简介上是没有地址的，所以也只能再点进去看公司详细地址。
因此，写了个爬虫，方便找工作。
##项目简介
主要代码是一个job_spider.py(用于爬虫), jobs_data_analyse.py(用于工作数据分析)
笔者先获取工作列表，取得简介后再取得详情。下载完成后，再进行分析。
```
# 获取工作简介
def fetch_job_introduce(web_type, keywords, page_count, area):
    url = ""
    decode_type = ""
    #根据不同网站设置不同的地址格式
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
```




##使用方法
打开项目文件jobs_data_analyse.py运行，可根据个人需求更改
```
def start():
    check_area_name()
    fetch_data(web_type=FindJobWebType.all, keywords=['iOS'], area='深圳', page_count=5)
    jobs_data_analyse()
```

###运行后，就会开始收集数据。
![数据爬虫](http://upload-images.jianshu.io/upload_images/2202779-eeff0380f42ca05a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

###收集完成后，会对收集来的薪酬数据简要分析。
![薪酬分析](http://upload-images.jianshu.io/upload_images/2202779-e07d07432fcd81bf.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

###最后会根据工作要求生成wordcloud。
![深圳iOS的词频](http://upload-images.jianshu.io/upload_images/2202779-d7aac00c1b9b7ab6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

为了方便按地区查看工作，笔者把工作简介放在jobs_data_introduce.csv,客官搜索自己要的地区进行查看。
![工作简介](http://upload-images.jianshu.io/upload_images/2202779-280b2e456ba2a4d4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

这个项目只是符合笔者需要，仅供参考。

[项目地址](https://github.com/luomagaoshou/find_job)
