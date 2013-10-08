from fabric.api import *
import fabric.network

import socket
from os.path import expanduser
from paramiko.config import SSHConfig
from fabric.exceptions import NetworkError
    
def local_uname():
    local('uname -a')

def remote_uname():
    with settings(warn_only=True):
        run('uname -a')

if __name__ == "__main__":
    env.use_ssh_config = True
    env.ssh_config_path = '~/.ssh/config'
    env.warn_only = True

    try:
        conf = SSHConfig()
        path = expanduser(env.ssh_config_path)
        with open(path) as fd:
            conf.parse(fd)
            env._ssh_config = conf
    except IOError:
        warn("Unable to load SSH config file '%s'" % path)

    for host_config in env._ssh_config._config:
        print host_config['host'], ' - ' , host_config['config'] 
    
    list_hosts = []
    for host_config in env._ssh_config._config:
        print host_config
        if host_config['host'][0]!='*':
            list_hosts.extend(host_config['host'])

    execute(remote_uname,hosts=list_hosts)
