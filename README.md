# kscreen_replicator
Script that sets the max common resolution for two output sources and activates screen mirroring between them.

When there're two output sources with different available resolutions (i.e. a hd monitor and a projector) 
and outputs are replicated the size of elements in KScreen (windows, position of docks, etc...) are totally out
of range for the low-res output.

This script tries to set outputs at the maximun common resolution of both. Also enables screen replication 
trying to be a "one-click" solution.
