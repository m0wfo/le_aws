import logging
import json

ACCOUNT_KEY = None
WORKING_DIR = None
AWS_SECRET_ACCESS_KEY = None
AWS_ACCESS_KEY_ID = None

from logentries import LogentriesHandler
logger = logging.getLogger('sync')

def set_working_dir(working_dir):
    global WORKING_DIR
    WORKING_DIR = working_dir

def set_account_key(conf_file_name):
    """
    """
    global ACCOUNT_KEY
    global WORKING_DIR
    if conf_file_name is None:
        conf_file_name='%slogentries.json'%(WORKING_DIR+'/' if WORKING_DIR is not None else '')

    try:
        account_key_file = open(conf_file_name,'r')
    except:
        logger.error('Could not open %s',conf_file_name)
        account_key_file = None

    # Retrieve account key from file
    global ACCOUNT_KEY
    if account_key_file is None:
        ACCOUNT_KEY = None
        return

    try:
        account_key_json = json.load(account_key_file)
    except:
        logger.error('Could not load json structure from %s'%conf_file_name)
        account_key_json = None

    if account_key_json is not None and 'account_key' in account_key_json.keys():
        ACCOUNT_KEY = account_key_json['account_key']
    else:
        ACCOUNT_KEY = None
        print 'Could not retrieve logentries account key from json in logentries.json'
        logger.error('Could not retrieve logentries account key from json in logentries.json')

def set_aws_credentials(conf_file_name):
    """
    """
    global AWS_SECRET_ACCESS_KEY
    global AWS_ACCESS_KEY_ID
    global WORKING_DIR
    if conf_file_name is None:
        conf_file_name='%saws.json'%(WORKING_DIR+'/' if WORKING_DIR is not None else '')
        print 'conf file name = %s'%conf_file_name
    try:
        aws_conf_file = open(conf_file_name,'r')
    except:
        logger.error('Could not open %s',conf_file_name)
        aws_conf_file = None
    # Retrieve account key from file
    if aws_conf_file is None:
        AWS_SECRET_ACCESS_KEY = None
        AWS_ACCESS_KEY_ID = None
        return

    try:
        aws_conf_json = json.load(aws_conf_file)
    except:
        logger.error('Could not load json structure from %s'%conf_file_name)
        aws_conf_json = None

    if aws_conf_json is not None:
        if 'aws_secret_access_key' in aws_conf_json.keys():
            AWS_SECRET_ACCESS_KEY = aws_conf_json['aws_secret_access_key']
        if 'aws_access_key_id' in aws_conf_json.keys():
            AWS_ACCESS_KEY_ID = aws_conf_json['aws_access_key_id']
    else:
        AWS_SECRET_ACCESS_KEY = None
        AWS_ACCESS_KEY_ID = None
        print 'Could not retrieve AWS credentials from json in %s'%conf_file_name
        logger.error('Could not retrieve AWS credentials from json in %s',conf_file_name)

def get_account_key():
    global ACCOUNT_KEY
    return ACCOUNT_KEY

def get_aws_secret_access_key():
    global AWS_SECRET_ACCESS_KEY
    return AWS_SECRET_ACCESS_KEY

def get_aws_access_key_id():
    global AWS_ACCESS_KEY_ID
    return AWS_ACCESS_KEY_ID

def set_logentries_logging():
    if get_account_key() is not None:
        logger = logging.getLogger('sync')
        log_handler = LogentriesHandler('2de80254-62bb-4ea3-9437-b79f6c20d314')
        logger.addHandler(log_handler)


