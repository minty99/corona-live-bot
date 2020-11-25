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

    async def send(self, channel, msg):
        await channel.send(msg)

    async def test_send(self, channel, msg):
        await self.test_channel.send(msg)