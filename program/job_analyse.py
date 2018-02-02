import os
from program import config
import pandas as pd
import math
import jieba
import jieba.posseg
import csv
import matplotlib.pyplot as plt

from program.job_spider import *
import numpy as np
from PIL import Image
from collections import Counter
from wordcloud import WordCloud
pd.set_option('expand_frame_repr', False)
def jobs_data_analyse():
    df = pd.read_csv(config.jobs_data_path, encoding='utf-8')
    df['薪酬'] = df['薪酬'].apply(unify_salary_form)
    salary_analyse(df)
    require_analyse(df)

#统一工资格式
def unify_salary_form(salary):

    if type(salary) == float and math.isnan(salary):
        return None
    month = 1
    if salary.endswith('/年'):
        month = 12
        salary = salary.replace('/年', '')
    elif salary.endswith('/月'):
        month = 1
        salary = salary.replace('/月', '')

    multiple = 1
    if salary.endswith('千'):
        multiple = 1000
        salary = salary.replace('千', '')
    elif salary.endswith('万'):
        multiple = 10000
        salary = salary.replace('万', '')

    # print(salary)
    try:
        min = int(float(salary.split('-')[0]) * multiple / month)
        max = int(float(salary.split('-')[1]) * multiple / month)
        return str(min), str(max), str(min) + '-' + str(max)
    except Exception as e:
        print(e)
        return None

#分析薪酬
def salary_analyse(df):
    df['low_薪酬'] = df['薪酬'].apply(lambda x: None if(x == None) else int(x[0]))
    df['high_薪酬'] = df['薪酬'].apply(lambda x: None if (x == None) else int(x[1]))

    print('该行业平均工资为: ', df.dropna(subset=['薪酬'])[['low_薪酬', 'high_薪酬']].mean().mean())
    index_max_salary = df['high_薪酬'].idxmax()
    index_min_salary = df['low_薪酬'].idxmin()
    print('最高薪酬的公司: %s 薪酬为: %d 链接如下\\n%s' % (df.loc[index_max_salary, '公司'], df['high_薪酬'].max(), df.loc[index_max_salary, '链接']))
    print('最低薪酬的公司: %s 薪酬为: %d 链接如下\\n%s' % (df.loc[index_min_salary, '公司'], df['low_薪酬'].min(), df.loc[index_min_salary, '链接']))

    for area, group in df.dropna(subset=['薪酬']).groupby('地区'):
        average_salary = group[['low_薪酬', 'high_薪酬']].mean().mean()
        print('该行业在地区:(%s)的平均薪酬为:%d' % (area, average_salary))


#分析要求
def require_analyse(df):
    all_require = ''
    for require in df['要求']:
        if type(require) == float and math.isnan(require):
            continue
        all_require += require
    _require_word_freq(all_require)
    _require_word_cloud()

def _require_word_freq(all_require):
    #设置用户词典
    jieba.load_userdict(os.path.join(config.jieba_dir, "user_dict.txt"))
    seg_lst = jieba.posseg.cut(all_require)
    counter = Counter()
    #设置停用词
    stopwords_path = os.path.join(config.jieba_dir,"stopwords.txt" )
    stopwords = [line.strip() for line in open(stopwords_path, "r", encoding="utf-8").readlines()]

    for seg in seg_lst:
        if seg.word in stopwords:
            continue
            #过滤符号
        elif seg.flag == 'x':
            continue
        counter[seg.word] += 1
    counter_sorted = sorted(counter.items(), key=lambda value: value[1], reverse=True)


    with open(config.jobs_require_word_freq_path, "w+", encoding="utf-8") as f:
        f_csv = csv.writer(f)
        f_csv.writerows(counter_sorted)
        print('词频文件保存成功,地址为：', config.jobs_require_word_freq_path)

def _require_word_cloud():
    word_freq_dic = dict()
    with open(config.jobs_require_word_freq_path, mode='r', encoding='utf-8') as f:
        f_csv = csv.reader(f)
        # print(f_csv)
        for row in f_csv:
            word_freq_dic[row[0]] = int(row[1])
        # print(word_freq_dic)

    #使用图片作为背景生成wordcloud
    #这里用alice的图 是从这里得来的http://blog.csdn.net/fontthrone/article/details/72775865
    # alice_coloring = np.array(Image.open(config.alice_png))
    # wc = WordCloud(font_path=config.wc_font_path, background_color='white', mask = alice_coloring,
    #                max_words=150, max_font_size=100, min_font_size=20)\
    #     .generate_from_frequencies(word_freq_dic)


    wc = WordCloud(font_path=config.wc_font_path,
                          max_words=150, height=800, width=1400).generate_from_frequencies(word_freq_dic)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis('off')
    plt.show()
    wc.to_file(config.wordcloud_png_path)


def start():
    check_area_name()
    fetch_data(web_type=WEBTYPE.all, keywords=['iOS'], area='深圳', page_count=5)
    jobs_data_analyse()


start()
