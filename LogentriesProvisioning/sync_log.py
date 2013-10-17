from fabric.api import *
from paramiko.config import SSHConfig

import logentriessdk.client as LogClient 
from logentriesprovisioning import ConfigFile
import logentriesprovisioning.constants
from logentriesprovisioning import utils

import os
import sys
import json
import logging

# get global logger
logger = logging.getLogger('sync')


def get_ssh_config(host_name):
    """
    Args:
    host_name is the name of a host in the current ssh_config_file.
    Returns the host name  and the ssh configuration of the host matching host_name.
    Returns None and an empty dictionary if no host matches host_name.
    """
    for host_config in env._ssh_config._config:
        if host_config['host'][0] != '*' and host_config['config']['hostname'] == host_name:
            return host_config['host'][0],host_config['config']
    return None,{}


def get_instance_log_paths(instance_id, ssh_config):
    """
    Args:
    instance_id is an instance identifier.
    ssh_config is the ssh configuration associated to the instance with id 'instance_id'.
    Returns the list of log paths for the instance with id 'instance_id'.
    Returns an empty list if no log file paths could be retrieved from the instance.
    """
    host_name = 'AWS_%s'%instance_id
    log_paths = []
    # Retrieve log filter if defined in ssh_config file. Else apply default filter.
    if 'logfilter' in ssh_config:
        log_filter = ssh_config['logfilter']
    else:
        log_filter = '^/var/log/.*log'

    # Retrieve log file paths that match the log filter
    output = sudo("find / -type f -regex '%s'"%(log_filter))

    if not output.succeeded:
        logger.warning('Could not retrieve log paths. hostname=%s, log_filter=%s, message=%s', host_name, log_filter, output.stdout.replace('\n',' \\ '))
        return log_paths
    # Clean output
    log_paths.extend([logpath.replace('\r','') for logpath in result.stdout.split('\n')])
    logger.info('Log Paths: %s',log_paths)
    return log_paths


def get_instance_log_conf(instance_id):
    """
    Args:
    instance_id is an instance identifier.
    Returns the Logentries-RSyslog configuration file deployed on the instance or None if the configuration does not exist or could not be retrieved. 
    """
    # Retrieve current log config file
    log_conf_file = None
    host_name='AWS_%s'%instance_id
    filename = 'logentries_%s.conf'%host_name
    rsyslog_conf_name = '/etc/rsyslog.d/%s'%filename
    local_conf_name = '/tmp/%s'%filename
    
    # Remove local version of the file if already present as it may be obsolete
    try:
        local('rm %s'%local_conf_name)
    except:
        logger.debug('No version of the file present locally. host_name=%s, remote_filename=%s, local_filename=%s', host_name, rsyslog_conf_name, local_conf_name)
    # Get remote conf file or return None if it cannot be retrieved
    try:
        get(rsyslog_conf_name,local_conf_name)
    except:
        logger.debug('No version of the file present remotely. host_name=%s, remote_filename=%s, local_filename=%s', host_name, rsyslog_conf_name, local_conf_name)
        return None
    # Open conf file or return None if it cannot be opened
    try:
        log_conf_file = open(local_conf_name,'r')
    except:
        logger.error('Cannot open Logentries-Rsyslog configuration file. host_name=%s, local_filename=%s', host_name, local_conf_name)
        return None
    logger.debug('Remote Logentries-Rsyslog configuration file successfully retrieved and opened. filename=%s, hostname=%s', rsyslog_conf_name, host_name)
    return log_conf_file


def load_conf_file(log_conf_file,instance_id):
    """
    """
    log_conf = None
    # conf file or return None if it cannot be opened
    if log_conf_file != None:
        log_conf = ConfigFile.LoggingConfFile.load_file(log_conf_file,instance_id)
        log_conf_file.close()
    return log_conf


def get_logentries_host(log_client,conf_host):
    """
    """
    account = log_client.get_account()
    matching_host = None
    for host in account.get_hosts():
        if host.get_key() == conf_host.get_key():
            matching_host = host
            break
    return matching_host

def update_instance_conf(log_paths, log_conf):
    """
    Returns the updated log_conf, taking into account new log files present on the instance as well as modifications made to the corresponding logentries host.
    """
    log_client = LogClient.Client(logentriesprovisioning.constants.ACCOUNT_KEY)
    instance_id, config = get_ssh_config(env.host)

    if log_conf is None and len(log_paths)>0:
        host = utils.create_host_logs(log_client,instance_id,log_paths)
        log_conf = ConfigFile.LoggingConfFile(name='logentries_%s.conf'%host.get_name(),host=host)
       
    elif log_conf is not None:
        conf_host = log_conf.get_host()
        if conf_host is None:
            logger.error('Error. This instance configuration is missing the corresponding model!! instance_id=%s',instance_id)
            host = utils.create_host_logs(log_client,instance_id,log_paths)
            log_conf = ConfigFile.LoggingConfFile(name='logentries_%s.conf'%host.get_name(),host=host)
            return log_conf

        if conf_host.get_key() is None:
            logger.warning('Host %s has an logentries-rsyslog config file but no account key!!',host.get_name())
            host = utils.create_host_logs(log_client,instance_id,log_paths)
            log_conf = ConfigFile.LoggingConfFile(name='logentries_%s.conf'%host.get_name(),host=host)
            return log_conf
        
        logentries_host = get_logentries_host(log_client,conf_host)
        # If there is no matching host, then it is assumed that it was deleted from Logentries and that no configuration should be associated to this instance.
        if logentries_host is None:
            host = utils.create_host_logs(log_client,instance_id,log_paths)
            log_conf = ConfigFile.LoggingConfFile(name='logentries_%s.conf'%host.get_name(),host=host)
            return log_conf

        for new_log in utils.get_new_logs(log_paths, log_conf):
            logentries_host = log_client.create_log_token(host=logentries_host,log_name=new_log)
        log_conf.set_host(logentries_host)
    return log_conf


def restart_rsyslog(instance_id):
    """
    Restarts RSyslog service.
    Returns True if and only if RSyslog was successfully restarted. 
    """
    host_name = 'AWS_%s'%instance_id
    try:
        output = sudo('service rsyslog restart')
    except:
        try:
            sudo('/etc/init.d/rsyslog restart')
        except:
            logger.error('Rsyslog could not be restarted. hostname=%s', host_name)

    if output.succeeded:
        logger.info('Rsyslog restarted successfully. hostname=%s', host_name)
    else:
        logger.error('Error restarting Rsyslog. hostname=%s, message=%s', host_name, output.stdout)
    return output.succeeded


def deploy_log_conf(instance_id, log_conf):
    """
    Deploys Logentries-RSyslog configuration file 'log_conf' and restart RSyslog so that this file is taken into account.
    Returns True if and only if log_conf was successfully deployed and RSyslog was successfully restarted. 
    """
    host_name = 'AWS_%s'%instance_id
    if log_conf is None:
        logger.warning('No RSyslog Configuration File was generated. hostname=%s', host_name)
        return False

    # Get current instance information
    local_conf_name = log_conf.get_name()

    # Save configuration in a file
    log_conf_file = log_conf.save()

    filename = os.path.basename(log_conf_file.name)
    log_conf_file.close()

    remote_conf_name = '/etc/rsyslog.d/%s'%filename
    
    try:
        put(local_conf_name,remote_conf_name,use_sudo=True)
    except:
        logger.error('Transfering %s to remote %s Failed',local_conf_name,remote_conf_name)
        return False
    logger.debug('Configuration file successfully deployed. local_filename=%s, remote_filename=%s, hostanme=%s', local_conf_name, remote_conf_name, host_name)
    return True


@parallel
def sync():
    # Get current instance information
    instance_id, ssh_config = get_ssh_config(env.host)

    log_paths = get_instance_log_paths(instance_id, ssh_config)
    logger.info('LOG_PATHS: %s'%log_paths)

    log_conf_file = get_instance_log_conf(instance_id)
    if log_conf is None:
        return
    log_conf = load_conf_file(log_conf_file,instance_id)

    if log_conf is None:
        logger.info('No existing logentries rsyslog configuration file was found on instance %s',instance_id)
        return

    log_conf = update_instance_conf(log_paths,log_conf)
    if log_conf is None:
        logger.info('No new rsyslog configuration was detected on instance %s',instance_id)
        return

    deploy_log_conf(instance_id, log_conf)
    # Restart Rsyslog
    restart_rsyslog(instance_id)  


def remove_log_conf(instance_id):
    """
    """
    host_name='AWS_%s'%instance_id
    remote_conf_filename = '/etc/rsyslog.d/logentries_%s.conf'%host_name

    try:
        # Remove logentries rsyslog conf file
        output = sudo('rm %s'%remote_conf_filename)
    except:
        logger.error('Could not remove %s from %s.',remote_conf_filename, host_name)
    if output.succeeded:
        logger.info('Successfully removed %s from %s.',remote_conf_filename, host_name)
    else:
        logger.warning('Could not remove %s from %s.',remote_conf_filename, host_name)
    return output.succeeded
        

@parallel
def deprovision(instance_id):
    """
    Deprovisions the instance by removing the logentries rsyslog config file from it, restarting rsyslog and removing the corresponding host from the logentries system.
    """
    log_conf_file = get_instance_log_conf(instance_id)
    if log_conf_file is None:
        return False
    log_conf = load_conf_file(log_conf_file,instance_id)

    if log_conf is None:
        logger.info('No existing logentries rsyslog configuration file was found on instance %s',instance_id)
        return

    conf_host = log_conf.get_host()
    if conf_host is None:
        logger.error('Error. This instance configuration is missing the corresponding model!! instance_id=%s',instance_id)
        return
    
    if conf_host.get_key() is None:
        logger.error('Host %s has an logentries-rsyslog config file but no account key!!',host.get_name())
    else:
        log_client = LogClient.Client(logentriesprovisioning.constants.ACCOUNT_KEY)
        logentries_host = get_logentries_host(log_client,conf_host)
        # If there is no matching host, then it is assumed that it was deleted from Logentries and that no configuration should be associated to this instance.
        if logentries_host is not None:
            succeeded = log_client.remove_host(logentries_host)
            if succeeded:
                logger.warning('Host %s was removed from Logentries.'%host.get_name())
                remove_log_conf(instance_id)
                restart_rsyslog(instance_id)
            else:
                logger.error('Could not remove Host %s from Logentries.'%host.get_name())
    return


def main(working_dir=None):
    if working_dir is None:
        return      

    logentriesprovisioning.constants.set_working_dir(working_dir)
    logentriesprovisioning.constants.set_account_key(None)
    logentriesprovisioning.constants.set_logentries_logging()

    if working_dir is None:
        ssh_config_name = 'ssh_config'
    else:
        ssh_config_name = '%s/ssh_config'%working_dir

    env.use_ssh_config = True
    try:
        config_file = file(ssh_config_name)
    except IOError:
        pass
    else:
        config = SSHConfig()
        config.parse(config_file)
        env._ssh_config = config
        for i in range(0,len(config._config)):
            print str(i), ' - ' , config._config[i]

    list_hosts = []
    for host_config in env._ssh_config._config:
        print host_config
        if host_config['host'][0]!='*':
            list_hosts.extend(host_config['host'])

    execute(sync,hosts=list_hosts)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'You must specify the path to your ssh config file.'
    else:
        logentriesprovisioning.constants.set_working_dir(sys.argv[1])
        logentriesprovisioning.constants.set_account_key(None)
        logentriesprovisioning.constants.set_logentries_logging()
        main('%s/ssh_config'%sys.argv[1])
