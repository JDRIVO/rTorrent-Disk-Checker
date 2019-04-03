# -*- coding: utf-8 -*-

import sys, os, time, config as cfg
from subprocess import Popen
from datetime import datetime
from remotecaller import xmlrpc

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
                from threading import Thread
                from guessit import guessit
                from imdbpie import Imdb

                def imdb_rating():
                        ratings.update(imdb.get_title_ratings(movie_imdb))

                def movie_country():
                        country.extend(imdb.get_title_versions(movie_imdb)['origins'])

                imdb = Imdb()
                torrent_info = guessit(torrent_name)
                movie_title = torrent_info['title'] + ' ' + str(torrent_info['year'])
                movie_imdb = imdb.search_for_title(movie_title)[0]['imdb_id']

                ratings = {}
                country = []
                t1 = Thread(target=imdb_rating)
                t2 = Thread(target=movie_country)
                t1.start()
                t2.start()
                t1.join()
                t2.join()
        except:
                return

        rating = ratings['rating']
        votes = ratings['ratingCount']

        if rating < minimum_rating or votes < minimum_votes:
                xmlrpc('d.erase', tuple([torrent_hash]))
                sys.exit()

        if skip_foreign:

                if 'US' not in country:
                        xmlrpc('d.erase', tuple([torrent_hash]))
                        sys.exit()

if torrent_label in cfg.imdb:
        minimum_rating, minimum_votes, skip_foreign = cfg.imdb[torrent_label]
        imdb_search()

if cfg.enable_disk_check:
        script_path = os.path.dirname(sys.argv[0])
        queue = script_path + '/queue.txt'

        with open(queue, 'a+') as txt:
                txt.write(torrent_hash + '\n')

        time.sleep(0.001)

        while True:

                try:

                        with open(queue, 'r') as txt:
                                queued = txt.read().strip().split('\n')

                        if queued[0] == torrent_hash:
                                break

                        if torrent_hash not in queued:

                                with open(queue, 'a') as txt:
                                        txt.write(torrent_hash + '\n')
                except:
                        pass

                time.sleep(0.01)

        current_date = datetime.now()
        remover = script_path + '/remover.py'
        remover_queue = script_path + '/' + torrent_hash
        emailer = script_path + '/emailer.py'
        last_torrent = script_path + '/hash.txt'
        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.ratio=', 'd.size_bytes=', 'd.hash=', 'd.directory='))
        completed.sort()

        try:
                last_hash = open(last_torrent).readline()
                downloading = xmlrpc('d.left_bytes', tuple([last_hash]))
        except:
                downloading = 0

        open(last_torrent, mode='w+').write(torrent_hash)
        disk = os.statvfs('/')
        available_space = (disk.f_bsize * disk.f_bavail - downloading) / 1073741824.0
        required_space = torrent_size - (available_space - cfg.minimum_space)
        requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.fallback_age, cfg.fallback_ratio
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

                Popen([sys.executable, remover, remover_queue, t_hash, t_path])
                freed_space += t_size

        if available_space >= required_space:
                xmlrpc('d.start', tuple([torrent_hash]))

        queued = open(queue).read().strip().split('\n')
        txt = open(queue, mode='w')
        [txt.write(torrent + '\n') for torrent in queued if torrent != torrent_hash]

        if available_space < required_space and cfg.enable_email:
                Popen([sys.executable, emailer, 'notify'])
else:
        xmlrpc('d.start', tuple([torrent_hash]))
