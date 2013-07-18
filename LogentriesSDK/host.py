from LogentriesSDK.log import Log

"""
Represents a Logentries Host
"""

class Host:
	def __init__(self, host_obj):
		self._name = host_obj['host']['name']
		self._hostname = host_obj['host']['name']
		self._key = host_obj['host']['key']
		self.logs = []

	def __repr__(self):
		return 'Host:%s' % self._name

	def get_name(self):
		return self._name

	def get_key(self):
		return self._key
