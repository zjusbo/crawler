#coding:utf-8
from Crawler import Crawler
'''Author: Song Bo 2014.5.4 
A simple Example''' 

url = "http://www.1688.com"

#Create crawler object with start url
crawler = Crawler(url)

#set search depth
crawler.setSearchDepth(3)

#disable arbitray search
crawler.enableArbitrarySearch(False)

#start crawler thread
crawler.start()

#optional: block main thread to wait crawler thread until it finished.
crawler.join()
