# -*- coding:utf-8 -*-
'''
Created on Apr 19, 2014
Webpage Defination
@author: Song Bo
'''

#re 正则表达式模块
#os 文件操作模块
#time 获取系统时间，生成日志时使用
#platform 获取操作系统信息
#socket 获取本机Ip地址
#const 全局常量
#var 全局变量
#urlparse 规范化url
#codecs 编码包
#BeautifulSoup 提取html的tag
import re,os
import time
import platform,socket
import const
import var
import urlparse
import codecs
from bs4 import BeautifulSoup
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib

#Web Page类定义
class WebPage:
	"""It contains basic attributes of a webpage"""
	startURL = ""			#start point of the crawler
	rootURL = '' 			#root url of a website. say, startURL 
	log_idx = 0 			#log index
	log_init = True

	def __init__(self, url, pathdepth = 0):
		self.url = url		#url of web page
		self.title ="" 		#title of web page, not implemented yet
		self.depth = 0		#depth of web page [from start url to current url], not implemented
		self.pathdepth = pathdepth	#number of jumps from startURL to current url
		self.content =""	#content of web page
		self.links = []		#links this web page contains
		self.classes = []	#classes this web page contains
		self.error = False	#error occours or not. It may happen in downloading the content
		self.header = []
		self.contenttype = ''
		self.charset = ''

	def extract_links(self):
		""" Extract hyperlinks in the webpage and store it in self.links[].
		Return False if error occurs, else return True 
		Basiclly download_content() should be called previously.
		But it's OK if you forget to do that since download_content() would be called automatically in this function. """
		
		#If error occurs in downloading the webpage, return False 
		if any(self.content) == False and self.error == True:
			return False

		elif any(self.content) == False:
			self.download_content()

		#Library BeautifulSoup is used to extract tags in 	
		try:	
			soup = BeautifulSoup(self.content)
		
		except Exception:
			print "[BeautifulSoup] Error"

		for tag in soup.findAll('a', href=True):
			tag['href'] = urlparse.urljoin(self.url, tag['href'])
			self.links.append(tag['href'])

		self.links = self.unique(self.links[:])
		
		for idx,link in enumerate(self.links[:]):
			if const.enable_Reverse_Search == False:
				if self.compute_depth(link) < self.depth:
					del self.links[idx]
		del soup
		return True

	def extract_classes(self):
		"""请在此完善代码
		Extract classes in the webpage.
		Return False if error occurs, else return True 
		Basiclly download_content() should be called previously.
		But it's OK if you forget to do that since download_content() would be called automatically in this function. """
		
		#If it can not download the page
		if any(self.content) == False and self.error == True:
			return False
		elif any(self.content) == False:
			self.download_content()
		
		#Add your code here
		#Extract classes
		#
		#
		#
		#只是简单的一句正则匹配，但需要用beautifulsoup进行优化
		self.classes = self.unique(re.findall('''class=['"](.[^'"]+)['""]''',self.content,re.I))
		return True
	
	def compute_depth(self):
		"""Compute depth of the webpage.
		Currently it counts the occurence times of slash "/" in url and minus that of startURL, naively """
		
		self.depth = self.url.count("/") - startURL.count("/")
	
	def compute_depth(self,url):
		"""Compute depth of the webpage specified by url."""
		
		return url.count("/")

	def unique(self,L):
		"""Eliminate duplicated elements in a list.
		Return a new list containing unique elements."""
    		
    		from sets import Set
    		return list(Set(L))
    
    	def generate_filename(self):
    		"""由当前网页的url生成储存文件时使用的文件名
    		算法：统一用 "#" 替换掉url中不合法的字符，并删除http://前缀"""

    		filename = self.url[:]

    		#delete "http://" prefix
    		if filename.startswith("http://"):
    			filename = filename[7:]
    		
    		#convert illegal characters ? /\:*?"<>|
    		illegal_characters =["?","\\","/","*","\"","<",">","|",":",'\t','\n']
    		for c in illegal_characters:
    			filename = filename.replace(c,"#")

    		#Windows下，中文用gbk编码，所以文件名也应用GBK编码，以免造成乱码
    		filename += ".html"
    		if isinstance(filename,unicode):
    			filename = filename.encode("gbk")
    		else:
    			filename = filename.decode("utf-8").encode("gbk")
    		return filename

    	def download_content(self):
    		"""下载当前网页
    		如果下载出错，该函数将self.error 置为True，并将错误原因写入错误日志中。
    		否则，self.content将储存网页源文件，并将网页下载信息写入信息日志中。
    		"""

    		#convert encode for Chinese character
		#url中若含有中文，将unicode 转换为utf-8
		flag = False
		url = self.url
		if isinstance(url,unicode):
			url = url.encode("utf-8")

		try:
			req = Request(url,headers=const.headers)

			self.charset = const.default_charset
		
			response = urlopen(req, timeout = 10)	
		
			self.header = response.info()
			self.contenttype = self.header.get('Content-Type')
			if self.contenttype == None:
				self.error = True
				info = '[Error] There is no Content-Type detected in response header'
				self.writeLog(info)	
				return
			idx = self.contenttype.find("charset=")
			
			if idx != -1:
				self.charset = self.contenttype[idx+8:].strip()
			
			if self.contenttype.find(const.contenttype) != -1:
				self.error = False
				self.content = response.read()
				info = '[Success] Download success.'

				self.writeLog(info)

			else:
				self.error = True
				info = '[Info] This isn\' a valid '+ const.contenttype + ' file\n Content-Type = ' + self.contenttype

				self.writeLog(info)

		except URLError, e:

			self.error = True
			
			if hasattr(e, 'reason'):

				info = '[Error] Failed to reach the server.\nReason: ' + str(e.reason)
				self.writeLog(info)

			elif hasattr(e, 'code'):

				info = '[Error] The server couldn\'t fullfill the request.\nError code: ' +str(e.code)
				self.writeLog(info)
			else:

				info = 'Unknown URLError'
				self.writeLog(info)
		
		except Exception:
			import traceback
			self.error = True
			self.writeLog("Generic exception: " + traceback.format_exc())
			
	def writeLog(self,msg):
		"""写日志文件
		将msg与下载信息写入日志文件中。如果self.error = True 则写入信息日志；如果self.error = False 则写入错误日志。
		注：已经支持中文信息
		"""
		current_path = os.getcwd()+"\\"+const.db_dirc_name

    		if os.path.isdir(current_path) == False:
			os.mkdir(current_path)

		info = ''
		if self.error:
			log_name = const.error_log_name
		else:
			log_name = const.log_name
		#如果是第一次写日志文件，则在文件头写入操作系统信息
		if WebPage.log_init:
			WebPage.log_init = False
			while True:
				WebPage.log_idx +=1
				filename = current_path + "\\" + log_name + "-" + str(WebPage.log_idx) + const.log_file_extension
				if not os.path.isfile(filename):
					break

			info = 'OS Name:\t' + platform.system() + ' ' + platform.release() +', '+ platform.architecture()[0] +'\n'
			info +='Processor Name:\t' + platform.processor() + '\n'
			info += 'Host Name:\t' + platform.node() + '\n'
			info += 'Host IP Address:\t' + socket.gethostbyname_ex(socket.gethostname())[2][0] +'\n'
		else:
			filename = current_path + "\\" + log_name + "-" + str(WebPage.log_idx) + const.log_file_extension

		currenttime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		info += '\n' + currenttime + '\n'
		if isinstance(WebPage.startURL,unicode):
			startURL = WebPage.startURL.encode("utf-8")
		else:
			startURL = WebPage.startURL
		info += 'Start Url:\t' + startURL + '\n'
		if isinstance(self.url,unicode):
			url = self.url.encode("utf-8")
		else:
			url = self.url
		info += 'Url:\t' +url + '\n'
		info += 'Depth:\t' + str(self.pathdepth) + '\n'
		
		var.thread_log_lock.acquire()
		fp = open(filename,"a")
		
		try:
			fp.write(info + msg + '\n')
		
		except Exception:
			import traceback
			print "[Error] webpage.writeLog() write error"
			self.writeLog("Generic exception: " + traceback.format_exc())
		finally:
			fp.close()
			var.thread_log_lock.release()
		
