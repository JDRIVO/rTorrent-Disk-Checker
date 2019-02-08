        my $torrentHash = dataToHex($self->{info_hash});
        my @script = split $/, `python2 /path/to/autodlcheck.py "$self->{ti}{torrentName}" "$self->{uploadMethod}{rtLabel}" "$self->{ti}{torrentSizeInBytes}" "$torrentHash"`;

        if ($script[0] eq "exit") {
                return;
        }

