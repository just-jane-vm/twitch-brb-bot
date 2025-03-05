import logging

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%s',
                    filename='./brbbot.log',
                    filemode='w')

__console = logging.StreamHandler()
__console.setLevel(logging.DEBUG)

__console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
logging.getLogger().addHandler(__console)

def get_logger(scope: str):
    return logging.getLogger(scope)
