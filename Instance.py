import json

from LogentriesSDK.models import Host
from LogentriesSDK.models import Log
from ConfigFile import LoggingConfFile

class Instance(object):
   """
   Instance class representing physical EC2 instances. Instance objects contain information about connecting to the corresponding EC2 instance, e.g. ip address, ssh key filename, username, etc, as well as information about the logging configuration associated to them. This logging configuration must comply to filters that are also attribute of this class. 
   """

   def __init__(self,aws_id,ssh_key_name=None,ip_address=None,port=None,logs=[],filters=['/var/log/'],log_conf=None,platform=None, username=None, name=None):
      """
      Args:
      aws_id represents the aws unique identifier for this instance
      ssh_key_name represents the name of the ssh key associated to this instance
      ip_address represents this instance ip address
      port represents the port on which to connect to this instance
      filters represents a list of path filters where log files under interest are located on the instance.
      logs represents the list of paths where .log files are present and that comply with filters
      log_conf represents the currently deployed Logentries log forwarding configuration on the instance.
      platform represents the os type that runs on the instance
      username represents the username with which to connect to the instance
      name is the name of the instance as defined in the ec2 tags.
      """
      self._aws_id = aws_id
      self._ssh_key_name = ssh_key_name
      self._ip_address = ip_address
      self._username = username
      self._port = port
      self._name = name
      self._logs = logs
      self._log_conf = log_conf
      self._filters = filters
      self._platform = platform


   def set_aws_id(self,aws_id):
      """
      Args: aws_id is a string. It represents the associated ec2 instance id.
      Sets the id of this instance to aws_id.
      """
      self._aws_id = aws_id

   def set_name(self,name):
      """
      Args: name is a string. It represents the name of the ec2 instance.
      Sets the name of this instance to name.
      """
      self._name = name

   def set_ssh_key_name(self,ssh_key_name):
      """
      Args: ssh_key_name is a string. It represents the location of a file containing an ssh key.
      Sets the path of the file containing the ssh key of allowing to connect to this instance to ssh_key_name.
      """
      self._ssh_key_name = ssh_key_name

   def set_logs(self,logs):
      """
      Args: logs is a list of strings. Each string represents the location of a log file present on the instance.
      Sets list of log file paths for log files present on the instance.
      """
      self._logs = logs

   def set_log_conf(self,log_conf):
      """
      Args: log_conf is a configuration file to follow logs on the instance
      Sets the configuration file to follow log files on the instance to log_conf
      """
      self._log_conf = log_conf

   def set_filters(self,filters):
      """
      Args: filters is a list of path where to consider log files.
      Sets the log file path filters to filters
      """
      self._filters = filters

   def set_ip_address(self,ip_address):
      """
      Args: ip_address is a string. It represents the ip_address of this instance.
      Sets the ip address of this instance to ip_address.
      """
      self._ip_address = ip_address

   def set_username(self,username):
      """
      Args: username is a string. It represents the user name with which to log on to this instance.
      Sets the user name of this instance to username.
      """
      self._username = username

   def get_aws_id(self):
      """
      Returns the aws id of this instance.
      """
      return self._aws_id

   def set_port(self,port):
      """
      Args: port is an integer. It represents the port on which this instance can be sshed.
      Sets the port on which to shh this instance to port.
      """
      self._port = port

   def get_port(self):
      """
      Returns the port on which to ssh this instance.
      """
      return self._port

   def get_name(self):
      """
      Returns the name of this instance.
      """
      return self._name


   def get_ssh_key_name(self):
      """
      Returns the location of a file containing an ssh key with which to connect to this instance.
      """
      return self._ssh_key_name

   def get_ip_address(self):
      """
      Returns this instance ip address.
      """
      return self._ip_address

   def get_username(self):
      """
      Returns the user name with which to connect to this instance.
      """
      return self._username

   def get_logs(self):
      """
      Returns the list of paths to log files present on the instance.
      """
      return self._logs

   def get_log_conf(self):
      """
      Returns the configuration file to follow log files on the instance
      """
      return self._log_conf

   def get_filters(self):
      """
      Returns the log file path filters
      """
      return self._filters


   @staticmethod
   def load_aws_data(i):
      """ 
      Args: i is a dict object containing an instance attributes.
      """
      if 'aws_id' in i:
         ssh_key_name = i['ssh_key_name'] if 'ssh_key_name' in i else None
         ip_address = i['ip_address'] if 'ip_address' in i else None
         name = i['name'] if 'name' in i else None

         log_conf = None
         log_conf_data = i['log_conf'] if 'log_conf' in i else None
         if log_conf_data is not None:
            log_conf = LoggingConfFile()
            log_conf.load_data(log_conf_data)
         
         host_data = i['host'] if 'host' in i else None
         if host_data is not None:
            host = Host()
            host.load_data(host_data)

         filters = i['filters'] if 'filters' in i else []
         logs =  i['logs'] if 'logs' in i else []

         platform = i['platform'] if 'platform' in i else None
         username = i['username'] if 'username' in i else None
         port = i['port'] if 'port' in i else None
         return Instance(aws_id=i['aws_id'],ssh_key_name=ssh_key_name,ip_address=ip_address,name=name,logs=logs,platform=platform,log_conf=log_conf,username=username,port=port)
      else:
         return None


   def remove_logs_from_conf(self):
      """
      Removes from the instance logentries conf the logs whose paths are not in the instance log paths list.
      """
      log_conf = self.get_log_conf()
      host = log_conf.get_host()
      if host is None:
         return
      updated_logs = []
      for log in host.get_logs():
         if log.get_filename() in self.get_logs():
            updated_logs.append(log)
      host.set_logs(updated_log)
      log_conf.set_host(host)
      self.set_log_conf(log_conf)

   def get_new_logs(self):
      """
      Returns the list of log paths that are not known by the log configuration associated to this instance
      """
      log_conf = self.get_log_conf()
      if log_conf is None or log_conf.get_host() is None:
         return self.get_logs()
      conf_logs = log_conf.get_host().get_logs()
      conf_log_names = [log.get_filename() for log in conf_logs]
      new_logs = [log_path for log_path in self.get_logs() if log_path not in conf_log_names]
      return new_logs
      

   def to_json(self):
      """
      Returns a dictionnary representing the attribute values of this instance.
      """
      result = {"aws_id":self.get_aws_id(),"ssh_key_name":self.get_ssh_key_name(),"ip_address":self.get_ip_address(), "username": self.get_username(),"port":self.get_port(),"filters":self.get_filters(),"logs":self.get_logs()}
      if self.get_log_conf() is not None:
         result['log_conf'] = self.get_log_conf().to_json()
      else:
         result['log_conf'] = None
      return result

   def __unicode__(self):
      return json.dumps(self.to_json())

   def __eq__(self, other):
      return (isinstance(other, self.__class__) and self.get_aws_id() == other.get_aws_id())

   def __ne__(self, other):
      return not self.__eq__(other)
