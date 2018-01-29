#!/usr/bin/env bash

# Start DBUS
/etc/init.d/dbus start

# Start CUPS
/etc/init.d/cups start

# Start XPRA as the virtue user
#su - virtue -c "export XDG_RUNTIME_DIR=/home/virtue/.xpra && xpra start --mdns=no --start-child=/opt/cxoffice/bin/cxsetup --bind-tcp=0.0.0.0:10000 --exit-with-children --log-file=/home/virtue/.xpra/crossover.log && sleep infinity"
su - virtue -c "export XDG_RUNTIME_DIR=/home/virtue/.xpra && xpra start --mdns=no --start-child-after-connect=/opt/cxoffice/bin/cxsetup --bind-tcp=0.0.0.0:10000 --exit-with-children=no --log-file=/home/virtue/.xpra/crossover.log && sleep infinity"
