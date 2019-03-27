# -*- coding: utf-8 -*-

import sys, os
from remotecall import xmlrpc

torrent_hash = sys.argv[1]
torrent_path = sys.argv[2]


t_hash = tuple([torrent_hash])
xmlrpc('d.tracker_announce', t_hash)
xmlrpc('d.open', t_hash)
xmlrpc('d.erase', t_hash)
files = xmlrpc('f.multicall', (torrent_hash, '', 'f.frozen_path='))

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
