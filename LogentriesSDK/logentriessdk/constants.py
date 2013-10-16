#
# Server Details
#

LE_SERVER_API = 'api.logentries.com'
LE_SERVER_API_LOCAL = '127.0.0.1'
LE_SERVER_API_PORT = 443

#
# API calls
#
API_GET_ACCOUNT = "get_user"

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
# Misc
#
ACCOUNT_KEY_ENV_VAR = 'LOGENTRIES_ACCOUNT_KEY'

RESP_OK = "ok"
DEFAULT_RETENTION = -1

COLORS=["ff0000", "ff9933", "009900", "663333", "66ff66", "333333", "000099", "0099ff"]
