<< 'COMMENT'

Manual Setup Instructions:

1. Make the scripts executable by pasting the following command in your terminal:

chmod +x checker.py config.py remotecaller.py remover.py emailer.py

2. rtorrent.rc File Modification

2a. Add the following code to ~/.rtorrent.rc !! Update the path to checker.py !! Restart rtorrent once added:

Python 2:
method.set_key = event.download.inserted_new,checker,"d.stop=,$d.hash=", "execute.throw.bg=python2,/path/to/checker.py,$d.name=,$d.custom1=,$d.hash=,$d.directory=,$d.size_bytes="

Python 3:
method.set_key = event.download.inserted_new,checker,"d.stop=,$d.hash=", "execute.throw.bg=python3,/path/to/checker.py,$d.name=,$d.custom1=,$d.hash=,$d.directory=,$d.size_bytes="

3. SCGI Address Addition

3a. Enter the following command in your terminal to obtain your SCGI address/port:

grep -oP "^[^#]*scgi.* = \K.*" ~/.rtorrent.rc

3b. Update the scgi variable in line 7 of config.py with your own SCGI address/port.

4. Python Module Installations Required for IMDB Function (Skip if Unused)

4a. Enter the following commands in your terminal to install guessit and ImdbPie:

pip install guessit
pip install imdbpie

COMMENT

chmod +x checker.py config.py remotecaller.py remover.py emailer.py

rtorrent="/home/$USER/.rtorrent.rc"

if [ -z "$rtorrent" ]; then
    echo 'rtorrent.rc file not found. Terminating script.'
    exit
fi

sed -i '/event.download.inserted_new,checker,"d.stop=/d' $rtorrent
printf '\nDo you want the script to be run in Python 2 or 3?

Enter 2 for Python 2 or 3 for Python 3.\n'

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
method.set_key = event.download.inserted_new,checker,\"d.stop=,\$d.hash=\", \"execute.throw.bg=$version,$PWD/checker.py,\$d.name=,\$d.custom1=,\$d.hash=,\$d.directory=,\$d.size_bytes=\"" $rtorrent

printf '\nWill you be using the IMDB function of the script (Y/N)?\n'

while true; do
    read answer
    case $answer in

        [yY] )
                 pip install imdbpie -q || sudo pip install imdbpie -q || printf '\n\033[0;36mFailed to install Python module: imdbpie\033[0m\n\n'
                 pip install guessit -q || sudo pip install guessit -q || printf '\n\033[0;36mFailed to install Python module: guessit\033[0m\n'
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

scgi=$(grep -oP "^[^#]*scgi.* = \K.*" $rtorrent)

if [ -z "$scgi" ]; then
    printf '\n\033[0;36mSCGI address not found. Locate it in your rtorrent.rc file and manually update it in the config.py file.\033[0m\n'
else
    sed -i "7s~.*~scgi = '$scgi'~" config.py
    printf '\nSCGI address has been updated in your config.py file.\n'
fi

printf '\nConfiguration completed.\n'
printf '\nRtorrent has to be restarted in order for the changes to take effect. Do you want to the script to attempt a rtorrent restart now (Y/N)?\n'

while true; do
    read answer
    case $answer in

        [yY] )
                 restart_rtorrent=true
                 break
                 ;;

        [nN] )
                 restart_rtorrent=false
                 break
                 ;;

        * )
              echo 'Enter y or n'
              ;;
    esac
done

if [ $restart_rtorrent = true ];  then

    printf '\nAttempting to restart rtorrent.\n'
    instance=$(pgrep rtorrent)

    if [ $instance ]; then

        while true; do
            kill -KILL $instance

            if : ! pgrep rtorrent; then
                screen -d -m rtorrent

                if : pgrep rtorrent; then
                    printf '\nRtorrent has been restarted successfully.\n\n'
                else
                    printf '\n\033[0;36mFailed to restart rtorrent. Please restart rtorrent manually.\033[0m\n\n'
                fi

                break
            fi
        done
    else
        printf '\n\033[0;36mFailed to restart rtorrent. Please restart rtorrent manually.\033[0m\n\n'
    fi
fi
