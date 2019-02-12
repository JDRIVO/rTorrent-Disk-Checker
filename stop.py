import sys
from remotecall import xmlrpc

while True:
        try:
                xmlrpc('d.stop', tuple([sys.argv[1]]))
                break
        except:
                pass
