from kdca_crawler import KdcaCrawler
import discord
from worker import Worker
from corona_live_crawler import CoronaLiveCrawler

client = discord.Client()
first_run = True


@client.event
async def on_ready():
    global first_run
    print(f"We have logged in as {client.user}")
    if first_run:
        first_run = False
        corona_live_crawler = CoronaLiveCrawler(Worker(client))
        client.loop.create_task(corona_live_crawler.run())
        kdca_crawler = KdcaCrawler(Worker(client))
        client.loop.create_task(kdca_crawler.run())


with open("token.txt", "r") as f:
    token = f.readline()

client.run(token)
