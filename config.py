include = yes = True
exclude =  no = False

############ USER DEFINED VARIABLES START ############

# SCGI address or unix socket file path found in your rtorrent.rc file
scgi = '127.0.0.1:5000'

# Unix domain socket - Automated creation by script
socket_file  = 'unix_socket'

# The wait time between cache creation iterations in seconds
cache_interval = 300

# Receive a notification when disk is full?
enable_email = no
enable_pushbullet = no
enable_telegram = no
enable_slack = no

###### DISK CHECK SECTION ######

# This script will auto detect mount points and only delete torrents inside the moint point that the torrent will be downloaded to

# The minimum amount of free space (in Gigabytes) to maintain
minimum_space = 5

# Optional - Specify minimum space values for specific mount points
minimum_space_mp = {
#                          '/' : 5,
#                          '/torrents' : 100,
                   }

# GENERAL RULES START

# All minimum requirements must be met by a torrent to be deleted

# Torrent Size in Gigabytes / Age in Days

minimum_size = 5
minimum_age = 7
minimum_ratio = 1.2

# Only the age of a torrent must be higher or equal to this number to be deleted (torrent size requirement remains) - no to disable
fallback_age = no

# Only the ratio of a torrent must be higher or equal to this number to be deleted (torrent size requirement remains) - no to disable
fallback_ratio = 1.1

# GENERAL RULES END


# Tracker Rules will override general rules - Fill to enable

# include: use general rules | exclude: exclude tracker

# Value Order: 1. Minimum Torrent Size (GB) 2. Minimum Age 3. Minimum Ratio 4. Fallback Age 5. Fallback Ratio

trackers = {
#                     'demonoid.pw' : [include],
#                     'hdme.eu' : [exclude],
#                     'redacted.ch' : (1, 7, 1.2, no, no),
#                     'hd-torrents.org' : (3, 5, 1.3, 9, 1.3),
#                     'privatehd.to' : (5, 6, 1.2, 12, no),
#                     'apollo.rip' : (2, 5, 1.4, no, 1.8),
           }

# Only delete torrents from trackers with a tracker rule (yes/no)
trackers_only = yes


# Label Rules will override general/tracker rules - Fill to enable

# include: use general/tracker rules | exclude: exclude label

# Value Order: 1. Minimum Torrent Size (GB) 2. Minimum Age 3. Minimum Ratio 4. Fallback Age 5. Fallback Ratio

labels = {
#                     'Trash' : [include],
#                     'TV' : [exclude],
#                     'HD' : (1, 5, 1.2, 15, 1.2),
         }

# Only delete torrents with labels that have a label rule (yes/no)
labels_only = no

# Exclude torrents without labels (yes/no)
exclude_unlabelled = no


###### NOTIFICATION SETTINGS ######

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
