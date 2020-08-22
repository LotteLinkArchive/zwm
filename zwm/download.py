#!/usr/bin/python

import term_layout
import urllib.request
import math

class download:
	def install_and_import(self, package):
		import importlib
		try:
			importlib.import_module(package)
		except ImportError:
			try:
				import pip
				pip.main(['install', package])
			except Exception as e:
				print(str(repr(e)))
				
				sys.exit()
		finally:
			globals()[package] = importlib.import_module(package)
	
	def sizeof_fmt(self, num, suffix='B'):
		for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
			if abs(num) < 1024.0:
				return "%3.1f %s%s" % (num, unit, suffix)
			num /= 1024.0
		return "%.1f %s%s" % (num, 'Yi', suffix)
	
	def progressBar(self, percent, total, current, text):
		r = math.floor(percent / 4)
		
		if current > total:
			current = total
		
		if total == -1:
			percent = '...'
			current = 0
			total = 0
		return text+'\n[' + colorama.Style.BRIGHT + colorama.Fore.MAGENTA + ('━' * r).ljust(25) + colorama.Style.RESET_ALL + colorama.Style.DIM + '] | '+str(percent)+'% | '+self.sizeof_fmt(current)+' of '+self.sizeof_fmt(total)
	
	def progressDisplay(self, blocknum, bs, size):
		if self.first == False and size == -1:
			self.output.warning('The specified collection URL is not reporting a filesize!')
			self.first = True
		percent = int(blocknum * bs * 100 / size)
		if percent > 100:
			percent = 100
		self.output.progress(str(self.progressBar(percent, size, blocknum * bs, 'Collecting ' + colorama.Fore.BLUE + self.current_file + colorama.Style.RESET_ALL + colorama.Style.DIM + '...')), False)
	
	def get(self, url, to):
		self.first = False
		urllib.request.URLopener.version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
		
		self.current_file = url
		
		result = open(urllib.request.urlretrieve(url=url, filename=to, reporthook=self.progressDisplay)[0], 'rb').read()
		self.output.next()
		self.output.success('Collection of '+url+' to '+to+' complete!')
	
	def __init__(self):
		self.install_and_import('colorama')
		self.output = term_layout.output()
		self.first = False
