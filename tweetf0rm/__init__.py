import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s-[%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger('tweepy.binder').setLevel(logging.WARNING)
