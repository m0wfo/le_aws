#!/bin/sh

set -e # Exit script immediately on first error.
set -x # Print commands and their arguments as they are executed.

# Create a new user and set ssh keys
USERNAME=testuser
SSH_DIR=/home/$USERNAME/.ssh

if id -u $USERNAME >/dev/null 2>&1; then
        echo "user already exists"
else
	adduser --disabled-password $USERNAME
fi

if [ ! -d $SSH_DIR ]; then
    mkdir $SSH_DIR
fi
if [ ! -f $SSH_DIR/authorized_keys ]; then
    touch $SSH_DIR/authorized_keys
fi
cat /vagrant/test_key.pub >> $SSH_DIR/authorized_keys
chown -R $USERNAME:$USERNAME $SSH_DIR
