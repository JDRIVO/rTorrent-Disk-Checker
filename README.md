## Script Explanation

#### This script is capable of the following functions prior to autodl-irssi sending a torrent to rTorrent.

**1**. It can check your available disk space. If your free disk space is not large enough to accommodate a pending torrent, the script will delete torrents based on criteria defined in the script. The script will scan through your torrents from oldest to newest, ensuring the oldest torrent that meets your criteria is deleted first. If your disk space is still too low, the torrent will be sent to rtorrent in a stopped state.	

**2**. It can check the IMDB ratings/votes of a movie. The script will prevent autodl-irssi from sending a torrent to rTorrent if the IMDB rating/votes don't meet your minimum requirements.


## Configuration Instructions After Downloading [autodlcheck.py](https://github.com/GangaBanga/AUTODL-IRSSI-IMDB-DISK-CHECK/blob/master/autodlcheck.py)

####  1. MatchedRealease.pm Modification

**1a**. Locate this file by entering the following command in your terminal:

`find /home/$USER -name MatchedRelease.pm`

**1b**. Add [this code](https://github.com/GangaBanga/AUTODL-IRSSI-IMDB-DISK-CHECK/blob/master/MatchedRelease.pm) to [line 629 of MatchedRelease.pm](https://github.com/autodl-community/autodl-irssi/blob/35957c4258a28d467974c93155a0a1e9a2b599a4/AutodlIrssi/MatchedRelease.pm#L629) **ensuring you update the path to autodlcheck.py.**

**1c**. Restart autodl-irssi for the changes to take effect. Enter the following command to achieve this:

`pkill irssi && screen -d -m irssi`

#### 2. Disk Check Function Configuration (Skip if Disabled): Setting SCGI Address/Port

**2a**. Enter the following command in your terminal to obtain your SCGI address/port:

`find /home/$USER -name '.rtorrent.rc' -print | xargs grep 'network.scgi.open_port = ' /dev/null`

**2b**. Update the host variable in [line 13 of autodlcheck.py](https://github.com/GangaBanga/AUTODL-IRSSI-IMDB-DISK-CHECK/blob/master/autodlcheck.py#L13) with your own SCGI address/port.

#### 3. Python Module Installations Required for IMDB Function (Skip if Unused)

**3a**. Enter the following commands in your terminal to install [parse-torrent-name](https://github.com/divijbindlish/parse-torrent-name) and [ImdbPie](https://github.com/richardARPANET/imdb-pie):

`pip install parse-torrent-name`

`pip install imdbpie`

## Usage

To enable the script set the .torrent action in autodl-irssi to **rtorrent**.

<p align="center">
  <img src="https://cdn.pbrd.co/images/HoXZLSN.png">
</p>

## [Test Script](https://github.com/GangaBanga/AUTODL-IRSSI-IMDB-DISK-CHECK/blob/master/testscript.py)

#### This script will show you what torrents the script will delete without actually deleting torrents.

Results will output to your terminal and a text file named **testresult.txt**

Enter the following command in your terminal to run it:

`python testscript.py 69`

**69** = torrent size in gigabytes

## Illustration of User Defined Variables 

```python
enable_disk_check = yes

host = 'scgi://127.0.0.1:5000'

minimum_space = 5

minimum_filesize = 5
minimum_age = 15
minimum_ratio = 1.2

fallback_age = 7
fallback_ratio = no

trackers = {
                     "demonoid.pw" : [include],
                     "hdme.eu" : [exclude],
                     "redacted.ch" : [1, 7, 1.2, no, no],
                     "hd-torrents.org" : [3, 5, 1.3, 9, 1.3],
                     "privatehd.to" : [5, 6, 1.2, 12, no],
                     "apollo.rip" : [2, 5, 1.4, no, 1.8],
           }

trackers_only = yes

labels = {
                     "Trash" : [include],
                     "TV" : [exclude],
                     "HD" : [1, 5, 1.2, 15, 1.2],
         }

labels_only = no

exclude_unlabelled = yes

imdb = {
                     "Hollywood Blockbusters" : [7, 80000, yes],
                     "Bollywood Classics" : [8, 60000, no],               
       }
```
