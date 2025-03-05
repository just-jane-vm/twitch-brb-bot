import pygame
from logo_sprite import DVD
from chatter_sprite import Chatter
import re
import os
from logger import get_logger

class Game():
    def __init__(self, config, kill_signal, event_ch):
        self.logger = get_logger('game_instance')
        self.event_ch = event_ch
        self.kill_ch = kill_signal
        self.cmd_pattern = re.compile(r"^cmd=(?P<cmd>\S*)\s?(?P<args>.*)")
        self.config = config

        pygame.init()
        path = os.path.join(config.assets_dir, 'Consolas.ttf')
        self.font = pygame.font.Font(path, 20)
        self.sprites = pygame.sprite.Group()
        self.chatters = pygame.sprite.Group()

        self.screen = pygame.display.set_mode(
            (config.resolution.w, config.resolution.h),
            pygame.NOFRAME)
    
        pygame.display.set_caption("just__jane")
        assets_dir = os.fsencode(config.assets_dir)
    
        self.splat = []
        self.bonk = []
        self.cheer = None
        for file in os.listdir(assets_dir):
            filename = os.fsdecode(file)

            if filename.startswith("splat"):
                self.splat.append(pygame.mixer.Sound(os.path.join(config.assets_dir, filename)))
            elif filename.startswith("bonk"):
                self.bonk.append(pygame.mixer.Sound(os.path.join(config.assets_dir, filename)))
            elif filename.startswith("cheer"):
                self.cheer = pygame.mixer.Sound(os.path.join(config.assets_dir, filename))
                continue

        self.player = DVD(self.screen, config, self.bonk, self.cheer, (self.sprites))

        self.fps = config.fps
        self.clock = pygame.time.Clock()
        self.running = True

    def _make_chatter(self, name, color):
        sound = self.splat.pop(0)
        self.splat.append(sound)
        Chatter(self.screen, name, color, sound, self.font, (self.sprites, self.chatters))

    def _step(self):
        while self.event_ch.poll():
            command = self.event_ch.recv()
            self.logger.trace(f'Received command: {command}')

            cmd, args = self._parse_cmd(command)
            if not cmd:
                return

            if cmd == 'speed_up':
                self.player.speed_up()
            elif cmd == 'slow_down':
                self.player.slow_down()
            elif cmd == 'add':
                if not args or len(args) != 2:
                    return

                name, color = args[0], args[1]
                self._make_chatter(name, color)
            elif cmd == 'frame':
                if not args:
                    return

                if args[0] == 'off':
                    self.screen = pygame.display.set_mode(
                        (self.config.resolution.w, self.config.resolution.h),
                        pygame.NOFRAME)
                elif args[0] == 'on':
                    self.screen = pygame.display.set_mode(
                        (self.config.resolution.w, self.config.resolution.h))
                else:
                    self.logger.error(f'Invalid argument to frame command: {args}'
                                      + 'expected [on] or [off].')

        for chatter in self.chatters:
            if self.player.rect.colliderect(chatter.rect):
                chatter.kill()
                break

        self.screen.fill((0, 0, 0))
        self.sprites.update()
        self.sprites.draw(self.screen)
        pygame.display.update()

    def _parse_cmd(self, command):
        match = self.cmd_pattern.match(command)
        if not match or 'cmd' not in match.groupdict():
            self.logger.error(f'received malformed command: {match}')
            return None, None

        cmd = match.group('cmd')
        if 'args' not in match.groupdict():
            return cmd, None

        args = match.group('args').split(',')
        return cmd, args

    def run(self):
        self.logger.debug("Game loop started")
        while self.running is True:
            self.clock.tick(self.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.kill_ch.poll():
                self.kill_ch.recv()
                self.kill_ch.close()
                self.kill_ch = None
                self.running = False

            self._step()

        pygame.quit()
