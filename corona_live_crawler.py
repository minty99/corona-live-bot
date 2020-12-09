import asyncio
from datetime import datetime, timedelta
from worker import Worker
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import traceback

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")
driver = webdriver.Chrome("./chromedriver", chrome_options=options)


class CoronaLiveCrawler:
    def __init__(self, worker: Worker):
        self.worker = worker
        self.latest = 0

    def _get_current(self):
        driver.get("https://www.corona-live.com/")
        time.sleep(10)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find_all(name="div", text="실시간 확진자수")
        curr = int(div[0].parent.contents[1].contents[0].contents[0].text)
        return curr

    async def run(self):
        while True:
            curr_time = datetime.today().strftime("%H:%M")
            try:
                curr = self._get_current()
                diff = curr - self.latest
                print(f"{curr_time}: {curr}")
                if self.latest < curr:
                    await self.worker.delete_latest()
                    await self.worker.send(msg=f"[Realtime] 확진자 수 변동: *{curr}* (+{diff})")
                    self.latest = curr
                if self.latest > curr:
                    await self.worker.delete_latest()
                    await self.worker.send(msg=f"[Realtime] 확진자 수 변동: {curr}")
                    self.latest = curr
            except Exception:
                err = traceback.format_exc()
                print(err)
                await self.worker.test_send(msg=f"[Realtime] {curr_time} corona-live-bot error!")
                await self.worker.test_send(msg=f"{err}")

            next_hour = datetime.today() + timedelta(hours=1)
            next_hour = next_hour.replace(minute=0, second=0, microsecond=0)
            sleep_sec = (next_hour - datetime.today()).total_seconds() + 1
            print(f"[CoronaLiveCrawler] Bot will sleep for {sleep_sec:.3f} seconds.")
            await asyncio.sleep(sleep_sec)