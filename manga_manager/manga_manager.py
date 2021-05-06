"""
TODO:
- Add support for MangaReader
- Make multithreaded downloading optional
- Add testing
- Find a better way to handle provider string -> class
- Allow referencing manga by index as well as title
- Add __getitem__ on MM as shortcut for .manga
- Add documentation for updated model classes
"""


import warnings

warnings.filterwarnings("ignore")

import itertools
import re
import json
import os
import shutil
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import traceback

from fuzzywuzzy import fuzz

from manga_manager.provider import find_provider
from manga_manager.model import Manga, Chapter

DYNAMIC_DL_SIZE = 2


class MangaManager:
    """Manages manga"""

    def __init__(
        self,
        manga=None,
        manga_path=Path(__file__).parent / "manga",
        data_path=Path(__file__).parent / "config.json",
        save=True
    ):
        self.data_path = data_path
        self.manga_path = manga_path
        self.manga = manga if manga else self.load()
        self.save_data = save

    def load(self):
        """Loads data from file"""

        data = None
        if not os.path.exists(self.data_path):
            open(self.data_path, "w").close()
            return {}
        else:
            with open(self.data_path, "r") as file:
                data = json.loads(file.read())
                data["manga"] = {
                    title: Manga._parse(manga) for title, manga in data["manga"].items()
                }
            return data["manga"]

    def save(self):
        """Saves data to file"""

        if self.save_data:
            try:
                raw_data = {
                    "manga": {
                        title: manga._to_dict() for title, manga in self.manga.items()
                    }
                }
                data = json.dumps(raw_data)
                with open(self.data_path, "w") as file:
                    file.write(data)
            except Exception:
                traceback.print_exc()

    def _update_chapter_paths(self, title, paths):
        """Updates paths in a manga's chapters"""
        for chapter in self.manga[title].chapters:
            if chapter.title in paths:
                chapter.path = paths[chapter.title]

    def add_manga(self, title, provider="Mangakakalot", download_mode="dynamic"):
        """Adds a manga to track

        Args:
            title (str): Manga title.
            provider (Provider): Optional; Instance of a provider class. Default is
                Mangakakalot.
            download_mode (str): Optional; Method for downloading manga. "dynamic" will
                download the first couple chapters of series and the system will download and
                delete chapters as the user reads. "all" will download all chapters of
                the manga at once. "none" will not download any manga at this time. Default
                is "dynamic".
        """

        provider = find_provider(provider)()
        page = 1
        manga_url, manga_title, manga_authors, manga_chapters = None, None, None, None
        while True:
            results, pages = provider.search(title)
            for i, result in enumerate(results):
                print(f"{i}: {result.format()}")
            selection = input("Selection (q-Quit, n-Next, p-Previous): ").lower()

            if selection == "q":
                return
            elif selection == "n":
                if page < pages:
                    page += 1
                    print()  # separating line
                    continue
            elif selection == "p":
                if page > 1:
                    page -= 1
                    continue
            else:
                try:
                    i = int(selection)
                    manga_url = results[i].link
                    manga_title = results[i].title
                    manga_authors = results[i].authors
                    manga_chapters = provider.chapter_list(manga_url)
                    break
                except Exception:
                    traceback.print_exc()
                    return

        if manga_title not in self.manga:
            self.manga[manga_title] = Manga(
                title=manga_title,
                link=manga_url,
                authors=manga_authors,
                download_mode=download_mode,
                provider=provider.name,
                current_chapter=0,
                chapters=[
                    Chapter(title=chapter[0], link=chapter[1])
                    for chapter in manga_chapters
                ],
            )
        if download_mode in ["dynamic", "all"]:
            chapter_limit = DYNAMIC_DL_SIZE if download_mode == "dynamic" else -1
            paths = provider.download(
                title=manga_title,
                chapters=self.manga[manga_title].chapters[:chapter_limit],
                dl_dir=self.manga_path / manga_title,
            )
            self._update_chapter_paths(manga_title, paths)

    def remove_manga(self, title, delete_files=True):
        """Removes a manga from manga_manager.

        Args:
            title (str): Title of manga to be remoevd.
            delete_files (bool): Optional; Option to delete locally stored manga.
                Default is false.
        """

        title = self._fuzzy_find_title(title)
        confirmation = input(
            f"Are you sure you want to delete {title}? ([y]/n):"
        ).lower()
        if confirmation == "n":
            return
        if delete_files:
            shutil.rmtree(self.manga_path / title)
        self.manga.pop(title)
        print(f"{title} was successfully deleted\n")

    def edit_manga(self, title):
        """Display's a manga's config and allows the user to edit values

        Args:
            title (str): Title of the manga to be edited.
        """

        title = self._fuzzy_find_title(title)
        try:
            while True:
                print(title.upper())
                print('-' * len(title))
                for key in [
                    "title",
                    "link",
                    "authors",
                    "download_mode",
                    "provider",
                    "current_chapter",
                ]:
                    print(f"{key} = {getattr(self.manga[title], key)}")
                key = input("\nWhat config do you want to change? (q - Quit): ").lower()
                if key == "q":
                    break
                elif not hasattr(self.manga[title], key) or key == "chapters":
                    print("Invalid key")
                else:
                    value = input(f"What should `{key}` be? ").lower()
                    if value.lower() in ["true", "false"]:
                        value = eval(value.title())
                    elif re.sub("[\d]", "", value) == "":
                        value = int(value)
                    setattr(self.manga[title], key, value)
        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            return

    def read_manga(self, title, chapter=None):
        """Opens a manga chapter for reading.
        This function opens the pdf of a manga chapter in the user's browser.
        Whenever a user moves to the next chapter, the current chapter is marked
        as read. If any chapter is not locally downloaded, the system will
        automatically download it (while the user is reading the current chapter
        if possible). If the manga's download mode is "dynamic", the system
        will also delete previous chapters as the user reads.

        Args:
            title (str): Title of the manga that will be read.
            chapter (int): Optional; Chapter to start reading. Default value
                is the manga's last saved current chapter.
        """

        title = self._fuzzy_find_title(title)
        provider = find_provider(self.manga[title].provider)()
        if not chapter:
            chapter = self.manga[title].current_chapter
        else:
            self.manga[title].current_chapter = chapter

        try:
            while True:
                offset = DYNAMIC_DL_SIZE
                current_chapter = self.manga[title].chapters[chapter]
                print(f"Name: {title}")
                print(f"Chapter: {current_chapter.title}\n")

                # check if current chapter is downloaded. if not, download it.
                if current_chapter.path == "":
                    print("Downloading current chapter...")
                    paths = provider.download(
                        title=title,
                        chapters=[current_chapter],
                        dl_dir=self.manga_path / title,
                        verbose=False,
                    )
                    self._update_chapter_paths(title, paths)

                # open current chapter
                webbrowser.get().open(f"file:///{current_chapter.path}")

                # delete chapters outside of offset
                if self.manga[title].download_mode == "dynamic":
                    # range for chapters outside of offset
                    pre_offset = range(max(0, chapter - offset))
                    post_offset = range(
                        min(len(self.manga[title].chapters), chapter + offset + 1),
                        len(self.manga[title].chapters),
                    )
                    offset_range = itertools.chain(pre_offset, post_offset)
                    # print(list(offset_range))
                    for c in offset_range:
                        try:
                            os.remove(self.manga[title].chapters[c].path)
                        except Exception:
                            """do nothing"""
                        finally:
                            self.manga[title].chapters[c].path = ""
                    # download chapters in offset
                    chapter_downloads = [
                        c
                        for c in self.manga[title].chapters[
                            max(0, chapter - offset) : min(
                                chapter + offset + 1, len(self.manga[title].chapters)
                            )
                        ]
                        if c.path == ""
                    ]
                    paths = provider.download(
                        title=title,
                        chapters=chapter_downloads,
                        dl_dir=self.manga_path / title,
                        verbose=False,
                    )
                    self._update_chapter_paths(title, paths)
                selection = input(
                    "\nAction? ([n - Next]/p - Previous/q - Quit): "
                ).lower()
                if selection == "q":
                    self.manga[title].current_chapter = chapter
                    break
                elif selection == "p":
                    chapter = max(chapter - 1, 0)
                else:
                    current_chapter.read = True
                    chapter = min(len(self.manga[title].chapters), chapter + 1)
        except KeyboardInterrupt:
            return

    def list_manga(self, new_chapters={}):
        """Lists the manga currently being tracked by manga_manager"""

        if len(self.manga.items()) == 0:
            return
        for i, (title, manga) in enumerate(self.manga.items()):
            chapters_read = len([chapter for chapter in manga.chapters if chapter.read])
            chapters = len(manga.chapters)
            output = [
                f"{i}: {title}",
                f"Read: {chapters_read}/{chapters}",
                f"Current Chapter: {manga.current_chapter + 1}",
            ]
            if title in new_chapters:
                output.append(f"{new_chapters[title]} new chapters!")
            print(" - ".join(output))
        print("\n")

    def _new_chapter_check(self, manga, new_chapters):
        """Checks manga for newly released chapters"""

        chapters = manga.provider().chapter_list(manga.link)
        chapter_names = [chapter.title for chapter in manga.chapters]
        for chapter in chapters:
            if chapter[0] not in chapter_names:
                manga.chapters.append(Chapter(name=chapter[0], link=chapter[1]))
                if manga.title in new_chapters:
                    new_chapters[manga.title] += 1
                else:
                    new_chapters[manga.title] = 1

    def new_chapters(self, multithreaded=True):
        """Returns new chapters for all manga"""

        new_chapters = {}
        if multithreaded:
            with ThreadPoolExecutor(max_workers=10) as executor:
                for manga in self.manga.values():
                    executor.submit(self._new_chapter_check, manga, new_chapters)
        else:
            for manga in self.manga.values():
                self._new_chapter_check(manga, new_chapters)
        return new_chapters

    def _fuzzy_find_title(self, title):
        """Returns the title of the manga closest to the submitted title"""

        return max(self.manga.keys(), key=lambda x: fuzz.ratio(title, x))
