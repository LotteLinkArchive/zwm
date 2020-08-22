import termios, fcntl, sys, os
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))
import term_layout
import subprocess
import time
import math
import uuid
import threading
import multiprocessing
import shutil
import textwrap
import random
import datetime
import psutil
import re

class Modules:
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
		
	def __init__(self):
		self.install_and_import('colorama')
		self.install_and_import('curtsies')
		self.install_and_import('pyparsing')
		self.install_and_import('pexpect')
		self.install_and_import('pyte')

class Window:
	__global_history = ['']

	# PUBLIC FUNCTIONS
	
	def clearlines(self):
		del self.__lines[:]
	
	def addline(self, line):
		r = []
		for x in line.split('\n'):
			r += textwrap.wrap(x, (self.__size[0] - 2))
			
		for x in r:
			self.__addline_preformatted(x)
			
	def addline_raw(self, line):
		r = line.split('\n')
			
		for x in r:
			self.__addline_preformatted(x)
		
	def stdin(self, byte):
		if self.__inputting == 0xFF:
			if byte.decode() == '\x7f':
				self.__input = self.__input[:-1]
			elif byte.decode() == '\n' or byte.decode() == '\x0d':
				self.__inputting = 0x88
			elif byte.decode() == '\x10':
				self.__history_index += 1
				if (self.__history_index) > len(self.__global_history) - 1:
					self.__history_index = len(self.__global_history) - 1

				self.__input = self.__global_history[self.__history_index]
			elif byte.decode() == '\x0e':
				self.__history_index -= 1
				if (self.__history_index) < 0:
					self.__history_index = 0

				self.__input = self.__global_history[self.__history_index]
			else:
				self.__input += byte.decode()
			
			self.footer('>>> '+self.__input)
			self.__draw_text()
			
	def footer(self, message):
		self.__footer = message
			
	def getinput(self):
		self.__footer_previous = self.__footer
		self.footer('>>> ')
		self.__draw_text()
		
		self.__input = ''
		self.__inputting = 0xFF
		
		while self.__inputting == 0xFF:
			time.sleep(0.25)
		
		self.footer(self.__footer_previous)
		self.__inputting = 0x00
		self.__draw_text()

		self.__global_history.append(self.__input)

		return self.__input
			
	def setline(self, line, content):
		self.__lines[line] = content
		self.__draw_text()
			
	def resize(self, size):
		self.__size = size
		self.__shepherd.draw()
		
	def move(self, position):
		self.__position = position
		self.__shepherd.draw()
		
	def getpos(self):
		return self.__position
		
	def getsize(self):
		return self.__size
		
	def public_redraw(self, force=False, wait=True):
		if force == True:
			temp_redrawable = self.redrawable
			self.redrawable = True
		
		self.__draw(True, wait)
		
		if force == True:
			self.redrawable = temp_redrawable
		
	def remove(self):
		self.redrawable = False
		self.__shepherd.unregister(self.uuid)
		self.__shepherd.draw()
	
	# PRIVATE FUNCTIONS
	
	def __addline_preformatted(self, line):
		while len(self.__lines) > (self.__size[1] - 3):
			del self.__lines[0]
			
		self.__lines.append(line)
		#self.__draw_text()
	
	def __escape_ansi(self, line):
		ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
		return ansi_escape.sub('', line)
	
	def __wait(self, repeat = 2):
		# O B S O L E T E
		
		pass
	
	def __io_wait(self, repeat = 4):
		for t in range(0, repeat):
			t = str(uuid.uuid4()) + str(t)
	
	def __draw_text(self):
		if self.redrawable == True:
			for k, v in enumerate(self.__lines):
				self.sui.write('\033['+str(self.__position[1]+k)+';'+str(self.__position[0]+1)+'H'+self.__background+self.__foreground+(' ' * (self.__size[0] - 2)))
				self.sui.write('\033['+str(self.__position[1]+k)+';'+str(self.__position[0]+1)+'H'+self.__background+self.__foreground+v+self.__background+self.__foreground)
			self.sui.flush()
			k = self.__size[1] - 2
			v = self.__footer
			self.sui.write('\033['+str(self.__position[1]+k)+';'+str(self.__position[0]+1)+'H'+self.__footerback+self.__footerfore+(' ' * (self.__size[0] - 2)))
			self.sui.write('\033['+str(self.__position[1]+k)+';'+str(self.__position[0]+1)+'H'+self.__footerback+self.__footerfore+v+self.__footerback+self.__footerfore)
			self.sui.flush()
			
	def __auto_redraw_text_thread(self):
		while True:
			if self.__redraw_last_compare != self.__lines + [self.__footer] and self.redrawable:
				self.__draw_text()
				
				self.__redraw_last_compare = self.__lines + [self.__footer]
			
			time.sleep(0.015)
	
	def __draw(self, flash=False, wait=True):
		if self.redrawable == True:
			self.sui.write('\033['+str(self.__position[1])+';'+str(self.__position[0])+'H'+self.__background+' ')
			self.sui.flush()
			self.__wait()
			
			for y in range((0 - 1), self.__size[1]):
				for x in range(0, self.__size[0]):
					background = self.__background
					foreground = self.__foreground
					symbol = ' '
					
					y_p = self.__position[1] + y
					x_p = self.__position[0] + x
					
					# DECORATIONS
					
					if y == (0 - 1):
						background = self.__titlebackg
						foreground = self.__titleforec
						symbol = self.__top
					if y == (self.__size[1] - 1):
						symbol = self.__bottom
					if x == 0 or x == (self.__size[0] - 1):
						if y != (0 - 1):
							symbol = self.__sides	
					if x == (self.__size[0] - 1) and y == (self.__size[1] - 1):
						symbol = self.__bottomright
					if x == 0 and y == (self.__size[1] - 1):
						symbol = self.__bottomleft
					if x == 0 and y == (0 - 1):
						symbol = self.__topleft
					if x == (self.__size[0] - 1) and y == (0 - 1):
						symbol = self.__topright
					
					self.sui.write('\033['+str(y_p)+';'+str(x_p)+'H'+background+foreground+symbol)
					
					self.sui.flush()
					self.__wait()
					
				if y == (0 - 1):
					if flash == False:
						self.sui.write('\033['+str(self.__position[1]-1)+';'+str(self.__position[0])+'H'+background+foreground+self.__topleft_expand+self.uuid)
						self.sui.flush()
					else:
						self.sui.write('\033['+str(self.__position[1]-1)+';'+str(self.__position[0])+'H'+background+foreground+self.__topleft_expand+self.__titleflash+self.uuid+foreground)
						self.sui.flush()
						if wait == True:
							time.sleep(0.1)
						self.sui.write('\033['+str(self.__position[1]-1)+';'+str(self.__position[0])+'H'+background+foreground+self.__topleft_expand+self.uuid)
						self.sui.flush()
					self.__wait()
					
			self.__draw_text()
	
	def __init__(self, shepherd, size, position, title='Untitled Window'):
		self.__background = colorama.Back.BLACK
		self.__foreground = colorama.Fore.WHITE
		self.__titlebackg = colorama.Back.WHITE
		self.__titleforec = colorama.Fore.BLACK
		self.__titleflash = colorama.Fore.RED
		self.__footerback = colorama.Back.WHITE
		self.__footerfore = colorama.Fore.BLACK
		
		self.pbackground = self.__background
		self.pforeground = self.__foreground
		self.ptitlebackg = self.__titlebackg
		self.ptitleforec = self.__titleforec
		self.ptitleflash = self.__titleflash
		self.pfooterback = self.__footerback
		self.pfooterfore = self.__footerfore
		
		self.sui = shepherd.sui
		
		self.__shepherd = shepherd
		self.__size = size
		self.__position = position
		self.__footer = '[ NO FOOTER ]'
		self.__input = ''
		self.__inputting = 0x00
		self.__history_index = 0
		
		self.__lines = []
		self.redrawable = True
		
		self.__sides = '│'
		self.__top = '─'
		self.__bottom = '─'
		self.__topleft = '╭'
		self.__topright = '╮'
		self.__bottomleft = '╰'
		self.__bottomright = '╯'
		self.__topleft_expand = self.__topleft + self.__top + '⚡' + self.__top
		
		calc_uuid = str(uuid.uuid4())
		calc_uuid = calc_uuid[:(0 - math.floor(len(calc_uuid) / 2))]
		
		if len(title) < 1:
			self.uuid = calc_uuid
		else:
			self.uuid = title+':'+calc_uuid
		
		self.__shepherd.register(self)
		
		self.__draw()
		
		self.__redraw_last_compare = self.__lines + [self.__footer]
		self.__redraw_thread = threading.Thread(target=self.__auto_redraw_text_thread)
		self.__redraw_thread.daemon = True
		self.__redraw_thread.start()

class AllWindowList(Window):
	def __init__(self, shepherd):
		global_size = shepherd.size()
		global_size = (48, global_size[1]-10)
		
		Window.__init__(self, shepherd, global_size, (3, 3), 'Window List')
		
class HelpWindow(Window):
	def __init__(self, shepherd, position):
		global_size = (48, 15)
		
		Window.__init__(self, shepherd, global_size, position, 'Help Window')
		
		self.addline('TAB    - Select a different window')
		self.addline('h      - Get this help menu')
		self.addline('q      - Quit desktop')
		self.addline('w      - Window list')
		self.addline('n      - New terminal window')
		self.addline('x      - Close window')
		self.addline('r      - Enable resize mode')
		self.addline('p      - Enable reposition mode')
		self.addline('ARROWS - Manipulate window in R/P modes')
		self.addline('z      - Exit R/P modes')
		self.addline('c      - Allow window to capture input')
		self.addline('CTRL+E - Exit window capture mode')
		self.addline('CTRL+/ - Terminate terminal application')
		
		self.footer('Copyright (C)  2018')
		
		self.public_redraw(False, False)
		
class CommandLineWindow(Window):
	# PUBLIC
	
	def stdin(self, byte):
		if self.__active == True:
			if byte.decode() == '\x1f':
				self.__active = False
			else:
				self.child.send(byte.decode())
		else:
			Window.stdin(self, byte)
		
	def resize(self, size):
		self.lock = True
		
		Window.resize(self, size)
		
		self.__size = size
		self.__shepherd.draw()
			
		self.lock = False
		
	# PRIVATE
		
	def __io_wait(self, repeat = 4):
		for t in range(0, repeat):
			t = str(uuid.uuid4()) + str(t)
			
	def __deactivate(self):
		time.sleep(0.025)
		self.__active = False
			
	def hex_to_rgb(self, value):
		value = value.lstrip('#')
		lv = len(value)
		return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

	def rgb_to_hex(self, red, green, blue):
		return '#%02x%02x%02x' % (red, green, blue)

	def __hex_col_to_ansi(self, h, bg=False):
		escape = '\x1b['

		if bg == False:
			mode = '38'
		else:
			mode = '48'
		
		ret = escape + mode + ';2;'

		rgb = self.hex_to_rgb(h)
		for x in rgb:
			ret += (str(x) + ';')

		return (ret[:-1] + 'm')

	def __output_thread(self):
		while self.__active:
			if self.lock != True:
				try:
					try:
						output = self.child.read_nonblocking(((self.__size[1] - 2) * (self.__size[0] - 2)) * 32, None).decode()
					except:
						self.__active = False
						
					if self.__buffer != output:
						self.__buffer = output
							
						self.__stream.feed(output)
						
						self.clearlines()
						
						for k, v in self.__screen.buffer.items():
							dispc = [' '] * (self.__size[0] - 2)
							dispr = [' '] * (self.__size[0] - 2)

							for m, b in v.items():
								try:
									fg = self.__foreground_colors[b[1]]
								except:
									fg = self.__hex_col_to_ansi(b[1], False)
								try:
									bg = self.__background_colors[b[2]]
								except:
									bg = self.__hex_col_to_ansi(b[2], True)
								
								style = colorama.Style.NORMAL
								if b[3] == True:
									style = colorama.Style.BRIGHT
								if b[4] == True:
									style = colorama.Style.DIM
								
								c = b[0]
								
								dispc[m] = fg + bg + style + c + self.pbackground + self.pforeground
								dispr[m] = c
								
							if k == self.__screen.cursor.y:
								dispc[self.__screen.cursor.x] = colorama.Back.WHITE + colorama.Fore.BLACK + dispr[self.__screen.cursor.x] + self.pbackground + self.pforeground
								
							dispc = ''.join(dispc)
							self.addline_raw(self.pbackground + self.pforeground + dispc)
						
						if self.child.isalive() != True:
							self.thread_d = threading.Thread(target=self.__deactivate)
							self.thread_d.daemon = True
							self.thread_d.start()
				except:
					pass
	
	def __code(self):
		command = ''
		while 'exit' not in command:
			command = self.getinput()

			self.clearlines()
			self.__buffer = ''
			if 'exit' not in command and command.startswith('cd ') != True:
				shell_cmd = command
				self.child = pexpect.spawn('/bin/bash', ['-c', shell_cmd])
				self.child.setwinsize(self.__size[1] - 2,self.__size[0] - 2)
				self.__active = True
				
				self.__screen = pyte.Screen(self.__size[0] - 2, self.__size[1] - 2)
				self.__stream = pyte.Stream(self.__screen)
				
				self.thread_o = threading.Thread(target=self.__output_thread)
				self.thread_o.daemon = True
				self.thread_o.start()
				
				while self.__active == True:
					time.sleep(0.025)
				
				self.__screen.reset()
				self.clearlines()
			elif 'cd ' in command:
				location = command.replace('cd ', '').split(';')[0]
				if location == '~':
					location = os.getenv("HOME")
				os.chdir(os.path.abspath(location))	
			
			time.sleep(0.025)
			
		self.remove()
	
	def __init__(self, shepherd, size, position):
		self.lock = False
		self.__size = size
		self.__shepherd = shepherd
		Window.__init__(self, shepherd, size, position, 'Terminal')
		
		self.pbackground = colorama.Back.BLACK
		self.pforeground = colorama.Fore.WHITE
		
		self.__background_colors = {
			'black':colorama.Back.BLACK,
			'blue':colorama.Back.BLUE,
			'green':colorama.Back.GREEN,
			'cyan':colorama.Back.CYAN,
			'red':colorama.Back.RED,
			'magenta':colorama.Back.MAGENTA,
			'brown':colorama.Back.YELLOW,
			'white':colorama.Back.WHITE,
			'default':self.pbackground
		}
		
		self.__foreground_colors = {
			'black':colorama.Fore.BLACK,
			'blue':colorama.Fore.BLUE,
			'green':colorama.Fore.GREEN,
			'cyan':colorama.Fore.CYAN,
			'red':colorama.Fore.RED,
			'magenta':colorama.Fore.MAGENTA,
			'brown':colorama.Fore.YELLOW,
			'white':colorama.Fore.WHITE,
			'default':self.pforeground
		}
		
		self.__active = False
		self.__buffer = ''
		
		self.thread = threading.Thread(target=self.__code)
		self.thread.daemon = True
		self.thread.start()

class Shepherd:
	__term_size = (80, 20)
	__windows = {}
		
	def window_list(self):
		window_list = AllWindowList(self)
		window_list.addline('\n'.join(self.__windows.keys()))
		
	def size(self):
		return self.__term_size
		
	def remove(self, uuid):
		self.__windows[uuid]['instance'].remove()
		try:
			self.iterateselect()
		except:
			pass
		
	def register(self, window):
		for k, v in self.__windows.items():
			v['instance'].redrawable = False
		
		self.__windows[window.uuid] = {
			'instance':window
		}
		
	def unregister(self, uuid):
		del self.__windows[uuid]
		
	def registry(self):
		return self.__windows
	
	def select(self, uuid, wait=True):
		for k, v in self.__windows.items():
			v['instance'].redrawable = False
		
		self.__windows[uuid]['instance'].redrawable = True
		self.__windows[uuid]['instance'].public_redraw(False, wait)
		
	def selected(self):
		for k, v in self.__windows.items():
			if v['instance'].redrawable == True:
				return k
		
	def iterateselect(self):
		try:
			copy = list(self.__windows)
			copy.remove(self.selected())
			self.select(random.choice(copy))
		except:
			self.select(random.choice(list(self.__windows)))
		
	def terminate(self, clear = False):
		#termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)
		#fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)
		
		if clear == True:
			self.sui.write('\33[2J\033[0;0H')
			self.sui.flush()
		
	def wait(self, repeat):
		#for x in range(0, repeat):
		#	t = uuid.uuid4()
		pass
		
	def __invert(self, i):
		return not i
		
	def draw(self):
		selected = self.selected()
		self.blacken()
		if self.optimize == False:
			self.set_background(self.background)
		
		for k, v in self.__windows.items():
			v['instance'].public_redraw(self.__invert(self.optimize), False)
		
		self.toolbar()
		
		try:
			self.select(selected, False)
		except:
			pass
		
	def blacken(self):
		r = ''
		for y in range(0, self.__term_size[1]+1):
			if self.optimize != True:
				for x in range(0, (self.__term_size[0]+1)-(self.padding + self.display_len)):
					r += '\033['+str(y)+';'+str(x)+'H'+colorama.Back.BLACK+' '
				for x in range((self.padding + self.display_len)+1, (self.__term_size[0]+1)):
					r += '\033['+str(y)+';'+str(x)+'H'+colorama.Back.BLACK+' '
			else:
				for x in range(0, (self.__term_size[0]+1)):
					r += '\033['+str(y)+';'+str(x)+'H'+colorama.Back.BLACK+' '
		
		self.sui.write(r)
		if self.optimize == True:
			self.sui.flush()
				 
	def toolbar(self):
		background = colorama.Back.WHITE
		foreground = colorama.Fore.BLACK
		
		dtstring = datetime.datetime.now().strftime("%I:%M:%S %p on %B %d, %Y")
		
		y = self.__term_size[1]
		for x in range(0, self.__term_size[0]+1):
			#self.sui.write('\033['+str(y-1)+';'+str(x)+'H'+background+' ')
			self.sui.write('\033['+str(y)+';'+str(x)+'H'+background+' ')
		
		#self.sui.write('\033['+str(y-1)+';1H'+background+foreground+' Memory Info: '+str(psutil.virtual_memory()))
		res = str(self.__term_size[0])+'x'+str(self.__term_size[1])
		self.sui.write('\033['+str(y)+';1H'+background+foreground+' '+dtstring+' - Press H for help - Copyright (C) /naphtha/naphtha 2018 - '+str(psutil.cpu_percent())+'% TOTAL CPU - '+str(psutil.virtual_memory()[2])+'% TOTAL MEMUSG - '+str(self.process.memory_info().rss)+'B PYTHON MEMUSG - '+res)
		self.sui.flush()
		
	def set_background(self, image):
		if len(self.background_buffer) < 1:
			message = subprocess.check_output([os.path.dirname(os.path.realpath(__file__))+os.sep+'c'+os.sep+'tiv', os.path.abspath(image), '-w', str(self.__term_size[0]), '-h', str(self.__term_size[1])]).decode()[:-1]
			self.background_buffer = message
		else:
			message = self.background_buffer
		r = ''
		for k, x in enumerate(message.split('\n')):
			if k == 0:
				ESC = pyparsing.Literal('\x1b')
				integer = pyparsing.Word(pyparsing.nums)
				escapeSeq = pyparsing.Combine(ESC + '[' + pyparsing.Optional(pyparsing.delimitedList(integer,';')) + 
								pyparsing.oneOf(list(pyparsing.alphas)))

				nonAnsiString = lambda s : pyparsing.Suppress(escapeSeq).transformString(s)

				unColorString = nonAnsiString(x)
				self.display_len = len(unColorString)
			
				self.padding = round((self.__term_size[0] / 2) - (self.display_len / 2))
			
			r += (colorama.Back.BLACK + ' ' * self.padding + x + os.linesep)
		
		self.sui.write('\033[0;0H'+r)
		
		self.sui.flush()
		
	def mainloop(self):
		while self.loop == True:
			self.toolbar()
			time.sleep(0.25)
		
	def __init__(self, sui, background):
		self.display_len = 0
		self.padding = 0
		self.background = background
		self.background_buffer = ''
		self.sui = sui
		self.loop = True
		self.optimize = False
		self.process = psutil.Process(os.getpid())
		
		Modules()
		
		colorama.init()
		
		self.__term_size = self.sui.size()

		if self.__term_size[0] < 170 or self.__term_size[0] < 46:
			raise SystemExit('Your terminal size is too small! It must be above 170 characters by 46 characters. Your terminal emulator needs to, like, get woke pronto!')

		'''
		self.fd = sys.stdin.fileno()

		self.oldterm = termios.tcgetattr(self.fd)
		self.newattr = termios.tcgetattr(self.fd)
		self.newattr[3] = self.newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(self.fd, termios.TCSANOW, self.newattr)

		self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
		fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)
		'''
		
		self.sui.write('\33[2J')
		self.sui.flush()
		
		self.draw()
		
class WindowTypeFactory:
	def SpawnTerminal(self):
		self.__windows.append(CommandLineWindow(self.__shepherd, (100, 25), (3 + self.__position_offset(), 4 + self.__position_offset())))
	
	def SpawnHelp(self):
		self.__windows.append(HelpWindow(self.__shepherd, (3 + self.__position_offset(), 4 + self.__position_offset())))
	
	def __position_offset(self):
		return random.randint(1,10)
	
	def __init__(self, shepherd):
		self.__shepherd = shepherd
		self.__windows = []
		
class Manager:
	__manipulation_step = 5
	
	def __optimize(self):
		self.shepherd.optimize = True
		self.shepherd.draw()
		
	def __unoptimize(self):
		self.shepherd.optimize = False
		self.shepherd.draw()
	
	def __thread(self):
		with curtsies.Input(keynames='curses') as input_generator:
			for e in input_generator:
				if 'Paste Event' in str(e):
					e = (str(e).replace('<Paste Event with data: ', '').replace(']>', ']').replace('\', \'', '')[2:][:-2])
				
				selection = self.shepherd.selected()
				
				if selection is not None:
					window = self.shepherd.registry()[selection]['instance']
				
				if selection is None and self.captured == True:
					self.captured = False
					window.public_redraw()
				
				if self.resizing != True and self.repositioning != True and self.captured != True:
					if e == '\t':
						self.shepherd.iterateselect()
					elif e == 'w':
						self.shepherd.window_list()
					elif e == 'q':
						self.shepherd.loop = False
					elif e == 'n':
						self.factory.SpawnTerminal()
					elif e == 'h':
						self.factory.SpawnHelp()
					if selection is not None:
						if e == 'x':
							self.shepherd.remove(selection)
						elif e == 'r':
							self.resizing = True
							self.__optimize()
						elif e == 'p':
							self.repositioning = True
							self.__optimize()
						elif e == 'c':
							window.public_redraw()
							self.captured = True
				elif self.resizing == True or self.repositioning == True:
					if e == 'z' or e == 'p' or e == 'r':
						self.resizing = False
						self.repositioning = False
						self.__unoptimize()
					
					if self.resizing == True:
						size = window.getsize()
						
						if e == 'KEY_DOWN':
							window.resize((size[0], size[1]+self.__manipulation_step))
						elif e == 'KEY_UP':
							window.resize((size[0], size[1]-self.__manipulation_step))
						elif e == 'KEY_LEFT':
							window.resize((size[0]-self.__manipulation_step, size[1]))
						elif e == 'KEY_RIGHT':
							window.resize((size[0]+self.__manipulation_step, size[1]))
					if self.repositioning == True:
						pos = window.getpos()
						
						if e == 'KEY_DOWN':
							window.move((pos[0], pos[1]+self.__manipulation_step))
						elif e == 'KEY_UP':
							window.move((pos[0], pos[1]-self.__manipulation_step))
						elif e == 'KEY_LEFT':
							window.move((pos[0]-self.__manipulation_step, pos[1]))
						elif e == 'KEY_RIGHT':
							window.move((pos[0]+self.__manipulation_step, pos[1]))
				elif self.captured == True:
					if e != '\x05' and selection is not None:
						e = e.replace('\n', '\x0d')
						e = e.replace('KEY_UP', '\x10')
						e = e.replace('KEY_DOWN', '\x0e')
						e = e.replace('KEY_LEFT', '\x02')
						e = e.replace('KEY_RIGHT', '\x06')
						
						e = e.replace('KEY_F(12)', '\033[24~')
						e = e.replace('KEY_F(9)', '\033[20~')
						e = e.replace('KEY_F(8)', '\033[19~')
						e = e.replace('KEY_F(7)', '\033[18~')
						e = e.replace('KEY_F(6)', '\033[17~')
						e = e.replace('KEY_F(5)', '\033[15~')
						e = e.replace('KEY_F(4)', '\033OS')
						e = e.replace('KEY_F(3)', '\033OR')
						e = e.replace('KEY_F(2)', '\033OQ')
						
						if 'x7f' in e:
							e = '\x7f'
						
						window.stdin(e.encode('utf-8'))
					else:
						self.captured = False
						window.public_redraw()
	
	def __init__(self, shepherd):
		self.shepherd = shepherd
		self.factory = WindowTypeFactory(self.shepherd)
		
		self.resizing = False
		self.repositioning = False
		self.captured = False
		
		self.thread = threading.Thread(target=self.__thread)
		self.thread.daemon = True
		self.thread.start()
			
class SUi:
	__term_size = (80, 20)
	__lock_wait = 0.000000001
	
	def write(self, string):
		while self.__lock == True:
			time.sleep(self.__lock_wait)
			
		self.__lock = True

		sys.stdout.write(string)
		#self.__buffer(string)
		
		self.__lock = False
		
	def flush(self):
		sys.stdout.flush()
	
	def goto(self, x, y):
		self.write('\033['+str(y)+';'+str(x)+'H')
		self.flush()
		
	def bottom(self):
		self.goto(0, self.__term_size[1] - 1)
	
	def size(self):
		return self.__term_size
	
	def clearline(self):
		self.write('\r')
		self.write(' ' * self.__term_size[0])
		self.write('\r')
		self.flush()
	
	def __buffer(self, string):
		rs = ''
		for k, v in enumerate(re.split(r'(\\033\[.[^m]+?H)', string)):
			if len(v) < 1:
				continue
			if v.startswith('\033[') and v.endswith('H'):
				r = v.replace('\033[', '').replace('H', '')
				s = r.split(';')
				y = int(s[0])
				x = int(s[1])
				
				self.__pointer_location_x = x+1
				self.__pointer_location_y = y+1
			else:
				c = ''
				for b in re.split(r'(\\033\[.*?m)', v):
					if len(b) < 1:
						continue
					if b.startswith('\033[') and b.endswith('m'):
						c += b
					else:
						x = list(b)
						rs += ('\033['+str(self.__pointer_location_y)+';'+str(self.__pointer_location_x) + 'H')
						for l in x:
							if l == '\n':
								self.__pointer_location_x = 0
								self.__pointer_location_y += 1
								continue
							
							self.__pointer_location_x += 1
							if self.__pointer_location_x > self.__term_size[0]:
								self.__pointer_location_x = 0
								self.__pointer_location_y += 1
							
							if self.__display[self.__pointer_location_x][self.__pointer_location_y] == c + l:
								self.__display[self.__pointer_location_x][self.__pointer_location_y] = c + l
							else:
								rs += (c + l)
						c = ''

		proc = []
		loc = ''
		pri = ''		
		for k, v in enumerate(re.split(r'(\\033\[.[^m]+?H)', rs)):
			if len(v) < 1:
				continue
			
			if v.startswith('\033[') and v.endswith('H'):
				loc += v
			else:
				pri += loc + v

				if k % 6 != True:
					proc.append(threading.Thread(target=self.__twrite, args=[pri]))
					proc[-1].daemon = True
					proc[-1].start()

					pri = ''

				loc = ''

		for x in proc:
			while x.is_alive():
				time.sleep(self.__lock_wait)
	
	def __twrite(self, string):
		sys.stdout.write(string)

	def __init__(self):
		self.__term_size = shutil.get_terminal_size(self.__term_size)
		self.__pointer_location_x = 0
		self.__pointer_location_y = 0
		self.__display = [[' '] * (self.__term_size[0] * 4)] * (self.__term_size[1] * 4)
		self.__lock = False
		
		'''
		ESC = pyparsing.Literal('\x1b')
		integer = pyparsing.Word(pyparsing.nums)
		escapeSeq = pyparsing.Combine(ESC + '[' + pyparsing.Optional(pyparsing.delimitedList(integer,';')) + 
						pyparsing.oneOf(list(pyparsing.alphas)))

		self.nonAnsiString = lambda s : pyparsing.Suppress(escapeSeq).transformString(s)
		'''
