import asyncio
from datetime import datetime
from worker import Worker
from selenium import webdriver
from bs4 import BeautifulSoup
import time

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")
driver = webdriver.Chrome("./chromedriver", chrome_options=options)


class Crawler:
    def __init__(self, worker: Worker):
        self.worker = worker
        self.latest = self._get_current()

    def _get_current(self):
        driver.get("https://www.corona-live.com/")
        while True:
            try:
                time.sleep(10)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                new_patients = soup.select(
                    "#root > div > div.sc-AxjAm.bRuiNy.sc-AxirZ.fZVwIW.sc-AxiKw.eSbheu > div:nth-child(3) > div.sc-AxjAm.fiWmrI.sc-AxirZ.heBhHx.sc-AxiKw.eSbheu > div.sc-AxjAm.hQNuxH.sc-AxirZ.idrxEV.sc-AxiKw.eSbheu > div.sc-AxjAm.lklBhC > span"
                )
                curr = int(new_patients[0].text)
            except Exception:
                continue
            break
        return curr

    async def run(self):
        while True:
            curr = self._get_current()
            diff = curr - self.latest
            curr_time = datetime.today().strftime("%Y.%m.%d %H:%M")
            print(f"{curr_time}: {curr}")
            if self.latest < curr:
                await self.worker.test_send(msg=f"{curr_time} 확진자 수 변동: {curr} (+{diff})")
                self.latest = curr

            if self.latest > curr:
                await self.worker.test_send(msg=f"{curr_time} 확진자 수 변동: {curr}")
                self.latest = curr
            await asyncio.sleep(600)