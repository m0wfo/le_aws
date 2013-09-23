#!/bin/bash

################################################
#                                              #
#  This script installs various                #
#  components that are necessary to            #
#  run the logentries aws setup script.        #
#                                              # 
################################################

# Fail on error
set -e

#################################################
# Get info about system: 
# https://github.com/coto/server-easy-install/blob/master/lib/core.sh
#################################################

lowercase(){
    echo "$1" | sed "y/ABCDEFGHIJKLMNOPQRSTUVWXYZ/abcdefghijklmnopqrstuvwxyz/"
}

shootProfile(){
    OS=`lowercase \`uname\``
    KERNEL=`uname -r`
    MACH=`uname -m`

    if [ "${OS}" == "windowsnt" ]; then
	OS=windows
    elif [ "${OS}" == "darwin" ]; then
	OS=mac
    else
	OS=`uname`
	if [ "${OS}" = "SunOS" ] ; then
	    OS=Solaris
	    ARCH=`uname -p`
	    OSSTR="${OS} ${REV}(${ARCH} `uname -v`)"
	elif [ "${OS}" = "AIX" ] ; then
	    OSSTR="${OS} `oslevel` (`oslevel -r`)"
	elif [ "${OS}" = "Linux" ] ; then
	    if [ -f /etc/redhat-release ] ; then
		DistroBasedOn='RedHat'
		DIST=`cat /etc/redhat-release |sed s/\ release.*//`
		PSUEDONAME=`cat /etc/redhat-release | sed s/.*\(// | sed s/\)//`
		REV=`cat /etc/redhat-release | sed s/.*release\ // | sed s/\ .*//`
	    elif [ -f /etc/SuSE-release ] ; then
		DistroBasedOn='SuSe'
		PSUEDONAME=`cat /etc/SuSE-release | tr "\n" ' '| sed s/VERSION.*//`
		REV=`cat /etc/SuSE-release | tr "\n" ' ' | sed s/.*=\ //`
	    elif [ -f /etc/mandrake-release ] ; then
		DistroBasedOn='Mandrake'
		PSUEDONAME=`cat /etc/mandrake-release | sed s/.*\(// | sed s/\)//`
		REV=`cat /etc/mandrake-release | sed s/.*release\ // | sed s/\ .*//`
	    elif [ -f /etc/debian_version ] ; then
		DistroBasedOn='Debian'
		DIST=`cat /etc/lsb-release | grep '^DISTRIB_ID' | awk -F= '{ print $2 }'`
		PSUEDONAME=`cat /etc/lsb-release | grep '^DISTRIB_CODENAME' | awk -F= '{ print $2 }'`
		REV=`cat /etc/lsb-release | grep '^DISTRIB_RELEASE' | awk -F= '{ print $2 }'`
	    fi
	    if [ -f /etc/UnitedLinux-release ] ; then
		DIST="${DIST}[`cat /etc/UnitedLinux-release | tr "\n" ' ' | sed s/VERSION.*//`]"
	    fi
	    OS=`lowercase $OS`
	    DistroBasedOn=`lowercase $DistroBasedOn`
	    readonly OS
	    readonly DIST
	    readonly DistroBasedOn
	    readonly PSUEDONAME
	    readonly REV
	    readonly KERNEL
	    readonly MACH
	fi	
    fi
}
shootProfile
echo "OS: $OS"
echo "DIST: $DIST"
echo "PSUEDONAME: $PSUEDONAME"
echo "REV: $REV"
echo "DistroBasedOn: $DistroBasedOn"
echo "KERNEL: $KERNEL"
echo "MACH: $MACH"
echo "========"


#################################################
# Get info about system: 
# https://github.com/coto/server-easy-install/blob/master/lib/core.sh
#################################################

# install pip and python-dev if not present on the system
# Debian/Ubuntu
if $DistroBasedOn=="debian"; then
    echo "Installing python-pip"
    sudo apt-get install python-pip
    # TODO: should we avoid installing python-dev and paramiko for a 'local' setup?
    echo "Installing python-dev"
    sudo apt-get install python-dev
else
    echo "Debian based distribution is required. Found $DistroBasedOn.";
    exit 1;
fi
# Fedora
#sudo yum install python-pip

# install virutalenv
pip install virtualenv

# install scripts in home dir
cd
mkdir aws_script
cd aws_script

# create virtual environment
virtualenv env

# install boto and paramiko in the virtual environment
env/bin/pip install boto
env/bin/pip install paramiko

#mv ../logentries_aws.tar.gz .
#tar xvzf logentries_aws.tar.gz
#mv aws_template.json aws.json
