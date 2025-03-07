from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatCommand, ChatMessage
from config import Config
from game import Game
import asyncio
import multiprocessing
import multiprocessing.connection
from logger import get_logger
from functools import wraps

SCOPES = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

def _start_game(event_queue):
    game = Game(event_queue)
    game.run()

class BRBBot():
    def event_ch_guard(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self.event_ch:
                return await func(self, *args, **kwargs)
            else:
                self.logger.warning("Event channel guard prevented access to null event channel.")
                return None
        return wrapper

    def __init__(self):
        self.config = Config()
        self.game = None
        self.game_process = None
        self.event_ch = None
        self.listener = None
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
        self.chat.unregister_command(self.config.twitch.commands.speed_up)
        self.chat.unregister_command(self.config.twitch.commands.slow_down)
        self.chat.unregister_event(ChatEvent.MESSAGE, self.on_message)

    def _stop_game(self):
        if not self.game_process:
            return

        try:
            self.logger.debug('Sending kill command')
            self.event_ch.send("cmd=die")
            self.event_ch.close()
            self.listener.close()
        except:
            self.logger.error("Error closing connection")
        finally:
            self.event_ch = None
            self.listener = None

        if self.game_process.is_alive():
            self.game_process.join()

        self.game_process = None
        self.logger.debug("Game killed")

    async def stop(self):
        self.chat.stop()
        await self.twitch.close()

    async def on_ready(self, ready_event: EventData):
        self.logger.debug('BRBBot ready for work.')
        for channel in (self.config.twitch.channel_names):
            await ready_event.chat.join_room(channel)
            self.logger.info(f'Joined [{channel}] succesfully.')

    @event_ch_guard
    async def on_message(self, msg: ChatMessage):
        self.event_ch.send(f'cmd=add {msg.user.display_name} {msg.user.color}')

    @event_ch_guard
    async def on_add(self, cmd: ChatCommand):
        self.event_ch.send(f'cmd=add {cmd.user.display_name} {cmd.user.color}')

    @event_ch_guard
    async def on_speed_up(self, cmd: ChatCommand):
        self.event_ch.send('cmd=speed_up')

    @event_ch_guard
    async def on_slow_down(self, cmd: ChatCommand):
        self.event_ch.send('cmd=slow_down')

    async def on_stop(self, cmd: ChatCommand):
        if cmd.user.name not in self.config.twitch.channel_names:
            return

        self._stop_game()
        self.unregister_commands()

    async def on_start(self, cmd: ChatCommand):
        if cmd.user.name not in self.config.twitch.channel_names:
            return

        if not self.game_process: 
            addr = ('localhost', 6063)
            self.listener = multiprocessing.connection.Listener(addr)
            self.game_process = multiprocessing.Process(target=_start_game, args=(addr,))
            self.logger.debug("Starting game...")
            self.game_process.start()
            self.event_ch = self.listener.accept()
            self.logger.debug("Game started...")
            self.register_commands()
 
async def main():
    bot = BRBBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())
