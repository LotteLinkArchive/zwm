import sys, os
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))+os.sep+'zwm'))
import zwm

if __name__ == '__main__':
	g = zwm.SUi()
	c = zwm.Shepherd(g, os.path.abspath(os.path.dirname(os.path.realpath(__file__))+os.sep+'assets'+os.sep+'wallpaper_blank.png'))
	m = zwm.Manager(c)
	
	c.mainloop()
	
	c.terminate(True)
