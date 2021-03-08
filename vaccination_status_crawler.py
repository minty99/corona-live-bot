"""Vaccination status crawler"""
import asyncio
import traceback
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver

from worker import Worker

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")
driver = webdriver.Chrome("./chromedriver", chrome_options=options)


class VaccinationStatusCrawler:
    """Vaccination status crawler task"""

    def __init__(self, worker: Worker):
        self.worker = worker
        self.latest = 0

    async def _get_current(self):
        driver.get("http://ncv.kdca.go.kr/content/vaccination.html?menu_cd=0201")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        text = (
            [item.text for item in soup.select("#content > div > div:nth-child(2) > table > tbody")][0]
            .strip()
            .split("\n")
        )
        numbers = []
        for word in text:
            comma_removed = word.replace(",", "")
            try:
                num = int(comma_removed)
                numbers.append(num)
            except ValueError:
                pass
        # (Cumulative total, Today) for 1st dose
        return (numbers[0], numbers[2])

    async def run(self):
        """Task runner"""
        while True:
            today = datetime.today()
            yesterday = (today - timedelta(days=1)).strftime("%Y.%m.%d")
            try:
                total, today = await self._get_current()
                if total > self.latest:
                    await self.worker.delete_latest()
                    await self.worker.send(msg=f"백신 접종 현황: *{total:,}* (+{today:,})")
                    self.latest = total
            except Exception:  # pylint: disable=broad-except
                err = traceback.format_exc()
                print(err)
                await self.worker.test_send(msg=f"{yesterday} vaccination_status_crawler error!")
                await self.worker.test_send(msg=f"{err}")

            next_hour = datetime.today() + timedelta(hours=1)
            next_hour = next_hour.replace(minute=0, second=0, microsecond=0)
            sleep_sec = (next_hour - datetime.today()).total_seconds() + 1
            print(f"[VaccinationStatusCrawler] Bot will sleep for {sleep_sec:.3f} seconds.")
            await asyncio.sleep(sleep_sec)
