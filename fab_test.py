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

global log_paths
global log_conf
try:
    account_key_file = open('logentries.json','r')
    account_key_json = json.load(account_key_file)
except:
    print 'Could not load json structure  from logentries.json'
    logger.error('Could not load json structure from logentries.json')

if 'account_key' in account_key_json.keys():
    account_key = account_key_json['account_key']
else:
    account_key = None
    print 'Could not retrieve logentries account key from json in logentries.json'
    logger.error('Could not retrieve logentries account key from json in logentries.json')

def print_host_string():
    for item in env.host_string:
        print 'i=%s'%unicode(item)

def get_new_logs(self):
    """
    Returns the list of log paths that are not known by the log configuration associated to this instance
    """
    global log_conf
    if log_conf is None or log_conf.get_host() is None:
        return self.get_logs()
    conf_logs = log_conf.get_host().get_logs()
    conf_log_names = [log.get_filename() for log in conf_logs]
    new_logs = [log_path for log_path in self.get_logs() if log_path not in conf_log_names]
    return new_logs


def get_ssh_config(host_name):
    for host_config in env._ssh_config._config:
        print host_config
        if host_config['host'][0] != '*' and host_config['config']['hostname'] == host_name:
            return host_config['host'][0],host_config['config']
    return None,{}


def get_instance_log_path():
    # Retrieve log file paths
    global log_paths
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
    return


def get_instance_log_conf():
    # Retrieve current log config
    global log_conf
    log_conf = None
    instance_id,_ = get_ssh_config(env.host)
    filename = 'logentries_%s.conf'%instance_id
    log_conf_file = None
    rsyslog_conf_name = '/etc/rsyslog.d/%s'%filename
    local_conf_name = '/tmp/%s'%filename
    try:
        get(rsyslog_conf_name,local_conf_name)
    except:
        print '%s does not exist on instance %s'%(rsyslog_conf_name,instance_id)
        logger.warning('%s does not exist on instance %s',rsyslog_conf_name,instance_id)
    try:
        log_conf_file = open(local_conf_name)
    except:
        print 'Cannot open %s from instance %s'%(local_conf_name,instance_id)
        logger.warning('Cannot open %s from instance %s',local_conf_name,instance_id)
    if log_conf_file != None:
        log_conf = ConfigFile.LoggingConfFile.load_file(log_conf_file,filename)
        # Set the configuration file name
        log_conf.set_name(filename)
        log_conf_file.close()
    print log_conf
    return


def deploy_log_conf():
    # Save log config in a file and retrieve its name
    instance_id, config = get_ssh_config(env.host)
    filename = 'logentries_%s.conf'%instance_id
    local_file_name = '/tmp/%s'%filename
    rsyslog_conf_name = '/etc/rsyslog.d/%s'%filename
    
    try:
        put(localfile_name,rsyslog_conf_name,use_sudo=True)
    except:
        print 'Transfering %s to remote %s Failed'%(local_file_name,rsyslog_conf_name)
        logger.error('Transfering %s to remote %s Failed',local_file_name,rsyslog_conf_name)
        
    try:
        sudo('/etc/init.d/rsyslog restart')
    except:
        print 'Rsyslog could not be restarted on %s'%instance_id
        logger.error('Rsyslog could not be restarted on %s',instance_id)
        return
    print 'Rsyslog restarted successfully on %s'%instance_id
    logger.info('Rsyslog restarted successfully on %s',instance_id)
    return


def update_instance_conf():
    """
    Returns the updated log_conf, taking into account new log files present on the instance as well as modifications made to the corresponding logentries host.
    """
    global log_conf
    global log_paths
    log_client = LogClient.Client(account_key)
    instance_id, config = get_ssh_config(env.host)

    if log_conf is None and len(log_paths)>0:
        host = log_client.create_host(name='AWS_%s'%instance_id,location='AWS')
        print 'CREATED HOST: %s'%str(instance_id)
        logger.info('Created Host: %s',str(instance_id))
        if host is None:
            print 'Error when creating host for instance %s'%instance_id
            logger.error('Error when creating host for instance %s',instance_id)
            return
        for log_name in log_paths:
            host = log_client.create_log_token(host=host,log_name=log_name)
        log_conf = ConfigFile.LoggingConfFile(name='logentries_%s.conf'%instance_id,host=host)
       
    elif log_conf is not None:
        conf_host = log_conf.get_host()
        if conf_host is None:
            print 'Error. This instance configuration is missing the corresponding model!! instance_id=%s'%instance_id
            logger.error('Error. This instance configuration is missing the corresponding model!! instance_id=%s',instance_id)
            return None

        account = log_client.get_account()
        matching_host = None
        for host in account.get_hosts():
            if host.get_key() == conf_host.get_key():
                matching_host = host
                break
        # If there is no matching host, then it is assumed that it was deleted from Logentries and that no configuration should be associated to this instance.
        if matching_host is None:
            return None
        # Addition to the matching host on Logentries are not taken into account (they may not make sense on the instance). Only log removal from Logentries are taken into account
        #for conf_log in conf_host.get_logs():
        #    matching_log = None
        #    for log in matching_host.get_logs():
        #        if log.get_key() == conf_log.get_key():
        #            matching_log = log.get_key()
        #            break
        # Remove conf_log from the current configuration if it no longer exsist on Logentries
        #    if matching_log is None:
        #        conf_host.remove_log(conf_log)
        # Finally add new logs if any. TODO: would it be better to do this at the beginning of this function?
        new_logs = get_new_logs()
        for new_log in new_logs:
            matching_host = log_client.create_log_token(host=matching_host,log_name=new_log)
        log_conf.set_host(matching_host)
    return


def sync():
    get_instance_log_path()
    get_instance_log_conf()
    update_instance_conf()
    deploy_log_conf()

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
