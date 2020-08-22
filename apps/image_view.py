import sys, os
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))+os.sep+'..'))
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))+os.sep+'..'+os.sep+'lib'))
import lib

if __name__ == '__main__':
    term = lib.output()

    term.image(sys.argv[1])