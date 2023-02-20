## rTorrent Disk Checker

#### This program is capable of the following when:
                 - a torrent is added by any program (autodl-irssi, RSS Downloader etc)
                 - a torrent is added remotely or locally

This program checks available disk space and deletes torrents based on criteria defined in [config.py](https://github.com/JDRIVO/rTorrent-Disk-Checker/blob/master/config.py) when there's insufficient space to accommodate a new torrent. If space is still inadequate, the torrent is sent to rTorrent in a stopped state, and notifications can be received from numerous messaging services.

## Requirements
* rTorrent 0.9.7+

* Python 3+

## [Setup](https://github.com/JDRIVO/rTorrent-Disk-Checker/blob/master/setup.sh)

Run the setup script by entering the following command in your terminal (Refer to this script for manual setup instructions):

`bash setup.sh`

## [Test Script](https://github.com/JDRIVO/rTorrent-Disk-Checker/blob/master/test.py)

#### This script will show you what torrents this program will delete without actually deleting torrents.

Results will output to your terminal and a text file named **testresult.txt**

This script accepts two arguments: 1. Torrent Size ( GB ) 2. Mount Point [Optional] Default mount point is "/"

`python test.py 69`

To send a test message:

`python messenger.py email pushbullet`

Accepted arguments: `email`, `pushbullet`, `pushover`, `telegram`, `discord`, `slack`
