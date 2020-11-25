class Worker:
    def __init__(self, client):
        for guild in client.guilds:
            if guild.name == "minty-botworld":
                self.minty_botworld = guild
            if guild.name == "설컴리창":
                self.snucse = guild

        for channel in self.snucse.channels:
            if channel.name == "maple":
                self.maple_channel = channel

        self.test_channel = self.minty_botworld.channels[2]

    async def send(self, msg, channel=None):
        if channel is None:
            channel = self.maple_channel
        await channel.send(msg)

    async def test_send(self, msg):
        await self.test_channel.send(msg)