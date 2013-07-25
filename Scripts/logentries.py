LE_SERVER_API = 'api.logentries.com'
LE_SERVER_PORT = 443
CONFIG_FILE = 'logentries_config.json'
ACCOUNT_KEY = ''
CONF_FILE = 'logentries.conf'


import urllib, httplib, getpass, sys, socket, subprocess

def die(cause, exit_code=0):
   print cause
   sys.exit(exit_code)

try:
   import ssl
except ImportError: die( 'NOTE: Please install Python "SSL" module')

try:
    import json
except ImportError:
    die( 'Could not import json')


def load_config(file):
   conf_str = open(file,'r')
   CONFIG = json.load(conf_str)
   try:
      ACCOUNT_KEY = CONFIG['account_key']
   except:
      print 'Please enter your account key in '
   return ACCOUNT_KEY,CONFIG

CONFIG = load_config(CONFIG_FILE)

def make_request(req_dict,conf):
   data = {}
   try:
      url = LE_SERVER_API
      c = httplib.HTTPConnection(url)
      
      request_encoded = urllib.urlencode(req_dict)
      print request_encoded
      c.request("POST", '/', request_encoded)
      r = c.getresponse()

      if r.status == None:
         print 'No response obtained!'
         c.close()
      elif r.status != 200:
         data = json.dumps({'response': 'error', 'reason': r.reason})
      else:
         data = r.read()
      c.close()
   except socket.error, e:
      print e
   except httplib.BadStatusLine, e:
      print e
   print 'Response: %s'%data
   print 'Data type: %s'%(type(data))
   return data

def create_host(instance_data,conf):
   """ Args: instance_data is a json representation of an instance as decribe in CONF_FILE """
   instance_name = instance_data["name"]
   instance_ip = instance_data["ip"]
   req_dict = {"user_key": conf['account_key'],"request":"register","name":'%s-%s'%(instance_name,instance_ip)}
   resp_data = make_request(req_dict,conf)
   print 'Returned Data: %s'%resp_data
   res = json.loads(resp_data)
   return res["host_key"]

def retrieve_log_names(instance,conf):
   p = subprocess.Popen(["ssh", "-i", instance['ssh_key'],"%s@%s"%(instance['user'],instance['ip']), "find /var/log/ -name *.log"], shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
   result = [item.split('\n')[0] for item in p.stdout.readlines()]
   if result == []:
      error = p.stderr.readlines()
      print >>sys.stderr, "ERROR: %s" % error
   return result

def create_log(logfile_path,instance_data,host_key,conf):
   """ Args: instance_data is a json representation of an instance as decribe in CONF_FILE
   logfile_path is the path of the log file to create"""
   instance_name = instance_data["name"]
   instance_ip = instance_data["ip"]
   # Get the file name from its path
   #name = logfile_path.rsplit('/',1)[0]
   request_uni = {"user_key": conf['account_key'],"request":"new_log","agent_key":host_key,"source":"token","name":logfile_path}
   resp = make_request(request_uni,conf)
   res = json.loads(resp)
   print 'Log created: %s'%res
   return res["log"]


def get_log(log_key):
   """ """
   request_uni = {"request":"get_log","log_key":log_key}
   resp = make_request(request_uni,conf)
   res = json.loads(resp)
   print 'Log retrieved: %s'%res
   return res["log"]


def get_log_list(host_key):
   """ """
   request_uni = {"request":"list_logs","log_key":log_key}
   resp = make_request(request_uni,conf)
   res = json.loads(resp)
   print 'Log retrieved: %s'%res
   return res["logs"]


def create_logs(logfile_paths,instance_data,host_key,conf,conf_file):
   templates = ""
   for logfile_path in logfile_paths:
      log_data = create_log(logfile_path,instance_data,host_key,conf)
      file_entry_rsyslog,template = create_rsyslog_entry(log_data)
      conf_file.write(file_entry_rsyslog)
      templates = templates + template + "\n"
   conf_file.write(get_poll_rsyslog_conf())
   conf_file.write(templates)

def create_rsyslog_entry(log_data):
   """ Returns the strings representing an rsyslog template as well as an rsyslog entry for the log data provided
   Args: log_data must contain the path to the log file to be followed by rsyslog"""
   file_path = log_data['name']
   file_id = file_path.replace('/','_')
   format_name = "LogentriesFormat_"+file_id
   return """# FILE
$InputFileName """+file_path+"""
$InputFileTag """+file_id+"""
$InputFileStateFile """+file_id+"""
$InputFileSeverity info
$InputFileFacility local7
$InputRunFileMonitor\n\n
""","""$template """+format_name+""",\""""+log_data['token']+""" %HOSTNAME% %syslogtag%%msg%\\n\"
if $programname == '"""+file_id+"""' then @@api.logentries.com:10000;"""+format_name+"""\n
"""


def get_start_rsyslog_conf():
   return """$Modload imfile\n\n"""

def get_poll_rsyslog_conf():
   return """
# check for new lines every 10 seconds
# Only entered once in case of following multiple files
$InputFilePollInterval 10\n\n"""


def deploy_rsyslog_conf(filename,instance):
   p = subprocess.Popen(["scp", "-i", instance['ssh_key'],filename,"%s@%s:/etc/rsyslog.d/."%(instance['user'],instance['ip'])], shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
   error = p.stderr.readlines()
   return error


def restart_rsyslog(instance):
   p = subprocess.Popen(["ssh", "-i", instance['ssh_key'],"%s@%s"%(instance['user'],instance['ip']), "/etc/init.d/rsyslog restart"], shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
   error = p.stderr.readlines()
   return error


if __name__ == '__main__':
   conf_file_name = 'logentries.conf'
   ACCOUNT_KEY,CONFIG = load_config(conf_file_name)
   for key in CONFIG:
      print '(%s : %s)'%(key,CONFIG[key])
   instance_data = CONFIG["instances"][0]
   host_key = create_host(instance_data,CONFIG)
   logfile_paths = retrieve_log_names(CONFIG["instances"][0],CONFIG)
   rsyslog_conf_file = open(conf_file_name,'w')
   rsyslog_conf_file.write(get_start_rsyslog_conf())
   create_logs(logfile_paths,instance_data,host_key,CONFIG,rsyslog_conf_file)
   rsyslog_conf_file.close()
   deploy_rsyslog_conf(conf_file_name,CONFIG["instances"][0])
   restart_rsyslog(CONFIG["instances"][0])
   
