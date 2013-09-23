import paramiko
import boto.ec2
import boto.manage.cmdshell

import os.path
import json
import Instance
import SSHKeys
from LogentriesSDK.models import Log
from LogentriesSDK.models import Host
from LogentriesSDK.client import Client
from LogentriesSDK.models import Account
from aws_client import *

class LoggingConfFile:
   """ """

   def __init__(self,name='logentries.conf',conf_format='rsyslog',host=None,polling_period=10):
      self._name = name
      self._conf_format = conf_format
      self._host=host
      self._polling_period = polling_period

   def set_format(self,conf_format):
      self._conf_format = conf_format

   def set_name(self,name):
      self._name = name

   def set_host(self,host):
      self._host = host


   def set_polling_period(polling_period):
      self._polling_period = polling_period

   def get_format(self):
      return self._conf_format

   def get_name(self):
      return self._name

   def get_host(self):
      return self._host

   def get_polling_period(self):
      return self._polling_period

   def to_model_rep(self):
      model_rep = '#LOGENTRIES_MODEL:'+unicode(self.get_host().get_key())+'\n'
      for log in self.get_host().get_logs():
         model_rep = model_rep + '#' + unicode(log.to_json()) + '\n' 
      return model_rep

   def open(self):
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
      if self.get_host() is None:
         print 'No configuration file saved for %s as host is None'%self.get_name()
         return
      # Open configuration file
      conf_file = open(self.get_name(),'w')
      # Set the rsyslog mode to follow files
      conf_file.write(self.get_start_rsyslog_conf())

      templates = ""
      for index in range(0,len(self.get_host().get_logs())):
         log = self.get_host().get_logs()[index]
         rsyslog_entry,template = self.create_rsyslog_entry(log,index)
         conf_file.write(rsyslog_entry)
         templates = templates + template + "\n"
      # Set the rsyslog polling policy 
      conf_file.write(self.get_poll_rsyslog_conf())
      conf_file.write(templates)
      conf_file.write(self.to_model_rep())
      conf_file.close()


   def load_data(self,conf_data):
      if 'name' in conf_data:
         self._name = conf_data['name']
      if 'conf_format' in conf_data:
         self._conf_format = conf_data['conf_format']
      if 'host' in conf_data:
         host = Host()
         host.load_data(conf_data['host'])
         self._host = host
      if 'polling_period' in conf_data:
         self._polling_period = conf_data['polling_period']

   @staticmethod
   def load_file(conf_file,filename):
      """
      """
      log_conf = LoggingConfFile(name=filename)
      host = Host(name=filename)
      logs = []
      for line in conf_file.readlines():
         if line.startswith('#LOGENTRIES_MODEL:'):
            host_key_array = line.split(':',1)
            if len(host_key_array) > 1:
               host.set_key(host_key_array[1])
            else:
               print 'Wrong format for Logentries Model in %s'%log_conf.get_name()
               return None
         elif line.startswith('#LOG:'):
            log_conf_array = line.split(':',1)
            if len(log_conf_array) > 1:
               log = Log()
               log.load_data(json.load(log_conf_array[1]))
               host.add_log(log)
            else:
               print 'Wrong log format for Logentries Model in %s'%log_conf.get_name()
               return None
      log_conf.set_host(host)
      return log_conf

   @staticmethod
   def load_rsyslog_conf(self, filename):
      """ 
      Returns the configuration loaded from filename
      """
      # Open configuration file
      conf_file = open(filename,'r')
      return load_file(conf_file,filename)

   def create_rsyslog_entry(self,log,index):
      """ 
      Args: log is a log instance.
      Returns the strings representing an rsyslog template as well as an rsyslog entry for the log data provided
      """
      if not log.get_token():
         return "","";
      file_path = log.get_filename()
      file_id = 'tag%s'%str(index)#file_path.replace('/','').replace('.','')
      format_name = 'format_%s'%file_id
      return """# FILE
            $InputFileName """+file_path+"""
            $InputFileTag """+file_id+"""
            $InputFileStateFile """+file_id+"""
            $InputFileSeverity info
            $InputFileFacility logentries0
            $InputRunFileMonitor\n\n
            ""","""$template """+format_name+""",\""""+log.get_token()+""" %HOSTNAME% %msg%\\n\"
            if $programname == '"""+file_id+"""' then @@api.logentries.com:10000;"""+format_name+"""\n& ~\n
            """


   def get_start_rsyslog_conf(self):
      return """$Modload imfile\n\n"""

   def get_poll_rsyslog_conf(self):
      return """
            # check for new lines every 10 seconds
            # Only entered once in case of following multiple files
            $InputFilePollInterval """+unicode(self.get_polling_period())+"""\n\n"""


   def to_json(self):
      """ """
      result = {"name":self.get_name(),"conf_format":self.get_format(),"host":(None if self.get_host() is None else self.get_host().to_json()),"polling_period":self.get_polling_period()}

      
if __name__ == '__main__':
   # Open the updated version of the aws config file
   aws_conf = AWSConfFile('aws.json')
   aws_client = AWS_Client(aws_conf)
   aws_client.aws_refresh()

   # Update logentries account and create rsyslog config files
   for instance in aws_client.get_aws_conf().get_instances():
      log_conf = aws_client.update_instance_conf(instance)
      if log_conf is not None:
         instance.set_log_conf(log_conf)
         instance.get_log_conf().save()
         aws_client.deploy_log_conf(instance)

   client = Client(aws_client.get_aws_conf().get_account_key())
   account = client.get_account()

   #for host in account.get_hosts():
      #log_str = "["
      #for log in host.get_logs():
      #   log_str = log_str + ", " + log.get_name()
      #print host.get_name() + " - " + log_str + "]"
      #print host.get_name() + " - " + str(len(host._logs))
   for instance in aws_client.get_aws_conf().get_instances():
      print str(instance.get_aws_id()) + " - " + str(instance.get_ip_address())
