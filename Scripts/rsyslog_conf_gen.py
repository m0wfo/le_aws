import boto.ec2
import os.path
import json

import ssh_keys
#import logentries

#CONF_FILE = 'logentries_config.json'
#ACCOUNT_KEY,CONFIG = logentries.load_config(CONF_FILE)

class Account:
   
   def __init__(self,account_key):
      self._key = account_ke
      self._hosts = None

   def set_key(self,key):
      self.key = key

   def get_key(self):
      return self._key

   def get_hosts(self):
      return self._hosts

   def add_host(self,host):
      """ Args: host is not None """
      if self.get_hosts() is None:
         self.set_hosts([host])
      else:
         self._hosts.append(host)

   @staticmethod
   def create(account_data):
      """ """
      account = Account(account_data["key"])
      for host_data in account_data["hosts"]:
         account.add_host(Host.create(host_data))
      return account

   def to_json(self):
      result = {"key":self.get_key()}
      hosts_json = []
      for host in self.get_hosts():
         hosts_json.append(host.to_json())
      result["hosts"] = hosts_json
      return result

   def __unicode__(self):
      return json.dumps(self.to_json())
   

class Log:

   def __init_(self,name=None,path=None,key=None,token=None,source=None):
      self._name = 'Default'
      self._path = path
      self._key = key
      self._token = token
      self._port = port
      self._source = source
   
   @staticmethod
   def create(log_data):
      log = Log()
      log.set_name(log_data["name"])
      log.set_path(log_data["path"])
      log.set_key(log_data["key"])
      log.set_token(log_data["token"])
      log.set_token(log_data["source"])
      log.set_port(log_data["port"])
      return log

   def to_json(self):
      return {"name":self.get_name(),"path":self.get_path(),"key":self.get_key(),"token":self.get_token()}

   def set_value(attr,value):
      attr = value

   def set_token(self,token):
      self._token = token

   def set_source(self,source):
      self._source = source

   def set_port(self,port):
      self._port = port

   def set_name(self,name):
      self._name = name

   def set_path(self,path):
      self._path = path

   def set_key(self,log_key):
      self._key = log_key

   def set_token(self,token):
      self._token = token

   def get_name(self):
      return self._name

   def get_path(self):
      return self._path

   def get_key(self):
      return self._key

   def get_token(self):
      return self._token

   def get_source(self):
      return self._source

   def get_port(self):
      return self._port
   
   def to_json(self):
      return {"key":self.get_key(),"name":self.get_name(),"path":self.get_path(),"token":self.get_token(),"source":self.get_source(),"port":self.get_port()}

   def __unicode__(self):
      return json.dumps(self.to_json())


class Host(object):
   
   def __init__(self,name=None,key=None,logs=[],platform=None):
      self._name = name
      self._key = key
      self._logs = logs
      self._platform = platform

   def create(cls,json_rep_str):
      host_data = json.loads(json_rep_str)
      host = Host()
      host.set_name(host_data["name"])
      host.add_logs(host_data["logs"])
      return host

   def set_name(self,name):
      self._name = name

   def set_platform(self,platform):
      self._platform = platform

   def set_key(self,key):
      self._key = key

   def add_log(self,log):
      """ Args: log is not None """
      if self._logs is None:
         self._logs = [log]
      else:
         self._logs.append(log)

   def add_logs(self,logs):
      for log in logs:
         self.add_log(log)

   def get_name(self):
      return self._name

   def get_platform(self):
      return self._platform

   def get_key(self):
      return self._key

   def get_log(self,log_key):
      """ """
      for log in self._logs:
         if log.get_key() == log_key:
            return log
      return None

   def get_logs(self):
      return self._logs

   @staticmethod
   def create(host_data):
      """ """
      host = Host(key=host_data["key"])
      name = host_data["name"]
      platform = host_data["platform"]
      if name is not None:
         host.set_name(name)
      if platform is not None:
         host.set_platform(platform)
      for log_data in host_data["logs"]:
         host.add_log(Log.create(log_data))
      return host

   def to_json(self):
      logs_json = [log.to_json() for log in self.get_logs()]
      return {"name":self.get_name(),"key":self.get_key(),"platform":self.get_platform(),"logs":logs_json}

   def __unicode__(self):
      return json.dumps(self.to_json())


class Instance(Host):
   """ """

   def __init__(self,aws_id,ssh_key_name=None,ip_address=None,name=None,key=None,logs=[],platform=None, user=None):
      self._aws_id = aws_id
      self._ssh_key_name = ssh_key_name
      self._ip_address = ip_address
      self._user = user
      super(Instance,self).__init__(name,key,logs,platform)

   def set_aws_id(self,aws_id):
      self._aws_id = aws_id

   def set_ssh_key_name(self,ssh_key_name):
      self._ssh_key_name = ssh_key_name

   def set_ip_address(self,ip_address):
      self._ip_address = ip_address

   def set_user(self,user):
      self._user = user

   def get_aws_id(self):
      return self._aws_id

   def get_ssh_key_name(self):
      return self._ssh_key_name

   def get_ip_address(self):
      return self._ip_address

   def get_user(self):
      return self._user

   @staticmethod
   def load(i):
      """ Args:
      instance_attr is a dict object containing an instance attributes
      """
      if 'aws_id' in i:
         ssh_key_name = i['ssh_key_name'] if 'ssh_key_name' in i else None
         ip_address = i['ip_address'] if 'ip_address' in i else None
         name = i['name'] if 'name' in i else None
         key = i['key'] if 'key' in i else None
         logs = i['logs'] if 'logs' in i else []
         platform = i['platform'] if 'platform' in i else None
         user = i['user'] if 'user' in i else None
         return Instance(aws_id=i['aws_id'],ssh_key_name=ssh_key_name,ip_address=ip_address,name=name,key=key,logs=logs,platform=platform,user=user)
      else:
         return None

   def to_json(self):
      result = {"aws_id":self.get_aws_id(),"ssh_key_name":self.get_ssh_key_name(),"ip_address":self.get_ip_address(), "user": self.get_user()}
      result.update(super(Instance,self).to_json())
      return result

   def __unicode__(self):
      return json.dumps(self.to_json())


class LoggingConfFile:
   """ """

   def __init__(self,name='logentries.conf',conf_format='rsyslog',host=None,polling_period=10):
      self._name = name
      self._conf_format = conf_format
      if host is None:
         self._logs = []
      else:
         self._logs = host.get_logs()
      self._polling_period = polling_period

   def set_format(self,conf_format):
      self._conf_format = conf_format

   def set_name(self,name):
      self._name = name

   def set_logs(self,logs):
      self._logs = logs

   def set_logs(self,host):
      self._logs = host.get_logs()

   def set_polling_perdiod(polling_period):
      self._polling_period = polling_period

   def get_format(self):
      return self._conf_format

   def get_name(self):
      return self._name

   def get_logs(self):
      return self._logs

   def get_polling_period(self):
      return self._polling_period

   @staticmethod
   def open():
      conf_file = open(self.get_name(),'r')
      conf_json = json.load(conf_file)
      conf_file.close()
      return create(conf_json)

   def save(self):
      """ """
      if self.get_format() == 'rsyslog':
         self.save_rsyslog_conf()
      else:
         print '%s is not a valid output type'%(self.get_format())

   def save_rsyslog_conf(self):
      """ """
      # Open configuration file
      conf_file = open(self.get_name(),'w')
      # Set the rsyslog mode to follow files
      conf_file.write(self.get_start_rsyslog_conf())

      templates = ""
      for log in self.get_logs():
         rsyslog_entry,template = self.create_rsyslog_entry(log)
         conf_file.write(rsyslog_entry)
         templates = templates + template + "\n"
      # Set the rsyslog polling policy 
      conf_file.write(self.get_poll_rsyslog_conf())
      conf_file.write(templates)
      conf_file.close()


   def create_rsyslog_entry(self,log):
      """ Returns the strings representing an rsyslog template as well as an rsyslog entry for the log data provided
      Args: log_data must contain the path to the log file to be followed by rsyslog"""
      file_path = log.get_name()
      file_id = file_path.replace('/','_')
      format_name = "LogentriesFormat_"+file_id
      return """# FILE
            $InputFileName """+file_path+"""
            $InputFileTag """+file_id+"""
            $InputFileStateFile """+file_id+"""
            $InputFileSeverity info
            $InputFileFacility local7
            $InputRunFileMonitor\n\n
            ""","""$template """+format_name+""",\""""+log.get_token()+""" %HOSTNAME% %syslogtag%%msg%\\n\"
            if $programname == '"""+file_id+"""' then @@api.logentries.com:10000;"""+format_name+"""\n
            """


   def get_start_rsyslog_conf(self):
      return """$Modload imfile\n\n"""

   def get_poll_rsyslog_conf(self):
      return """
            # check for new lines every 10 seconds
            # Only entered once in case of following multiple files
            $InputFilePollInterval """+unicode(self.get_polling_period())+"""\n\n"""


class AWSConfFile:

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
         if key_id not in conf_json:
            print '%s missing in %s'%(key_id,filename)
            self._aws_access_key_id = None
         else:
            self._aws_access_key_id = conf_json[key_id]
         if secret_key not in conf_json:
            print '%s missing in %s'%(secret_key,filename)
            self._aws_secret_access_key = None
         else:
            self._aws_secret_access_key = conf_json[secret_key]
         if 'usernames' not in conf_json:
            print 'usernames missing in %s'%(filename)
            self._usernames = None
         else:
            self._usernames = conf_json['usernames']
         if 'ssh_key_paths' not in conf_json:
            print 'ssh_key_paths missing in %s'%(filename)
            self._ssh_key_paths = None
         else:
            self._ssh_key_paths = conf_json['ssh_key_paths']
         if 'ssh_keys' not in conf_json:
            print 'ssh_keys missing in %s'%(filename)
            self._ssh_keys = None
         else:
            self._ssh_keys = conf_json['ssh_keys']
         if 'instances' not in conf_json:
            print 'instances missing in %s'%(filename)
            self._instances = None
         else:
            self._instances = []
            for instance in conf_json['instances']:
               self._instances.append(Instance.load(instance))

   def set_name(self,name):
      self._name = name

   def get_name(self):
      return self._name

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
         self.set_instances([instance])
      elif instance not in self.get_instances():
         self.get_instances().append(instance)

   def add_instances(self,instances):
      for instance in instances:
         self.add_instance(instance)

   def get_instances(self):
      return self._instances

   @staticmethod
   def open(filename):
      try:
         conf_file = open(filename,'r')
         conf_json = json.load(conf_file)
      except IOError:
         print 'Cannot open file %s'%filename
         return None
      else:
         conf_file.close()
      return self.__init__(conf_json)

   def save(self):
      conf_file = open(self.get_name(),'w')
      conf_file.write(json.dumps(self.to_json()))
      conf_file.close()

   def to_json(self):
      instance_list = []
      for instance in self.get_instances():
         instance_list.append(instance.to_json())
      return {"aws_access_key_id":self.get_aws_access_key_id(),"aws_secret_access_key":self.get_aws_secret_access_key(),"usernames":self.get_usernames,"ssh_key_paths":self.get_ssh_key_paths(),"usernames":self.get_usernames(),"ssh_keys":self.get_ssh_keys(),"instances":instance_list}

   def __unicode__(self):
      return json.dumps(self.to_json())

if __name__ == '__main__':
   log1 = Log()
   log1.set_name('test_log1')
   log1.set_token('log1_token')
   print 'log1:%s'%(unicode(log1))
   log2 = Log()
   log2.set_name('test_log2')
   log2.set_token('log1_token')
   log2_rep_str = unicode(log2)
   print 'log2:%s'%log2_rep_str
   log2_data = json.loads(log2_rep_str)
   log3 = Log.create(log2_data)
   log3.set_name('log3')
   print 'log3:%s'%unicode(log3)

   host = Host()
   host.set_name('test_host')
   host.add_logs([log1,log2])
   print 'host:%s'%unicode(host)
   
   rsys_conf_file = LoggingConfFile(host=host)
   rsys_conf_file.save()
