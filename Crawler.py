 # -*- coding:utf-8 -*-	
'''
Created on Apr 19, 2014
Crawler
@author: SRTP-Team
@description: 爬虫函数，调用Webpage与Downloader
用sqlite
'''
import const
import var
import time
import signal
import sys
import thread,threading
import sqlite3
import os
from WebPage import WebPage
from Downloader import Downloader

# def sigint_handler(signal, frame):

# 	print 'You pressed Ctrl+C!'
# signal.signal(signal.SIGINT, sigint_handler)
class Crawler:		

	def __init__(self, startURL):
		WebPage.startURL = startURL
		self.db_name = ''
		self.conn = ''
		self.cu = ''
		self.numOfThread = 0
		self.lock = threading.Condition()
		self.init()
		
	
	def setStartURL(self, startURL):
		WebPage.startURL = startURL
	
	def getStartURL(self):
		return WebPage.startURL
	
	def setSearchDepth(self, depth):
		const.search_depth = depth

	def enableArbitrarySearch(self, switch):
		const.enable_Arbitrary_Search = switch
	
	def create_thread(self):
		newconn = sqlite3.connect(self.db_name,check_same_thread = False)
		newthread = Downloader(newconn, "Thread-"+str(self.numOfThread))
		var.thread_ids_lock.acquire()
		var.thread_ids.append(newthread)
		var.thread_ids_lock.release()
		newthread.start()
		self.numOfThread += 1

	def init(self):
		#检查URL是否合法
		#插入HTTP前缀
		if not WebPage.startURL.startswith("http://"):
			WebPage.startURL = "http://" + WebPage.startURL
		
		#得到数据库名称		
		db_path = ".\\" + const.db_dirc_name 
		if not os.path.isdir(db_path):
			os.mkdir(db_path)
		self.db_name = db_path + "\\" + const.db_name

		#连接数据库，如不存在，则创建相关表单
		self.conn = sqlite3.connect(self.db_name,check_same_thread = False)
		self.cu = self.conn.cursor()
		fp = open("init.sql","r")
		query = fp.read()
		self.cu = self.conn.cursor()
		self.cu.executescript(query)
		self.conn.commit()
		


	def insertLinkIntoDB(self, linkURL,depth):
		self.cu.execute("INSERT INTO link(linkURL, depth, isVisited, isSimilar) VALUES (?, ?, 0,0)",('%s' %linkURL, depth))
		
		var.thread_lock.acquire()
		self.conn.commit()
		var.thread_lock.release()

	def getNumOfUnvisitedLink(self):
		self.cu.execute("SELECT COUNT(linkID) FROM link WHERE isVisited = 0 AND depth <= %s GROUP BY isVisited" %const.search_depth)
		item = self.cu.fetchone()
		if item == None:
			return 0
		else:
			return item[0]

	def start(self):
		self.insertLinkIntoDB(WebPage.startURL,0)
		thread.start_new_thread(self.threadManager,(self,))
	
	def join(self):
		self.lock.acquire()
		self.lock.wait()
		self.lock.release()
		
	
	def threadManager(self, *arg):
		"""线程管理者，动态地分配并回收线程downloader"""
		
		lastNumOfVisitedLink = -1
		print "[ThreadManager] I'm created."
		
		#初始阶段，创建一个爬虫线程
		self.create_thread()
		while True:

			var.thread_ids_lock.acquire()
			self.numOfThread = len(var.thread_ids)
			var.thread_ids_lock.release()
			NumOfUnvisitedLink = self.getNumOfUnvisitedLink()
			
			#所有网页均已爬完,结束该线程
			if self.numOfThread == 0 and NumOfUnvisitedLink == 0:
				break

			#未爬完，创建一个新线程
			if self.numOfThread == 0 and NumOfUnvisitedLink > 0:
				self.create_thread()
			
			#如果单个爬虫线程分配的任务(网页)过多，则尝试新建一个爬虫线程
			if NumOfUnvisitedLink / self.numOfThread > const.page_per_thread:
				
				#如果线程数超过阈值，则显示Warning信息，待完善
				if self.numOfThread >= const.max_threads_num:
					info = ''"[Warning] Can not create thread. Maximun number of thread reaches."
					#writeLog(info)
				else:
					#Crate thread
					self.create_thread()

			#状态变化时，在控制台输出信息
			if(lastNumOfVisitedLink != var.numOfVisitedLink):
				print "Num of threads:" + str(self.numOfThread)
				print "Num of unvisited links: " + str(NumOfUnvisitedLink)
				print "Num of visited links: "+ str(var.numOfVisitedLink)
				lastNumOfVisitedLink = var.numOfVisitedLink
		
		#线程管理者结束
		#输出最后的状态信息
		NumOfUnvisitedLink = self.getNumOfUnvisitedLink()
		print "Num of threads:" + str(self.numOfThread)
		print "Num of unvisited links: " + str(NumOfUnvisitedLink)
		print "Num of visited links: "+ str(var.numOfVisitedLink)
		print "[ThreadManager] I'm terminated."
		self.lock.acquire()
		self.lock.notify()
		self.lock.release()
