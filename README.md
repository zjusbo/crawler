Crawler
=======

A simple web crawler, implemented in Python.

###Install instruction

Download all the source files in this repo and run **Main.py** to see the result.


###Prerequisites
Installing of following software is required.
- [Python 2.7.6](https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi)
- [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/#Download)

###File description
- **Main.py** contains a simple example with a start url and some search modes. You can simply run main.py to see the result of this web crawler.

- **Crawler.py** provides some interfaces which can be called by main.py. See the code in it to discover more features of it.

- **Downloader.py** contains class *Downloader* which inherits class *threading*. Each crawler thread is an object of *Downloader*.
- **const.py** all the global consts are defined in this file.
- **var.py** all the global variables are defined in this file.
- **WebPage.py** contains class *WebPage* which stores basic attributes and behaviors of a webpage. Each downloaded webpage is regarded as an object of *WebPage*
- **init.sql** sql script, for database initializing.  
