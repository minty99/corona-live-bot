import asyncio
from datetime import datetime, timedelta
from worker import Worker
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import traceback

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")
driver = webdriver.Chrome("./chromedriver", chrome_options=options)


class KdcaCrawler:
    def __init__(self, worker: Worker):
        self.worker = worker
        self.latest = 0

    async def _get_current(self, month, day):
        while datetime.today().hour < 11:
            driver.get("http://www.kdca.go.kr/board/board.es?mid=a20501000000&bid=0015")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            items = [
                item.text for item in soup.select(f"#listView > ul > li.title.title2 > a > span")
            ]
            answer_idx = -1
            for idx, item in enumerate(items):
                if "0시" in item and f"{month}월" in item and f"{day}일" in item:
                    answer_idx = idx * 2 + 1
                    break
            if answer_idx == -1:
                await asyncio.sleep(30)
                continue
            target_page = driver.find_element_by_css_selector(
                f"#listView > ul:nth-child({answer_idx}) > li.title.title2 > a"
            )
            target_page.click()
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            items = [
                item.text
                for item in soup.select(
                    "#content_detail > div.tstyle_view.bd2 > div.tb_contents > p"
                )
            ]
            regex = ".*국내.*\\s([0-9,]+)명.*해외.*\\s([0-9,]+)명.*누적.*\\s([0-9,]+)명.*해외.*\\s([0-9,]+)명.*"
            p = re.compile(regex)
            for item in items:
                m = p.findall(item)
                if len(m) == 1:
                    # matched!
                    new_domestic, new_foreign, cum_total, cum_foreign = [
                        int(x.replace(",", "")) for x in m[0]
                    ]
                    break
            else:
                await asyncio.sleep(30)
                continue
            return new_domestic, new_foreign, cum_total, cum_foreign
        raise "[KdcaCrawler] Failed to fetch today's official announcement."

    async def run(self):
        if datetime.today().hour < 9:
            today_9am = datetime.today()
            today_9am = today_9am.replace(hour=9, minute=0, second=0, microsecond=0)
            sleep_sec = (today_9am - datetime.today()).total_seconds() + 1
            print(f"[KdcaCrawler] Bot will sleep for {sleep_sec:.3f} seconds.")
            await asyncio.sleep(sleep_sec)

        while True:
            today = datetime.today()
            yesterday = (today - timedelta(days=1)).strftime("%Y.%m.%d")
            success = False
            try:
                new_domestic, new_foreign, cum_total, cum_foreign = await self._get_current(
                    today.month, today.day
                )
                new_total = new_domestic + new_foreign
                print(
                    f"{yesterday} OFFICIAL: {new_total} (domestic {new_domestic}, foreign {new_foreign}, cumulative total {cum_total}, cumulative foreign {cum_foreign})"
                )
                await self.worker.send(
                    msg=f"[Yesterday] OFFICIAL\n신규 확진자 수: *{new_total}* ({new_domestic} + {new_foreign})\n누적 확진자 수: {cum_total} ({cum_total - cum_foreign} + {cum_foreign})"
                )
                success = True
            except Exception:
                err = traceback.format_exc()
                print(err)
                await self.worker.test_send(msg=f"{yesterday} kdca_crawler error!")
                await self.worker.test_send(msg=f"{err}")

            if success:
                next_day = datetime.today() + timedelta(days=1)
                next_day = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
                sleep_sec = (next_day - datetime.today()).total_seconds() + 1
                print(f"[KdcaCrawler] Bot will sleep for {sleep_sec:.3f} seconds.")
                await asyncio.sleep(sleep_sec)