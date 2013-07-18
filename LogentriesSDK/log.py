"""
Represents a Logentries log object
"""
LOG_SOURCE_TOKEN = 

rel = {}


class Log:
	def __init__(self, log_data):
		self._name = log_data['log']['name']
		self._key = log_data['log']['key']
		self._type = log_data['log']['type']

	def __repr__(self):
		return "Log:%s" %self._name

	def get_name(self):
		return self._name

	def get_source
