from fabric.api import *
import paramiko
from paramiko.config import SSHConfig
from os.path import expanduser
import instance


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
        self._config = get_config(filename)

        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def get_config(self):
        return self._config

    def get_instance_logpaths(self,instance):
        """ """
        result = []
        ssh = self.get_client()
        ssh.connect(hostname=instance.get_name(),ip=instance.get_ip_address(),username=instance.get_user(),port=instance.get_port(), allow_agent=True, look_for_keys=True)
        stdin, stdout, stderr = ssh.exec_command('find /var/log/ -name *.log')
        return [item.split('\n')[0] for item in stdout.readlines()], stderr


    def add_ec2_instances(self,instances):
        """ """
        pass
