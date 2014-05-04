# -*- coding:utf-8 -*-
'''
Created on Apr 19, 2014
Global Constant
@author: SRTP-Team
存放所有的全局常量
'''

import threading

#Debug 开关，如果开启，则在命令行显示更多的调试信息
debug = False

#directory name of database
db_dirc_name = "db"
db_name = "db.sqlite3"
db_init_sql_name = "init.sql"

log_name = "Log"
error_log_name = 'ErrorLog'
log_file_extension = '.txt'

#Disguise crawler as a browser 
#by changing headers in a http request
headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6' 
}

#下载的网页类型
contenttype = 'text/html'

#允许跳转到任意网站，
#若为True 则不受限制
#若为False 只允许搜索位于Start_Url以下的网页
enable_Arbitrary_Search = False

#允许逆向搜索
#若为True 则允许子网页搜寻父网页
#若为False 则只允许从父网页搜寻子网页
#例: 若为False，不能从www.baidu.com/web/2014 向上搜寻到www.baidu.com/web
enable_Reverse_Search = False

#搜索深度
search_depth = 3

#最大线程数
max_threads_num = 80

#每个线程的下载等待队列中的最大网页数
#如果网页超过该阈值，则新建一个线程
#例：如果 queue.size() / num_current_thread > page_per_thread 则新建一个线程，num_curent_thread++
page_per_thread = 20

#默认网页解码方式
default_charset = 'utf-8'
