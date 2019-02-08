## Script Explanation

#### This script is capable of the following functions prior to autodl-irssi sending a torrent to rTorrent.

**1**. It can check your available disk space. If your free disk space is not large enough to accommodate a pending torrent, the script will delete torrents based on criteria defined in [config.py](https://github.com/GangaBanga/AUTODL-IRSSI-IMDB-DISK-CHECK/blob/master/config.py). The script will scan through your torrents from oldest to newest, ensuring the oldest torrent that meets your criteria is deleted first. If your disk space is still too low, the torrent will be sent to rtorrent in a stopped state.	

**2**. It can check the IMDB ratings/votes of a movie. The script will prevent autodl-irssi from sending a torrent to rTorrent if the IMDB rating/votes don't meet your minimum requirements.

## Installation

Run the installation script by entering the following command in your terminal:

`bash install.sh`

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
