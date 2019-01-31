#!/bin/bash

export XDG_RUNTIME_DIR=~/.xpra
~/set-authorized-keys.sh
mkdir ~/.xpra
xpra start --bind-ws=0.0.0.0:2023 --start-child="$APP_TO_RUN" --log-file=/home/virtue/xpra.log --exit-with-children
/usr/sbin/sshd -D -f ~/sshd_config
