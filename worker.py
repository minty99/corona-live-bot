from discord import Client, Guild, TextChannel, Message


class Worker:
    def __init__(self, client: Client, debug: bool = False):
        self.debug = debug
        for guild in client.guilds:
            if guild.name == "minty-botworld":
                self.minty_botworld: Guild = guild
            if guild.name == "설컴리창":
                self.snucse: Guild = guild

        for channel in self.snucse.channels:
            if channel.name == "maple":
                self.maple_channel: TextChannel = channel

        self.test_channel: TextChannel = self.minty_botworld.channels[2]
        self.latest_message: Message = None

    async def send(self, msg, channel=None):
        if channel is None:
            channel = self.maple_channel
        if self.debug:
            channel = self.test_channel
        self.latest_message = await channel.send(msg)

    async def test_send(self, msg):
        await self.test_channel.send(msg)

    async def delete_latest(self):
        if self.latest_message is not None:
            try:
                await self.latest_message.delete()
            except Exception:
                self.latest_message = None
