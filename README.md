# Script Explanation

#### This script is capable of the following functions prior to autodl-irssi sending a torrent to rTorrent.

**1**. It can check your available disk space. If your free disk space is not large enough to accommodate a pending torrent, the script will delete torrents based on criteria defined in the script. The script will scan through your torrents from oldest to newest, ensuring the oldest torrent that meets your criteria is deleted first.

**2**. It can check the IMDB ratings/votes of a movie. The script will prevent autodl-irssi from sending a torrent to rTorrent if the IMDB rating/votes don't meet your minimum requirements.


# Configuration Instructions After Downloading [autodlcheck.py](https://github.com/GangaBanga/AUTODL-IRSSI-IMDB-DISK-CHECK/blob/master/autodlcheck.py)

####  1. MatchedRealease.pm Modification

**1a**. Locate this file by entering the following command in your terminal:

`find /home/$USER -name MatchedRelease.pm`

**1b**. Add [this code](https://github.com/GangaBanga/AUTODL-IRSSI-IMDB-DISK-CHECK/blob/master/MatchedRelease.pm) to [line 629 of MatchedRelease.pm](https://github.com/autodl-community/autodl-irssi/blob/35957c4258a28d467974c93155a0a1e9a2b599a4/AutodlIrssi/MatchedRelease.pm#L629) ensuring you update the path to autodlcheck.py.

**1c**. Restart autodl-irssi for the changes to take effect. Enter the following commands to achieve this:

`pkill irssi`

`screen -d -m irssi`

#### 2. Disk Check Function Configuration: Setting SCGI Address/Port

**2a**. Enter the following command in your terminal to obtain your SCGI address/port:

`find /home/$USER -name '.rtorrent.rc' -print | xargs grep 'network.scgi.open_port = ' /dev/null`

**2b**. Update the host variable in [line 22 of autodlcheck.py](https://github.com/GangaBanga/AUTODL-IRSSI-IMDB-DISK-CHECK/blob/master/autodlcheck.py#L22) with your own SCGI address/port.

#### 3. Python Module Installations Required for IMDB Function - Skip if Unused

**3a**. Enter the following commands in your terminal to install [parse-torrent-name](https://github.com/divijbindlish/parse-torrent-name) and [ImdbPie](https://github.com/richardARPANET/imdb-pie):

`pip install parse-torrent-name`

`pip install imdbpie`

# Usage

To enable the script set the .torrent action in autodl-irssi to **rtorrent**.

<p align="center">
  <img src="https://cdn.pbrd.co/images/HoXZLSN.png">
</p>

# [Test Script](https://github.com/GangaBanga/AUTODL-IRSSI-IMDB-DISK-CHECK/blob/master/testscript.py)

#### This script will show you what torrents the script will delete without actually deleting torrents.

Results will outputted to your terminal and a text file named **testresult.txt**

Enter the following command in your terminal to run it:

`python testscript.py 69`

**69** = torrent size in gigabytes
