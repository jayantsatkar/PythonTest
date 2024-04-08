import logging

class LogError:
    def __init__(self):
        print('In Constructor of error logger')

    @staticmethod
    def LogError():
        LOG_FORMAT = '%(levelname)s %(asctime)s -- %(message)s'
        Date_Format = '%y-%m-%d %H:%M:%S'
        logging.basicConfig(filename='logs.log',format=LOG_FORMAT,
        level=logging.DEBUG,
        datefmt=Date_Format)

        logger = logging.getLogger(__name__)
        return logger
