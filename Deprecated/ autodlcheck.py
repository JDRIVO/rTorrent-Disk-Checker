include = True
exclude = False
yes = True
no = False

############ USER DEFINED VARIABLES START ############

# no to disable
enable_disk_check = yes

###### DISK CHECK SECTION - IGNORE IF DISABLED ######

host = 'scgi://127.0.0.1:5000'

# The minimum amount of free space (in Gigabytes) to maintain
minimum_space = 5

# GENERAL RULES START

# All minimum requirements must be met by a torrent to be deleted

# Filesize in Gigabytes / Age in Days

minimum_filesize = 5
minimum_age = 7
minimum_ratio = 1.2

# Only the age of a torrent must be higher or equal to this number to be deleted (filesize requirement remains) - no to disable
fallback_age = no

# Only the ratio of a torrent must be higher or equal to this number to be deleted (filesize requirement remains) - no to disable
fallback_ratio = 1.4

# GENERAL RULES END


# Tracker Rules will override general rules - Fill to enable

# include: use general rules | exclude: exclude tracker

# Value Order: 1. Minimum Filesize (GB) 2. Minimum Age 3. Minimum Ratio 4. Fallback Age 5. Fallback Ratio

trackers = {
#                     "demonoid.pw" : [include],
#                     "hdme.eu" : [exclude],
#                     "redacted.ch" : [1, 7, 1.2, no, no],
#                     "hd-torrents.org" : [3, 5, 1.3, 9, 1.3],
#                     "privatehd.to" : [5, 6, 1.2, 12, no],
#                     "apollo.rip" : [2, 5, 1.4, no, 1.8],
           }

# Only delete torrents from trackers with a tracker rule (yes/no)
trackers_only = yes


# Label Rules will override general/tracker rules - Fill to enable

# include: use general/tracker rules | exclude: exclude label

# Value Order: 1. Minimum Filesize (GB) 2. Minimum Age 3. Minimum Ratio 4. Fallback Age 5. Fallback Ratio

labels = {
#                     "Trash" : [include],
#                     "TV" : [exclude],
#                     "HD" : [1, 5, 1.2, 15, 1.2],
         }

# Only delete torrents with labels that have a label rule (yes/no)
labels_only = yes

# Exclude torrents without labels (yes/no)
exclude_unlabelled = no


###### IMDB SECTION - IGNORE IF UNWANTED ######

# The IMDB function will only execute if the torrent is attached to a label with an IMDB rule

# Value Order: 1. Minimum IMDB Rating 2. Minimum Votes 3. Skip Foreign Movies (yes/no)

imdb = {
#                     "Hollywood Blockbusters" : [7, 80000, yes],
#                     "Bollywood Classics" : [8, 60000, no],
       }

############ USER DEFINED VARIABLES END ############

import sys, os, shutil, xmlrpclib, urllib, urlparse, socket, re, cStringIO as StringIO
from urlparse import uses_netloc
from datetime import datetime

class SCGIRequest(object):

        def __init__(self, url):
                self.url = url
                self.resp_headers = []

        def __send(self, scgireq):
                scheme, netloc, path, query, frag = urlparse.urlsplit(self.url)
                host, port = urllib.splitport(netloc)

                if netloc:
                        inet6_host = ''

                        if len(inet6_host) > 0:
                                addrinfo = socket.getaddrinfo(inet6_host, port, socket.AF_INET6, socket.SOCK_STREAM)
                        else:
                                addrinfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)

                        assert len(addrinfo) == 1, "There's more than one? %r" % addrinfo

                        sock = socket.socket(*addrinfo[0][:3])
                        sock.connect(addrinfo[0][4])
                else:
                        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        sock.connect(path)

                sock.send(scgireq)
                recvdata = resp = sock.recv(1024)

                while recvdata != '':
                        recvdata = sock.recv(1024)
                        resp += recvdata

                sock.close()
                return resp

        def send(self, data):
                "Send data over scgi to url and get response"
                scgiresp = self.__send(self.add_required_scgi_headers(data))
                resp, self.resp_headers = self.get_scgi_resp(scgiresp)
                return resp

        @staticmethod
        def encode_netstring(string):
                "Encode string as netstring"
                return '%d:%s,'%(len(string), string)

        @staticmethod
        def make_headers(headers):
                "Make scgi header list"
                return '\x00'.join(['%s\x00%s'%t for t in headers])+'\x00'

        @staticmethod
        def add_required_scgi_headers(data, headers = []):
                "Wrap data in an scgi request,\nsee spec at: http://python.ca/scgi/protocol.txt"
                headers = SCGIRequest.make_headers([('CONTENT_LENGTH', str(len(data))),('SCGI', '1'),] + headers)
                enc_headers = SCGIRequest.encode_netstring(headers)
                return enc_headers+data

        @staticmethod
        def gen_headers(file):
                "Get header lines from scgi response"
                line = file.readline().rstrip()

                while line.strip():
                        yield line
                        line = file.readline().rstrip()

        @staticmethod
        def get_scgi_resp(resp):
                "Get xmlrpc response from scgi response"
                fresp = StringIO.StringIO(resp)
                headers = []

                for line in SCGIRequest.gen_headers(fresp):
                        headers.append(line.split(': ', 1))

                xmlresp = fresp.read()
                return (xmlresp, headers)

def imdb_search(torrent_name, minimum_rating, minimum_votes, skip_foreign):

        try:
                import PTN
                from imdbpie import Imdb

                imdb = Imdb()
                torrent_info = PTN.parse(torrent_name)

                search = imdb.get_title_ratings(imdb.search_for_title(str(torrent_info['title']) + ' ' + str(torrent_info['year']))[0]['imdb_id'])
                rating = search['rating']
                votes = search['ratingCount']
        except:
                return
        else:
                if rating < minimum_rating or votes < minimum_votes:
                        print 'exit'
                        quit()

        if skip_foreign:
                country = imdb.get_title_versions(imdb.search_for_title(str(torrent_info['title']) + ' ' + str(torrent_info['year']))[0]['imdb_id'])['origins']

                if 'US' not in country:
                        print 'exit'
                        quit()

def xmlrpc(methodname, params):
        xmlreq = xmlrpclib.dumps(params, methodname)
        xmlresp = SCGIRequest(host).send(xmlreq)
        return xmlrpclib.loads(xmlresp)[0][0]

torrent_name = str(sys.argv[1])
torrent_label = str(sys.argv[2])
torrent_size = int(sys.argv[3])

if torrent_label in imdb:
        minimum_rating = imdb[torrent_label][0]
        minimum_votes = imdb[torrent_label][1]
        skip_foreign = imdb[torrent_label][2]
        imdb_search(torrent_name, minimum_rating, minimum_votes, skip_foreign)

if enable_disk_check:
        uses_netloc.append('scgi')
        disk = os.statvfs('/')
        torrent_size /= 1073741824.0
        downloading = xmlrpc('d.multicall2', ('', 'leeching', 'd.down.total='))
        available_space = disk.f_bsize * disk.f_bavail / 1073741824.0
        min_filesize = minimum_filesize
        min_age = minimum_age
        min_ratio = minimum_ratio
        fb_age = fallback_age
        fb_ratio = fallback_ratio
        torrents = {}
        fallback_torrents = {}
        fallback = False
        override = False

        if downloading and [0] in downloading:

                try:
                        available_space -= float(open('autodlcheck.txt').readline())
                except:
                        pass

        with open('autodlcheck.txt', 'w+') as textfile:
                textfile.write(str(torrent_size))

        zero = 0
        required_space = torrent_size - (available_space - minimum_space)

        while zero < required_space:

                if not torrents and not fallback and fallback_torrents:
                        fallback = True

                if not torrents and not fallback:
                        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.size_bytes=', 'd.ratio=', 'd.base_path=', 'd.hash='))

                        for date, label, tracker, filesize, ratio, path, torrent in completed:
                                torrents[datetime.utcfromtimestamp(date)] = label, tracker, filesize, ratio, path, torrent

                if not fallback:
                        oldest_torrent = min(torrents)

                        if override:
                                override = False
                                min_filesize = minimum_filesize
                                min_age = minimum_age
                                min_ratio = minimum_ratio
                                fb_age = fallback_age
                                fb_ratio = fallback_ratio

                        if exclude_unlabelled and not label:
                                del torrents[oldest_torrent]

                                if not torrents and not fallback_torrents:
                                        break

                                continue

                        if labels:
                                label = urllib.unquote(torrents[oldest_torrent][0])

                                if label in labels:

                                        if not labels[label][0]:
                                                del torrents[oldest_torrent]

                                                if not torrents and not fallback_torrents:
                                                        break

                                                continue

                                        elif labels[label][0] is not include:
                                                override = True
                                                min_filesize = labels[label][0]
                                                min_age = labels[label][1]
                                                min_ratio = labels[label][2]
                                                fb_age = labels[label][3]
                                                fb_ratio = labels[label][4]

                                elif labels_only:
                                        del torrents[oldest_torrent]

                                        if not torrents and not fallback_torrents:
                                                break

                                        continue

                        if trackers and not override:
                                tracker = torrents[oldest_torrent][1]
                                rule = [rule for rule in trackers for url in tracker if rule in url[0]]

                                if rule:
                                        rule = rule[0]

                                        if not trackers[rule][0]:
                                                del torrents[oldest_torrent]

                                                if not torrents and not fallback_torrents:
                                                        break

                                                continue

                                        elif trackers[rule][0] is not include:
                                                override = True
                                                min_filesize = trackers[rule][0]
                                                min_age = trackers[rule][1]
                                                min_ratio = trackers[rule][2]
                                                fb_age = trackers[rule][3]
                                                fb_ratio = trackers[rule][4]

                                elif trackers_only:
                                        del torrents[oldest_torrent]

                                        if not torrents and not fallback_torrents:
                                                break

                                        continue

                        age = (datetime.now() - oldest_torrent).days
                        filesize = torrents[oldest_torrent][2] / 1073741824.0
                        ratio = torrents[oldest_torrent][3] / 1000.0
                        path = torrents[oldest_torrent][4]
                        torrent = torrents[oldest_torrent][5]

                        if filesize < min_filesize or age < min_age or ratio < min_ratio:

                                if fb_age is not no and filesize >= min_filesize and age >= fb_age:
                                        fallback_torrents[oldest_torrent] = path, torrent, filesize

                                elif fb_ratio is not no and filesize >= min_filesize and ratio >= fb_ratio:
                                        fallback_torrents[oldest_torrent] = path, torrent, filesize

                                del torrents[oldest_torrent]

                                if not torrents:

                                        if fallback_torrents:
                                                continue

                                        break

                                continue
                else:
                        oldest_torrent = min(fallback_torrents)
                        path = fallback_torrents[oldest_torrent][0]
                        torrent = fallback_torrents[oldest_torrent][1]
                        filesize = fallback_torrents[oldest_torrent][2]

                xmlrpc('d.tracker_announce', tuple([torrent]))
                xmlrpc('d.erase', tuple([torrent]))

                if os.path.isdir(path):
                        shutil.rmtree(path)
                else:
                        os.remove(path)

                if not fallback:
                        del torrents[oldest_torrent]
                else:
                        del fallback_torrents[oldest_torrent]

                zero += filesize

                if not torrents and not fallback_torrents:
                        break

print 'finish'
