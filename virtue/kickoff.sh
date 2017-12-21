#!/bin/bash
/home/virtue/set-authorized-keys.sh
xpra -d all,-window start :100 --start-child=gedit
/usr/sbin/sshd -d -f /home/virtue/sshd_config
