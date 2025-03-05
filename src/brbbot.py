from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatCommand, ChatMessage
from config import Config
from game import Game
import asyncio
import multiprocessing
from logger import get_logger
from functools import wraps

SCOPES = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

class BRBBot():
    def event_ch_guard(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self.event_ch:
                return await func(self, *args, **kwargs)
            else:
                self.logger.error("Event channel guard prevented access to null event channel.")
                return None
        return wrapper

    def __init__(self):
        self.config = Config()
        self.game = None
        self.game_process = None
        self.event_ch = None
        self.kill_ch = None
        self.chat = None
        self.twitch = None
        self.logger = get_logger('BRBBot')

    async def start(self):
        self.twitch = await Twitch(self.config.twitch.app_id, self.config.twitch.app_secret)
        auth = UserAuthenticator(self.twitch, SCOPES)
        token, refresh_token = await auth.authenticate()
        await self.twitch.set_user_authentication(token, SCOPES, refresh_token)

        self.chat = await Chat(self.twitch)

        self.chat.register_event(ChatEvent.READY, self.on_ready)

        if (self.config.twitch.commands.start):
            self.chat.register_command(self.config.twitch.commands.start, self.on_start)

        if (self.config.twitch.commands.stop):
            self.chat.register_command(self.config.twitch.commands.stop, self.on_stop)

        try:
            self.chat.start()
            user_input = None
            while user_input != 'exit':
                user_input = input('Enter help for commands: ').lower()
                if user_input.startswith('frame'):
                    if self.event_ch:
                        self.event_ch.send(f'cmd={user_input}')
                    continue

                if user_input == 'help':
                    print('TODO: add help message...')

        finally:
            self._stop_game()
            self.chat.stop()
            await self.twitch.close()

    def register_commands(self):
        if (self.config.twitch.commands.add_user):
            self.chat.register_command(self.config.twitch.commands.add_user, self.on_add)

        if (self.config.twitch.commands.speed_up):
            self.chat.register_command(self.config.twitch.commands.speed_up, self.on_speed_up)

        if (self.config.twitch.commands.slow_down):
            self.chat.register_command(self.config.twitch.commands.slow_down, self.on_slow_down)

        if (self.config.twitch.add_user_on_msg):
            self.chat.register_event(ChatEvent.MESSAGE, self.on_message)

    def unregister_commands(self):
        self.chat.unregister_command(self.config.twitch.commands.add_user)
        self.chat.unregister_command(self.config.twitch.commands.speed_upp)
        self.chat.unregister_command(self.config.twitch.commands.slow_down)
        self.chat.unregister_event(ChatEvent.MESSAGE)

    def _start_game(self, ch1, ch2, config):
        self.logger.debug("Game process start")
        game = Game(config, ch1, ch2)
        game.run()
        self.logger.debug("Game process exit")

    def _stop_game(self):
        if not self.game_process:
            return

        if not self.game_process.is_alive():
            self.logger.error('Game process was closed unexpectedly.')
            self.game_process = None
            self.kill_ch = None
            self.event_ch = None
            return

        self.kill_ch.send("die")
        self.game_process.join()

        self.kill_ch.close()
        self.event_ch.close()
        self.game_process = None
        self.kill_ch = None
        self.event_ch = None

        self.logger.debug("Game killed")

    async def stop(self):
        self.chat.stop()
        await self.twitch.close()

    async def on_ready(self, ready_event: EventData):
        self.logger.debug('BRBBot ready for work.')
        for channel in (self.config.twitch.channel_names):
            await ready_event.chat.join_room(channel)
            self.logger.debug(f'Joined [{channel}] succesfully.')

    @event_ch_guard
    async def on_message(self, msg: ChatMessage):
        self.event_ch.send(f'cmd=add {msg.user.display_name},{msg.user.color}')

    @event_ch_guard
    async def on_add(self, cmd: ChatCommand):
        self.event_ch.send(f'cmd=add {cmd.user.display_name},{cmd.user.color}')

    @event_ch_guard
    async def on_speed_up(self, cmd: ChatCommand):
        self.event_ch.send('cmd=speed_up')

    @event_ch_guard
    async def on_slow_down(self, cmd: ChatCommand):
        self.event_ch.send('cmd=slow_down')

    async def on_stop(self, cmd: ChatCommand):
        if cmd.user.name != self.config.twitch.channel_names:
            return

        self._stop_game()
        self.unregister_commands()

    async def on_start(self, cmd: ChatCommand):
        if cmd.user.name not in self.config.twitch.channel_names:
            return

        if not self.game_process: 
            self.kill_ch, ch1 = multiprocessing.Pipe()
            self.event_ch, ch2 = multiprocessing.Pipe()
            self.game_process = multiprocessing.Process(target=self._start_game, args=(ch1, ch2,self.config))
            self.logger.debug("Starting game...")
            self.game_process.start()
            self.logger.debug("Game started...")
            self.register_commands()
 
async def main():
    bot = BRBBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())

