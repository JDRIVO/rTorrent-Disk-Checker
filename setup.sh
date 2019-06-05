<< 'COMMENT'

Manual Setup Instructions:

Ensure system.file.allocate.set = 0. This is the default setting in rtorrent so it's not necessary to include it in your rtorrent.rc file.

1. Make the scripts executable by pasting the following command in your terminal:

chmod +x checker.py config.py remotecaller.py remover.py emailer.py cacher.py cleaner.py

2. rtorrent.rc File Modification

2a. Add the following code to ~/.rtorrent.rc !! Update the path to cleaner, cacher.py & checker.py !! Restart rtorrent once added:

Python 2:
schedule2 = cleanup, 0, 0, "execute.throw.bg=python2,/path/to/cleaner.py"
schedule2 = update_cache, 1, 30, "execute.throw.bg=python2,/path/to/cacher.py"
#                            30 is the time in seconds to update torrent information
method.set_key = event.download.inserted_new, checker, d.stop=, "execute.throw.bg=python2,/path/to/checker.py,$d.name=,$d.custom1=,$d.hash=,$d.directory=,$d.size_bytes="

Python 3:
schedule2 = cleanup, 0, 0, "execute.throw.bg=python3,/path/to/cleaner.py"
schedule2 = update_cache, 1, 30, "execute.throw.bg=python3,/path/to/cacher.py"
#                            30 is the time in seconds to update torrent information
method.set_key = event.download.inserted_new, checker, d.stop=, "execute.throw.bg=python3,/path/to/checker.py,$d.name=,$d.custom1=,$d.hash=,$d.directory=,$d.size_bytes="

3. SCGI Addition

3a. Enter the following command in your terminal to obtain your SCGI address/port or unix socket file path:

grep -oP "^[^#]*scgi.* = \K.*" ~/.rtorrent.rc

3b. Update the scgi variable in line 7 of config.py with your own SCGI address/port or unix socket file path.

4. Python Module Installations Required for IMDB Function (Skip if Unused)

4a. Enter the following commands in your terminal to install guessit and ImdbPie:

pip install guessit
pip install imdbpie

COMMENT

chmod +x checker.py config.py remotecaller.py remover.py emailer.py cacher.py cleaner.py

rtorrent="/home/$USER/.rtorrent.rc"

if [ ! -f "$rtorrent" ]; then
    echo 'rtorrent.rc file not found. Terminating script.'
    exit
fi

allocation=$(grep -oP "system.file.allocate.* = \K.*" $rtorrent)

if [ $allocation == 1 ]; then
    printf '\nThe script has detected that system.file.allocate is set to 1. This can cause the script to delete more files than necessary.'
    printf '\n\nEnter [Y] to permit the script to set system.file.allocate to 0 or Enter [Q] to exit: '

    while true; do
            read answer
            case $answer in

                    [yY] )
                                    sed -i '/system.file.allocate/d' $rtorrent
                                    sed -i '1i system.file.allocate.set = 0' $rtorrent
                                    break
                                    ;;

                    [qQ] )
                                    exit
                                    ;;

                    * )
                                    printf '\nEnter [Y] or [Q]: '
                                    ;;
            esac
    done
fi

sed -i '/schedule2 = cleanup/d' $rtorrent
sed -i '/schedule2 = update_cache/d' $rtorrent
sed -i '/event.download.inserted_new, checker, d.stop=/d' $rtorrent
printf '\nDo you want the script to be run in Python 2 or 3?

Enter [2] for Python 2 or [3] for Python 3: '

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
              printf '\nEnter [2] or [3]: '
              ;;
    esac
done

while true; do
    printf '\nEnter the time in seconds to repeatedly update torrent information: '
    read update
    printf "\nYou have entered $update seconds\n"
    printf '\nEnter [Y] to confirm or [N] to re-enter: '
    read answer

    if [[ $answer =~ ^[Yy]$ ]]; then
            break
    fi
done

sed -i "1i\
method.set_key = event.download.inserted_new, checker, d.stop=, \"execute.throw.bg=$version,$PWD/checker.py,\$d.name=,\$d.custom1=,\$d.hash=,\$d.directory=,\$d.size_bytes=\"" $rtorrent

sed -i "1i\
schedule2 = update_cache, 1, $update, \"execute.throw.bg=$version,$PWD/cacher.py\"" $rtorrent

sed -i "1i\
schedule2 = cleanup, 0, 0, \"execute.throw.bg=$version,$PWD/cleaner.py\"" $rtorrent

printf '\nWill you be using the IMDB function of the script [Y]/[N]?: '

while true; do
    read answer
    case $answer in

        [yY] )
                 pip install imdbpie -q && printf '\nimdbpie installed\n' || sudo pip install imdbpie -q && printf '\nimdbpie installed\n' || printf '\n\033[0;36mFailed to install Python module: imdbpie\033[0m\n\n'
                 pip install guessit -q && printf '\nguessit installed\n' || sudo pip install guessit -q && printf '\nguessit installed\n' || printf '\n\033[0;36mFailed to install Python module: guessit\033[0m\n'
                 break
                 ;;

        [nN] )
                 break
                 ;;

        * )
              printf '\nEnter [Y] or [N]: '
              ;;
    esac
done

scgi=$(grep -oP "^[^#]*scgi.* = \K.*" $rtorrent)

if [ -z "$scgi" ]; then
    printf '\n\033[0;36mUnable to locate a SCGI address or unix socket file path. Check your rtorrent.rc file and update the SCGI variable in config.py.\033[0m\n'
else
    sed -i "7s~.*~scgi = '$scgi'~" config.py
    printf '\nSCGI has been updated in your config.py file.\n'
fi

printf '\nConfiguration completed.\n'
printf '\nRtorrent has to be restarted in order for the changes to take effect.

Do you want to the script to attempt a rtorrent restart now [Y]/[N]?: '

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
              printf '\nEnter [Y] or [N]: '
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
