def parse_boolean( b_value ):
	""" Parses string booleans. """
	if b_value.lower() == 'false':
		return False
	elif b_value.lower() == 'true':
		return True
	else:
		return None

class Log:
	def __init__(self):
		self._key = None
		self._name = None
		self._filename = None
		self._type = None
		self._retention = None
		self._object = None
		self._follow = None
		self._created = None
		self._port = None
		self._token = None

	def __repr__(self):
		return 'Log:%s' % self._name

	def load_data(self, log_obj):
		self._key = str(log_obj['key'])
		self._name = str(log_obj['name'])
		self._filename = str(log_obj['filename'])
		self._type = str(log_obj['type'])
		self._retention = log_obj['retention']
		self._object = str(log_obj['object'])
		self._follow = parse_boolean(log_obj['follow'])
		self._created = log_obj['created']
		self._port = log_obj['port'] if 'port' in log_obj else None
		self._token = str(log_obj['token']) if 'token' in log_obj else None

	def get_key(self):
		return self._key

	def to_json(self):
		log_repr = {'key':self._key,'name':self._name,'filename':self._filename,'type':self._type,
					'retention':self._retention,'object':self._object, 'follow':self._follow,'created':self._created}
		if self._port is not None:
			log_repr['port'] = self._port
		elif self._token is not None:
			log_repr['token'] = self._token

		return log_repr

class Host(object):
	def __init__(self):
		self._name = None
		self._location = None
		self._key = None
		self._logs = []

	def __repr__(self):
		return 'Host:%s' % self._name

	def load_data(self, host_obj):
		self._name = str(host_obj['host']['name'])
		self._location = str(host_obj['host']['hostname'])
		self._key = str(host_obj['host']['key'])

	def get_key(self):
		return self._key

	def add_log(self, log):
		# TODO  Should the list allow duplicates?
		self._logs.append(log)

	def add_logs(self, logs):
		for log in logs:
			self.add_log(log)

	def rm_log(self, log_key):
		self._logs = [x for x in self._logs if log.get_key() != log_key]

	def to_json(self):
		host_repr = {'key':self._key,'name':self._name,'hostname':self._location,'logs':[]}
		for log in self._logs:
			host_repr['logs'].append(log.to_json())
		return host_repr


class Account:
	def __init__(self, account_key=None):
		self._account_key = str(account_key)
		self._hosts = []

	def add_host(self, host_data):
		host = Host()
		host.load_data( host_data )
		self._hosts.append(host)
		return host

	def edit_host(self, host_data):
		pass

	def rm_host(self, host_key):
		self._hosts = [x for x in self._hosts if x.key != host_key]

	def add_log_to_host(self, host_key, log_data):
		log = Log()
		log.load_data( log_data['log'] )
		for host in self._hosts:
			if host.get_key() == host_key:
				host.add_log(log)
		return log

	def rm_log_from_host(self, host_key, log_key):
		for host in self._hosts:
			if host.get_key() == host_key:
				host.rm_log(log_key)

	def to_json(self):
		account_repr = {'account_key':self._account_key, 'hosts':[]}
		for host in self._hosts:
			account_repr['hosts'].append(host.to_json())
		return str(account_repr)

	@staticmethod
	def load_json(self, json_data):
		account = Account