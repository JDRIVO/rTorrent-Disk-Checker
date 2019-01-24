        my @script = split $/, `python /path/to/autodlcheck.py '$self->{ti}{torrentName}' '$self->{uploadMethod}{rtLabel}' '$self->{ti}{torrentSizeInBytes}'`;

        if ($script[0] eq "exit") {
                return;
        }

