# -*- coding: utf-8 -*-

import sys, os, time
from remotecaller import xmlrpc

queue = sys.argv[1]
torrent_hash = sys.argv[2]
torrent_path = sys.argv[3]

with open(queue, 'a+') as txt:
        txt.write(torrent_hash + '\n')

time.sleep(0.001)

while True:

        try:

                with open(queue, 'r') as txt:
                        queued = txt.read().strip().split('\n')

                if queued[0] == torrent_hash:
                        break

                if torrent_hash not in queued:

                        with open(queue, 'a+') as txt:
                                txt.write(torrent_hash + '\n')
        except:
                pass

        time.sleep(0.01)

t_hash = tuple([torrent_hash])
xmlrpc('d.open', t_hash)
xmlrpc('d.tracker_announce', t_hash)
files = xmlrpc('f.multicall', (torrent_hash, '', 'f.frozen_path='))
xmlrpc('d.erase', t_hash)

if len(files) <= 1:
        os.remove(files[0][0])
else:
        [os.remove(file[0]) for file in files]

        try:
                os.rmdir(torrent_path)
        except:

                for root, directories, files in os.walk(torrent_path, topdown=False):

                        try:
                                os.rmdir(root)
                        except:
                                pass

queued = open(queue).read().strip().split('\n')
txt = open(queue, mode='w')
[txt.write(torrent + '\n') for torrent in queued if torrent != torrent_hash]
time.sleep(5)

try:
        queued = open(queue).read()

        if not queued:
                os.remove(queue)
except:
        pass
