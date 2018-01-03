#!/bin/bash
~/set-authorized-keys.sh
mkdir ~/.xpra
xpra -d all,-window start :100 --start-child=gedit
xpra start --bind-tcp=0.0.0.0:2023 --html=on --start-child=gedit
xpra start --bind-tcp=0.0.0.0:2024 --html=on --start-child=firefox
/usr/sbin/sshd -D -f ~/sshd_config
