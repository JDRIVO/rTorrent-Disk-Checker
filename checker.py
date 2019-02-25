import sys, os, shutil, subprocess, config as cfg
from datetime import datetime
from remotecall import xmlrpc

try:
        from urllib import parse as urllib
except:
        import urllib

torrent_name = sys.argv[1]
torrent_label = sys.argv[2]
torrent_size = int(sys.argv[3])
torrent_hash = sys.argv[4]

def imdb_search():

        try:
                import PTN
                from imdbpie import Imdb

                imdb = Imdb()
                torrent_info = PTN.parse(torrent_name)

                search = imdb.get_title_ratings(imdb.search_for_title(torrent_info['title'] + ' ' + str(torrent_info['year']))[0]['imdb_id'])
                rating = search['rating']
                votes = search['ratingCount']
        except:
                return
        else:
                if rating < minimum_rating or votes < minimum_votes:
                        xmlrpc('d.erase', tuple([torrent_hash]))
                        quit()

        if skip_foreign:
                country = imdb.get_title_versions(imdb.search_for_title(torrent_info['title'] + ' ' + str(torrent_info['year']))[0]['imdb_id'])['origins']

                if 'US' not in country:
                        xmlrpc('d.erase', tuple([torrent_hash]))
                        quit()


if torrent_label in cfg.imdb:
        minimum_rating = cfg.imdb[torrent_label][0]
        minimum_votes = cfg.imdb[torrent_label][1]
        skip_foreign = cfg.imdb[torrent_label][2]
        imdb_search()

if cfg.enable_disk_check:
        downloading = xmlrpc('d.multicall2', ('', 'leeching', 'd.down.total=', 'd.hash='))
        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.ratio=', 'd.size_bytes=', 'd.hash=', 'd.base_path='))
        completed.sort()
        disk = os.statvfs('/')
        available_space = disk.f_bsize * disk.f_bavail / 1073741824.0
        queued = os.path.dirname(sys.argv[0]) + '/downloading.txt'
        torrent_size /= 1073741824.0
        fallback_torrents = []
        min_size = cfg.minimum_size
        min_age = cfg.minimum_age
        min_ratio = cfg.minimum_ratio
        fb_age = cfg.fallback_age
        fb_ratio = cfg.fallback_ratio
        include = True
        exclude = False
        fallback = False
        override = False
        no = False

        if [list for list in downloading if list[1] is not torrent_hash and 0 is list[0]]:
                available_space -= float(open(queued).readline())

        with open(queued, 'w+') as textfile:
                textfile.write(str(torrent_size))

        zero = 0
        required_space = torrent_size - (available_space - cfg.minimum_space)

        while zero < required_space:

                if not completed and not fallback and fallback_torrents:
                        fallback = True

                if not fallback:
                        t_age, t_label, t_tracker, t_ratio, t_size, t_hash, t_path = completed[0]

                        if override:
                                override = False
                                min_size = cfg.minimum_size
                                min_age = cfg.minimum_age
                                min_ratio = cfg.minimum_ratio
                                fb_age = cfg.fallback_age
                                fb_ratio = cfg.fallback_ratio

                        if cfg.exclude_unlabelled and not t_label:
                                del completed[0]

                                if not completed and not fallback_torrents:
                                        break

                                continue

                        if cfg.labels:
                                t_label = urllib.unquote(t_label)

                                if t_label in cfg.labels:

                                        if not cfg.labels[t_label][0]:
                                                del completed[0]

                                                if not completed and not fallback_torrents:
                                                        break

                                                continue

                                        elif cfg.labels[t_label][0] is not include:
                                                override = True
                                                min_size, min_age, min_ratio, fb_age, fb_ratio = cfg.labels[t_label]

                                elif cfg.labels_only:
                                        del completed[0]

                                        if not completed and not fallback_torrents:
                                                break

                                        continue

                        if cfg.trackers and not override:
                                rule = [rule for rule in cfg.trackers for url in t_tracker if rule in url[0]]

                                if rule:
                                        rule = rule[0]

                                        if not cfg.trackers[rule][0]:
                                                del completed[0]

                                                if not completed and not fallback_torrents:
                                                        break

                                                continue

                                        elif cfg.trackers[rule][0] is not include:
                                                override = True
                                                min_size, min_age, min_ratio, fb_age, fb_ratio = cfg.trackers[rule]

                                elif cfg.trackers_only:
                                        del completed[0]

                                        if not completed and not fallback_torrents:
                                                break

                                        continue

                        t_age = (datetime.now() - datetime.utcfromtimestamp(t_age)).days
                        t_ratio /= 1000.0
                        t_size /= 1073741824.0

                        if t_age < min_age or t_ratio < min_ratio or t_size < min_size:

                                if fb_age is not no and t_age >= fb_age and t_size >= min_size:
                                        fallback_torrents.append([t_hash, t_path, t_size])

                                elif fb_ratio is not no and t_ratio >= fb_ratio and t_size >= min_size:
                                        fallback_torrents.append([t_hash, t_path, t_size])

                                del completed[0]

                                if not completed:

                                        if fallback_torrents:
                                                continue

                                        break

                                continue
                else:
                        t_hash, t_path, t_size = fallback_torrents[0]

                t_hash = tuple([t_hash])
                xmlrpc('d.tracker_announce', t_hash)
                xmlrpc('d.erase', t_hash)

                if os.path.isdir(t_path):
                        shutil.rmtree(t_path)
                else:
                        os.remove(t_path)

                if not fallback:
                        del completed[0]
                else:
                        del fallback_torrents[0]

                zero += t_size

                if not completed and not fallback_torrents:
                        break

        if available_space < required_space:
                xmlrpc('d.stop', tuple([torrent_hash]))
