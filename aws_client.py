from fabric.api import *
import paramiko
import boto.ec2
import boto.manage.cmdshell

import json
import os
import socket

import Instance
import SSHKeys
import LogentriesSDK.client as LogClient 
from ec2_filter import *
from log_filter import *
import ConfigFile

class AWSConfFile(object):

   def __init__(self,filename='aws.json',instances=[]):
      try:
         conf_file = open(filename,'r')
      except IOError:
         print 'Cannot open file %s'%filename
      else:
         conf_json = json.load(conf_file)
         conf_file.close()
         self._name = filename
         key_id = 'aws_access_key_id'
         secret_key = 'aws_secret_access_key'

         if key_id in conf_json:
            self._aws_access_key_id = conf_json[key_id]
         else:
            print '%s missing in %s'%(key_id,filename)
            self._aws_access_key_id = None

         # TODO: Account key is not aws specific. The name of this class should probably change.
         if 'account_key' in conf_json:
            self._account_key = conf_json['account_key']
         else:
            print '%s missing in %s'%('account_key',filename)
            self._account_key = None

         if 'ec2_filters' in conf_json:
            self._ec2_filters = [EC2Filter.load_json(ec2_filter_raw) for ec2_filter_raw in conf_json['ec2_filters']]
         else:
            print '%s missing in %s'%('ec2_filters',filename)
            self._ec2_filters = []

         if 'log_filters' in conf_json:
            self._log_filters = [LogFilter.load_json(log_filter_raw) for log_filter_raw in conf_json['log_filters']]
         else:
            print '%s missing in %s'%('log_filters',filename)
            self._log_filters = {}

         if secret_key in conf_json:
            self._aws_secret_access_key = conf_json[secret_key]
         else:
            print '%s missing in %s'%(secret_key,filename)
            self._aws_secret_access_key = None

         if 'usernames' in conf_json:
            self._usernames = conf_json['usernames']
         else:
            print 'usernames missing in %s'%(filename)
            self._usernames = None

         if 'ssh_key_paths' in conf_json:
            self._ssh_key_paths = conf_json['ssh_key_paths']
         else:
            print 'ssh_key_paths missing in %s'%(filename)
            self._ssh_key_paths = None

         if 'ssh_keys' in conf_json:
            self._ssh_keys = conf_json['ssh_keys']
         else:
            print 'ssh_keys missing in %s'%(filename)
            self._ssh_keys = None

         if 'instances' in conf_json:
            self._instances = []
            #for instance in conf_json['instances']:
            #   instance2 = Instance.Instance.load_aws_data(instance)
            #   self._instances.append(instance2)
         else:
            print 'instances missing in %s'%(filename)
            self._instances = None

   def set_name(self,name):
      self._name = name

   def get_name(self):
      return self._name

   def set_ec2_filters(self,ec2_filters):
      self._ec2_filters = ec2_filters

   def get_ec2_filters(self):
      return self._ec2_filters

   def set_log_filters(self,log_filters):
      self._log_filters = log_filters

   def get_log_filters(self):
      return self._log_filters

   def set_account_key(self,account_key):
      self._account_key = account_key

   def get_account_key(self):
      return self._account_key

   def set_aws_access_key_id(self,aws_access_key_id):
      self._aws_access_key_id = aws_access_key_id

   def get_aws_access_key_id(self):
      return self._aws_access_key_id

   def set_aws_secret_access_key(self,aws_secret_access_key):
      self._aws_secret_access_key = aws_secret_access_key

   def get_aws_secret_access_key(self):
      return self._aws_secret_access_key

   def set_usernames(self,usernames):
      self._usernames = usernames

   def add_username(self,username):
      if username not in self._usernames:
         self._usernames.append(username)

   def add_usernames(self,usernames):
      for username in usernames:
         add_username(username)

   def get_usernames(self):
      return self._usernames

   def set_ssh_key_paths(self,ssh_key_paths):
      self._ssh_key_paths = ssh_key_paths

   def get_ssh_key_paths(self):
      return self._ssh_key_paths

   def add_ssh_key_path(self,ssh_key_path):
      if self.get_ssh_key_paths() is None:
         self.set_ssh_key_paths([ssh_key_path])
      elif ssh_key_path not in _ssh_key_paths:
         self.get_ssh_key_paths().append(ssh_key_path)

   def set_ssh_keys(self,ssh_keys):
      self._ssh_keys = ssh_keys

   def add_ssh_key(self,name,path):
      self._ssh_keys[name] = path

   def add_ssh_keys(self,ssh_keys):
      self._ssh_keys.update(ssh_keys)

   def get_ssh_keys(self):
      return self._ssh_keys

   def set_instances(self,instances):
      self._instances = instances

   def add_instance(self,instance):
      if self.get_instances() is None:
         self._instances = [instance]
      elif instance not in self.get_instances():
         self._instances.append(instance)
      else:
         for i in range(0,len(self.get_instances())):
            if self.get_instances()[i] == instance:
               self._instances[i] = Instance.load_aws_data(instance.to_json())
               break

   def add_instances(self,instances):
      for instance in instances:
         self.add_instance(instance)

   def get_instance_with_id(self,aws_id):
      for i in self.get_instances():
         if i.get_aws_id() == aws_id:
            return i
      return None

   def set_instance(self,aws_id,instance):
      for k in range(0,len(self.get_instances())):
         i = self.get_instances()[k]
         if i is None:
             print 'Error. Instance is None, id=%s'%aws_id
         if i.get_aws_id() == aws_id:
            self._instances[k] = instance
            return
      self.add_instance(instance)
      return

   def get_instances(self):
      return self._instances

   @staticmethod
   def open(filename):
      try:
         return AWSConfFile(filename=filename)
      except IOError:
         print 'Cannot open file %s'%filename
         return None

   def save(self):
      conf_file = open(self.get_name(),'w')
      conf_file.write(json.dumps(self.to_json(),indent=2))
      conf_file.close()

   def to_json(self):
      instance_list = []
      for instance in self.get_instances():
         instance_list.append(instance.to_json())
      return {"account_key":self.get_account_key(),"aws_access_key_id":self.get_aws_access_key_id(),"aws_secret_access_key":self.get_aws_secret_access_key(),"usernames":self.get_usernames,"ssh_key_paths":self.get_ssh_key_paths(),"usernames":self.get_usernames(),"ssh_keys":self.get_ssh_keys(),"instances":instance_list,"ec2_filters": [ec2_filter.to_json() for ec2_filter in self.get_ec2_filters()],"log_filters": [log_filter.to_json() for log_filter in self.get_log_filters()]}

   def __unicode__(self):
      return json.dumps(self.to_json())



class AWS_Client(object):

   def __init__(self,aws_conf=None,ec2_instances=[]):    
       self._aws_conf = aws_conf
       self._ec2_instances = ec2_instances

   def get_aws_conf(self):
       return self._aws_conf

   def set_aws_conf(self,aws_conf):
       self._aws_conf = aws_conf

   def get_ec2_instances(self):
       return self._ec2_instances

   def set_ec2_instances(self,ec2_instances):
       self._ec2_instances = ec2_instances

   def add_ec2_instance(self,ec2_instance):
       ec2_instances = self.get_ec2_instances()
       if ec2_instance in ec2_instances:
           return
       ec2_instances.append(ec2_instance)
       self.set_ec2_instances(ec2_instances)

   def remove_ec2_instance(self,ec2_instance):
       ec2_instances = self.get_ec2_instances()
       ec2_instances.remove(ec2_instance)
       self.set_ec2_instances(ec2_instances)


   def get_ec2_instance(self,ec2_instance_id):
       for ec2_instance in self.get_ec2_instances():
           if ec2_instance.id == ec2_instance_id:
               return ec2_instance
       return None

   def get_instance(self,local_keys,ec2_instance):
      """
      Args:
      local_keys is a dictionnary mapping ssh key names to their location.
      ec2_instance is a Boto instance object.
      """
      if local_keys[ec2_instance.key_name] is not None:
         if ec2_instance.platform is None:
            print 'Platform is Linux for instance with id=%s and can be ssh-ed!'%ec2_instance.id
            platf = 'linux'
         else:
            platf = ec2_instance.platform
            print 'Platform is %s for instance with id=%s'%(platf,ec2_instance.id)
         if 'Name' in ec2_instance.tags:
            name = ec2_instance.tags['Name']
         else:
            name = ec2_instance.id+'_'+ec2_instance.ip_address
         if 'user' in ec2_instance.tags:
            username = ec2_instance.tags['user']
         else:
            username = None
         return Instance.Instance(aws_id=ec2_instance.id,ssh_key_name=local_keys[ec2_instance.key_name],ip_address=ec2_instance.ip_address,name=name,platform=platf,username=username)


   def refresh_instance(self,local_keys,ec2_instance):
      """ """
      if ec2_instance.platform == 'windows':
         print 'No attempt to ssh instance %s as its platform is %s'%(ec2_instance.id,ec2_instance.platform)
         return None

      instance = self.get_aws_conf().get_instance_with_id(ec2_instance.id)
      if instance is None:
         instance = self.get_instance(local_keys,ec2_instance)
      
      if instance.get_username() is None:
         usernames = self.get_aws_conf().get_usernames()
      else:
         usernames = [instance.get_username()]
      for username in usernames:
         key_filename = os.path.expanduser(instance.get_ssh_key_name())
         try:
             ssh = paramiko.SSHClient()
             ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
             ssh.connect(ec2_instance.ip_address, username=username, key_filename=key_filename)
             #ssh = boto.manage.cmdshell.sshclient_from_instance(ec2_instance,key_filename,user_name=username)
         except paramiko.SSHException as e:
             print 'Connection to %s with user %s and ssh key %s failed. %s'%(instance.get_ip_address(),username,key_filename,e)
             continue
         except socket.error as e1:
             print 'Connection to %s with user %s and ssh key %s failed. %s'%(instance.get_ip_address(),username,key_filename,e1)
             continue
         # Retrieve log file paths
         log_paths = []
         for path in instance.get_filters():
             tmp_file_name = '/tmp/log_list.txt'
             chan = ssh.get_transport().open_session()
             chan.get_pty()
             chan.exec_command("sudo find %s -type f -regex '.*log' > %s"%(path,tmp_file_name))
             if chan.recv_stderr_ready():
                 print chan.recv_stderr(1024)
             #stdin, stdout, stderr = 
             try:
                 f = ssh.open_sftp().open(tmp_file_name)
             except IOError as e:
                 print 'Could not open %s. %s'%(tmp_file_name,e.message)
             log_paths.extend([logpath.split('\n')[0] for logpath in f.readlines()])
         print 'Log Paths: %s'%log_paths
         # Remove the remote tmp file
         _, _, stderr = ssh.exec_command('rm /tmp/log_list.txt')
         if stderr != '':
            print 'Error while removing temporary file /tmp/log_list.txt on %s. %s'%(instance.get_ip_address(),stderr.read())

         # Retrieve current log config
         filename = 'logentries_%s.conf'%instance.get_aws_id()
         log_conf = None
         log_conf_file = None
         #if ssh.exists('/etc/rsyslog.d/%s'%filename):
         rsyslog_conf_name = '/etc/rsyslog.d/%s'%filename
         try:
             log_conf_file = ssh.open_sftp().open(rsyslog_conf_name)
         except:
             print 'Cannot open %s on remote instance %s'%(rsyslog_conf_name,instance.get_aws_id())
         if log_conf_file != None:
             log_conf = ConfigFile.LoggingConfFile.load_file(log_conf_file,filename)
             # Set the configuration file name
             log_conf.set_name(filename)

         # Update instance information with username, log paths and current log config
         instance.set_username(username)
         instance.set_logs([log_path for log_path in log_paths])
         instance.set_log_conf(log_conf)
         break
      return instance


   def aws_refresh(self):
      """
      This function updates information about running aws ec2 instances and the log files that they contain.
      """
      regions_info = boto.ec2.regions()
      for region in [boto.ec2.get_region(region_info.name) for region_info in regions_info]:
          print region
          con = boto.ec2.connection.EC2Connection(aws_access_key_id=self.get_aws_conf().get_aws_access_key_id(), aws_secret_access_key=self.get_aws_conf().get_aws_secret_access_key(),region=region)
          if con is not None:
              try:
                  key_pairs = con.get_all_key_pairs()
              except boto.exception.EC2ResponseError as e:
                  print e.message
              else:
                  key_names = [key_pair.name for key_pair in key_pairs]
                  ssh_k = SSHKeys.ssh_keys(paths=self.get_aws_conf().get_ssh_key_paths(),names=key_names)
                  local_keys = ssh_k.get_keys_onpaths(ssh_k.get_paths(),ssh_k.get_names())
                  
                  reservations = con.get_all_instances()
                  for reservation in reservations:
                      for ec2_instance in reservation.instances:
                          if ec2_instance.state != 'running':
                              print 'Instance %s is not running, state=%s'%(ec2_instance.id,ec2_instance.state)
                              continue
                          instance = self.refresh_instance(local_keys,ec2_instance)
                          if instance is not None:
                              self.get_aws_conf().set_instance(ec2_instance.id,instance)
                              self.add_ec2_instance(ec2_instance)
                  con.close()
      self.get_aws_conf().save()

   def deploy_log_conf(self,instance):
       if instance is None:
           return
       ec2_instance = self.get_ec2_instance(instance.get_aws_id())
       # Save log config in a file and retrieve its name
       instance.get_log_conf().save()
       filename = instance.get_log_conf().get_name()
       
       if instance.get_username() is None:
           usernames = self.get_aws_conf().get_usernames()
       else:
           usernames = [instance.get_username()]
       for username in usernames:
           key_filename = os.path.expanduser(instance.get_ssh_key_name())
           try:
               ssh = paramiko.SSHClient()
               ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
               ssh.connect(ec2_instance.ip_address, username=username, key_filename=key_filename)
               #ssh = boto.manage.cmdshell.sshclient_from_instance(ec2_instance,key_filename,user_name=username)
           except paramiko.SSHException as e:
               print 'Connection to %s with user %s and ssh key %s failed. %s'%(instance.get_ip_address(),username,key_filename,e)
               continue
           # Copy the file previously saved onto the instance
           try:
               ssh.open_sftp().put(filename,'/tmp/%s'%filename)
           except:
               print 'Transfering %s to remote /tmp/%s Failed'%(filename,filename)
           # Restart syslogd
           # TODO: Capture errors and report them
           chan = ssh.get_transport().open_session()
           chan.get_pty()
           try:
               chan.exec_command('sudo mv /tmp/%s /etc/rsyslog.d/.'%filename)

               chan = ssh.get_transport().open_session()
               chan.get_pty()
               chan.exec_command('sudo /etc/init.d/rsyslog restart')
           except paramiko.SSHException as e:
               print 'Connection to %s with user %s and ssh key %s failed. %s'%(instance.get_ip_address(),username,key_filename,e)
           except:
               print 'Connection to %s with user %s and ssh key %s failed. %s'%(instance.get_ip_address(),username,key_filename)

           if chan.recv_stderr_ready():
               print 'Error when restarting rsyslog. %s'%chan.recv_stderr(1024)
               return
           print 'Rsyslog restarted successfully on %s'%instance.get_aws_id()

   def update_instance_conf(self,instance):
       """
       Returns the updated log_conf, taking into account new log files present on the instance as well as modifications made to the corresponding logentries host.
       """
       log_conf = None
       log_client = LogClient.Client(self.get_aws_conf().get_account_key()) 
       if instance.get_log_conf() is None and len(instance.get_logs())>0:
           host = log_client.create_host(name='AWS_%s'%instance.get_aws_id(),location='AWS')
           print 'CREATED HOST: %s'%str(host.get_name())
           if host is None:
               print 'Error when creating host for instance %s'%instance.get_aws_id()
               return
           for log_name in instance.get_logs():
               host = log_client.create_log_token(host=host,log_name=log_name)
           log_conf = ConfigFile.LoggingConfFile(name='logentries_%s.conf'%instance.get_aws_id(),host=host)
       
       elif instance.get_log_conf() is not None:
           log_conf = instance.get_log_conf()
           conf_host = log_conf.get_host()
           if conf_host is None:
               print 'Error. This instance configuration is missing the corresponding model!! instance_id=%s'%instance.get_aws_id()
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
           new_logs = instance.get_new_logs()
           for new_log in new_logs:
               matching_host = log_client.create_log_token(host=matching_host,log_name=new_log)
           log_conf.set_host(matching_host)
       return log_conf
