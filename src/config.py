import yaml
import os

error_count = 0

def assert_condition(condition, on_fail):
    if condition:
        return

    global error_count
    error_count += 1
    print(error_count)

    print('[ERROR] ' + on_fail)

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
        self.assets = Assets(config['assets']) 
        self.twitch = TwitchConfig(config['twitch'])

    def validate(self):
        assert_condition(isinstance(self.fps, int) 
                         and  self.fps > 0 
                         and self.fps <= 120, 
                         'fps must be between 1 and 120 inclusive')

        self.resolution.validate()
        self.assets.validate()
        self.twitch.validate()

class Assets():
    def __init__(self, config):
        self.logo = config['logo_path']
        self.bonks = config['bonks']
        self.splats = config['splats']
        self.cheer = config['cheer']
        self.font = config['font']

    def validate(self):
        assert_condition(os.path.exists(self.logo), 'logo path does not exist')
        assert_condition(os.path.exists(self.bonks), 'bonk path does not exist')
        assert_condition(os.path.exists(self.splats), 'splat path does not exist')
        assert_condition(os.path.exists(self.cheer), 'cheer path does not exist')
        assert_condition(os.path.exists(self.font), 'font path does not exist')

class Resolution():
    def __init__(self, h, w):
        self.h = h
        self.w = w

    def validate(self):
        assert_condition(isinstance(self.w, int) 
                         and self.w > 0, 
                         'resolution.width must be a positive integer')

        assert_condition(isinstance(self.h, int)
                         and self.h > 0, 
                         'resolution.height must be a positive integer')
class TwitchConfig():
    def __init__(self, config):
        self.channel_names = tuple(name.lower() for name in config['channel_names'])

        self.app_id = config['app_id']
        self.app_secret = config['app_secret']

        self.add_user_on_msg = config['add_user_on_msg']
        self.commands = TwitchCommands(config['commands'])

    def validate(self):
        return
    
class TwitchCommands():
    def __init__(self, commands):
        self.start = commands['start']
        self.stop = commands['stop']
        self.add_user = commands['add_user']
        self.speed_up = commands['speed_up']
        self.slow_down = commands['slow_down']

def get_config() -> tuple[bool, Config]:
    global error_count
    error_count = 0

    config = Config()
    config.validate()

    print(error_count)
    return error_count == 0, config

if __name__ == '__main__':
    is_valid, _ = get_config()
    if not is_valid:
        print(f'Config file contains {error_count} errors')
