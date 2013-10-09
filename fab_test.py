from fabric.api import *
from paramiko.config import SSHConfig

import LogentriesSDK.client as LogClient 
import ConfigFile

import json
import logging
logging.basicConfig(filename='logentries_setup.log',level=logging.DEBUG)
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


try:
    account_key_file = open('logentries.json','r')
except:
    print 'Could not open logentries.json'
    logger.error('Could not open logentries.json')

try:
    account_key_json = json.load(account_key_file)
except:
    print 'Could not load json structure  from logentries.json'
    logger.error('Could not load json structure from logentries.json')
    account_key_json = None

if account_key_json is not None and 'account_key' in account_key_json.keys():
    account_key = account_key_json['account_key']
else:
    account_key = None
    print 'Could not retrieve logentries account key from json in logentries.json'
    logger.error('Could not retrieve logentries account key from json in logentries.json')
print 'account_key=%s'%account_key

def print_host_string():
    for item in env.host_string:
        print 'i=%s'%unicode(item)

def get_new_logs(log_paths,log_conf):
    """
    Returns the list of log paths that are not known by the log configuration associated to this instance
    """
    if log_conf is None or log_conf.get_host() is None:
        return log_paths
    conf_logs = log_conf.get_host().get_logs()
    new_logs = [log_path for log_path in log_paths if log_path not in conf_logs]
    print 'New logs detected on %s: %s'(log_conf.get_host().get_name(), new_logs)
    logger.info('New logs detected on %s: %s',log_conf.get_host().get_name(), new_logs)
    return new_logs

def create_host(log_client, instance_id):
    host = log_client.create_host(name='AWS_%s'%instance_id,location='AWS')
    print 'CREATED HOST: %s'%str(instance_id)
    logger.info('Created Host: %s',str(instance_id))
    if host is None:
        print 'Error when creating host for instance %s'%instance_id
        logger.error('Error when creating host for instance %s',instance_id)
    return host

def create_logs(log_client, host, log_paths):
    for log_name in log_paths:
        host = log_client.create_log_token(host=host,log_name=log_name)
    return host

def create_host_logs(log_client, instance_id, log_paths):
    host = create_host(log_client,instance_id)
    host = create_logs(log_client,host,log_paths)
    return ConfigFile.LoggingConfFile(name='logentries_%s.conf'%instance_id,host=host)
    

def get_ssh_config(host_name):
    for host_config in env._ssh_config._config:
        print host_config
        if host_config['host'][0] != '*' and host_config['config']['hostname'] == host_name:
            return host_config['host'][0],host_config['config']
    return None,{}


def get_instance_log_path():
    # Retrieve log file paths
    log_paths = []
    print env.host
    _,ssh_config = get_ssh_config(env.host)
    print ssh_config
    if 'logfilter' in ssh_config:
        log_filter = ssh_config['logfilter']
    else:
        log_filter = '^/var/log/.*log'
    print log_filter
    result = sudo("find / -type f -regex '%s'"%(log_filter))
    print result.stdout
    log_paths.extend([logpath.replace('\r','') for logpath in result.stdout.split('\n')])
    print 'Log Paths: %s'%log_paths
    logger.info('Log Paths: %s',log_paths)
    return log_paths


def get_instance_log_conf():
    """
    Returns the 
    """
    # Retrieve current log config
    log_conf = None
    instance_id,_ = get_ssh_config(env.host)
    filename = 'logentries_%s.conf'%instance_id
    log_conf_file = None
    rsyslog_conf_name = '/etc/rsyslog.d/%s'%filename
    local_conf_name = '/tmp/%s'%filename
    try:
        local('rm %s'%local_conf_name)
    except:
        print 'Could not remove %s. It may not exist'%(local_conf_name)
        logger.warning('Could not remove %s. It may not exist'%(local_conf_name))
    try:
        get(rsyslog_conf_name,local_conf_name)
    except:
        print '%s does not exist on instance %s'%(rsyslog_conf_name,instance_id)
        logger.warning('%s does not exist on instance %s',rsyslog_conf_name,instance_id)
    try:
        log_conf_file = open(local_conf_name,'rw')
    except:
        print 'Cannot open %s from instance %s'%(local_conf_name,instance_id)
        logger.warning('Cannot open %s from instance %s',local_conf_name,instance_id)
    if log_conf_file != None:
        log_conf = ConfigFile.LoggingConfFile.load_file(log_conf_file,filename)
        # Set the configuration file name
        log_conf.set_name(local_conf_name)
        log_conf.save()
    return log_conf


def update_instance_conf(log_paths, log_conf):
    """
    Returns the updated log_conf, taking into account new log files present on the instance as well as modifications made to the corresponding logentries host.
    """
    log_client = LogClient.Client(account_key)
    instance_id, config = get_ssh_config(env.host)

    if log_conf is None and len(log_paths)>0:
        print 'log_conf is None'
        log_conf = create_host_logs(log_client,instance_id,log_paths)
       
    elif log_conf is not None:
        print 'log_conf is not None'
        conf_host = log_conf.get_host()
        if conf_host is None:
            print 'Error. This instance configuration is missing the corresponding model!! instance_id=%s'%instance_id
            logger.error('Error. This instance configuration is missing the corresponding model!! instance_id=%s',instance_id)
            log_conf = create_host_logs(log_client,instance_id,log_paths)
            return log_conf

        if conf_host.get_key() is None:
            print 'Host %s has an logentries-rsyslog config file but no account key!!'%host.get_name()
            logger.warning('Host %s has an logentries-rsyslog config file but no account key!!',host.get_name())
            log_conf = create_host_logs(log_client,instance_id,log_paths)
            return log_conf

        account = log_client.get_account()
        matching_host = None
        for host in account.get_hosts():
            if host.get_key() == conf_host.get_key():
                matching_host = host
                break
        # If there is no matching host, then it is assumed that it was deleted from Logentries and that no configuration should be associated to this instance.
        if matching_host is None:
            log_conf = create_host_logs(log_client,instance_id,log_paths)
            return log_conf

        for new_log in get_new_logs(log_paths, log_conf):
            # Update matching host so that each new log becomes part of it.
            matching_host = log_client.create_log_token(host=matching_host,log_name=new_log)
        log_conf.set_host(matching_host)
    return log_conf


def deploy_log_conf(log_conf):
    if log_conf is None:
        print 'No RSyslog Configuration File was generated'
        logger.warning('No RSyslog Configuration File was generated')
        return
    # Save log config in a file and retrieve its name
    instance_id, config = get_ssh_config(env.host)
    local_file_name = log_conf.get_name()
    filename = local_file_name.rsplit('/')[0]
    rsyslog_conf_name = '/etc/rsyslog.d/%s'%filename
    
    try:
        put(local_file_name,rsyslog_conf_name,use_sudo=True)
    except:
        print 'Transfering %s to remote %s Failed'%(local_file_name,rsyslog_conf_name)
        logger.error('Transfering %s to remote %s Failed',local_file_name,rsyslog_conf_name)
        return
    try:
        sudo('service rsyslog restart')
    except:
        try:
            sudo('/etc/init.d/rsyslog restart')
        except:
            print 'Rsyslog could not be restarted on %s'%instance_id
            logger.error('Rsyslog could not be restarted on %s',instance_id)
            return
    print 'Rsyslog restarted successfully on %s'%instance_id
    logger.info('Rsyslog restarted successfully on %s',instance_id)
    return



def sync():
    log_paths = get_instance_log_path()
    print 'LOG_PATHS: %s'%log_paths
    logger.info('LOG_PATHS: %s'%log_paths)

    log_conf = get_instance_log_conf()
    print 'LOG_CONF_INIT: %s'%log_conf.to_json()
    logger.info('LOG_CONF_INIT: %s'%log_conf.to_json())

    log_conf = update_instance_conf(log_paths,log_conf)
    if log_conf is not None:
        print 'LOG_CONF_UPDATED: %s'%log_conf.to_json()
        logger.info('LOG_CONF_UPDATED: %s'%log_conf.to_json())
    else:
        print 'LOG_CONF_UPDATED: None'
        logger.info('LOG_CONF_UPDATED: None')

    deploy_log_conf(log_conf)

if __name__ == "__main__":
    env.use_ssh_config = True
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

    for host_config in env._ssh_config._config:
        print host_config['host'], ' - ' , host_config['config'] 
     
    list_hosts = []
    for host_config in env._ssh_config._config:
        print host_config
        if host_config['host'][0]!='*':
            list_hosts.extend(host_config['host'])

    execute(sync,hosts=list_hosts)
