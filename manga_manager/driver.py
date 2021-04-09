import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from PIL import Image

import itertools
import threading
import time
import sys


def animate(event, dir, count):
    for c in itertools.cycle(["|", "/", "-", "\\"]):
        if event.is_set():
            break
        try:
            sys.stdout.write(f"\rdownloading - {len(os.listdir(dir))}/{count} - {c}")
        except Exception:
            sys.stdout.write(f"\rdownloading - {c}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\rDone!                              \n")


def downloading_animation(dir, count):
    e = threading.Event()
    e.clear()
    t = threading.Thread(target=animate, args=(e, dir, count))
    t.start()
    return t, e


def clean_text(chapter_name):
    return re.sub(" +", " ", re.sub("\n", "", chapter_name)).strip()


def download_image(identifier, link, images_list):
    im = Image.open(requests.get(link, stream=True).raw)
    if im.mode == "RGBA":
        im = im.convert("RGB")
    images_list.append([identifier, im])


def manga2pdf(image_links, dirname, chapter_name, paths=None):
    path = Path(__file__).parent / "manga"
    if dirname not in os.listdir(path):
        os.mkdir(path / dirname)
    path = (
        path
        / dirname
        / (re.sub(" ", "-", re.sub("[^a-zA-Z0-9 ]", "", chapter_name))[:240] + ".pdf")
    )

    images = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i, link in enumerate(image_links):
            executor.submit(download_image, i, link, images)

    images.sort(key=lambda x: x[0])
    images = [image[1] for image in images]
    images[0].save(path, save_all=True, quality=100, append_images=images[1:])
    if paths != None:
        paths[chapter_name] = str(path)


class Mangakakalot:
    name = "Mangakakalot"

    def download(self, manga_name, chapters, verbose=True):
        thread, event = None, None
        if verbose:
            print("\n" + manga_name.upper())
            print(len(manga_name) * "-")
            thread, event = downloading_animation(
                Path(__file__).parent / "manga" / manga_name, len(chapters)
            )

        paths = {}
        with ThreadPoolExecutor(max_workers=20) as executor:
            for chapter in chapters:
                try:
                    response = requests.get(chapter["link"])
                    soup = BeautifulSoup(response.text, "html.parser")
                    image_links = [
                        image["data-src"] for image in soup.select("img.img-loading")
                    ]

                    executor.submit(
                        manga2pdf, image_links, manga_name, chapter["name"], paths=paths
                    )
                except Exception as e:
                    if verbose:
                        print(e)
                    pass
        if verbose:
            event.set()
            thread.join()
        return paths

    def search(self, search_query):
        response = requests.get(
            requests.utils.requote_uri(
                f"https://ww.mangakakalot.tv/search/{search_query}"
            )
        )
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select("div.story_item")
        titles = [result.select_one("h3.story_name > a") for result in results]
        info = [result.select("span") for result in results]
        authors = [clean_text(i[0].text) for i in info]
        updates = [clean_text(i[1].text) for i in info]
        results = [
            {
                "title": clean_text(titles[i].text),
                "link": titles[i]["href"],
                "authors": authors[i],
                "updates": updates[i],
            }
            for i in range(len(titles))
        ]
        for i, result in enumerate(results):
            print(f"{i}: {result['title']} - {result['authors']} - {result['updates']}")
        selection = input("Selection (q-Quit, n-Next, p-Previous): ").lower()

        if selection == "q":
            return None, None, None, None
        elif selection == "n":
            """go to next page of results"""
        elif selection == "p":
            """go to previous page of results"""
        else:
            try:
                i = int(selection)
                manga_url = f"https://ww.mangakakalot.tv{results[i]['link']}"
                manga_name = results[i]["title"]
                manga_authors = results[i]["authors"]
                manga_chapters = self.get_chapter_list(manga_url)
                return manga_url, manga_name, manga_authors, manga_chapters
            except Exception:
                print("Invalid input")
                return None, None, None, None

    def get_chapter_list(self, manga_link):
        response = requests.get(manga_link)
        soup = BeautifulSoup(response.text, "html.parser")

        return [
            [clean_text(chapter.text), f"https://ww.mangakakalot.tv{chapter['href']}"]
            for chapter in soup.select("div.row > span > a")
        ][::-1]

    def new_chapters(self, manga):
        chapter_list = self.get_chapter_list(manga["link"])
        chapter_names = [chapter["name"] for chapter in manga["chapters"]]
        return [
            {"name": chapter[0], "link": chapter[1], "path": "", "read": False}
            for chapter in chapter_list
            if chapter[0] not in chapter_names
        ]
