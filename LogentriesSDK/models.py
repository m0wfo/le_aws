import LogentriesSDK.helpers

class Log:
	def __init__(self, log_obj):
		self._key = log_obj['key']
		self._name = log_obj['name']
		self._filename = log_obj['filename']
		self._type = log_obj['type']
		self._retention = log_obj['retention']
		self._object = log_obj['log']
		self._followed = log_obj['followed']
		self._created = log_obj['created']

	def __repr__(self):
		return 'Log:%s' % self.name

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, value):
		self._name = value

	@property
	def key(self):
		return self._key
	
	@key.setter
	def key(self, value):
		self._key = value

	@property
	def filename(self):
		return self._filename
	
	@filename.setter
	def filename(self, value):
		self._filename = value

	@property
	def source(self):
		return self._type

	@source.setter
	def source(self, value):
	    self._type = value


class Host:
	def __init__(self, host_obj):
		self._name = host_obj['host']['name']
		self._location = host_obj['host']['hostname']
		self._key = host_obj['host']['key']
		self.logs = []

	def __repr__(self):
		return 'Host:%s' % self._name

	@property
	def name(self):
		return self._name

	@property
	def location(self):
		return self._location

	@property
	def key(self):
		return self._key

	@name.setter
	def name(self, value):
		self._name = value

	@location.setter
	def location(self, value):
		self._location = value

	def add_log(self, log):
		self.logs.append(log)

	def add_logs(self, logs):
		for log in logs:
			self.add_log(log)

class Account:
	def __init__(self, account_key=None):
		self._account_key = account_key
		self._hosts = []

	def add_host(self, host_data):
		host = Host( host_data )
		self.hosts.append(host)
		return Host

	def change_host(self, host_data):
		pass

	def rm_host(self, host_key):
		self._hosts = [x for x in self._hosts if x.key != host_key]

	def add_log_to_host(self, host_key, log_data):
		pass
