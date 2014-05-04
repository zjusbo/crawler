# -*- coding:utf-8 -*-	
'''
Created on Apr 19, 2014
Global Variable
@author: SRTP-Team
存放所有的全局变量
'''
import threading
import Queue
import sqlite3

#全局队列，储存待下载网页
q_webpage = Queue.Queue()

#下载的网页数
numOfVisitedLink = 0

#线程id号全局数组，不可更改
#thread_ids锁
thread_ids = []
thread_ids_lock = threading.Lock()

#进程锁，所有进程共用一个
thread_lock = threading.Condition()

#日志文件锁
thread_log_lock = threading.Lock()

#数据库锁
thread_db_lock = threading.Lock()
