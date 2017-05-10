# import logging
#
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO, format='%(levelname)s-[%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s')
# logging.

#
import config
import logging
import logging.handlers
from logging.config import dictConfig

logger = logging.getLogger(__name__)

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

dictConfig(DEFAULT_LOGGING)

default_formatter = logging.Formatter('%(levelname)s-[%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s')

file_handler = logging.handlers.RotatingFileHandler(config.LOG_FILE, maxBytes=10485760, backupCount=3000, encoding='utf-8')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler.setFormatter(default_formatter)
console_handler.setFormatter(default_formatter)

logging.root.setLevel(logging.INFO)
logging.root.addHandler(file_handler)
logging.root.addHandler(console_handler)

logging.getLogger("requests").setLevel(logging.INFO)
logging.getLogger('tweepy.binder').setLevel(logging.INFO)
 
# try:
#   ora_conn = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASSWORD, dsn=config.ORACLE_DSN)
# except cx_Oracle.DatabaseError as exception:
#   logger.INFO ('Failed to connect to %s\n', config.ORACLE_DSN)
#   logger.INFO(exception)
#   raise

