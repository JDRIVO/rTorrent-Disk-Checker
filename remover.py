# -*- coding: utf-8 -*-

import sys, os, time, shutil
from remotecall import xmlrpc

queue = sys.argv[1]
queue_position = sys.argv[2]
torrent_hash = sys.argv[3]
torrent_path = sys.argv[4]

def remover():
        t_hash = tuple([torrent_hash])
        xmlrpc('d.tracker_announce', t_hash)
        xmlrpc('d.open', t_hash)
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

with open(queue, 'a+') as txt:
        txt.write(queue_position + '\n')

time.sleep(0.01)

while True:

        try:
                with open(queue, 'r') as txt:
                        queued = txt.read()

                if queued[0] == queue_position:
                        break
        except:
                pass

        time.sleep(0.01)

remover()
queue_copy = queue + 'c'

with open(queue_copy, 'w+') as txt:

        for number in queued.strip().split('\n'):

                if number != queue_position:
                        txt.write(number + '\n')

shutil.move(queue_copy, queue)
time.sleep(180)

try:
        os.remove(queue)
except:
        pass
