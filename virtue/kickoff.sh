#!/bin/bash
/root/set-authorized-keys.sh
xpra start :100 --start-child=gedit
/usr/sbin/sshd -d
