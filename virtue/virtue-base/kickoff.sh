#!/bin/bash

export XDG_RUNTIME_DIR=/home/virtue/.xpra
/virtue/set-authorized-keys.sh
mkdir -p /home/virtue/.xpra
xpra start --bind-ws=0.0.0.0:2023 --start-child="$APP_TO_RUN" --log-file=/home/virtue/xpra.log --exit-with-children
/usr/sbin/sshd -D -f /virtue/sshd_config
