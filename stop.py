import sys
from xmlrpc import xmlrpc

decimals = sys.argv[1].split(' ')
hexadecimal = []

for decimal in decimals:
        hexadecimal.append(format(int(decimal), '02x'))

torrent_hash = ''.join(hexadecimal).upper()

while True:
        try:
                xmlrpc('d.stop', tuple([torrent_hash]))
                break
        except:
                pass
