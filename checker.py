# -*- coding: utf-8 -*-

import sys, os, threading, config as cfg
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

def remover(t_hash, t_path):
        files = xmlrpc('f.multicall', (t_hash, '', 'f.frozen_path='))
        t_hash = tuple([t_hash])
        xmlrpc('d.tracker_announce', t_hash)
        xmlrpc('d.erase', t_hash)

        if len(files) <= 1:
                os.remove(files[0][0])
        else:
                [os.remove(file[0]) for file in files]

                try:
                        os.rmdir(t_path)
                except:

                        for root, directories, files in os.walk(t_path, topdown=False):

                                try:
                                        os.rmdir(root)
                                except:
                                        pass

if torrent_label in cfg.imdb:
        minimum_rating, minimum_votes, skip_foreign = cfg.imdb[torrent_label]
        imdb_search()

if cfg.enable_disk_check:
        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.ratio=', 'd.size_bytes=', 'd.hash=', 'd.directory='))
        completed.sort()
        downloading = xmlrpc('d.multicall2', ('', 'leeching', 'd.left_bytes='))
        downloading = sum([torrent[0] for torrent in downloading])
        disk = os.statvfs('/')
        available_space = (disk.f_bsize * disk.f_bavail - downloading) / 1073741824.0
        required_space = torrent_size - (available_space - cfg.minimum_space)
        requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.fallback_age, cfg.fallback_ratio
        current_date = datetime.now()
        include = override = True
        exclude = no = False
        freed_space = 0
        fallback_torrents = []

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

                threading.Thread(target=remover, args=(t_hash, t_path,)).start()
                freed_space += t_size

        if available_space < required_space:
                xmlrpc('d.stop', tuple([torrent_hash]))
