from logentries import LogentriesHandler
import logentriesprovisioning
from LogentriesSDK import logentriessdk

# create logger
logger = logging.getLogger('sync')
logger.setLevel(logging.DEBUG)
# create logger handlers
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
format_handler = logging.StreamHandler()
format_handler.setFormatter(formatter)
logger.addHandler(format_handler)

# 
constants.set_account_key()
if constants.ACCOUNT_KEY is not None:
    log_handler = LogentriesHandler('2de80254-62bb-4ea3-9437-b79f6c20d314')
    logger.addHandler(log_handler)
