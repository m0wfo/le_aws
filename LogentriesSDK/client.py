#!/usr/bin/python

#
# Logentries agent <https://logentries.com/>.
# This work is licensed under a <http://creativecommons.org/licenses/by/3.0/> Creative Commons Attribution 3.0 Unported License
#
# Mark Lacomber <mark@logentries.com>

"""The **LogentriesSDK.client.LogentriesClient** class provides a Python interface to the Logentries API,
allowing you to programmatically access Logentries resources.

You can instantiate this class as follows:    client = LogentriesClient('my_account_key'), where you would provide your Logentries
Account Key as the only parameter, if you don't provide it as a parameter, you must set an environment variable called 
LOGENTRIES_ACCOUNT_KEY contaning your account key.

Once created, you have the following methods at your disposal.  * indicates a parameter is optional

client.create_host( name )
client.update_host( host, *name, *location )
client.remove_host( host )
client.create_log_token( host, logname )
client.create_log_http( host, logname )
client.create_log_agent( host, logname, filename )
client.create_log_syslog( host, logname )
client.remove_log( host, log )

See individual calls for more information
"""

#
# Constants
#

VERSION="0.1"

#
# Modules
#
import os
import sys

#
# Le Modules
#
from LogentriesSDK.connection import LogentriesConnection 
from LogentriesSDK.exception import InvalidParametersException, InvalidLogSourceException
import LogentriesSDK.constants as constants
import LogentriesSDK.helpers as helpers
import LogentriesSDK.models as models
import inspect

class Client(models.Account):

	def __init__(self, account_key=None):
		acc_key = helpers.check_user_key(account_key)
		models.Account.__init__(self, acc_key)
		self._conn = LogentriesConnection()

	def _create_log( self, host, log_name, source, filename=None):

		if isinstance( host, models.Host ):
			host_key = host.get_key()
		elif isinstance( host, str):
			host_key = host
		else:
			raise InvalidParametersException

		if not helpers.is_valid_log_source( source ):
			raise InvalidLogSourceException

		request = {
			'request': constants.API_NEW_LOG,
			'user_key': self._account_key,
			'host_key': host_key,
			'name': log_name,
			'type': '',
			'retention': constants.DEFAULT_RETENTION,
			'source': source
		}

		request['filename'] = filename if filename is not None else ''

		log_data, success = self._conn.request( request )

		if success:
			return self.add_log_to_host( host_key, log_data )
		else:
			return None

	def create_host( self, name, **optionals ):
		""" Creates a new host on Logentries. 
		Required Parameters:
			name     (This is the name of the host)
		Optional Parameters:
			location (This is the name of the server)

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

		location = optionals.get( 'location','' )

		request = {
			'request': constants.API_NEW_HOST,
			'user_key': self._account_key,
			'name': name,
			'hostname': location,
			'distver': '',
			'system': '',
			'distname': ''
		}

		host_data, success = self._conn.request( request )

		if success:
			return self.add_host(host_data)
		else:
			return None

	def update_host( self, host, **optionals ): 
		""" Updates an existing host on Logentries.
			Required Parameters:
				host (Host object returned by the create_host method or the host_key UUID for it)
			Optional Parameters:
				name	 (The new name you would like to give the host)
				location (The new name of the server you would like to give the host

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

		host_key = helpers.validate_parameter( models.Host, host, 'key' )

		name = optionals.get( 'name', '' )
		location = optionals.get( 'location', '' )

		if helpers.parameters_are_empty( name, location ):
			raise InvalidParametersException("You must provide either 'name' or 'hostname' values to update a host")
			
		request = {
			'request': constants.API_SET_HOST,
			'user_key': self._account_key,
			'host_key': host_key,
		}

		if name != '':
			request['name'] = name

		if location != '':
			request['hostname'] = location

		host_data, success = self._conn.request( request )

	def remove_host( self, host, **optionals ):
		""" Removes an existing host on Logentries.
			Required Parameters:
				host (host object returned by the create_host method)			
			
			Successful response returns object as follows:
			{
				"response":"ok",
				"host_key":"12345678-1234-1234-1234-123456789123",
				"user_key":"12345678-1234-1234-1234-123456789123",
				"reason": "Host 'host_name' removed."
			}"""

		host_key = helpers.validate_parameter( models.Host, host, 'key' )

		request = {
			'request': constants.API_RM_HOST,
			'user_key': self._account_key,
			'host_key': host_key
		}

		removed_host, success = self._conn.request( request )
		self.rm_host( host_key )

		if success:
			return True
		else:
			return False

	def create_log_token( self, host, log_name, **optionals ):
		""" Creates a log of source type Token TCP. 
			Required Parameters:
				host (The host object returned by create_host you wish to create the log in)
				log_name (The name you would like to give the new log)

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

		return self._create_log( host, log_name, constants.LOG_TOKEN )

	def create_log_http( self, host, log_name, **optionals ):
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

		return self._create_log( host, log_name, constants.LOG_HTTP )

	def create_log_agent( self, host, log_name, filename, **optionals ):
		""" Creates a log of source type 'agent'. To be used in conjunction with logentries agent.
			Required Parameters:
				host (The host object returned by create_host you wish to create the log in)
				log_name (The name you would like to give the new log)
				filename (The full location of the file on your machine)

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

		return self._create_log( host, log_name, constants.LOG_AGENT, filename )

	def create_log_syslog( self, host, log_name, **optionals ):
		""" Creates a log of source type Syslog.
			Required Parameters:
				host (The host object returned by create_host you wish to create the log in)
				log_name (The name you would like to give the new log)

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

		return self._create_log( host_key, log_name, constants.LOG_SYSLOG )

	def remove_log( self, host, log, **optionals ):
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

		host_key = helpers.validate_parameter( Host, host, 'key' )
		log_key = helpers.validate_parameter( Log, log, 'key' )

		request = {
			'request': API_RM_LOG,
			'user_key': self._account_key,
			'host_key': host_key,
			'log_key': log_key
		}

		removed_log, success = self._conn.request( request )

		self.rm_log_from_host( host_key, log_key )
		if success:
			return True
		else:
			return False