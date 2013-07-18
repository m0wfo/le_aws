import boto.ec2
import os.path
import json

import ssh_keys
import logentries

POLLING_PERIOD = 10
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
   def load_json(json_rep_str):
      account_data = json.loads(json_rep_str)
      account = Account(account_data["key"])
      for 
      return account

   def to_json(self):
      return unicode(self)

   def __unicode__(self):
      return '{"name":"%s","path":"%s","key":"%s","token":"%s"}'%(self._name,self._path,self._key,self._token)
   

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
   def load_json(json_rep_str):
      log_data = json.loads(json_rep_str)
      log = Log()
      log.set_name(log_data["name"])
      log.set_path(log_data["path"])
      log.set_key(log_data["key"])
      log.set_token(log_data["token"])
      log.set_token(log_data["source"])
      log.set_port(log_data["port"])
      return log

   def convert()

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
   
   def to_json(self):
      return unicode(self)

   def __unicode__(self):
      return '{"name":"%s","path":"%s","key":"%s","token":"%s"}'%(self._name,self._path,self._key,self._token)


class Host:
   
   _name = None
   _key = None
   _logs = None

   def __init__(self):
      self._name = 'Default'
      self._logs = []

   def load_json(cls,json_rep_str):
      host_data = json.loads(json_rep_str)
      host = Host()
      host.set_name(host_data["name"])
      host.add_logs(host_data["logs"])
      return host

   def set_name(self,name):
      self._name = name

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

   def get_log(self,log_key):
      """ """
      for log in self._logs:
         if log.get_key() == log_key:
            return log
      return None

   def get_logs(self):
      return self._logs

   def to_json(self):
      return unicode(self)

   def __unicode__(self):
      log_list_string = '['
      for log in self._logs:
         log_list_string = log_list_string + unicode(log)+','
      log_list_string = log_list_string + ']'
      return '{"name":"%s","logs":"%s"}'%(self._name,log_list_string)


class ConfFile:

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
   log3 = Log.load_json(log2_rep_str)
   log3.set_name('log3')
   print 'log3:%s'%unicode(log3)

   host = Host()
   host.set_name('test_host')
   host.add_logs([log1,log2])
   print 'host:%s'%unicode(host)
   
   rsys_conf_file = ConfFile(host=host)
   rsys_conf_file.save()
