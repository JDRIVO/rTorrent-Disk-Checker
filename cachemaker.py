# -*- coding: utf-8 -*-

import pprint
from remotecaller import xmlrpc

completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.ratio=', 'd.size_bytes=', 'd.name=', 'd.hash=', 'd.directory='))

with open('cache.py', 'w+') as txt:
        txt.write('cache = ' + pprint.pformat(completed))
