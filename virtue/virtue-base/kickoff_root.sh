#!/bin/bash

# This script is ran by the root user; add any necessary
# root commands that must be ran during startup such as
# adding iptable rules.

# Allow enough time for the network rules to be copied over
sleep 10

# Loop through the networkRules file and add them to the
# iptable rule chains
cat /etc/networkRules | while read line; do
	iptables $line
done


# Since the virtue user has a `nologin` shell, we cannot simply
# `su` to virtue. Instead we execute the script on behalf of the
# virtue user.
runuser -u virtue -- /home/virtue/kickoff.sh
