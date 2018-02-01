import os
from enum import Enum


http_headers = {'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36'}

current_file = __file__
#根目录
root_dir = os.path.abspath(os.path.join(current_file, os.path.pardir, os.path.pardir))
#数据目录
data_dir = os.path.abspath(os.path.join(root_dir, 'data'))
wordcloud_png_path = os.path.abspath((os.path.join(data_dir, 'wordcloud.png')))
#jieba
jieba_dir = os.path.abspath(os.path.join(data_dir, 'jieba'))
alice_png = os.path.abspath(os.path.join(jieba_dir, 'alice.png'))
#字体
wc_font_path = os.path.abspath(os.path.join(data_dir, 'font', 'msyh.ttf'))
#工作数据文件地址
job_data_dir = os.path.abspath(os.path.join(data_dir, 'job_data'))
jobs_data_path = os.path.abspath(os.path.join(job_data_dir, 'jobs_data.csv'))
jobs_data_introduce_path = os.path.abspath(os.path.join(job_data_dir, 'jobs_data_introduce.csv'))
jobs_require_word_freq_path = os.path.abspath(os.path.join(job_data_dir, 'jobs_require_word_freq.csv'))