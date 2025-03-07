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
        self.resolution = Resolution(height, width)
        self.fps = config['fps']
        self.assets_dir = config['assets_dir']

        self.twitch = TwitchConfig(config['twitch'])

class Resolution():
    def __init__(self, h, w):
        self.h = h
        self.w = w

class TwitchConfig():
    def __init__(self, config):
        self.channel_names = config['channel_names']
        self.app_id = config['app_id']
        self.app_secret = config['app_secret']
        self.add_user_on_msg = config['add_user_on_msg']
        self.commands = TwitchCommands(config['commands'])
    
class TwitchCommands():
    def __init__(self, commands):
        self.start = commands['start']
        self.stop = commands['stop']
        self.add_user = commands['add_user']
        self.speed_up = commands['speed_up']
        self.slow_down = commands['slow_down']


