import re
from concurrent.futures import ThreadPoolExecutor
import traceback

import requests
from bs4 import BeautifulSoup

from manga_manager.provider.provider import Provider
from manga_manager.model import SearchResult
from manga_manager.util import chapter_filename, clean_text


class Mangakakalot(Provider):
    name = "Mangakakalot"

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
                    response = requests.get(chapter.link)
                    soup = BeautifulSoup(response.text, "html.parser")
                    image_links = [
                        image["data-src"] for image in soup.select("img.img-loading")
                    ]

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

    def search(self, search_query, page=1):
        response = requests.get(
            requests.utils.requote_uri(
                f"https://ww.mangakakalot.tv/search/{search_query}?page={page}"
            )
        )
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select("div.story_item")
        titles = [result.select_one("h3.story_name > a") for result in results]
        info = [result.select("span") for result in results]
        authors = [clean_text(i[0].text) for i in info]
        updates = [clean_text(i[1].text) for i in info]
        pages = int(
            re.sub(
                "[^0-9]",
                "",
                soup.select_one(
                    "body > div.container > div.main-wrapper > div.leftCol > div.panel_page_number > div.group_page > a.page_blue.page_last"
                ).text,
            )
        )

        return (
            [
                SearchResult(
                    title=clean_text(titles[i].text),
                    link=f"https://ww.mangakakalot.tv{titles[i]['href']}",
                    authors=authors[i],
                    updates=updates[i],
                )
                for i in range(len(titles))
            ],
            pages,
        )

    def chapter_list(self, manga_link):
        response = requests.get(manga_link)
        soup = BeautifulSoup(response.text, "html.parser")

        return [
            [clean_text(chapter.text), f"https://ww.mangakakalot.tv{chapter['href']}"]
            for chapter in soup.select("div.row > span > a")
        ][::-1]
