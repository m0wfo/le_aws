#!/usr/bin/python

#
# Logentries agent <https://logentries.com/>.
# This work is licensed under a <http://creativecommons.org/licenses/by/3.0/> Creative Commons Attribution 3.0 Unported License
#
# Mark Lacomber <mark@logentries.com>

"""The **LogentriesSDK.client** module provider a Python interface to the Logentries API,
allowing you to programmatically access Logentries resources.

Each method that requires authentication will take an optional Logentries Account Key as 
the last parameter but it will also check for a $LOGENTRIES_ACCOUNT_KEY environment variable."""

#
# Constants
#

VERSION="0.1"
LE_SERVER_API = 'api.logentries.com'
LE_SERVER_API_LOCAL = '127.0.0.1'
LE_SERVER_API_PORT = 443

ACCOUNT_KEY_ENV_VAR = 'LOGENTRIES_ACCOUNT_KEY'

RESP_OK = "ok"
DEFAULT_RETENTION = -1

#
# API calls
#
API_NEW_HOST = "register"
API_SET_HOST = "set_host"
API_RM_HOST = "rm_host"

API_NEW_LOG = "new_log"
API_SET_LOG = "set_log"
API_GET_LOG = "get_log"
API_RM_LOG = "rm_log"

#
# Log Sources 
#
LOG_TOKEN = "token"
LOG_HTTP = "api"
LOG_AGENT = "agent"
LOG_SYSLOG = "syslog"

LOG_SOURCES = [ LOG_TOKEN, LOG_HTTP, LOG_AGENT, LOG_SYSLOG ]

#
# Modules
#
import urllib
import httplib
import os
import sys

#
# Le Modules
#
from LogentriesSDK.host import Host

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

def _make_api_call( request ):
	try:
		http = httplib.HTTPSConnection( LE_SERVER_API, LE_SERVER_API_PORT )
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

	if data[ 'response'] != RESP_OK:
		return data, False

	return data, True

def _user_key_required( account_key ):
	""" Returns the user_key or None if not provided """
	env_key = os.getenv( ACCOUNT_KEY_ENV_VAR )

	if env_key is None and account_key is None:
		raise InvalidAccountKeyException

	return env_key or account_key

def _parameters_are_empty( *params ):
	""" Returns True if list of parameters is empty or all values blank strings. """
	return len([x for x in params if x != '']) == 0

def _is_valid_log_source( source ):
	""" Returns True is source is a valid Log Source. """
	return source in LOG_SOURCES

def _is_object( obj ):
	"""
	"""
def create_host( name, **optionals ):
	""" Creates a new host on Logentries. 
		Required Parameters:
			name     (This is the name of the host)
		Optional Parameters:
			location (This is the name of the server)
			account_key ( Logentries Account Key, can be environment variable or passed to method )

		Successful response returns object as follows:
		{
			"response": "ok",
			"host": { "logs"    : [],    # List of logs inside host, not applicable for creation
					  "c"       : 123445678,  #Creation date in Unix Epoch
					  "name"    : "name you provided",
					  "distver" : "",  
					  "hostname": "location you provided, else 'nolocation'",
					  "object"  : "host",
					  "distname": "",
					  "key"     : "12345678-1234-1234-1234-123456789123",
					},
			"user_key":"12345678-1234-1234-1234-123456789123",
			"agent_key":"12345678-1234-1234-1234-123456789123"
		}"""

	user_key = _user_key_required( optionals.get('account_key', None) )
	location = optionals.get( 'location','' )

	request = {
		'request': API_NEW_HOST,
		'user_key': user_key,
		'name': name,
		'hostname': location,
		'distver': '',
		'system': '',
		'distname': ''
	}

	host_data, success = _make_api_call( request )

	if success:
		return Host(host_data)
	else:
		#XXX Empty host or Failure Object?
		pass

def update_host( host, **optionals ): 
	""" Updates an existing host on Logentries.
		Required Parameters:
			host (Host object returned by the create_host method)
		Optional Parameters:
			name	 (The new name you would like to give the host)
			location (The new name of the server you would like to give the host
			account_key (Logentries Account Key, can be environment variable, or passed to method)

		Successful response returns object as follows:
		{	
			"response":"ok",
			"host": { "logs"    : [],    # List of logs inside host, not applicable for creation
					  "c"       : 123445678,  #Creation date in Unix Epoch
					  "name"    : "name you provided",
					  "distver" : "",  
					  "hostname": "location you provided, else 'nolocation'",
					  "object"  : "host",
					  "distname": "",
					  "key"     : "12345678-1234-1234-1234-123456789123",
					},
			"user_key":"12345678-1234-1234-1234-123456789123"
		}"""

	user_key = _user_key_required( optionals.get('account_key', None) )
	name = optionals.get( 'name', '' )
	location = optionals.get( 'location', '' )

	if _parameters_are_empty( name, location ):
		raise InvalidParametersException("You must provide either 'name' or 'hostname' values to update a host")
		
	request = {
		'request': API_SET_HOST,
		'user_key': user_key,
		'host_key': host[ 'key'],
	}

	if name != '':
		request['name'] = name

	if location != '':
		request['hostname'] = location

	return _make_api_call( request )

def remove_host( host, **optionals ):
	""" Removes an existing host on Logentries.
		Required Parameters:
			host (host object returned by the create_host method)
		Optional Parameters:
			account_key (Logentries Account Key, can be environment variable or passed to method)			
		
		Successful response returns object as follows:
		{
			"response":"ok",
			"host_key":"12345678-1234-1234-1234-123456789123",
			"user_key":"12345678-1234-1234-1234-123456789123",
			"reason": "Host 'host_name' removed."
		}"""

	user_key = _user_key_required( optionals.get('account_key', None) )

	request = {
		'request': API_RM_HOST,
		'user_key': user_key,
		'host_key': host[ 'key']
	}

	return _make_api_call( request )

def _create_log( account_key, host, log_name, source, filename='' ):

	request = {
		'request': API_NEW_LOG,
		'user_key': account_key,
		'host_key': host[ 'key'],
		'name': log_name,
		'type': '',
		'filename': filename,
		'retention': DEFAULT_RETENTION,
		'source': source
	}

	return _make_api_call( request )

def _update_log( account_key, host_key, log_key ):

	request = {
		'request': API_SET_LOG,
		'user_key': account_key,
		'host_key': host_key,
		'log_key': log_key,
	}
	return 1	

def create_log_token( host, log_name, **optionals ):
	""" Creates a log of source type Token TCP. 
		Required Parameters:
			host (The host object returned by create_host you wish to create the log in)
			log_name (The name you would like to give the new log)
		Optional Parameters:
			account_key (Logentries Account Key, can be environment variable or passed to method)	

		Successful response returns object as follows:
		{
			"response":"ok",
			"log_key" :"12345678-1234-1234-123456789123",
			"log":{
					"token"  :"12345678-1234-1234-123456789123",#Use this Token to send events
					"created":12345678910, 						#Unix Epoch creation
					"name"   :"log_name",
					"retention":-1,  							#Default retention
					"filename":"", 							#Only used for agent logs
					"object" :"log",
					"type"   :"token",
					"key"	 :"12345678-1234-1234-1234-123456789123",
					"follow" :"false" 
				  }
		}"""

	user_key = _user_key_required( optionals.get('account_key',None) )

	return _create_log( user_key, host, log_name, LOG_TOKEN )

def create_log_http( host, log_name, **optionals ):
	""" Creates a log of source type HTTP PUT. 
		Required Parameters:
			host (The host object returned by create_host you wish to create the log in)
			log_name (The name you would like to give the new log)
		Optional Parameters:
			account_key (Logentries Account Key, can be environment variable or passed to method)	

		Successful response returns object as follows:
		{
			"response":"ok",
			"log_key" :"12345678-1234-1234-123456789123",
			"log":{
					"created":12345678910, 					#Unix Epoch creation
					"name"   :"log_name",
					"retention":-1,  						#Default retention
					"filename":"", 							#Only used for agent logs
					"object" :"log",
					"type"   :"api",
					"key"	 :"12345678-1234-1234-1234-123456789123",
					"follow" :"false" 
				  }
		}"""

	user_key = _user_key_required( optionals.get('account_key', None) )

	return _create_log( user_key, host, log_name, LOG_HTTP )

def create_log_agent( host, log_name, filename, **optionals ):
	""" Creates a log of source type 'agent'. To be used in conjunction with logentries agent.
		Required Parameters:
			host (The host object returned by create_host you wish to create the log in)
			log_name (The name you would like to give the new log)
			filename (The full location of the file on your machine)
		Optional Parameters:
			account_key (Logentries Account Key, can be environment variable or passed to method)	

		Successful response returns object as follows:
		{
			"response":"ok",
			"log_key" :"12345678-1234-1234-123456789123",
			"log":{
					"created":12345678910, 						#Unix Epoch creation
					"name"   :"log_name",
					"retention":-1,  							#Default retention
					"filename":"filename", 
					"object" :"log",
					"type"   :"agent",
					"key"	 :"12345678-1234-1234-1234-123456789123",
					"follow" :"true" 
				  }
		}"""

	user_key = _user_key_required( optionals.get('account_key',None) )

	return _create_log( user_key, host, log_name, LOG_AGENT, filename )

def create_log_syslog( host, log_name, **optionals ):
	""" Creates a log of source type Syslog.
		Required Parameters:
			host (The host object returned by create_host you wish to create the log in)
			log_name (The name you would like to give the new log)
		Optional Parameters:
			account_key (Logentries Account Key, can be environment variable or passed to method)	

		Successful response returns object as follows:
		{
			"response":"ok",
			"log_key" :"12345678-1234-1234-123456789123",
			"log":{
					"port":12345 					#Use this port to send events
					"created":12345678910, 			#Unix Epoch creation
					"name"   :"log_name",
					"retention":-1,  				#Default retention
					"filename":"", 					#Not used for token logs
					"object" :"log",
					"type"   :"token",
					"key"	 :"12345678-1234-1234-1234-123456789123",
					"follow" :"false" 
				  }
		}"""

	user_key = _user_key_required( optionals.get('account_key',None) )

	return _create_log( user_key, host_key, log_name, LOG_SYSLOG )

def update_log( host, log, **optionals ):
	""" Updates a logfile on Logentries.
		Required Parameters:
			host (The host object returned by create_host that contains the log)
			log (The log object returned by create_log that you want to update)
		Optional Parameters:
			account_key (Logentries Account Key, can be environment variable or passed to method)
			log_name (The new name you would like to give the log
			source (The new source you would like to give the log, can only be 'token','api','agent' or 'syslog'
		
		Successful response returns object as follows:
		{

		}"""
	
	user_key = _user_key_required( optionals.get('account_key',None) )
	source = optionals.get( 'source','' )

	if not _is_valid_source( source ):
		raise InvalidParametersException("The source you provided is not a valid option, Options are: 'token','api','agent' and 'syslog'")

	return 1 

def remove_log( host_key, log_key, **optionals ):
	""" Deletes an existing logfile on Logentries.
		Required Parameters:
			host_key (The UUID key of the host containing the log)
			log_key (The UUID key of the log you would like to remove)
		Optional Parameters:
			account_key (Logentries Account Key, can be environment variable or passed to method)

		Successful response returns the following object:
		{
			"response":"ok",
			"host_key":"12345678-1234-1234-1234-123456789123",
			"reason"  :"Log 'log_name' removed",
			"user_key":"12345678-1234-1234-1234-123456789123",
			"log_key" :"12345678-1234-1234-1234-123456789123"
		}"""

	user_key = _user_key_required( optionals.get('account_key',None) )

	request = {
		'request': API_RM_LOG,
		'user_key': user_key,
		'host_key': host_key,
		'log_key': log_key
	}

	return _make_api_call( request )
