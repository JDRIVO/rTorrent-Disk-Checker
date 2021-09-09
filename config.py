yes, no = True, False
age, ratio, seeders, size = 'age', 'ratio', 'seeders', 'size'
fb_mode, fb_age, fb_ratio, fb_seeders, fb_size = 'fb_mode', 'fb_age', 'fb_ratio', 'fb_seeders', 'fb_size'
include, exclude, whitelist, blacklist, tracker, label, unmatched = 'include', 'exclude', 'whitelist', 'blacklist', 'tracker', 'label', 'unmatched'

############ USER DEFINED VARIABLES START ############

# SCGI address or unix socket file path found in your rtorrent.rc file
scgi = '127.0.0.1:5000'

# Unix domain socket - This program will automatically create this file
socket_file = 'unix_socket'

# Amount of seconds to wait before updating the cache
cache_interval = 300


###### DISK CHECKER SETTINGS ######

# This program will auto detect mount points and only delete torrents inside the mount point that the torrent will be downloaded to

# The minimum amount of free space (in gigabytes) to maintain
minimum_space = 5

# Optional - Specify minimum space values for specific mount points
minimum_space_mp = {
#                        '/': 5,
#                        '/torrents': 100,
                   }

# Sort priority - If torrents are sorted first by age for instance and there are multiple torrents aged the same, the torrents of the same age will be
# sorted by the next element in the list until there are no matching values or until the sort options have been exhausted
sort_order = [age, ratio, seeders, size]

# Group order provides finer control over which torrents are presented first to be deleted - Sort order is preserved
# If a torrents label and tracker are both included in the label and tracker lists, the torrent will be grouped with labels
group_order = [
#                   [label, 'unwanted', 'tv', 'movies'],
#                   [tracker, 'demonoid.pw'],
#                   unmatched,
              ]


### GENERAL RULES ###

# All minimum requirements must be met by a torrent for it to be deleted

# If all minimum requirements aren't met, the torrent will run through fallback conditions.
# If all or any (dependent on fallback mode) minimum fallback requirements are met, the torrent will be added to a fallback queue.

# Fallback torrents will only be deleted:
#         -  once all torrents have been checked to verify minimum requirement satisfaction &
#         -  insufficient disk space had been freed

# Fallback Modes:
# 1 = Satisfy all requirements
# 2 = Satisfy any requirement

# To disable fallback either omit fb_mode or set fb_mode to 0

# No requirements = ignore torrents attributes
# Age in days | Size in gigabytes
general_rules = {
#                     age: 14,
#                     ratio: 1.2,
#                     seeders: 4,
#                     size: 5,
#                     fb_mode: 1,
#                     fb_age: 7,
#                     fb_ratio: 1.2,
#                     fb_seeders: 2,
#                     fb_size: 4,
                }


### TRACKER RULES ###

# Tracker Rules will override general rules - Fill to enable

# include = use general rules | exclude = exclude tracker

tracker_rules = {
#                     include: ['demonoid.pw'],
#                     exclude: ['hdme.eu', 'blutopia.xyz'],

#                     'redacted.ch': {
#                                       age: 20,
#                                       ratio: 1,
#                                       seeders: 5,
#                                       size: 10,
#                                       fb_mode: 2,
#                                       fb_age: 7,
#                                       fb_ratio: 1,
#                                       fb_seeders: 3,
#                                       fb_size: 5,
#                                    },
#                     'privatehd.to': {
#                                        age: 14,
#                                        ratio: 2,
#                                     },
#                     'hd-torrents.org': {
#                                           age: 7,
#                                           ratio: 1.1,
#                                           size: 5,
#                                           fb_mode: 2,
#                                           fb_age: 30,
#                                        },
#                     ('torrentleech.me', 'tpb.com'): {size: 10},
                }

# Only delete torrents from trackers with a tracker rule? (yes/no)
trackers_only = no


### LABEL RULES ###

# Label Rules will override general/tracker rules - Fill to enable

# include = use tracker rules (if defined) otherwise use general rules | exclude = exclude label

# whitelist = allowed trackers | blacklist = disallowed trackers

label_rules = {
#                     include: ['Trash', 'MOV', 'MP4'],
#                     exclude: ['TV', 'Classics'],

#                     'Games': [include, whitelist, ['passthepopcorn'] ],
#                     'Music': [include, blacklist, ['redacted.ch', 'orpheus.network'] ],
#                     'Movie': {
#                                 age: 21,
#                                 ratio: 2,
#                                 seeders: 3,
#                                 size: 5,
#                                 fb_mode: 1,
#                                 fb_age: 7,
#                                 fb_ratio: 3,
#                                 fb_seeders: 3,
#                                 fb_size: 4,
#                              },
#                     'HD': {
#                              age: 7,
#                              ratio: 1,
#                              whitelist: ['blutopia.xyz', 'hd-torrents.org'],
#                           },
#                     '4K': {
#                              age: 15,
#                              ratio: 3,
#                              size: 10,
#                              fb_mode: 2,
#                              fb_ratio: 2,
#                              blacklist: ['blutopia.xyz'],
#                           },
#                     ('Sony', 'Nintendo'): {seeders: 2},
              }

# Only delete torrents with labels that have a label rule? (yes/no)
labels_only = no

# Exclude torrents without labels? (yes/no)
exclude_unlabelled = no


###### NOTIFICATION SETTINGS ######

# Receive a notification when disk is full? (yes/no)
enable_email = no
enable_pushbullet = no
enable_telegram = no
enable_slack = no

# Amount of minutes to wait before sending another notification between torrent downloads
notification_interval = 60

# Subject/Title if applicable
subject = 'Warning: Disk Full'
message = 'Free disk space ASAP.'

### EMAIL SETTINGS ###

smtp_server = 'smtp.gmail.com'
port = 587
tls = yes
ssl = no

account = 'youremail@gmail.com'
password = 'yourpassword'

receiver = 'youremail@gmail.com'

### PUSHBULLET SETTINGS ###

pushbullet_token = ''

# Limit message to specific devices? | Empty list = Send to all devices
specific_devices = []

### TELEGRAM SETTINGS ###

telegram_token = ''
chat_id = ''

### SLACK SETTINGS ###

slack_token = ''

# Limit message to specific channels? | Empty list = Send to all channels
specific_channels = []
