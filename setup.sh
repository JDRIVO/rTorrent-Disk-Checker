<< 'COMMENT'

Manual Setup Instructions:

1. Make the scripts executable by pasting the following command in your terminal:

chmod +x checker.py config.py remotecall.py

2. rtorrent.rc File Modifcation

2a. Add the following code to your rtorrent.rc file !! Update the path to checker.py !! Restart rtorrent once added:

method.set_key = event.download.inserted_new,script,"execute=/usr/bin/python,/path/to/checker.py,$d.name=,$d.custom1=,$d.size_bytes=,$d.hash="

3. Disk Check Function Configuration (Skip if Disabled)

3a. Enter the following command in your terminal to obtain your SCGI address/port:

find /home/$USER -name '.rtorrent.rc' -print | xargs grep -oP "^[^#]*scgi.* = \K.*"

3b. Update the scgi variable in line 14 of config.py with your own SCGI address/port.

4. Python Module Installations Required for IMDB Function (Skip if Unused)

4a. Enter the following commands in your terminal to install parse-torrent-name and ImdbPie:

pip install parse-torrent-name
pip install imdbpie

COMMENT

chmod +x checker.py config.py remotecall.py

echo "Will you be using the IMDB function of the script (Y/N)?"

while true; do
    read answer
    case $answer in

        [yY] )
                 pip install imdbpie -q || sudo pip install imdbpie -q
                 pip install parse-torrent-name -q || sudo pip install parse-torrent-name -q
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

scgi=$(find /home/$USER -name '.rtorrent.rc' -print | xargs grep -oP "^[^#]*scgi.* = \K.*")

if [ -z "$scgi" ]; then
    echo 'SCGI address not found. Manually update it in the config.py file.'
else
    sed -i "14s~.*~scgi = \"$scgi\"~" config.py
fi

rtorrent=$(find /home/$USER -name '.rtorrent.rc')
sed -i "1i\
method.set_key = event.download.inserted_new,script,\"execute=/usr/bin/python,$PWD/checker.py,\$d.name=,\$d.custom1=,\$d.size_bytes=,\$d.hash=\"" "$rtorrent"
printf "\nRestart rtorrent for the changes to take effect.\n\n"
printf  "\nFinished\n"
