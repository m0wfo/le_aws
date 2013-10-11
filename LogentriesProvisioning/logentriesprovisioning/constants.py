ACCOUNT_KEY = None

def set_account_key(conf_file_name):
    """
    """
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
        logger.error('Could not load json structure from logentries.json')
        account_key_json = None

    if account_key_json is not None and 'account_key' in account_key_json.keys():
        ACCOUNT_KEY = account_key_json['account_key']
    else:
        ACCOUNT_KEY = None
        print 'Could not retrieve logentries account key from json in logentries.json'
        logger.error('Could not retrieve logentries account key from json in logentries.json')
