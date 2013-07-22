import constants
from LogentriesSDK.exception import InvalidServerResponse, MissingModuleException

try:
	import ssl
except ImportError:
	raise MissingModuleException("Please install the python SSL module to use this SDK.")

try:
	import json
except ImportError:
	try:
		import simplejson
	except ImportError:
		raise MissingModuleException("Please install the python JSON module to use this SDK.")

class LogentriesConnection:
	def __init__(self):
		pass

	def _make_api_call( self, request ):
		try:
			http = httplib.HTTPSConnection( constants.LE_SERVER_API, constants.LE_SERVER_API_PORT )
			params = urllib.urlencode(request)
			http.request( "POST", "/", params)
			resp = http.getresponse()
		except socket.sslerror, msg:
			raise InvalidServerResponse(msg)
		except socket.error, msg:
			raise InvalidServerResponse(msg)
		except httplib.BadStatusLine:
			raise InvalidServerResponse("Unrecognised status code returned from Logentries server.")

		try:
			data = json.loads( resp.read() )
		except AttributeError:
			data = simplejson.loads( resp.read() )

		http.close()	

		if data[ 'response'] != constants.RESP_OK:
			return data, False

		return data, True

	def request( self, request ):
		return _make_api_call( request )