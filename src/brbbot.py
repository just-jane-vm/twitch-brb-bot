from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatCommand
from config import Config
from game import Game
import asyncio
import multiprocessing

SCOPES = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

class BRBBot():
    def __init__(self):
        self.config = Config()
        self.game = None
        self.game_process = None
        self.event_ch = None
        self.kill_ch = None
        self.chat = None
        self.twitch = None

    async def start(self):
        self.twitch = await Twitch(self.config.twitch.app_id, self.config.twitch.app_secret)
        auth = UserAuthenticator(self.twitch, SCOPES)
        token, refresh_token = await auth.authenticate()
        await self.twitch.set_user_authentication(token, SCOPES, refresh_token)

        self.chat = await Chat(self.twitch)

        self.chat.register_event(ChatEvent.READY, self.on_ready)

        self.chat.register_command(self.config.twitch.start, self.on_start)
        self.chat.register_command(self.config.twitch.stop, self.on_stop)
        self.chat.register_command(self.config.twitch.add_chatter, self.on_add)
        self.chat.register_command(self.config.twitch.speed_up, self.on_speed_up)
        self.chat.register_command(self.config.twitch.slow_down, self.on_slow_down)

        self.chat.start()

        try:
            input('press ENTER to stop\n')
        finally:
            # now we can close the chat bot and the twitch api client
            if self.game_process:
                self.kill_ch.send("die")

            self.chat.stop()
            await self.twitch.close()

    def _start_game(self, ch1, ch2, config):
        print("Game process start")
        game = Game(config, ch1, ch2)
        game.run()
        print("Game process exit")

    def _stop_game(self):
        if not self.game_process:
            return

        self.kill_ch.send("die")
        self.game_process.join()
        self.game_process = None
        self.kill_ch.close()
        self.kill_ch = None

        self.event_ch.close()
        self.event_ch = None
        print("Game killed")

    async def stop(self):
        self.chat.stop()
        await self.twitch.close()

    async def on_ready(self, ready_event: EventData):
        print('BRBBot ready for work.')
        await ready_event.chat.join_room(self.config.twitch.channel_name)
        print(f'Joined channel: {self.config.twitch.channel_name} succesfully')

    async def on_add(self, cmd: ChatCommand):
        if (self.event_ch):
            self.event_ch.send(f'cmd=add {cmd.user.name},{cmd.user.color}')

    async def on_stop(self, cmd: ChatCommand):
        if cmd.user.name != self.config.twitch.channel_name:
            return

        self._stop_game()

    async def on_speed_up(self, cmd: ChatCommand):
        if (self.event_ch):
            self.event_ch.send('cmd=speed_up')
        return

    async def on_slow_down(self, cmd: ChatCommand):
        if (self.event_ch):
            self.event_ch.send('cmd=slow_down')
        return

    async def on_start(self, cmd: ChatCommand):
        if cmd.user.name != self.config.twitch.channel_name:
            return

        if not self.game_process: 
            self.kill_ch, ch1 = multiprocessing.Pipe()
            self.event_ch, ch2 = multiprocessing.Pipe()
            self.game_process = multiprocessing.Process(target=self._start_game, args=(ch1, ch2,self.config))
            print("Starting game...")
            self.game_process.start()
            print("Game started...")

async def main():
    bot = BRBBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())

