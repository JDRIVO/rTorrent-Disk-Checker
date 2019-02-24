<< 'COMMENT'

Manual Setup Instructions:

1. Make the scripts executable by pasting the following command in your terminal:

chmod +x checker.py config.py remotecall.py


2. Disk Check Function Configuration (Skip if Disabled)

2a. Enter the following command in your terminal to obtain your SCGI address/port:

find /home/$USER -name '.rtorrent.rc' -print | xargs grep -oP "^[^#]*scgi.* = \K.*"

2b. Update the scgi variable in line 14 of config.py with your own SCGI address/port.

2c. Add this code to your rtorrent.rc file if you want the script to execute when you remotely or directly add torrents to rtorrent:
    !! Update the path to checker.py !! Restart rtorrent once added.

method.set_key = event.download.inserted_new,script,"execute=/usr/bin/python,/path/to/checker.py,$d.name=,$d.custom1=,$d.size_bytes=,$d.hash="

2d. Follow these steps if you want the script to be exexcuted by autodl-irssi:

1. Access the autodl-irssi filters from within rutorrent
2. Click on a filter and access the action tab
3. Set the .torrent action to 'rtorrent'
4. Paste the following code into the commands box !! Update the path to checker.py !!:

execute=/usr/bin/python,/path/to/checker.py,\$d.name=,\$d.custom1=,\$d.size_bytes=,\$d.hash=


3. Python Module Installations Required for IMDB Function (Skip if Unused)

3a. Enter the following commands in your terminal to install parse-torrent-name and ImdbPie:

pip install parse-torrent-name
pip install imdbpie

COMMENT

chmod +x checker.py config.py remotecall.py

scgi=$(find /home/$USER -name '.rtorrent.rc' -print | xargs grep -oP "^[^#]*scgi.* = \K.*")

if [ -z "$scgi" ]; then
    echo 'SCGI address not found. Manually change it in the config.py file.'
else
    sed -i "14s~.*~scgi = \"$scgi\"~" config.py
fi

echo "Do you want the script to execute before adding torrents to rtorrent remotely or directly (Y/N)?"

while true; do
    read answer
    case $answer in

        [yY] )
                 rtorrent=$(find /home/$USER -name '.rtorrent.rc')
                 sed -i "1i\
                 method.set_key = event.download.inserted_new,script,\"execute=/usr/bin/python,$PWD/checker.py,\$d.name=,\$d.custom1=,\$d.size_bytes=,\$d.hash=\"" "$rtorrent"
                 printf "Restart rtorrent for the changes take effect.\n\n"
                 break
                 ;;

        [nN] )
                 break
                 ;;

        * )
              echo "Enter y or n"
              ;;
    esac
done

echo "Will you be using the IMDB function of the script (Y/N)?"

while true; do
    read answer
    case $answer in

        [yY] )
                 pip install imdbpie || sudo pip install imdbpie
                 pip install parse-torrent-name || sudo pip install parse-torrent-name
                 break
                 ;;

        [nN] )
                 break
                 ;;

        * )
              echo "Enter y or n"
              ;;
    esac
done

echo "Do you want the script to be executed by autodl-irssi (Y/N)?"

while true; do
    read answer
    case $answer in

        [yY] )
                 echo "To enable this action perform the following:"
                 echo "1. Access the autodl-irssi filters from within rutorrent"
                 echo "2. Click on a filter and access the action tab"
                 echo "3. Set the .torrent action to 'rtorrent'"
                 echo "4. Paste the following code into the commands box:"
                 echo "execute=/usr/bin/python,$PWD/checker.py,\$d.name=,\$d.custom1=,\$d.size_bytes=,\$d.hash="
                 break
                 ;;

        [nN] )
                 break
                 ;;

        * )
              echo "Enter y or n"
              ;;
    esac
done

printf  "\nFinished\n"
