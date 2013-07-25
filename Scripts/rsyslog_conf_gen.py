import boto.ec2
import os.path
import json

import ssh_keys
import logentries

CONF_FILE = 'logentries_config.json'
ACCOUNT_KEY,CONFIG = logentries.load_config(CONF_FILE)

class Account:
   _key = None
   _hosts = None
   
   def __init__(self,account_key):
      self._key = account_key

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

   _name = None
   _path = None
   _key = None
   _token = None
   _port = None
   _source = None
   
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
   
   _name = None
   _key = None
   _logs = None
   _platform = None

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
   _aws_id = None
   _ssh_key_name = None
   _ip_address = None
   _user = None

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

   def to_json(self):
      result = {"aws_id":self.get_aws_id(),"ssh_key_name":self.get_ssh_key_name(),"ip_address":self.get_ip_address(), "user": self.get_user()}
      result.update(super(Instance,self).to_json())
      return result

   def __unicode__(self):
      return json.dumps(self.to_json())


class LoggingConfFile:
   """ """
   _name = None
   _conf_format = None
   _logs = None
   _polling_period = 0


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


class ConfFile:

   _name = None
   _instances = None

   def __init__(self,name='logentries_conf.json',instances=[]):
      self._name = name
      self._instances = instances

   def create(self,conf_json):
      pass

   def set_name(self,name):
      _name = name

   def get_name(self):
      return _name

   def set_instances(self,instances):
      _instances = instances

   def get_instances(self):
      return _instances

   @staticmethod
   def open():
      conf_file = open(self.get_name(),'r')
      conf_json = json.load(conf_file)
      conf_file.close()
      return create(conf_json)

   def save(self):
      conf_file = open(self.get_name(),'w')
      conf_file.write(json.dumps(self.to_json()['instances']))
      conf_file.close()

   def to_json(self):
      instance_list = []
      for instance in self.get_instances():
         instance_list.append(instance.to_json())
      return {"name":self.get_name(),"instances":instance_list}

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
