# -*- coding: utf-8 -*-

import sys, os, shutil, config as cfg
from datetime import datetime
from remotecall import xmlrpc

try:
        from urllib import parse as urllib
except:
        import urllib

torrent_name = sys.argv[1]
torrent_label = sys.argv[2]
torrent_size = int(sys.argv[3]) / 1073741824.0
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
        minimum_rating, minimum_votes, skip_foreign = cfg.imdb[torrent_label]
        imdb_search()

if cfg.enable_disk_check:
        downloading = xmlrpc('d.multicall2', ('', 'leeching', 'd.hash=', 'd.down.total='))
        disk = os.statvfs('/')
        available_space = disk.f_bsize * disk.f_bavail / 1073741824.0
        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.ratio=', 'd.size_bytes=', 'd.hash=', 'd.directory='))
        completed.sort()
        queued = os.path.dirname(sys.argv[0]) + '/downloading.txt'
        requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.fallback_age, cfg.fallback_ratio
        current_date = datetime.now()
        include = override = True
        exclude = no = False
        freed_space = 0
        fallback_torrents = []

        if [list for list in downloading if list[0] != torrent_hash and list[1] == 0]:
                available_space -= float(open(queued).readline())

        with open(queued, 'w+') as textfile:
                textfile.write(str(torrent_size))

        required_space = torrent_size - (available_space - cfg.minimum_space)

        while freed_space < required_space:

                if not completed and not fallback_torrents:
                        break

                if completed:
                        t_age, t_label, t_tracker, t_ratio, t_size, t_hash, t_path = completed[0]

                        if override:
                                override = False
                                min_size, min_age, min_ratio, fb_age, fb_ratio = requirements

                        if cfg.exclude_unlabelled and not t_label:
                                del completed[0]
                                continue

                        if cfg.labels:
                                t_label = urllib.unquote(t_label)

                                if t_label in cfg.labels:
                                        label_rule = cfg.labels[t_label]
                                        rule = label_rule[0]

                                        if rule is exclude:
                                                del completed[0]
                                                continue

                                        if rule is not include:
                                                override = True
                                                min_size, min_age, min_ratio, fb_age, fb_ratio = label_rule

                                elif cfg.labels_only:
                                        del completed[0]
                                        continue

                        if cfg.trackers and not override:
                                tracker_rule = [rule for rule in cfg.trackers for url in t_tracker if rule in url[0]]

                                if tracker_rule:
                                        tracker_rule = cfg.trackers[tracker_rule[0]]
                                        rule = tracker_rule[0]

                                        if rule is exclude:
                                                del completed[0]
                                                continue

                                        if rule is not include:
                                                override = True
                                                min_size, min_age, min_ratio, fb_age, fb_ratio = tracker_rule

                                elif cfg.trackers_only:
                                        del completed[0]
                                        continue

                        t_age = (current_date - datetime.utcfromtimestamp(t_age)).days
                        t_ratio /= 1000.0
                        t_size /= 1073741824.0

                        if t_age < min_age or t_ratio < min_ratio or t_size < min_size:

                                if fb_age is not no and t_age >= fb_age and t_size >= min_size:
                                        fallback_torrents.append([t_hash, t_path, t_size])

                                elif fb_ratio is not no and t_ratio >= fb_ratio and t_size >= min_size:
                                        fallback_torrents.append([t_hash, t_path, t_size])

                                del completed[0]
                                continue

                        del completed[0]
                else:
                        t_hash, t_path, t_size = fallback_torrents[0]
                        del fallback_torrents[0]

                t_hash = tuple([t_hash])
                files = xmlrpc('f.multicall', (t_hash, '', 'f.frozen_path='))
                xmlrpc('d.tracker_announce', t_hash)
                xmlrpc('d.erase', t_hash)
                [os.remove(''.join(file)) for file in files]

                if os.path.exists(t_path):

                        try:
                                os.rmdir(t_path)
                        except:

                                for root, directories, files in os.walk(t_path, topdown=False):

                                        for directory in directories:

                                                try:
                                                        os.rmdir(root + '/' + directory)
                                                except:
                                                        pass

                                try:
                                        os.rmdir(t_path)
                                except:
                                        pass

                freed_space += t_size

        if available_space < required_space:
                xmlrpc('d.stop', tuple([torrent_hash]))
