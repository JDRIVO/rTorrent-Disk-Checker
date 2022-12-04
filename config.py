yes, no = True, False
age, ratio, seeds, size = 'age', 'ratio', 'seeds', 'size'
fb_mode, fb_age, fb_ratio, fb_seeds, fb_size = 'fb_mode', 'fb_age', 'fb_ratio', 'fb_seeds', 'fb_size'
include, exclude, whitelist, blacklist, trackers, labels, unmatched = 'include', 'exclude', 'whitelist', 'blacklist', 'trackers', 'labels', 'unmatched'

############ USER DEFINED VARIABLES START ############

# SCGI address or unix socket file path found in your rtorrent.rc file
scgi = '127.0.0.1:5000'

# Unix domain socket - This program will automatically create this file
socket_file = 'unix_socket'


###### CACHE SETTINGS ######

# Enable torrent cache? (yes/no)
# If the cache is disabled, torrent data will be refreshed each time the disk check is run, thereby extending the execution time of the disk check
enable_cache = yes

# Amount of seconds to wait before updating the torrent cache
cache_interval = 300

# Update cache and check again if insufficient disk space is cleared? (yes/no)
# In case updated torrent data meets your criteria, potentially allowing the program to clear enough disk space for the torrent to download
repeat_check = no


###### DISK CHECKER SETTINGS ######

# This program will auto-detect mount points and only delete torrents inside the mount point that the torrent will be downloaded to

# The minimum amount of free space (in gigabytes) to maintain
minimum_space = 5

# Optional - Specify minimum space values for specific mount points
minimum_space_mp = {
#                        '/': 5,
#                        '/torrents': 100,
                   }

# Sort priority - If torrents are sorted first by age for instance and there are multiple torrents aged the same, the torrents of the same age will be
# sorted by the next element in the list until there are no matching values or until the sort options have been exhausted
sort_order = [age, ratio, seeds, size]

# Group order provides finer control over which torrents are presented first to be deleted - Sort order is preserved within groups
# If a torrents label and tracker are both included in the label and tracker lists, the torrent will be grouped with labels unless you have
# specified specific trackers within a tuple "()" in the labels group, in which case only torrents from trackers matching the specified trackers
# will be grouped with that label
group_order = [
#                   [labels, ('unwanted', 'hd-torrents.org'), 'tv', 'movies'],
#                   [trackers, 'demonoid.pw'],
#                   unmatched,
              ]


### GENERAL RULES ###

# All minimum requirements must be met by a torrent for it to be deleted

# If all minimum requirements aren't met, the torrent will run through fallback conditions
# If all or any (dependent on fallback mode) minimum fallback requirements are met, the torrent will be added to a fallback queue

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
#                     seeds: 4,
#                     size: 5,
#                     fb_mode: 1,
#                     fb_age: 7,
#                     fb_ratio: 1.2,
#                     fb_seeds: 2,
#                     fb_size: 4,
                }

# Only delete torrents from trackers with a tracker rule? (yes/no)
trackers_only = no

# Only delete torrents with labels that have a label rule? (yes/no)
labels_only = no

# Only delete torrents with labels that have a label rule or are from trackers with a tracker rule? (yes/no)
# Valid if you have both label and tracker rules
labels_and_trackers_only = no

# Exclude torrents without labels? (yes/no)
exclude_unlabelled = no


### TRACKER RULES ###

# Tracker Rules will override general rules - Fill to enable

# include = use general rules | exclude = exclude tracker

tracker_rules = {
#                     include: ['demonoid.pw'],
#                     exclude: ['hdme.eu', 'blutopia.xyz'],

#                     'redacted.ch': {
#                                       age: 20,
#                                       ratio: 1,
#                                       seeds: 5,
#                                       size: 10,
#                                       fb_mode: 2,
#                                       fb_age: 7,
#                                       fb_ratio: 1,
#                                       fb_seeds: 3,
#                                       fb_size: 5,
#                                    },
#                     'privatehd.to': {
#                                        age: 14,
#                                        ratio: 1,
#                                     },
#                     'hd-torrents.org': {
#                                           age: 7,
#                                           ratio: 1.1,
#                                           size: 5,
#                                           fb_mode: 1,
#                                           fb_age: 30,
#                                        },
#                     ('torrentleech.me', 'tpb.com'): {size: 10},
                }


### LABEL RULES ###

# Label Rules will override general/tracker rules - Fill to enable

# include = use tracker rules (if defined) otherwise use general rules | exclude = exclude label

# whitelist = allowed trackers | blacklist = disallowed trackers

label_rules = {
#                     include: ['Trash', 'MOV', 'MP4'],
#                     exclude: ['HD', 'Classics'],

#                     'Games': [include, whitelist, ['tpb.org'] ],
#                     'Music': [include, blacklist, ['redacted.ch', 'orpheus.network'] ],
#                     'Movie': {
#                                 age: 21,
#                                 ratio: 2,
#                                 seeds: 3,
#                                 size: 5,
#                                 fb_mode: 1,
#                                 fb_age: 7,
#                                 fb_ratio: 3,
#                                 fb_seeds: 3,
#                                 fb_size: 4,
#                              },
#                     'TV': {
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
#                              fb_seeds: 2,
#                              blacklist: ['blutopia.xyz'],
#                           },
#                     ('Sony', 'Nintendo'): {seeds: 2},
              }


###### NOTIFICATION SETTINGS ######

# Receive a notification when disk is full? (yes/no)
enable_email = no
enable_pushbullet = no
enable_pushover = no
enable_telegram = no
enable_discord = no
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
pushbullet_devices = []

### PUSHOVER SETTINGS ###

pushover_token = ''
pushover_user_key = ''
pushover_priority = ''
pushover_sound = ''

# Limit message to specific devices? | Empty list = Send to all devices
pushover_devices = []

### TELEGRAM SETTINGS ###

telegram_token = ''
telegram_chat_id = ''

### DISCORD SETTINGS ###

discord_webhook_url = ''

### SLACK SETTINGS ###

slack_token = ''

# Limit message to specific channels? | Empty list = Send to all channels
slack_channels = []
