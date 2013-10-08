from fabric.api import *
from fabric import network

from paramiko.config import SSHConfig


def print_host_string():
    for item in env.host_string:
        print 'i=%s'%unicode(item)

def get_ssh_config(host_name):
    for host_config in env._ssh_config._config:
        if host_config['host'][0] == host_name:
            return host_config['config']
    return {}


def get_instance_log_path():
    # Retrieve log file paths
    log_paths = []
    print env.host
    ssh_config = get_ssh_config(env.host)
    print ssh_config
    if 'logfilter' in ssh_config:
        log_filter = ssh_config['logfilter']
    else:
        log_filter = '/var/log/.*log'
    print log_filter
    result = sudo("find -type f -regex '%s'"%(log_filter))
    log_paths.extend([logpath.split('\n')[0] for logpath in result.stdout.readlines()])
    print 'Log Paths: %s'%log_paths
    logger.info('Log Paths: %s',log_paths)
    self.set_logs([log_path for log_path in log_paths])
    return



def local_uname():
    local('uname -a')

def remote_uname():
    run('uname -a')

if __name__ == "__main__":

    try:
        config_file = file('ssh_config')
    except IOError:
        pass
    else:
        config = SSHConfig()
        config.parse(config_file)
        env._ssh_config = config
        for i in range(0,len(config._config)):
            print str(i), ' - ' , config._config[i]
            print 'ssh_config=%s'%network.ssh_config(config._config[i]['host'][0])

    for host_config in env._ssh_config._config:
        print host_config['host'], ' - ' , host_config['config'] 
     
    list_hosts = []
    for host_config in env._ssh_config._config:
        print host_config
        if host_config['host'][0]!='*':
            list_hosts.extend(host_config['host'])

    execute(get_instance_log_path,hosts=list_hosts)
