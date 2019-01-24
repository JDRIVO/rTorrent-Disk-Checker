        my @decimals = unpack 'U*', $self->{info_hash};
        my @script = split $/, `python2 /path/to/autodlcheck.py "$self->{ti}{torrentName}" "$self->{uploadMethod}{rtLabel}" "$self->{ti}{torrentSizeInBytes}" "@decimals"`;

        if ($script[0] eq "exit") {
                return;
        }

