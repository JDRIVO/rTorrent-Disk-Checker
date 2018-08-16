print "DD = Download Date  TN = Torrent Name  TL = Torrent Label  TT = Torrent Tracker\n"

import sys, os, shutil, cStringIO as StringIO
import xmlrpclib, urllib, urlparse, socket, re
from urlparse import uses_netloc
from datetime import datetime

startTime = datetime.now()

yes = True
no = False

include = True
exclude = False

uses_netloc.append('scgi')

enable_disk_check = yes

host = 'scgi://127.0.0.1:5000'
disk = os.statvfs('/')

# The minimum amount of free space (in Gigabytes) to maintain
minimum_space = 5

# General Rules

# Filesize in Gigabytes / Age in Days
minimum_filesize = 5
minimum_age = 7
minimum_ratio = 1.2

# Fallback Age - Only the age of a torrent must be higher or equal to this number to be deleted - no to disable
fallback_age = no

# Fallback Ratio - Only the ratio of a torrent must be higher or equal to this number to be deleted - no to disable
fallback_ratio = 1.4

# End of General Rules


# Tracker Rules will override general rules - Fill to enable

# include: use general rules
# exclude: exclude tracker

# Value Order - 1. Minimum Filesize (GB) 2. Minimum Age 3. Minimum Ratio 4. Fallback Age 5. Fallback Ratio
trackers = {}

# Example
#trackers = {
#                     "demonoid.pw" : [include],
#                     "hdme.eu" : [exclude],
#                     "redacted.ch" : [1, 7, 1.2, no, no],
#                     "hd-torrents.org" : [3, 5, 1.3, 9, 1.3],
#                     "privatehd.to" : [5, 6, 1.2, 12, no],
#                     "apollo.rip" : [2, 5, 1.4, no, 1.8],
#           }

# Only delete torrents from trackers in your tracker dictionary (yes/no)
trackers_only = no

# Add/Exclude labels or set Label Rules - Label Rules will override general/tracker rules - Fill to enable

# include: use general/tracker rules
# exclude: exclude label

# Value Order - 1. Minimum Filesize (GB) 2. Minimum Age 3. Minimum Ratio 4. Fallback Age 5. Fallback Ratio
labels = {}

# Example
#labels = {
#                     "Trash" : [include],
#                     "TV" : [exclude],
#                     "HD" : [1, 5, 1.2, 15, 1.2],
#         }

# Only delete torrents with labels in your label dictionary (yes/no)
labels_only = no

# Exclude torrents without labels (yes/no)
exclude_unlabelled = no

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

def xmlrpc(methodname, params):
        xmlreq = xmlrpclib.dumps(params, methodname)
        xmlresp = SCGIRequest(host).send(xmlreq)
        return xmlrpclib.loads(xmlresp)[0][0]

torrent_size = float(sys.argv[1])

if enable_disk_check:
        downloading = xmlrpc('d.multicall2', ('', 'leeching', 'd.down.total='))
        available_space = disk.f_bsize * disk.f_bavail / 1073741824.0
        min_filesize = minimum_filesize
        min_age = minimum_age
        min_ratio = minimum_ratio
        fb_age = fallback_age
        fb_ratio = fallback_ratio
        torrents = {}
        fallback_torrents = {}
        deleted = []
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
        count = 0
        required_space = torrent_size - (available_space - minimum_space)

        while zero < required_space:

                if not torrents and not fallback and fallback_torrents:
                        fallback = True

                if not torrents and not fallback:
                        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.size_bytes=', 'd.ratio=', 'd.name=', 'd.hash='))

                        for date, label, tracker, filesize, ratio, name, torrent in completed:
                                torrents[datetime.utcfromtimestamp(date)] = label, tracker, filesize, ratio, name, torrent

                if not fallback:
                        oldest_torrent = min(torrents)
                        label = urllib.unquote(torrents[oldest_torrent][0])
                        tracker = torrents[oldest_torrent][1]

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
                        name = torrents[oldest_torrent][4]
                        torrent = torrents[oldest_torrent][5]

                        if filesize < min_filesize or age < min_age or ratio < min_ratio:

                                if fb_age is not no and filesize >= min_filesize and age >= fb_age:
                                        fallback_torrents[oldest_torrent] = filesize, name, label, tracker

                                elif fb_ratio is not no and filesize >= min_filesize and ratio >= fb_ratio:
                                        fallback_torrents[oldest_torrent] = filesize, name, label, tracker

                                del torrents[oldest_torrent]

                                if not torrents:

                                        if fallback_torrents:
                                                continue

                                        break

                                continue
                else:
                        oldest_torrent = min(fallback_torrents)
                        filesize = fallback_torrents[oldest_torrent][0]
                        name = fallback_torrents[oldest_torrent][1]
                        label = fallback_torrents[oldest_torrent][2]
                        tracker = fallback_torrents[oldest_torrent][3]

                if not fallback:
                        del torrents[oldest_torrent]
                else:
                        del fallback_torrents[oldest_torrent]

                zero += filesize
                count += 1

                deleted.append("%s. DD: %s\n%s. TN: %s\n%s. TL: %s\n%s. TT: %s\n" % (count, oldest_torrent, count, name, count, label, count, tracker))

                if not torrents and not fallback_torrents:
                        break

time = datetime.now() - startTime
calc = available_space + zero - torrent_size

with open('testresult.txt', 'w+') as textfile:
        textfile.write("Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB\n" % (time, count, zero))
        textfile.write("%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download\n\n" % (available_space, calc, torrent_size))
        textfile.write("DD = Download Date  TN = Torrent Name  TL = Torrent Label  TT = Torrent Tracker\n\n")

        for result in deleted:
                textfile.write(result.encode('utf-8') + "\n")

for result in deleted:
        print result

print "Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB" % (time, count, zero)
print "%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download" % (available_space, calc, torrent_size)
