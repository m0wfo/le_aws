from LogentriesSDK.exception import InvalidAccountKeyException, InvalidParametersException
import constants

"""
Some helper methods used by the SDK
"""

def get_env_user_key( self ):
	""" Returns the user_key or None if not provided """
	env_key = os.getenv( constants.ACCOUNT_KEY_ENV_VAR )

	return env_key

def check_user_key(self, account_key):
	if account_key is None:
		acc_key = get_env_user_key()
		if acc_key is none:
			raise InvalidAccountKeyException
	
	return True

def is_valid_log_source( source ):
	""" Returns True is source is a valid Log Source. """
	return source in constants.LOG_SOURCES

def parameters_are_empty( *params ):
	""" Returns True if list of parameters is empty or all values blank strings. """
	return len([x for x in params if x != '']) == 0

def validate_parameter( obj, k, v ):
	if isinstance( v, obj ):
		return obj[k]
	elif isinstance( v, str ):
		return v
	else:
		raise InvalidParametersException