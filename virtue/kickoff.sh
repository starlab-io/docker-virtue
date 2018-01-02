#!/bin/bash
~/set-authorized-keys.sh
mkdir ~/.xpra
xpra -d all,-window start :100 --start-child=gedit
/usr/sbin/sshd -D -f ~/sshd_config
