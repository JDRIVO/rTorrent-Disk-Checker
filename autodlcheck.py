import sys, os, urllib, shutil, subprocess
import config as g
from datetime import datetime
from xmlrpc import xmlrpc

torrent_name = str(sys.argv[1])
torrent_label = str(sys.argv[2])
torrent_size = int(sys.argv[3])

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


if torrent_label in g.imdb:
        minimum_rating = g.imdb[torrent_label][0]
        minimum_votes = g.imdb[torrent_label][1]
        skip_foreign = g.imdb[torrent_label][2]
        imdb_search(torrent_name, minimum_rating, minimum_votes, skip_foreign)

if g.enable_disk_check:
        queued = g.folder_path + '/' + 'autodlcheck.txt'
        disk = os.statvfs('/')
        torrent_size /= 1073741824.0
        downloading = xmlrpc('d.multicall2', ('', 'leeching', 'd.down.total='))
        available_space = disk.f_bsize * disk.f_bavail / 1073741824.0
        min_filesize = g.minimum_filesize
        min_age = g.minimum_age
        min_ratio = g.minimum_ratio
        fb_age = g.fallback_age
        fb_ratio = g.fallback_ratio
        fallback_torrents = []
        include = True
        exclude = False
        request = False
        fallback = False
        override = False
        no = False

        if downloading and [0] in downloading:

                try:
                        available_space -= float(open(queued).readline())
                except:
                        pass

        with open(queued, 'w+') as textfile:
                textfile.write(str(torrent_size))

        zero = 0
        required_space = torrent_size - (available_space - g.minimum_space)

        while zero < required_space:

                if not request:
                        request = True
                        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.size_bytes=', 'd.ratio=', 'd.base_path=', 'd.hash='))
                        completed.sort()

                if not completed and not fallback and fallback_torrents:
                        fallback = True

                if not fallback:
                        oldest_torrent = completed[0]

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
                                label = urllib.unquote(oldest_torrent[1])

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
                                tracker = oldest_torrent[2]
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
                        filesize = oldest_torrent[3] / 1073741824.0
                        ratio = oldest_torrent[4] / 1000.0
                        path = oldest_torrent[5]
                        torrent = oldest_torrent[6]

                        if filesize < min_filesize or age < min_age or ratio < min_ratio:

                                if fb_age is not no and filesize >= min_filesize and age >= fb_age:
                                        fallback_torrents.append([path, torrent, filesize])

                                elif fb_ratio is not no and filesize >= min_filesize and ratio >= fb_ratio:
                                        fallback_torrents.append([path, torrent, filesize])

                                del completed[0]

                                if not completed:

                                        if fallback_torrents:
                                                continue

                                        break

                                continue
                else:
                        oldest_torrent = fallback_torrents[0]
                        path = oldest_torrent[0]
                        torrent = oldest_torrent[1]
                        filesize = oldest_torrent[2]

                xmlrpc('d.tracker_announce', tuple([torrent]))
                xmlrpc('d.erase', tuple([torrent]))

                if os.path.isdir(path):
                        shutil.rmtree(path)
                else:
                        os.remove(path)

                if not fallback:
                        del completed[0]
                else:
                        del fallback_torrents[0]

                zero += filesize

                if not completed and not fallback_torrents:
                        break

if available_space < required_space:
    subprocess.Popen(['python', g.folder_path + '/' + 'stop.py', sys.argv[4]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

print 'finish'
