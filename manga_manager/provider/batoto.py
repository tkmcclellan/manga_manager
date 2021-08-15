import re
from concurrent.futures import ThreadPoolExecutor
import traceback

import requests
from bs4 import BeautifulSoup

from manga_manager.provider.provider import Provider
from manga_manager.model import SearchResult
from manga_manager.util import chapter_filename, clean_text

class Batoto(Provider):
    name = "Batoto"

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
        # with ThreadPoolExecutor(max_workers=20) as executor:
        #     for chapter in chapters:
        #         try:
        #             response = requests.get(chapter.link)
        #             soup = BeautifulSoup(response.text, "html.parser")
        #             image_links = [
        #                 image["data-src"] for image in soup.select("img.img-loading")
        #             ]

        #             executor.submit(
        #                 self.manga2pdf,
        #                 image_links,
        #                 title,
        #                 chapter.title,
        #                 paths=paths,
        #             )
        #         except Exception:
        #             if verbose:
        #                 traceback.print_exc()
        #             pass
        # if verbose:
        #     event.set()
        #     thread.join()
        # return paths
