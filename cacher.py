# -*- coding: utf-8 -*-

import sys, os, time, pprint
from remotecaller import xmlrpc

script_path = os.path.dirname(sys.argv[0])
queue = script_path + '/cachequeue.txt'
torrent_cache = script_path + '/torrents.py'
mp_cache = script_path + '/mountpoints.py'

def enter_queue(identity):

        with open(queue, 'a+') as txt:
                txt.write(identity + '\n')

        time.sleep(0.001)

        while True:

                try:
                        with open(queue, 'r') as txt:
                                queued = txt.read().strip().splitlines()

                        if queued[0] == identity:
                                break

                        if identity not in queued:

                                with open(queue, 'a') as txt:
                                        txt.write(identity + '\n')
                except:
                        pass

                time.sleep(0.01)

def leave_queue(identity):
        txt = open(queue, mode='r+')
        queued = txt.read().strip().splitlines()
        txt.seek(0)
        [txt.write(queuer + '\n') for queuer in queued if queuer != identity]
        txt.truncate()

def build_cache():
        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.ratio=', 'd.size_bytes=', 'd.name=', 'd.hash=', 'd.directory='))
        completed.sort()
        [list.append(list[7].rsplit('/', 1)[0]) if list[5] in list[7] else list.append(list[7]) for list in completed]

        enter_queue('schedule')

        if os.path.isfile(torrent_cache):
                cache = open(torrent_cache, mode='r+')
                cache.seek(0)
                cache.write('completed = ' + pprint.pformat(completed))
                cache.truncate()
        else:
                cache = open(torrent_cache, mode='w+')
                cache.write('completed = ' + pprint.pformat(completed))

        leave_queue('schedule')

        if not os.path.isfile(mp_cache):
                mount_points = {}

                for list in completed:
                        parent_directory = list[8]
                        mount_point = [path for path in [parent_directory.rsplit('/', num)[0] for num in range(parent_directory.count('/'))] if os.path.ismount(path)]
                        mount_point = mount_point[0] if mount_point else '/'
                        mount_points[parent_directory] = mount_point

                open(mp_cache, mode='w+').write('mount_points = ' + pprint.pformat(mount_points))

if __name__ == "__main__":
        build_cache()
