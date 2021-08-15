import re
from concurrent.futures import ThreadPoolExecutor
import traceback

import asyncio
import requests
import re
from bs4 import BeautifulSoup
from pyppeteer import launch

from manga_manager.provider.provider import Provider
from manga_manager.model import SearchResult
from manga_manager.util import chapter_filename, clean_text

class Batoto(Provider):
    name = "Batoto"

    async def _get_link_html(self, link):
        browser = await launch()
        page = await browser.newPage()
        await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1')
        await page.setExtraHTTPHeaders({ 'referrer': link })
        await page.goto(link)
        result = await page.content()
        await browser.close()
        return result


    def download(self, title, chapters, dl_dir, verbose=True):
        thread, event = None, None
        if verbose:
            print("\n" + title.upper())
            print(len(title) * "-")
            thread, event = self.downloading_animation(
                chapter_names=[chapter_filename(chapter.title) for chapter in chapters],
                dir=dl_dir,
                count=len(chapters),
            )

        paths = {}
        with ThreadPoolExecutor(max_workers=20) as executor:
            for chapter in chapters:
                try:
                    response = asyncio.get_event_loop().run_until_complete(self._get_link_html(chapter.link))
                    image_links = re.search(r'const\simages\s=\s\[(.*)\];', response).group(1).replace("\"/", "https://xcdn-227.bato.to/").replace("\"", "").split(",")
                    executor.submit(
                        self.manga2pdf,
                        image_links,
                        title,
                        chapter.title,
                        paths=paths,
                    )
                except Exception:
                    if verbose:
                        traceback.print_exc()
                    pass
        if verbose:
            event.set()
            thread.join()
        return paths


    def search(self, word=1):
        repsonse = requests.get(
            requests.utils.requote_url(
                f"https://bato.to/search?word={word}"
            )
        )
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select("div.series-list > div.item")
        titles = [result.select_one("div.item-text > a.item-title")]
        info = [result.select("span") for result in results]
        authors = [clean_text(i[0].text) for i in info]
        updates = [clean_text(i[1].text) for i in info]
        pages = int(
            re.sub(
                "[^0-9]",
                "",
                soup.select_one(
                    "body > "
                )
            )
        )

    def chapter_list(self, manga_link):
        response = asyncio.get_event_loop().run_until_complete(self._get_link_html(manga_link))
        soup = BeautifulSoup(response, "html.parser")

        return [
            [clean_text(chapter.text), f"https://bato.to{chapter['href']}"]
            for chapter in soup.select("div.episode-list > div.main > div > a")
        ][::-1]
