import sys
from xmlrpc import xmlrpc

decimals = sys.argv[1].split(' ')
hex = []

for decimal in decimals:
   hex.append(format(int(decimal), '02x'))

torrent_hash = ''.join(hex).upper()

while True:
    try:
        xmlrpc('d.stop', tuple([torrent_hash]))
        break
    except:
        pass
