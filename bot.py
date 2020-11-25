import discord
import schedule
from worker import Worker

client = discord.Client()


@client.event
async def on_ready():
    global worker
    print(f"We have logged in as {client.user}")
    worker = Worker(client)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!debug"):
        await worker.test_send(message.channel, "debugging here!")


with open("token.txt", "r") as f:
    token = f.readline()

client.run(token)
