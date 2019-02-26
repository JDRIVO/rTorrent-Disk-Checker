<< 'COMMENT'

Manual Setup Instructions:

1. Make the scripts executable by pasting the following command in your terminal:

chmod +x checker.py config.py remotecall.py

2. rtorrent.rc File Modification

2a. Locate your rtorrent.rc file via this command:

find /home/$USER -name '.rtorrent.rc'

2b. Add the following code to your rtorrent.rc file !! Update the path to checker.py !! Restart rtorrent once added:

Python 2:
method.set_key = event.download.inserted_new,checker,"execute=python,/path/to/checker.py,$d.name=,$d.custom1=,$d.size_bytes=,$d.hash="

Python 3:
method.set_key = event.download.inserted_new,checker,"execute=python3,/path/to/checker.py,$d.name=,$d.custom1=,$d.size_bytes=,$d.hash="

3. SCGI Address Addition

3a. Enter the following command in your terminal to obtain your SCGI address/port:

find /home/$USER -name '.rtorrent.rc' -print | xargs grep -oP "^[^#]*scgi.* = \K.*"

3b. Update the scgi variable in line 9 of config.py with your own SCGI address/port.

4. Python Module Installations Required for IMDB Function (Skip if Unused)

4a. Enter the following commands in your terminal to install parse-torrent-name and ImdbPie:

pip install parse-torrent-name
pip install imdbpie

COMMENT

chmod +x checker.py config.py remotecall.py

rtorrent=$(find /home/$USER -name '.rtorrent.rc')

if [ -z "$rtorrent" ]; then
    echo 'Unable to locate your rtorrent.rc file. Terminating script.'
    exit
fi

echo 'Do you want the script to be run in Python 2 or 3? Python 3 is faster.

Enter 2 for Python 2 or 3 for Python 3.'

while true; do
    read answer
    case $answer in

        [2] )
                 version='python2'
                 break
                 ;;

        [3] )
                 version='python3'
                 break
                 ;;

        * )
              echo 'Enter 2 or 3'
              ;;
    esac
done

sed -i "1i\
method.set_key = event.download.inserted_new,checker,\"execute=$version,$PWD/checker.py,\$d.name=,\$d.custom1=,\$d.size_bytes=,\$d.hash=\"" "$rtorrent"

scgi=$(find /home/$USER -name '.rtorrent.rc' | xargs grep -oP "^[^#]*scgi.* = \K.*")

if [ -z "$scgi" ]; then
    echo 'SCGI address not found. Locate it in your rtorrent.rc file and manually update it in the config.py file.'
else
    sed -i "9s~.*~scgi = \"$scgi\"~" config.py
fi

echo 'Will you be using the IMDB function of the script (Y/N)?'

while true; do
    read answer
    case $answer in

        [yY] )
                 pip install imdbpie -q || sudo pip install imdbpie -q || echo 'Failed to install Python module: imdbpie'
                 pip install parse-torrent-name -q || sudo pip install parse-torrent-name -q || echo 'Failed to install Python module: parse-torrent-name'
                 break
                 ;;

        [nN] )
                 break
                 ;;

        * )
              echo 'Enter y or n'
              ;;
    esac
done

printf "\nRestart rtorrent for the changes to take effect.\n\n"
printf  "Configuration completed.\n\n"
