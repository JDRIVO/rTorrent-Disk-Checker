sed -i "629i\\
        my \$torrentHash = dataToHex(\$self->{info_hash});\n\
        my @script = split $/, \`python2 \"$PWD/autodlcheck.py\" \"\$self->{ti}{torrentName}\" \"\$self->{uploadMethod}{rtLabel}\" \"\$self->{ti}{torrentSizeInBytes}\" \"\$torrentHash\"\`;\n\n\
        if (\$script[0] eq \"exit\") {\n\
                return;\n\
        }" "/home/$USER/.irssi/scripts/AutodlIrssi/MatchedRelease.pm"

pkill irssi && screen -d -m irssi
