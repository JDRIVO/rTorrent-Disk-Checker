<< 'COMMENT'

Manual Setup Instructions:

Ensure system.file.allocate.set = 0. This is the default setting in rtorrent so it's not necessary to include it in your rtorrent.rc file.

1. Add the following code to your ~/.rtorrent.rc file !! making sure to update the paths to server.py & client.py !!

execute.throw.bg = python3, "/path/to/server.py"
method.set_key = event.download.inserted_new, checker, "branch=((and,((not,((d.is_meta)))),((d.state)))),((dcheck))"
method.insert = dcheck, simple, d.stop=, "execute.throw.bg=python3,/path/to/client.py,$d.name=,$d.hash=,$d.directory=,$d.size_bytes="

2. SCGI Addition

2a. Enter the following command in your terminal to obtain your SCGI address/port or unix socket file path:

grep -oP "^[^#]*scgi.* = \K.*" ~/.rtorrent.rc

2b. Update the scgi variable in line 7 of config.py with your own SCGI address/port or unix socket file path.

3. Run python setup.py. If it fails, you will need to restart rtorrent for your changes to the rtorrent.rc file to take effect.

4. Optional: As an additional layer of protection you may add the close_low_diskspace command to rtorrent. This command will make rtorrent periodically
check your disk space and stop all downloading torrents if your disk space falls below a threshold.

schedule2 = low_diskspace,0,55,close_low_diskspace=1G

55 = the time in seconds the check is ran
1G = the threshold in Gigabytes

COMMENT


low_diskspace=false
rtorrent="$HOME/.rtorrent.rc"

if [[ ! -f $rtorrent ]]; then
	echo '.rtorrent.rc file not found in $HOME. Terminating script.'
	exit
fi

allocation=$(grep -oP "system.file.allocate.* = \K.*" $rtorrent)

if [[ $allocation == 1 ]]; then
	printf '\nThe script has detected that system.file.allocate is set to 1. This can cause the script to delete more files than necessary.'
	printf '\n\nEnter [Y] to permit the script to set system.file.allocate to 0 or Enter [Q] to exit: '

	while true; do
		read answer
		case $answer in

			[yY] )
				sed -i '/system.file.allocate/d' $rtorrent
				sed -i '1isystem.file.allocate.set = 0' $rtorrent
				break ;;

			[qQ] )
				exit ;;

			* )
				printf '\nEnter [Y] or [Q]: ' ;;

		esac
	done
fi

printf '\nDo you want rtorrent to stop all downloading torrents when your available space falls below a threshold? [Y]/[N]: '

while true; do
	read answer
	case $answer in

		[yY] )
			low_diskspace=true
			printf '\nPlease enter a number representing the time in seconds the check will run per cycle: '
			while true; do
				read interval
				case $interval in

					''|*[!0-9]* ) printf '\nPlease enter a number: ' ;;

					* ) break ;;

				esac
			done

			printf '\nPlease enter a number representing the threshold in Gigabytes: '

			while true; do
				read amount
				case $amount in

					''|*[!0-9]* ) printf '\nPlease enter a number: ' ;;

					* ) break ;;

				esac
			done

			sed -i '/schedule2 = low_diskspace/d' $rtorrent
			sed -i "1ischedule2 = low_diskspace,0,$interval,close_low_diskspace="$amount"G" $rtorrent
			break ;;

		[nN] )
			break ;;

		* )
			printf '\nEnter [Y] or [N]: ' ;;
	esac
done

# Delete existing entries
sed -i '/method.set_key = event.download.inserted_new, checker/d' $rtorrent
sed -i '/method.insert = dcheck, simple, d.stop=/d' $rtorrent
sed -i "\|execute.throw.bg = python3, \"$PWD/server.py|d" $rtorrent

# Add to file
sed -i '1imethod.set_key = event.download.inserted_new, checker, "branch=((and,((not,((d.is_meta)))),((d.state)))),((dcheck))"' $rtorrent
sed -i '1imethod.insert = dcheck, simple, d.stop=, "execute.throw.bg=python3,'"$PWD"'/client.py,$d.name=,$d.hash=,$d.directory=,$d.size_bytes="' $rtorrent
sed -i "1iexecute.throw.bg = python3, \"$PWD/server.py\"" $rtorrent

scgi=$(grep -oP "^[^#]*scgi.* = \K.*" $rtorrent)

if [[ -z $scgi ]]; then
	printf '\n\033[0;36mUnable to locate a SCGI address or unix socket file path. Check your rtorrent.rc file and update the SCGI variable in config.py.\033[0m\n'
	printf '\nRtorrent has to be restarted in order for the changes to take effect.'
else
	sed -i "7s~.*~scgi = '$scgi'~" config.py
	printf '\nSCGI has been updated in your config.py file.\n'

	if [ "$low_diskspace" = true ]; then
		python3 "$PWD/setup.py" $interval $amount
	else
		python3 "$PWD/setup.py"
	fi
fi

printf '\nSetup has completed.\n'
