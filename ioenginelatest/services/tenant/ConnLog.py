from logging.handlers import TimedRotatingFileHandler
import logging

def create_log_file(filename="/var/log/autointelli/server.log"):
  try:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter( "%(asctime)s | %(funcName)s | %(levelname)s | %(message)s ")
    handler = TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=10)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return(logger)
  except Exception as e:
    return(False)

def logit(logobj, logtype, message):
  try:
    if logtype == "info":
      logobj.info(message)
    if logtype == "warn":
      logobj.warn(message)
    if logtype == "error":
      logobj.error(message)
  except Exception as e:
    return(False)

