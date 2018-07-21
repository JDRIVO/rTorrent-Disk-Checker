        my @script = split $/, `python /home/user/scripts/autodlcheck.py '$self->{ti}{torrentName}' '$self->{uploadMethod}{rtLabel}' '$self->{ti}{torrentSizeInBytes}'`;

        if ($script[0] eq "exit") {
                return;
        }
