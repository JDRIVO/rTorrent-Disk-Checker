<< 'COMMENT'

Manual Setup Instructions:

Ensure system.file.allocate.set = 0. This is the default setting in rtorrent so it's not necessary to include it in your rtorrent.rc file.

1. Add the following code to your ~/.rtorrent.rc file !! making sure you update the path to server.py & client.py !!

execute.throw.bg = python3, "/path/to/server.py"
method.set_key = event.download.inserted_new, checker, "branch=((and,((not,((d.is_meta)))),((d.state)))),((dcheck))"
method.insert = dcheck, simple, d.stop=, "execute.throw.bg=python3,/path/to/client.py,$d.name=,$d.hash=,$d.directory=,$d.size_bytes="

2. Run python setup.py. If it fails, restart rtorrent and then progress to step 3.

3. SCGI Addition

3a. Enter the following command in your terminal to obtain your SCGI address/port or unix socket file path:

grep -oP "^[^#]*scgi.* = \K.*" ~/.rtorrent.rc

3b. Update the scgi variable in line 7 of config.py with your own SCGI address/port or unix socket file path.

COMMENT

rtorrent="$HOME/.rtorrent.rc"

if [[ ! -f "$rtorrent" ]]; then
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

# Delete existing entries
sed -i '/method.set_key = event.download.inserted_new, checker/d' $rtorrent
sed -i '/method.insert = dcheck, simple, d.stop=/d' $rtorrent
sed -i "\|execute.throw.bg = python3, \"$PWD/server.py|d" $rtorrent

# Add to file
sed -i '1imethod.set_key = event.download.inserted_new, checker, "branch=((and,((not,((d.is_meta)))),((d.state)))),((dcheck))"' $rtorrent
sed -i '1imethod.insert = dcheck, simple, d.stop=, "execute.throw.bg=python3,'"$PWD"'/client.py,$d.name=,$d.hash=,$d.directory=,$d.size_bytes="' $rtorrent
sed -i "1iexecute.throw.bg = python3, \"$PWD/server.py\"" $rtorrent

scgi=$(grep -oP "^[^#]*scgi.* = \K.*" $rtorrent)

if [[ -z "$scgi" ]]; then
	printf '\n\033[0;36mUnable to locate a SCGI address or unix socket file path. Check your rtorrent.rc file and update the SCGI variable in config.py.\033[0m\n'
	printf '\nRtorrent has to be restarted in order for the changes to take effect.'
else
	sed -i "7s~.*~scgi = '$scgi'~" config.py
	printf '\nSCGI has been updated in your config.py file.\n'
	python3 "$PWD/setup.py"
fi

printf '\nSetup has completed.\n'
