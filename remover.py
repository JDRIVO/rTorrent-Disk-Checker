# -*- coding: utf-8 -*-

import sys, os, cacher, time
from torrents import completed
from remotecaller import xmlrpc

queue = sys.argv[1]
torrent_hash = sys.argv[2]
torrent_path = sys.argv[3]
subtractions = sys.argv[4]

files = xmlrpc('f.multicall', (torrent_hash, '', 'f.size_bytes=', 'f.frozen_path='))
t_hash = (torrent_hash,)
xmlrpc('d.tracker_announce', t_hash)
xmlrpc('d.erase', t_hash)

with open(queue, 'a+') as txt:
        txt.write(torrent_hash + '\n')

time.sleep(0.001)

while True:

        try:
                with open(queue, 'r') as txt:
                        queued = txt.read().strip().splitlines()
        except:
                with open(queue, 'a+') as txt:
                        txt.write(torrent_hash + '\n')

        try:
                if queued[0] == torrent_hash:
                        break

                if torrent_hash not in queued:

                        with open(queue, 'a') as txt:
                                txt.write(torrent_hash + '\n')
        except:
                pass

        time.sleep(0.01)

try:
        freed_bytes = int(open(subtractions, mode='r').read())
except:
        open(subtractions, mode='w+').close()
        freed_bytes = 0

if len(files) <= 1:
        
        try:
                freed_bytes += files[0][0]

                with open(subtractions, 'r+') as txt:
                        txt.write(str(freed_bytes))
                        txt.truncate()

                os.remove(files[0][1])
        except:
                pass
else:

        for file in files:
                freed_bytes += file[0]

                with open(subtractions, 'r+') as txt:
                        txt.write(str(freed_bytes))
                        txt.truncate()

                os.remove(file[1])

        try:
                os.rmdir(torrent_path)
        except:

                for root, directories, files in os.walk(torrent_path, topdown=False):

                        try:
                                os.rmdir(root)
                        except:
                                pass

txt = open(queue, mode='r+')
queued = txt.read().strip().splitlines()
txt.seek(0)
[txt.write(torrent + '\n') for torrent in queued if torrent != torrent_hash]
txt.truncate()
time.sleep(1)

try:
        queued = open(queue).read()

        if not queued:
                os.remove(queue)
                cacher.build_cache(torrent_hash)
except:
        pass
