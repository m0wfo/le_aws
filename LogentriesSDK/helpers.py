from LogentriesSDK.exception import InvalidAccountKeyException, InvalidParametersException
import LogentriesSDK.constants as constants
import LogentriesSDK.models as models

"""
Some helper methods used by the SDK
"""

def get_env_user_key( ):
	""" Returns the user_key or None if not provided """
	env_key = os.getenv( constants.ACCOUNT_KEY_ENV_VAR )

	return env_key

def check_user_key( account_key):
	if account_key is None:
		acc_key = get_env_user_key()
		if acc_key is None:
			raise InvalidAccountKeyException
	
	return account_key or acc_key

def is_valid_log_source( source ):
	""" Returns True is source is a valid Log Source. """
	return source in constants.LOG_SOURCES

def parameters_are_empty( *params ):
	""" Returns True if list of parameters is empty or all values blank strings. """
	return len([x for x in params if x != '']) == 0

def inspect_host( host ):
	if isinstance( host, models.Host ):
		host_key = host.get_key()
	elif isinstance( host, str):
		host_key = host
	else:
		raise InvalidParametersException

	return host_key

def inspect_log( log ):
	if isinstance( log, models.Log ):
		log_key = log.get_key()
	elif isinstance( log, str):
		log_key = log
	else:
		raise InvalidParametersException

	return log_key