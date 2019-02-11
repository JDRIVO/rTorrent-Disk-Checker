print "TA = Torrent Age  TN = Torrent Name  TL = Torrent Label  TT = Torrent Tracker\n"

import sys, os, urllib, shutil, subprocess
import config as g
from datetime import datetime
from xmlrpc import xmlrpc

startTime = datetime.now()

torrent_size = float(sys.argv[1])

if g.enable_disk_check:
        disk = os.statvfs('/')
        downloading = xmlrpc('d.multicall2', ('', 'leeching', 'd.down.total='))
        available_space = disk.f_bsize * disk.f_bavail / 1073741824.0
        min_filesize = g.minimum_filesize
        min_age = g.minimum_age
        min_ratio = g.minimum_ratio
        fb_age = g.fallback_age
        fb_ratio = g.fallback_ratio
        fallback_torrents = []
        deleted = []
        include = True
        exclude = False
        request = False
        fallback = False
        override = False
        no = False
        count = 0
        zero = 0
        required_space = torrent_size - (available_space - g.minimum_space)

        while zero < required_space:

                if not request:
                        request = True
                        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.size_bytes=', 'd.ratio=', 'd.base_path=', 'd.name='))
                        completed.sort()

                if not completed and not fallback and fallback_torrents:
                        fallback = True

                if not fallback:
                        oldest_torrent = completed[0]
                        label = urllib.unquote(oldest_torrent[1])
                        tracker = oldest_torrent[2]

                        if override:
                                override = False
                                min_filesize = g.minimum_filesize
                                min_age = g.minimum_age
                                min_ratio = g.minimum_ratio
                                fb_age = g.fallback_age
                                fb_ratio = g.fallback_ratio

                        if g.exclude_unlabelled and not oldest_torrent[1]:
                                del completed[0]

                                if not completed and not fallback_torrents:
                                        break

                                continue

                        if g.labels:

                                if label in g.labels:

                                        if not g.labels[label][0]:
                                                del completed[0]

                                                if not completed and not fallback_torrents:
                                                        break

                                                continue

                                        elif g.labels[label][0] is not include:
                                                override = True
                                                min_filesize = g.labels[label][0]
                                                min_age = g.labels[label][1]
                                                min_ratio = g.labels[label][2]
                                                fb_age = g.labels[label][3]
                                                fb_ratio = g.labels[label][4]

                                elif g.labels_only:
                                        del completed[0]

                                        if not completed and not fallback_torrents:
                                                break

                                        continue

                        if g.trackers and not override:
                                rule = [rule for rule in g.trackers for url in tracker if rule in url[0]]

                                if rule:
                                        rule = rule[0]

                                        if not g.trackers[rule][0]:
                                                del completed[0]

                                                if not completed and not fallback_torrents:
                                                        break

                                                continue

                                        elif g.trackers[rule][0] is not include:
                                                override = True
                                                min_filesize = g.trackers[rule][0]
                                                min_age = g.trackers[rule][1]
                                                min_ratio = g.trackers[rule][2]
                                                fb_age = g.trackers[rule][3]
                                                fb_ratio = g.trackers[rule][4]

                                elif g.trackers_only:
                                        del completed[0]

                                        if not completed and not fallback_torrents:
                                                break

                                        continue

                        age = (datetime.now() - datetime.utcfromtimestamp(oldest_torrent[0])).days
                        date = oldest_torrent[0]
                        filesize = oldest_torrent[3] / 1073741824.0
                        ratio = oldest_torrent[4] / 1000.0
                        path = oldest_torrent[5]
                        name = oldest_torrent[6]

                        if filesize < min_filesize or age < min_age or ratio < min_ratio:

                                if fb_age is not no and filesize >= min_filesize and age >= fb_age:
                                        fallback_torrents.append([age, name, label, filesize, tracker])

                                elif fb_ratio is not no and filesize >= min_filesize and ratio >= fb_ratio:
                                        fallback_torrents.append([age, name, label, filesize, tracker])

                                del completed[0]

                                if not completed:

                                        if fallback_torrents:
                                                continue

                                        break

                                continue
                else:
                        oldest_torrent = fallback_torrents[0]
                        age = oldest_torrent[0]
                        name = oldest_torrent[1]
                        label = oldest_torrent[2]
                        filesize = oldest_torrent[3]
                        tracker = oldest_torrent[4]

                if not fallback:
                        del completed[0]
                else:
                        del fallback_torrents[0]

                count += 1
                zero += filesize
                deleted.append("%s. TA: %s Days Old\n%s. TN: %s\n%s. TL: %s\n%s. TT: %s\n" % (count, age, count, name, count, label, count, tracker))

                if not completed and not fallback_torrents:
                        break

time = datetime.now() - startTime
calc = available_space + zero - torrent_size

with open('testresult.txt', 'w+') as textfile:
        textfile.write("Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB\n" % (time, count, zero))
        textfile.write("%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download\n\n" % (available_space, calc, torrent_size))
        textfile.write("TA = Torrent Age  TN = Torrent Name  TL = Torrent Label  TT = Torrent Tracker\n\n")

        for result in deleted:
                textfile.write(result.encode('utf-8') + "\n")

for result in deleted:
        print result

print "Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB" % (time, count, zero)
print "%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download" % (available_space, calc, torrent_size)
