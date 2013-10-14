#import constants
import logentriessdk
import logging

# create logger
logger = logging.getLogger('sync')
logger.setLevel(logging.DEBUG)
# create logger handlers
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
format_handler = logging.StreamHandler()
format_handler.setFormatter(formatter)
logger.addHandler(format_handler)
