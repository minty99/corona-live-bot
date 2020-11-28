import discord
from worker import Worker
from crawler import Crawler

client = discord.Client()
worker = None
crawler = None


@client.event
async def on_ready():
    global worker, crawler
    print(f"We have logged in as {client.user}")
    if worker is None:
        worker = Worker(client)
        crawler = Crawler(worker)
        client.loop.create_task(crawler.run())


with open("token.txt", "r") as f:
    token = f.readline()

client.run(token)
