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
if [ "$DistroBasedOn" == "debian" ]; then
    # TODO: Check if this is really necessary or if this could be avoided by not specifying the virtualenv version
    echo "Updating apt"
    sudo apt-get update
    # Installing curl
    echo "Installing wget if not already present."
    sudo apt-get install wget
    # TODO: should we avoid installing python-dev and paramiko for a 'local' setup?
    echo "Installing python-dev"
    sudo apt-get install python-dev
elif [ "$OS" == "mac" ]; then
    # Checking the presence of python development tools and headers: http://stackoverflow.com/questions/4848566/check-for-existence-of-python-dev-files-from-bash-script 
    # first, makes sure distutils.sysconfig usable
    #if ! $(python -c "import sys\ntry:\n\timport distutils.sysconfig\nsys.exit(0)\nexcept:\n\tsys.exit(1)" &> /dev/null); then
    #   echo "Could not verify the presence of python development headers and tools. Please install them onto your system if they are not present (e.g. thourgh Xcode)." >&2
    #   exit 2;
    #fi

    # get include path for this python version
    INCLUDE_PY=$(python -c "from distutils import sysconfig as s; print s.get_config_vars()['INCLUDEPY']")
    if [ ! -f "${INCLUDE_PY}/Python.h" ]; then
       echo "Python development headers and tools could not be found. Please install them first (e.g. thourgh Xcode)." >&2
       exit 3;
    fi
else
    echo "Debian based distribution is required. Found $DistroBasedOn.";
    exit 1;
fi
# Fedora
#sudo yum install python-pip

# create working directory
if [ ! -d logentries ]; then
    mkdir logentries;
fi
cd logentries


# install virutalenv
if [ `command -v wget` != "" ]; then
   wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.10.tar.gz
elif [ `command -v curl` != "" ]; then
   curl -O --insecure https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.10.tar.gz
fi
tar xvfz virtualenv-1.10.tar.gz
python virtualenv-1.10/virtualenv.py env

GIT_REPO_LOCATION=file:///home/benoit/Logentries/git_repo/awswork

# install boto and paramiko in the virtual environment
env/bin/pip install boto
env/bin/pip install fabric
env/bin/pip install logentries
env/bin/pip install $GIT_REPO_LOCATION/LogentriesSDK/dist/LogentriesSDK-0.1.0.tar.gz
env/bin/pip install $GIT_REPO_LOCATION/LogentriesProvisioning/dist/LogentriesProvisioning-0.1.0.tar.gz

# Create aws conf file
echo '{"aws_secret_access_key": "0vNc1N5F84mnkyE6Z5hTRBpp1JIjozhMgszrQ6Mu",' >> aws.json
echo '"aws_access_key_id": "AKIAINT5AHHNNBWO3IOQ",' >> aws.json
echo '"usernames": ["ec2-user","root","ubuntu"],' >> aws.json
echo '"filters": [' >> aws.json
echo '{"ec2_filter": {"tag:Name":"ubuntu_w_key"},' >> aws.json
echo '"log_filter": "^/var/log/.*\\.log"}' >> aws.json
echo '],' >> aws.json
echo '"ssh_key_paths": ["~/.ssh/"]}' >> aws.json

# Create logentries conf file
echo '{"account_key": "9d1d1f88-eb3a-4522-8196-f45414530ef7"}' >> logentries.json

WORKING_DIR=`pwd`
# Create sync setup command
echo "#! $WORKING_DIR/env/bin/python" >> sync
echo 'import os' >> sync
echo 'from logentriesprovisioning import sync_log' >> sync
echo 'sync_log.main(working_dir=os.getcwd())' >> sync
chmod +x sync

# Create aws setup command
echo "#! $WORKING_DIR/env/bin/python" >> aws_sync
echo 'import os' >> aws_sync
echo 'from logentriesprovisioning import aws_client' >> aws_sync
echo 'from logentriesprovisioning import sync_log' >> aws_sync
echo 'aws_client.create_ssh_config(working_dir=os.getcwd())' >> aws_sync
echo 'sync_log.main(working_dir=os.getcwd())' >> aws_sync
chmod +x aws_sync
