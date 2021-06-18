## Script Explanation

#### This script is capable of the following when:
                 - a torrent is added by any program (autodl-irssi, RSS Downloader etc)
                 - a torrent is added remotely or directly 

This script checks your available disk space. If your free disk space is not large enough to accommodate a pending torrent, the script will delete torrents based on criteria defined in [config.py](https://github.com/JDRIVO/rTorrent-Disk-Checker/blob/master/config.py). The script will scan through your torrents from oldest to newest, ensuring the oldest torrent that meets your criteria is deleted first. If your disk space is still too low, the torrent will be sent to rtorrent in a stopped state.	

## Requirements:
* rTorrent 0.9.7+

* Python 3+

## [Setup](https://github.com/JDRIVO/rTorrent-Disk-Checker/blob/master/setup.sh)

Run the setup script by entering the following command in your terminal (Refer to this script for manual setup instructions):

`bash setup.sh`

## [Test Script](https://github.com/JDRIVO/rTorrent-Disk-Checker/blob/master/test.py)

#### This script will show you what torrents the script will delete without actually deleting torrents.

Results will output to your terminal and a text file named **testresult.txt**

The script accepts two arguments: 1. Torrent Size ( GB ) 2. Mount Point ( 0 will default to mount '/' )

`python test.py 69 0`

To send a test message (accepted arguments: email, pushbullet, telegram, slack):

`python messenger.py`
