import sys, os
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))+os.sep+'lib'))
import lib

if __name__ == '__main__':
	g = lib.SUi()
	c = lib.Shepherd(g, os.path.abspath(os.path.dirname(os.path.realpath(__file__))+os.sep+'assets'+os.sep+'wallpaper_blank.png'))
	m = lib.Manager(c)
	
	c.mainloop()
	
	c.terminate(True)
