#!/bin/bash
echo "$SSHPUBKEY" > ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
