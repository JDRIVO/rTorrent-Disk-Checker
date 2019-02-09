: '

Manual Installation Instructions:

1. MatchedRealease.pm Modification

1a. Locate this file by entering the following command in your terminal:

 find /home/$USER -name MatchedRelease.pm

1b. Add the following code to line 629 of MatchedRelease.pm ensuring you update the path to autodlcheck.py:

        my $torrentHash = dataToHex($self->{info_hash});
        my @script = split $/, `python2 /path/to/autodlcheck.py "$self->{ti}{torrentName}" "$self->{uploadMethod}{rtLabel}" "$self->{ti}{torrentSizeInBytes}" "$torrentHash"`;

        if ($script[0] eq "exit") {
                return;
        }

1c. Restart autodl-irssi for the changes to take effect. Enter the following command to achieve this:

 pkill irssi && screen -d -m irssi


2. Disk Check Function Configuration (Skip if Disabled): Setting SCGI Address/Port

2a. Enter the following command in your terminal to obtain your SCGI address/port:

 find /home/$USER -name '.rtorrent.rc' -print | xargs grep '^network.scgi.open_port = '

2b. Update the host variable in line 16 of config.py with your own SCGI address/port.


3. Python Module Installations Required for IMDB Function (Skip if Unused)

3a. Enter the following commands in your terminal to install parse-torrent-name and ImdbPie:

 pip install parse-torrent-name
 pip install imdbpie

'

chmod +x autodlcheck.py
chmod +x config.py
chmod +x stop.py
chmod +x xmlrpc.py

scgi=$(find /home/$USER -name '.rtorrent.rc' -print | xargs grep -oP "^network.scgi.open_port = \K.*")

sed -i "9s~.*~folder_path = \"$PWD\"~" config.py
sed -i "16s~.*~host = \"scgi://$scgi\"~" config.py

sed -i "629i\\
        my \$torrentHash = dataToHex(\$self->{info_hash});\n\
        my @script = split $/, \`python2 \"$PWD/autodlcheck.py\" \"\$self->{ti}{torrentName}\" \"\$self->{uploadMethod}{rtLabel}\" \"\$self->{ti}{torrentSizeInBytes}\" \"\$torrentHash\"\`;\n\n\
        if (\$script[0] eq \"exit\") {\n\
                return;\n\
        }" "/home/$USER/.irssi/scripts/AutodlIrssi/MatchedRelease.pm"

chmod 444 "/home/$USER/.irssi/scripts/AutodlIrssi/MatchedRelease.pm"
pkill irssi && screen -d -m irssi

echo "Will you be using the IMDB function of the script?"

while true; do
    read answer
    case $answer in

        [yY] )
                 pip install imdbpie || sudo pip install imdbpie
                 pip install parse-torrent-name || sudo pip install parse-torrent-name
                 break
                 ;;

        [nN] )
                 exit
                 ;;

        * )
              echo "Enter y or n"
              ;;
    esac
done
