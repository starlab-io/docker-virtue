#!/bin/bash

# This script is ran by the root user; add any necessary
# root commands that must be ran during startup such as
# adding iptable rules.


# Loop through the networkRules file and add them to the
# iptable rule chains
cat /home/virtue/networkRules | while read line; do
	iptables $line
done


# Since the virtue user has a `nologin` shell, we cannot simply
# `su` to virtue. Instead we execute the script on behalf of the
# virtue user.
su -s /bin/sh -c '/home/virtue/kickoff.sh' virtue
