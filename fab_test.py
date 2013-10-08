from fabric.api import *
from fabric import network

from os.path import expanduser
from paramiko.config import SSHConfig
#env.hosts = ['d1']
#env.user = 'benoit'
#env.key_filename = '~/.ssh/id_rsa_logentries'

    # From there config._config is a list of dictiionnaries {'host': [hostnames], 'config': {attributes}}

def print_host_string():
    for item in env.host_string:
        print 'i=%s'%unicode(item)


def local_uname():
    local('uname -a')

def remote_uname():
    run('uname -a')

if __name__ == "__main__":
#    env.use_ssh_config = True
#    env.ssh_config_path = '~/.ssh/config'

    try:
        config_file = file(expanduser('~/.ssh/config'))
    except IOError:
        pass
    else:
        config = SSHConfig()
        config.parse(config_file)
        for i in range(0,len(config._config)):
            print str(i), ' - ' , config._config[i]
            print 'ssh_config=%s'%network.ssh_config(config._config[i]['host'][0])
        execute(remote_uname,hosts=[config._config[i]['host'][0] for i in range(1,len(config._config))])
