from fabric.api import *

from os.path import expanduser
from paramiko.config import SSHConfig
#env.hosts = ['d1']
#env.user = 'benoit'
#env.key_filename = '~/.ssh/id_rsa_logentries'

env.use_ssh_config = True
env.ssh_config_path = '~/.ssh/config'

try:
    config_file = file(expanduser('~/.ssh/config'))
except IOError:
    pass
else:
    config = SSHConfig()
    config.parse(config_file)
    # From there config._config is a list of dictiionnaries {'host': [hostnames], 'config': {attributes}}
    for i in range(0,len(config._config)):
        print str(i), ' - ' , config._config[i]

def local_uname():
    local('uname -a')

def remote_uname():
    run('uname -a')

def main():
    local_uname()
    remote_uname()

if __name__ == "__main__":
    main()
