import yaml
from collections import namedtuple

class Config():
    def __init__(self):
        with open('../config.yaml', 'r') as file:
            try:
                config = yaml.safe_load(file)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file: {e}")
                exit()

        height, width = config['resolution']['height'], config['resolution']['width']
        self.resolution = namedtuple('Resolution', ('h', 'w'))(height, width)
        self.fps = config['fps']
        self.assets_dir = config['assets_dir']

        twitch_fields = ['channel_name',
                          'start',
                          'stop',
                          'add_chatter',
                          'speed_up',
                          'slow_down',
                          'app_id',
                          'app_secret']
                        
        TwitchConfig = namedtuple('TwitchConfig', twitch_fields)
        t = config['twitch']
        self.twitch = TwitchConfig(
            t['channel_name'],
            t['start'],
            t['stop'],
            t['add_chatter'],
            t['speed_up'],
            t['slow_down'],
            t['app_id'],
            t['app_secret'])
                


