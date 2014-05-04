# -*- coding:utf-8 -*-
'''
Created on Apr 19, 2014
Downloader
@author: SRTP-Team
每个线程所运行的函数，下载网页，调用WebPage对象
'''
import Queue,threading
import var,const
import os
from WebPage import WebPage
import time
class Downloader(threading.Thread):
	"""多线程，下载网页
	调用WebPage类中的相关函数"""
	def __init__(self, conn, name="Thread", lock=var.thread_lock):
		"""name: 函数名称，可任取
		lock: 进程锁
		queue: 储存待下载的网页对象，每个元素为一个WebPage的对象"""
		threading.Thread.__init__(self)
		self.lock = lock
		self.name = name
		self.error = False
		self.count = 0
		self.conn = conn
		self.cu = conn.cursor()
		self.filePath = ''
		self.isBlocked = False
		self.isKilled = False
		self.errorTimes = 0
	def setBlocked(self):
		self.isBlock = True
	def isBlocked(self):
		return self.isBlocked
	def setActive(self):
		self.isBlocked = False
		#To be checked
		self.lock.notify()
	def Kill(self):
		self.isKilled = True
	def run(self):
		#算法：
		#如果数据库表link中存在未访问网页：
		#	拿出一条未访问记录，下载内容，存到文件中，提取超链接，提取网页中的class
		#	如果下载出现错误(webpage.error == True) 跳过该网页(写入错误日志中)，继续第一步
		#	如果当前网页达到搜索深度，忽视网页超链接，返回第一步；
		#		否则，将该网页所有符合条件的超链接存入数据库Link表中
		#		将class存入class表中，将page，class，link的关系存入相关表中
		try:
			while True:
				if self.isKilled:
					print "[Thread] Thread is killed."
					break
				if self.isBlocked:
					self.lock.acquire()
					self.lock.wait()
					self.lock.release()
				self.lock.acquire()
				self.cu.execute("SELECT * FROM link WHERE isVisited = 0 AND isSimilar = 0 AND depth <= %s LIMIT 0,1" % const.search_depth)
				item = self.cu.fetchone()
				if item != None:
					self.cu.execute("UPDATE link SET isVisited = 1 WHERE linkID = ?", (item[0],))
					self.conn.commit()
				self.lock.release()

				#item: linkID, linkURL, depth, isVisited, Similar
				if item == None:
					self.errorTimes += 1
					if(self.errorTimes > 3):
						self.isKilled = True
					print "[Thread] No suitable item in db, sleep for 0.1s"
					time.sleep(0.1)
					continue
				
				linkID = item[0]
				linkURL = item[1]
				linkDepth = item[2]
				webpage = WebPage(linkURL, linkDepth)
				webpage.download_content()
				
		 		if webpage.error:
		 			continue
		 		
		 		webpage.extract_links()
		 		webpage.extract_classes()
				
		 		self.save(webpage)
		 		paraValue = []
		 		for link in webpage.links:
					if isinstance(link,str):
						link = link.decode("utf-8")

					if not const.enable_Arbitrary_Search and link.find(webpage.startURL) == -1:
						#如果搜索到指向当前网站之外的链接，仍将其存入数据库中，但将其标记为已访问
						paraValue.append(("%s" % link, webpage.pathdepth + 1, 1, 0))

					elif not const.enable_Reverse_Search and webpage.compute_depth(link) < webpage.depth:
						#如果搜索到逆向连接（由子页面指向父页面），仍将其存入数据库中，但标记为已访问，即不进行搜索
						paraValue.append(("%s" % link, webpage.pathdepth + 1, 1, 0))
					
					else:
						paraValue.append(("%s" % link, webpage.pathdepth + 1, 0, 0))
		 		
		 		#将结果写入数据库
		 		#注意要先取得进程锁
		 		if isinstance(self.filePath,str):
		 			self.filePath = self.filePath.decode("gbk")
		 		if isinstance(webpage.url, str):
		 			webpage.url = webpage.url.decode("utf-8")

		 		self.lock.acquire()
		 		self.cu.execute("INSERT INTO page(pageURL, depth, filePath) VALUES (?,?,?)",("%s" %webpage.url, webpage.pathdepth, "%s" %self.filePath))
		 		self.cu.executemany("INSERT INTO link(linkURL, depth, isVisited, isSimilar) VALUES(?,?,?,?)", paraValue)
		 		self.conn.commit()
		 		
		 		#在此添加代码
		 		#写class表，写三个关系表class_contain_link, page_contain_class, page_contain_link
		 		#"INSERT INTO page_contain_link(FX_page_pageID, FX_link_linkID) VALUES (?,?)"

		 		var.numOfVisitedLink += 1
		 		
		 		self.lock.release()
		 		
		 		#释放资源
		 		del webpage
		 		del paraValue

		except Exception:
			import traceback
		 	self.error = True
		 	self.writeLog("Generic exception: " + traceback.format_exc())
		 	print traceback.format_exc()
		finally:
			var.thread_ids_lock.acquire()
			var.thread_ids.remove(self)
			var.thread_ids_lock.release()		

	def save(self,webpage):
    		"""Save downloaded webpage to file.
    		Save path can be changed by modifying variable 'db_dirc_name' in file 'const.py' """
    		
    		if webpage.error == True:
    			return False

    		if os.path.isdir(".\\"+const.db_dirc_name) == False:
    		
			os.mkdir(".\\"+const.db_dirc_name)
	
		if os.path.isdir(".\\"+const.db_dirc_name+"\\"+"pathdepth-"+str(webpage.pathdepth))== False :
	
			os.mkdir(".\\"+const.db_dirc_name+"\\"+"pathdepth-"+str(webpage.pathdepth))
	
		current_path = ".\\"+const.db_dirc_name+"\\"+ "pathdepth-"+str(webpage.pathdepth)
	
		filename = webpage.generate_filename()
		filename = current_path + "\\" + filename
		if isinstance(webpage.content, unicode):
			content = webpage.content.encode("gbk")
		else:
			content = webpage.content
		fp = open(filename,"w")
		fp.write(webpage.content)
		fp.close()
		self.filePath = filename
		return True

	def writeLog(self, msg):
		pass
