import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%s',
                    filename='./brbbot.log',
                    filemode='w')

__console = logging.StreamHandler()
__console.setLevel(logging.INFO)
__console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
logging.getLogger().addHandler(__console)

# the twitchAPI logs are kind of noisy to be on the screen all the time.
logging.getLogger("twitchAPI.chat").setLevel(logging.ERROR)

def get_logger(scope: str):
    return logging.getLogger(scope)
