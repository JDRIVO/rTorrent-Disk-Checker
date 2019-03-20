from remotecall import xmlrpc

try:
        xmlrpc('d.multicall2', ('', 'leeching', 'd.down.total='))
except:
        print('SCGI address not configured properly. Please adjust it in your config.py file before continuing.')
        quit()

print('\nTA = Torrent Age  TN = Torrent Name  TL = Torrent Label  TT = Torrent Tracker\n')

import sys, os, config as cfg
from datetime import datetime

try:
        from urllib import parse as urllib
except:
        import urllib

startTime = datetime.now()

torrent_size = float(sys.argv[1])

if cfg.enable_disk_check:
        completed = xmlrpc('d.multicall2', ('', 'complete', 'd.timestamp.finished=', 'd.custom1=', 't.multicall=,t.url=', 'd.ratio=', 'd.size_bytes=', 'd.base_path=', 'd.name='))
        completed.sort()
        disk = os.statvfs('/')
        available_space = disk.f_bsize * disk.f_bavail / 1073741824.0
        requirements = cfg.minimum_size, cfg.minimum_age, cfg.minimum_ratio, cfg.fallback_age, cfg.fallback_ratio
        current_date = datetime.now()
        include = override = True
        exclude = no = False
        fallback_torrents = []
        deleted = []
        count = 0
        freed_space = 0
        required_space = torrent_size - (available_space - cfg.minimum_space)

        while freed_space < required_space:

                if not completed and not fallback_torrents:
                        break

                if completed:
                        t_age, t_label, t_tracker, t_ratio, t_size, t_path, t_name = completed[0]
                        t_label = urllib.unquote(t_label)

                        if override:
                                override = False
                                min_size, min_age, min_ratio, fb_age, fb_ratio = requirements

                        if cfg.exclude_unlabelled and not t_label:
                                del completed[0]
                                continue

                        if cfg.labels:

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
                                        fallback_torrents.append([t_age, t_label, t_tracker, t_size, t_name])

                                elif fb_ratio is not no and t_ratio >= fb_ratio and t_size >= min_size:
                                        fallback_torrents.append([t_age, t_label, t_tracker, t_size, t_name])

                                del completed[0]
                                continue

                        del completed[0]
                else:
                        t_age, t_label, t_tracker, t_size, t_name = fallback_torrents[0]
                        del fallback_torrents[0]

                count += 1
                freed_space += t_size
                deleted.append('%s. TA: %s Days Old\n%s. TN: %s\n%s. TL: %s\n%s. TT: %s\n' % (count, t_age, count, t_name, count, t_label, count, t_tracker))

time = datetime.now() - startTime
calc = available_space + freed_space - torrent_size

with open('testresult.txt', 'w+') as textfile:
        textfile.write('Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB\n' % (time, count, freed_space))
        textfile.write('%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download\n\n' % (available_space, calc, torrent_size))
        textfile.write('TA = Torrent Age  TN = Torrent Name  TL = Torrent Label  TT = Torrent Tracker\n\n')

        for result in deleted:
                textfile.write(result + '\n')

for result in deleted:
        print(result)

print('TA = Torrent Age  TN = Torrent Name  TL = Torrent Label  TT = Torrent Tracker\n')
print('Script Executed in %s Seconds\n%s Torrent(s) Deleted Totaling %.2f GB' % (time, count, freed_space))
print('%.2f GB Free Space Before Torrent Download\n%.2f GB Free Space After %.2f GB Torrent Download\n' % (available_space, calc, torrent_size))
