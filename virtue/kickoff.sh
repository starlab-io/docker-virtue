#!/bin/bash

export XDG_RUNTIME_DIR=~/.xpra
~/set-authorized-keys.sh
mkdir ~/.xpra
xpra start --bind-tcp=0.0.0.0:2023 --html=on --start-child=$APP_TO_RUN
/usr/sbin/sshd -D -f ~/sshd_config
