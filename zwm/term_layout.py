#!/usr/bin/python

from PIL import Image, ImageOps

class output:
	__term_size = (80, 20)
	__spinner_stages = ['/', '-', '\\', '|']
	
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
			
	def install_module(self, package):
		import pip
		pip.main(['install', package])
		
	def import_module(self, package):
		globals()[package] = importlib.import_module(package)
			
	def split_by_n(self, t, n, wordwrap):
		import textwrap
		f = []
		
		if wordwrap == True:
			for x in t.split('\n'):
				f += textwrap.wrap(x, n)
		else:
			for x in t.split('split_me'):
				f.append(x)
		
		return f
			
	def multiline(self, message, color, wordwrap):
		r = ''
		b = self.split_by_n(message, (self.__term_size[0] - 10), wordwrap)
		c = 1
		for k, v in enumerate(b):
			if k + 1 == len(b):
				s = '└'
			else:
				s = '├'
			
			ln = str(c).zfill(3)
			if c % 3 != True:
				ln = ' v '
			if c == len(b):
				ln = str(c).zfill(3)
				
			if c != 1:
				r += colorama.Style.DIM+ln+colorama.Style.RESET_ALL+' ⥅ ' + ' '+s+' ' + color + v + colorama.Style.RESET_ALL + '\n'
			else:
				r += color + v + colorama.Style.RESET_ALL + '\n'
			c += 1
			if c > 999:
				self.error('Line limit reached!')
				
				return 0, ''
			
		return len(b), r[:-1]
			
	def display(self, message, symbol, text_color, back_color, progress=False, **kwargs):
		import sys
		
		try:
			t = kwargs['word_wrap']
		except:
			kwargs['word_wrap'] = True
		
		if progress == True:
			symbol = ' '+self.__spinner_stages[self.spinner_stage]+' '
			self.spinner_stage += 1
			if self.spinner_stage > len(self.__spinner_stages) - 1:
				self.spinner_stage = 0
		else:
			symbol = ' '+symbol+' '
		pointer = '─'
		
		b, message = self.multiline(message, text_color, kwargs['word_wrap'])
		
		if b > 1:
			pointer = '┬'
		
		if b > 1:
			symbol = '001' + symbol
		else:
			symbol = ' ↮ ' + symbol
		
		if self.nexted == False:
			for x in range(0, self.last):
				sys.stdout.write('\033[F')
				sys.stdout.flush()
		sys.stdout.write('\r' + back_color + colorama.Fore.WHITE + colorama.Style.BRIGHT + symbol + colorama.Style.RESET_ALL + ' '+pointer+' ' + colorama.Style.NORMAL + message + colorama.Style.RESET_ALL)
		sys.stdout.flush()
		
		self.last = b - 1
		self.nexted = False
	
	def error(self, message, n=True):
		self.display(message, 'X', colorama.Fore.RED, colorama.Back.RED)
		if n == True:
			self.next()
		
	def info(self, message, n=True):
		self.display(message, 'i', colorama.Fore.CYAN, colorama.Back.CYAN)
		if n == True:
			self.next()
		
	def warning(self, message, n=True):
		self.display(message, '!', colorama.Fore.YELLOW, colorama.Back.YELLOW)
		if n == True:
			self.next()
		
	def success(self, message, n=True):
		self.display(message, '✓', colorama.Fore.GREEN, colorama.Back.GREEN)
		if n == True:
			self.next()
		
	def progress(self, message, n=True):
		self.display(message, '•', colorama.Style.DIM+colorama.Fore.WHITE, colorama.Style.DIM+colorama.Back.WHITE, True)
		if n == True:
			self.next()
		
	def invert(self, i):
		if i == 0:
			i = 1
		else:
			i = 0
		
		return i	
			
	def slice_per(self, source, step):
		return [source[i::step] for i in range(step)]
			
	def image(self, image, n=True):
		import math
		from sys import platform
		import os
		
		if platform == "linux" or platform == "linux2":
		#if True == False:
			import subprocess
			
			message = subprocess.check_output([os.path.dirname(os.path.realpath(__file__))+os.sep+'c'+os.sep+'tiv', os.path.abspath(image), '-w', str(self.__term_size[0]/1.25), '-h', str(self.__term_size[1])]).decode()[:-1].replace('\n', 'split_me')
		else:
			img = Image.open(image).convert('RGB')
			
			multi = 1.9
			
			basewidth = math.floor(self.__term_size[0]*multi)
			wpercent = (basewidth/float(img.size[0]))
			hsize = int((float(img.size[1])*float(wpercent)))
			img = img.resize((math.floor(basewidth),hsize), Image.ANTIALIAS)
			
			img = img.rotate(90, expand=True).transpose(Image.FLIP_TOP_BOTTOM)
			
			#basewidth = math.floor(self.__term_size[0] / 2.05)
			basewidth = math.floor(self.__term_size[0]*multi)
			wpercent = (basewidth/float(img.size[0]))
			hsize = int((float(img.size[1])*float(wpercent)))
			img = img.resize((math.floor(basewidth),hsize), Image.ANTIALIAS)
			
			pixels = img.load()
			width, height = img.size
			
			message_a = []
			for x in range(math.floor(width / 8)):
				t = ''
				for y in range(math.floor(height / 4)):
					cpixel = []
					
					c = [[], [], []]
					b = [[], [], []]
					#a = [[], [], []]
					l = [255, 255, 255]
					h = [0, 0, 0]
					for v in range(0, 8):
						for k in range(0, 4):
							pixel = pixels[(x * 8)+v, (y * 4)+k]
							cpixel.append(pixel)
							if v < 4:
								for z in range(0, 3):
									c[z].append(pixel[z])
							else:
								for z in range(0, 3):
									b[z].append(pixel[z])
								
							for z in range(0, 3):
									#a[z].append(pixel[z])
									if pixel[z] < l[z]:
										l[z] = pixel[z]
									elif pixel[z] > h[z]:
										h[z] = pixel[z]
					
					p = []
					for z in range(0, 3):
						c[z] = math.floor(sum(c[z]) / float(len(c[z])))
						b[z] = math.floor(sum(b[z]) / float(len(b[z])))
						#a[z] = math.floor(sum(a[z]) / float(len(a[z])))
						
						f = l[z] - h[z]
						if f < 0:
							f = ~f
							
						p.append(f)
						
					'''
					i = sorted(zip(p, range(0, len(p))), reverse=True)[:1]
					channel = i[0][1]
					crange = i[0][0]
					
					#copybitmap = []
					bitmap = 0
					for v in range(0, 8):
						for k in range(0, 4):
							bitmap = bitmap << 1
							pixel = pixels[(x * 8)+v, (y * 4)+k]
							if (pixel[channel] & 255) > (crange / 2):
								#copybitmap.append(1)
								bitmap = (bitmap | 1)
					'''
					'''
					copybitmap_str_o = ''
					for v in copybitmap:
						copybitmap_str_o += str(v)
					copybitmap_str = self.slice_per(copybitmap_str_o, 8)
					print('\n'.join(copybitmap_str))
					print(crange)
					'''
					'''
					copybitmap_str_o = ''
					for v in bin(bitmap).replace('0b', ''):
						copybitmap_str_o += str(self.invert(v))
					#copybitmap_str_o = copybitmap_str_o[::-1]
					bitmap = int(copybitmap_str_o, 2)
					print(hex(bitmap))
					#bitmap = math.floor(int(hex(int(copybitmap_str_o, 2) & 0xffffffff).replace('0x', '')[::-1].ljust(8, '0'), 16) - 0x0000ffff)
					#bitmap = math.floor(int(hex(int(copybitmap_str_o, 2) & 0xffffffff).replace('0x', '').ljust(8, '0'), 16) - 0x0000ffff)
					#if bitmap < 0:
					#	bitmap = ~ bitmap
					#bitmap = int(hex(bitmap).replace('0x', '')[::-1], 16)
					bestDiff = 0xffffffff
					invert = False
					for i, l in self.bitmaps.items():
						diff = (i ^ bitmap).bit_length()
						if (diff < bestDiff):
							character = l
							bestDiff = diff
							#invert = False
							invert = True
						diff = ((~ i) ^ bitmap).bit_length()
						if (diff < bestDiff):
							character = l
							bestDiff = diff
							#invert = True
							invert = False
					'''
					
					symbol = '\u2580'
					
					'''
					dither = self.dither[3]
					
					background_color = self.colorbacktuples[str(tuple([self.invert(round(x/255)) for x in cpixel]))]
					
					if str(tuple([(round(x/127.5)) for x in cpixel])) in self.colortuples:
						dither = self.dither[2]
					elif str(tuple([(round(x/85)) for x in cpixel])) in self.colortuples:
						dither = self.dither[1]
					elif str(tuple([(round(x/63.75)) for x in cpixel])) in self.colortuples:
						dither = self.dither[0]
					
					color = self.colortuples[str(tuple([(round(x/255)) for x in cpixel]))]
					brightness = self.brightness[round((sum(cpixel) / 3) / 15.9375)]
					#brightness = self.brightness[2]
					t += (background_color + color + brightness + dither)
					'''
					
					#background_color = self.colorbacktuples[str(tuple([(round(x/255)) for x in cpixel[1]]))]
					#color = self.colortuples[str(tuple([(round(x/255)) for x in cpixel]))]
					#brightness = self.brightness_simp[round((sum(cpixel) / 3) / 127.5)]
					
					#if invert == True:
					#	temp = c
					#	c = b
					#	b = temp
					
					#background_color = '\033[48;2;'+str(b[0])+';'+str(b[1])+';'+str(b[2])+'m'
					#color = '\033[38;2;'+str(c[0])+';'+str(c[1])+';'+str(c[2])+'m'
					#brightness = ''
					#else:
					background_color = self.colorbacktuples[str(tuple([(round(x/255)) for x in b]))]
					color = self.colortuples[str(tuple([(round(x/255)) for x in c]))]
					brightness = self.brightness_simp[round((sum(b) / 3) / 127.5)]
					t += background_color + color + brightness + symbol + colorama.Style.RESET_ALL
					
				message_a.append(t)
			
			message = 'split_me'.join(message_a)
		
		self.display(message, '🖌', colorama.Fore.BLUE, colorama.Back.BLUE, word_wrap = False)
		if n == True:
			self.next()
		
	def question(self, message, info=''):
		self.display(message, '?', colorama.Fore.MAGENTA, colorama.Back.MAGENTA)
		self.next()
		
		if len(info) > 0:
			info += ']: '
			info = '[' + info
		
		return input("    ⇱  ← "+colorama.Style.DIM+info+colorama.Style.RESET_ALL)
			
	def next(self):
		import sys
		sys.stdout.write('\n')
		sys.stdout.flush()
		self.nexted = True
		
		self.__term_size = shutil.get_terminal_size(self.__term_size)
			
	def __init__(self):
		self.last = 0
		self.nexted = True
		self.spinner_stage = 0
		
		self.install_and_import('colorama')
		self.install_and_import('shutil')

		colorama.init()
		
		self.__term_size = shutil.get_terminal_size(self.__term_size)
		
		'''
		colorama.Fore.BLACK   + '█' + colorama.Style.RESET_ALL,
		colorama.Fore.BLACK   + '▓' + colorama.Style.RESET_ALL,
		colorama.Fore.BLACK   + '▒' + colorama.Style.RESET_ALL,
		colorama.Fore.BLACK   + '░' + colorama.Style.RESET_ALL,
		'''
		'''
		self.brightness = [
			colorama.Style.DIM    + '░' + colorama.Style.RESET_ALL,
			colorama.Style.DIM    + '▒' + colorama.Style.RESET_ALL,
			colorama.Style.DIM    + '▓' + colorama.Style.RESET_ALL,
			colorama.Style.NORMAL + '▒' + colorama.Style.RESET_ALL,
			
			colorama.Style.NORMAL + '▓' + colorama.Style.RESET_ALL,
			colorama.Style.BRIGHT + '▓' + colorama.Style.RESET_ALL,
			colorama.Style.NORMAL + '█' + colorama.Style.RESET_ALL,
			colorama.Style.BRIGHT + '█' + colorama.Style.RESET_ALL
		]
		'''
		
		self.brightness_simp = [
			colorama.Style.DIM,
			colorama.Style.NORMAL,
			colorama.Fore.WHITE,
		]
		
		'''
		self.brightness = [
			colorama.Fore.BLACK + colorama.Back.BLACK,
			colorama.Fore.BLACK + colorama.Back.BLACK,
			colorama.Fore.BLACK,
			colorama.Fore.BLACK,
			colorama.Style.DIM,
			colorama.Style.DIM,
			colorama.Style.DIM,
			colorama.Style.NORMAL,
			colorama.Style.NORMAL,
			colorama.Style.NORMAL,
			colorama.Style.BRIGHT,
			colorama.Style.BRIGHT,
			colorama.Style.BRIGHT,
			colorama.Fore.WHITE,
			colorama.Fore.WHITE,
			colorama.Fore.WHITE + colorama.Back.WHITE,
			colorama.Fore.WHITE + colorama.Back.WHITE,
		]
		
		self.dither = [
			'░' + colorama.Style.RESET_ALL,
			'▒' + colorama.Style.RESET_ALL,
			'▓' + colorama.Style.RESET_ALL,
			'█' + colorama.Style.RESET_ALL,
		]
		'''
		
		self.colortuples = {
			'(0, 0, 0)':colorama.Fore.BLACK,
			'(0, 0, 1)':colorama.Fore.BLUE,
			'(0, 1, 1)':colorama.Fore.CYAN,
			'(1, 1, 1)':colorama.Fore.WHITE,
			'(1, 0, 0)':colorama.Fore.RED,
			'(1, 1, 0)':colorama.Fore.YELLOW,
			'(1, 0, 1)':colorama.Fore.MAGENTA,
			'(0, 1, 0)':colorama.Fore.GREEN,
		}
		
		self.colorbacktuples = {
			'(0, 0, 0)':colorama.Back.BLACK,
			'(0, 0, 1)':colorama.Back.BLUE,
			'(0, 1, 1)':colorama.Back.CYAN,
			'(1, 1, 1)':colorama.Back.WHITE,
			'(1, 0, 0)':colorama.Back.RED,
			'(1, 1, 0)':colorama.Back.YELLOW,
			'(1, 0, 1)':colorama.Back.MAGENTA,
			'(0, 1, 0)':colorama.Back.GREEN,
		}
		
		'''
		self.bitmaps = {
			0x00000000:'\u00a0',

			0x0000000f:'\u2581', # lower 1/8
			0x000000ff:'\u2582', # lower 1/4
			0x00000fff:'\u2583',
			0x0000ffff:'\u2584', # lower 1/2
			0x000fffff:'\u2585',
			0x00ffffff:'\u2586', # lower 3/4
			0x0fffffff:'\u2587',
			#0xffffffff:'\u2588',
			#0xffff0000:'\u2580',

			0xeeeeeeee:'\u258a', # left 3/4
			0xcccccccc:'\u258c', # left 1/2
			0x88888888:'\u258e', # left 1/4

			0x0000cccc:'\u2596', # quadrant lower left
			0x00003333:'\u2597', # quadrant lower right
			0xcccc0000:'\u2598', # quadrant upper left
			0xcccc3333:'\u259a', # diagonal 1/2
			0x33330000:'\u259d', # quadrant upper right

			0x000ff000:'\u2501', # Heavy horizontal
			0x66666666:'\u2503', # Heavy vertical

			0x00077666:'\u250f', # Heavy down and right
			0x000ee666:'\u2513', # Heavy down and left
			0x66677000:'\u2517', # Heavy up and right
			0x666ee000:'\u251b', # Heavy up and left

			0x66677666:'\u2523', # Heavy vertical and right
			0x666ee666:'\u252b', # Heavy vertical and left
			0x000ff666:'\u2533', # Heavy down and horizontal
			0x666ff000:'\u253b', # Heavy up and horizontal
			0x666ff666:'\u254b', # Heavy cross

			0x000cc000:'\u2578', # Bold horizontal left
			0x00066000:'\u2579', # Bold horizontal up
			0x00033000:'\u257a', # Bold horizontal right
			0x00066000:'\u257b', # Bold horizontal down

			0x06600660:'\u254f', # Heavy double dash vertical

			0x000f0000:'\u2500', # Light horizontal
			0x0000f000:'\u2500', #
			0x44444444:'\u2502', # Light vertical
			0x22222222:'\u2502',

			0x000e0000:'\u2574', # light left
			0x0000e000:'\u2574', # light left
			0x44440000:'\u2575', # light up
			0x22220000:'\u2575', # light up
			0x00030000:'\u2576', # light right
			0x00003000:'\u2576', # light right
			0x00004444:'\u2575', # light down
			0x00002222:'\u2575', # light down
			
			0x44444444:'\u23a2', # [ extension
			0x22222222:'\u23a5', # ] extension

			0x0f000000:'\u23ba', # Horizontal scanline 1
			0x00f00000:'\u23bb', # Horizontal scanline 3
			0x00000f00:'\u23bc', # Horizontal scanline 7
			0x000000f0:'\u23bd', # Horizontal scanline 9

			0x00066000:'\u25aa', # Black small square
		}
		'''
		
		self.reset_orig = colorama.Style.RESET_ALL
		colorama.Style.RESET_ALL = self.reset_orig
		
	
# TESTING MATERIAL

#if __name__ == '__main__':
	#import subprocess
	#import sys
	#import uuid
	#test = 'Hello world!\nHello World!\nHello World!'
	
	#term = output()
	#term.image('./test/dictator.jpg')
	#term.image('./test/detail.png')
	#term.image('./test/test.jpg')
	#term.image('./test/makism.png')
	#term.image('./test/table.jpg')
	#term.image('./test/retarded_jeremy.jpeg')
	#term.image('./test/bigmare.jpg')
	
	'''
	term.error(test)
	term.info(test)
	term.warning(test)
	term.progress(test)
	term.success(test)
	
	term.success(term.question(test, 'Y/N'))
	
	
	for x in range(0, 512):
		term.progress(str(uuid.uuid4())+'\n'+str(uuid.uuid4())+' '+str(x+1), False)
	term.next()
	for x in range(0, 128):
		term.progress(str(uuid.uuid4())+'\n'+str(uuid.uuid4()), False)
	term.next()
	term.error('Whoops! An error occurred!')
	for x in range(0, 128):
		term.progress(str(uuid.uuid4())+'\n'+str(uuid.uuid4()), False)
	term.next()
	#term.info(test)
	'''

	'''
	import builtins

	def _print(message, **kwargs):
		try:
			t = kwargs['end']
		except:
			term.progress(message)
		else:
			term.progress(message+kwargs['end'], False)
	
	def _input(message):
		return term.question(message)
	
	builtins.print = _print
	builtins.input = _input
	'''
	
	#term.info(subprocess.check_output(sys.argv[1:]).decode())

