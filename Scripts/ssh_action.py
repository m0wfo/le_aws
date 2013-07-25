from fabric.api import *
import paramiko
from paramiko.config import SSHConfig
from os.path import expanduser


class Connection:

    def get_config(filename):
        """ """
        try:
            if filename == None:
                config_file = file(expanduser('~/.ssh/config'))
            else:
                config_file = file(filename)
        except IOError:
            pass
        else:
            config = SSHConfig()
            config.parse(config_file)
            return config


    def __init__(self,filename=None):
        self.client = paramiko.SSHClient()
        self.config = get_config(filename)
        self.config.load_system_host_keys()
        self.config.set_missing_host_key_policy(paramiko.AutoAddPolicy())


    def get_instance_logpaths(self,instance):
        """ """
        result = []
        ssh = self.get_client()
        ssh.connect(instance)
        stdin, stdout, stderr = ssh.exec_command('find /var/log/ -name *.log')
        return [item.split('\n')[0] for item in stdout.readlines()], stderr


    def add_ec2_instances(self,instances):
        """ """
        
