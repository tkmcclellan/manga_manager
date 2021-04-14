import itertools
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from PIL import Image

from manga_manager.util import chapter_filename


class Provider:
    """Interface and superclass for an online manga provider"""

    name = "Provider"

    def _animate(self, event, chapter_names, dir, count):
        """Animation thread function for the downloading animation.

        Args:
            event (threading.Event): Event for stopping this thread.
            downloaded (func): Function that returns the number of downloaded manga.
            count (int): The number of manga to be downloaded
        """

        for c in itertools.cycle(["|", "/", "-", "\\"]):
            if event.is_set():
                break
            try:
                sys.stdout.write(
                    f"\rdownloading - {len([name for name in chapter_names if name in os.listdir(dir)])}/{count} - {c}"
                )
            except Exception:
                sys.stdout.write(f"\rdownloading - {c}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\rDone!                              \n")

    def downloading_animation(self, chapter_names, dir, count):
        """Starts a downloading animation

        Args:
            chapter_names (List(str)): List of chapter filenames
            dir (pathlib.Path): Path to download directory
            count (int): The number of manga to be downloaded

        Returns:
            t (threading.Thread): Animation thread.
            e (threading.Event): Event that stops the thread.
        """

        e = threading.Event()
        e.clear()
        t = threading.Thread(target=self._animate, args=(e, chapter_names, dir, count))
        t.start()
        return t, e

    def _download_image(self, identifier, link, images_list):
        """Thread function for downloading an image

        Args:
            identifier (int): identifier for downloaded image.
            link (str): link to image
            images_list (List(str)): list of downloaded images
        """
        im = Image.open(requests.get(link, stream=True).raw)
        if im.mode == "RGBA":
            im = im.convert("RGB")
        images_list.append([identifier, im])

    def manga2pdf(self, image_links, dirname, chapter_name, paths=None):
        """Turns image links into a PDF

        Args:
            image_links (List(str)): list of links to images in a chapter.
            dirname (str): name of directory to store manga PDF in.
            chapter_name (str): name of manga chapter.
            paths (Dict): Optional; dictionary of chapter paths (used in multithreaded downloading)

        Returns:
            path (str): path to manga PDF.
        """

        path = Path(__file__).parent.parent
        if "manga" not in os.listdir(path):
            os.mkdir(path / "manga")
        path = path / "manga"
        if dirname not in os.listdir(path):
            os.mkdir(path / dirname)
        path = path / dirname / chapter_filename(chapter_name)

        if not os.path.exists(path):
            images = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                for i, link in enumerate(image_links):
                    executor.submit(self._download_image, i, link, images)

            images.sort(key=lambda x: x[0])
            images = [image[1] for image in images]
            images[0].save(path, save_all=True, quality=100, append_images=images[1:])
            if paths != None:
                paths[chapter_name] = str(path)
        return path

    def download(self, manga_name, chapters, verbose=True):
        """Downloads a manga.

        This function should download the chapters from the provider's site
        and save them under "manga/{manga_name}/{chapter_name}". It is recommended
        to use multithreading for downloading the chapters (but don't use more than
        20 threads for this). To download and convert panels into a PDF,
        use the function manga2pdf. This function should return a dictionary of paths
        in the form {chapter_name: chapter_path}.

        Args:
            manga_name (str): Title of manga to be downloaded.
            chapters (List(Dict)): List of chapter dicts in the form
                {"name": name, "link": link, "path": path, "read": read}.
            verbose (bool): Optional; Determines if the download should be
                loud. Default is True.

        Returns:
            paths (Dict): Dictionary of downloaded chapter paths in the form
                {chapter_name: chapter_path}.
        """

    def search(self, search_query, page=1):
        """Searches the provider's site for manga.

        This function should search the provider's site for manga and return
        a list of results in the form {"title": title, "link": link, "authors": authors,
        "updates": last updated}.

        Args:
            search_query (str): Search query.
            page (int): Optional; Results page to return. Default is 1.

        Returns:
            results (List(Dict)): Search results in the form {"title": title,
                "link": link, "authors": authors, "updates": last updated}.
            pages (int): Number of pages of search results.
        """

    def chapter_list(self, manga_link):
        """Returns a list of a manga's chapters.

        Args:
            manga_link (str): Link to a manga on the provider's site.

        Returns:
            chapters (List(List)): List of chapters in the form[[chapter_name, chapter_link], ...]
        """
