import os, sys, json, string, time

class Store:
	__file = '.'+os.sep+'data'+os.sep+'local_storage.json'
	
	def __j_decode(self, data):
		return json.loads(data)
	
	def __j_encode(self, data):
		return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
	
	def __f_get(self):
		file = open(self.__file,'r')
		data = file.read().strip()
		file.close()
		
		return data
		
	def __f_set(self, data):
		file = open(self.__file,'w+')
		file.write(data)
		file.close()
		
	def __d_get_final(self):
		return self.__j_decode(self.__f_get())
	
	def __d_set_final(self, data):
		self.__f_set(self.__j_encode(data))
	
	def listall(self):
		full = self.__d_get_final()
		
		r = []
		for key, value in full.items():
			r.append(key)
		
		return r
	
	def get(self, name, default=False):
		full = self.__d_get_final()
		
		try:
			data = full[name]
		except:
			data = default
			
		return data
		
	def set(self, name, data):
		full = self.__d_get_final()
		full['last_edit'] = float(time.time())
		full[name] = data
		
		self.__d_set_final(full)
	
	def exists(self, name):
		full = self.__d_get_final()
		
		try:
			data = full[name]
		except:
			data = False
		else:
			data = True
			
		return data
	
	def purge(self, name):
		full = self.__d_get_final()
		try:
			del full[name]
		except:
			return False
		
		self.__d_set_final(full)
		return True
		
	def setfile(self, loc):
		self.__file = loc
		if os.path.isfile(self.__file) != True:
			file = open(self.__file,'w+')
			file.write(self.__j_encode({}))
			file.close()
		
	def __init__(self):
		self.setfile(self.__file)
