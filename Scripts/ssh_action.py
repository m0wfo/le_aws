from fabric.api import *
import paramiko
import boto.manage.cmdshell
from os.path import expanduser
import rsyslog_conf_gen as ConfFile
import ec2_connection

class Connection:

    def __init__(self,filename=None):
        self._config = ConfFile.AWSConfFile(filename)

    def get_config(self):
        return self._config


    def get_instance_logpaths(self,ec2_instance):
        """ """
        result = []
        instance = self.get_config().get_instance(ec2_instance.id)
        if instance.get_platform() == 'windows':
            print 'No attempt to ssh instance %s as its platform is %s'%(instance.get_aws_id(),instance.get_platform())
            return
        if instance.get_username() is not None:
            usernames = [instance.get_username()]
        else:
            usernames = self.get_config().get_usernames()
        for username in usernames:
            key_filename = expanduser(instance.get_ssh_key_name())
            try:
                ssh = boto.manage.cmdshell.sshclient_from_instance(ec2_instance,key_filename,user_name=username)
            except paramiko.SSHException as e:
                print 'Connection to %s with user %s and ssh key %s failed. %s'%(instance.get_ip_address(),username,key_filename,e)
                continue
            chan = ssh.run_pty('sudo find /var/log/ -name *.log > /tmp/log_list.txt')
            stdin, stdout, stderr = ssh.run('cat /tmp/log_list.txt')
            result = [logpath for logpath in stdout.split('\n') if '.log' in logpath]
            # Remove the remote tmp file
            _, _, stderr = ssh.run('rm /tmp/log_list.txt')
            if stderr != '':
                print 'Error while removing temporary file /tmp/log_list.txt on %s. %s'%(instance.get_ip_address(),stderr)
            # Update instance information with username and log paths
            
            break
        print result
        return result


    def add_ec2_instances(self,instances):
        """ """
        pass

    def restart_rsyslog(self):
        sudo("/etc/init.d/rsyslogd restart", pty=False)

if __name__ == '__main__':
    conn = Connection('aws.json')

    for region in ec2_connection.get_regions():
        con = ec2_connection.get_con(region)
        if con is not None:
            reservations = con.get_all_instances()
            for reservation in reservations:
                for ec2_instance in reservation.instances:
                    logpaths = conn.get_instance_logpaths(ec2_instance)
        con.close()
