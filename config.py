include = yes = True
exclude = no = False
whitelist = 'whitelist'
blacklist = 'blacklist'

############ USER DEFINED VARIABLES START ############

# SCGI address or unix socket file path found in your rtorrent.rc file
scgi = '127.0.0.1:5000'

# Unix domain socket - This program will automatically create this file
socket_file = 'unix_socket'

# Amount of seconds to wait before updating the cache
cache_interval = 300


###### DISK CHECKER SETTINGS ######

# This program will auto detect mount points and only delete torrents inside the mount point that the torrent will be downloaded to

# The minimum amount of free space (in Gigabytes) to maintain
minimum_space = 5

# Optional - Specify minimum space values for specific mount points
minimum_space_mp = {
#                          '/': 5,
#                          '/torrents': 100,
                   }


### GENERAL RULES ###

# All minimum requirements must be met by a torrent for it to be deleted | To ignore a requirement set it to 0

# Torrent Size in Gigabytes / Age in Days
minimum_size = 5
minimum_age = 7
minimum_ratio = 1.2

# If all minimum requirements aren't met, the torrent will run through fallback conditions.
# If all or any (dependent on fallback mode) minimum fallback requirements are met, the torrent will be added to a fallback queue.

# Fallback torrents will only be deleted:
#         -  once all torrents have been checked to verify minimum requirement satisfaction &
#         -  insufficient disk space had been freed

# Fallback Modes:
# 0 = Disable fallback
# 1 = Satisfy all conditions | To ignore a requirement set it to 0
# 2 = Satisfy any condition  | To disable a requirement set it to no

fallback_mode = 0

fallback_size = 5
fallback_age = 5
fallback_ratio = 1


### TRACKER RULES ###

# Tracker Rules will override general rules - Fill to enable

# include = use general rules | exclude = exclude tracker

# Value Order: 1. Minimum Size 2. Minimum Age 3. Minimum Ratio 4. Fallback Mode 5. Fallback Size 6. Fallback Age 7. Fallback Ratio

trackers = {
#                     include: ['demonoid.pw'],
#                     exclude: ['hdme.eu', 'blutopia.xyz'],

#                     'redacted.ch': [1, 7, 1.2,
#                                     0,
#                                     1, 1, 1],
#                     'hd-torrents.org': [3, 7, 1.3,
#                                         1,
#                                         5, 0, 1.3],
#                     'privatehd.to': [30, 6, 1.2,
#                                       1,
#                                      15, 5, 0],
#                     'apollo.rip': [2, 6, 1.4,
#                                    2,
#                                    5, 3, no],
           }

# Only delete torrents from trackers with a tracker rule? (yes/no)
trackers_only = no


### LABEL RULES ###

# Label Rules will override general/tracker rules - Fill to enable

# include = use tracker rules (if defined) otherwise use general rules | exclude = exclude label

# whitelist = allowed trackers | blacklist = disallowed trackers

# Value Order: 1. Minimum Size 2. Minimum Age 3. Minimum Ratio 4. Fallback Mode 5. Fallback Size 6. Fallback Age 7. Fallback Ratio

labels = {
#                     include: ['Trash', 'MOV', 'MP4'],
#                     exclude: ['TV', 'Classics'],

#                     'Games': [include, whitelist, ['tpb.org'] ],
#                     'Music': [include, blacklist, ['redacted.ch', 'orpheus.network'] ],
#                     'Movie': [15, 7, 2,
#                                0,
#                                1, 1, 1],
#                     'HD': [6, 5, 1.2,
#                            1,
#                            3, 3, 1.2,
#                            whitelist, ['blutopia.xyz', 'hd-torrents.org'] ],
#                     '4K': [60, 7, 2,
#                             2,
#                            no, 5, 1.2,
#                            blacklist, ['blutopia.xyz'] ],
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

# Amount of minutes to wait before sending a notification between torrent downloads
interval = 60

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
