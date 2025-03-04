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

        self.twitch = TwitchConfig(config['twitch'])

class TwitchConfig():
    def __init__(self, config):
        self.channel_names = config['channel_names']
        self.app_id = config['app_id']
        self.app_secret = config['app_secret']
        self.add_user_on_msg = config['add_user_on_msg']

        TwitchCommands = namedtuple(
            'TwitchCommands', 
            ('start', 'stop', 'add_user', 'speed_up', 'slow_down'))

        cmd = config['commands']
        self.commands = TwitchCommands(
            cmd['start'],
            cmd['stop'],
            cmd['add_user'],
            cmd['speed_up'],
            cmd['slow_down'])

                


