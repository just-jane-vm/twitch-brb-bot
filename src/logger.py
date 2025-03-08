import logging
from datetime import datetime
import os

if not os.path.exists('../logs'):
    os.makedirs('../logs')

logging.basicConfig(
        level=logging.INFO, 
        filename=f'../logs/brbbot-{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', 
        filemode='w',
        format='%(asctime)-12s %(name)s %(levelname)s %(message)s')

__console = logging.StreamHandler()
__console.setLevel(logging.DEBUG)
__console.setFormatter(logging.Formatter('%(name)s %(levelname)s %(message)s'))
logging.getLogger().addHandler(__console)

# the twitchAPI logs are kind of noisy to be on the screen all the time.
logging.getLogger("twitchAPI.chat").setLevel(logging.ERROR)

def get_logger(scope: str):
    return logging.getLogger(scope)
