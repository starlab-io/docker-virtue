#!/bin/bash
echo "$SSHPUBKEY" > /home/virtue/.ssh/authorized_keys
chmod 600 /home/virtue/.ssh/authorized_keys
