class InvalidAccountKeyException(Exception):
	""" This Exception is raised when no Logentries Account Key is provided for an API call that requires authentication.
		It can provided as a parameter to the method or by setting a $LOGENTRIES_ACCOUNT_KEY environment variable."""
	pass

class MissingModuleExcpetion(Exception):
	""" This Exception is raised when a python module is missing which is required to use this SDK. """
	pass

class InvalidParametersException(Exception):
	""" This Exception is raised when not enough parameters are provided to do anything with the API call."""
	pass

class InvalidServerResponse(Exception):
	""" This Exception is raised when an invalid response is returned from the Logentries server."""
	pass 

class InvalidLogSourceException(Exception):
	""" This Exception is raised when an invalid source is provided for a log object."""
	pass