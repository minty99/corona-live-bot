"""Main bot script"""
from argparse import ArgumentParser

import discord

from corona_live_crawler import CoronaLiveCrawler
from kdca_crawler import KdcaCrawler
from vaccination_status_crawler import VaccinationStatusCrawler
from worker import Worker

client = discord.Client()
FIRST_RUN = True


@client.event
async def on_ready():
    """Discord bot client ready handler"""
    global FIRST_RUN  # pylint: disable=global-statement
    print(f"We have logged in as {client.user}")
    if FIRST_RUN:
        FIRST_RUN = False
        corona_live_crawler = CoronaLiveCrawler(Worker(client, debug=args.debug))
        client.loop.create_task(corona_live_crawler.run())
        kdca_crawler = KdcaCrawler(Worker(client, debug=args.debug))
        client.loop.create_task(kdca_crawler.run())
        vaccine_status_crawler = VaccinationStatusCrawler(Worker(client, debug=args.debug))
        client.loop.create_task(vaccine_status_crawler.run())


parser = ArgumentParser(description="Corona live bot.")
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

with open("token.txt", "r") as f:
    token = f.readline()

client.run(token)
