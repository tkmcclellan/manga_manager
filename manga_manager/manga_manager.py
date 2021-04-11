import warnings

warnings.filterwarnings("ignore")

import itertools
import json
import os
import shutil
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fuzzywuzzy import fuzz

from manga_manager.provider import *
from manga_manager.util import argument_parser

DYNAMIC_DL_SIZE = 2


def _load():
    """Loads config from file"""
    path = Path(__file__).parent
    config = None
    if "config.json" not in os.listdir(path):
        open(path / "config.json", "w").close()
        return {"manga": {}}
    else:
        with open(path / "config.json", "r") as file:
            config = json.loads(file.read())
        return config


def save():
    """Saves config to file"""
    path = Path(__file__).parent
    try:
        data = json.dumps(config)
        with open(path / "config.json", "w") as file:
            file.write(data)
    except Exception as e:
        print(e)


def _update_chapter_paths(manga_name, paths):
    """Updates paths in a manga's chapters"""
    for chapter in config["manga"][manga_name]["chapters"]:
        if chapter["name"] in paths:
            chapter["path"] = paths[chapter["name"]]


def add_manga(title, provider=Mangakakalot(), download_mode="dynamic"):
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

    page = 1
    manga_url, manga_name, manga_authors, manga_chapters = None, None, None, None
    while True:
        results, pages = provider.search(title)
        for i, result in enumerate(results):
            print(f"{i}: {result['title']} - {result['authors']} - {result['updates']}")
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
                manga_url = results[i]["link"]
                manga_name = results[i]["title"]
                manga_authors = results[i]["authors"]
                manga_chapters = provider.chapter_list(manga_url)
                break
            except Exception:
                print("Invalid input")
                return

    if manga_name not in config["manga"]:
        config["manga"][manga_name] = {
            "name": manga_name,
            "link": manga_url,
            "authors": manga_authors,
            "download_mode": download_mode,
            "provider": provider.name,
            "current_chapter": 0,
            "chapters": [
                {"name": chapter[0], "link": chapter[1], "path": "", "read": False}
                for chapter in manga_chapters
            ],
        }
    if download_mode in ["dynamic", "all"]:
        paths = provider.download(
            manga_name,
            config["manga"][manga_name]["chapters"][
                : (DYNAMIC_DL_SIZE if download_mode == "dynamic" else -1)
            ],
        )
        _update_chapter_paths(manga_name, paths)


def remove_manga(title, delete_files=True):
    """Removes a manga from manga_manager.

    Args:
        title (str): Title of manga to be remoevd.
        delete_files (bool): Optional; Option to delete locally stored manga.
            Default is false.
    """

    confirmation = input(f"Are you sure you want to delete {title}? ([y]/n):").lower()
    if confirmation == "n":
        return
    if delete_files:
        shutil.rmtree(Path(__file__).parent / "manga" / title)
    config["manga"].pop(title)
    print(f"{title} was successfully deleted\n")


def edit_manga(title):
    """Display's a manga's config and allows the user to edit values

    Args:
        title (str): Title of the manga to be edited.
    """

    manga = config["manga"][title]

    for key, value in manga.items():
        if key != "chapters":
            print(f"{key} = {value}")

    while True:
        key = input("What config do you want to change? (q - Quit): ").lower()
        if key == "q":
            break
        elif key not in manga or key == "chapters":
            print("Invalid key")
        else:
            value = input(f"What should `{key}` be? ").lower()
            if value in ["true", "false"]:
                value = bool(value.title())
            manga[key] = value


def read_manga(title, chapter=None):
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

    manga = config["manga"][title]
    provider = eval(f"{manga['provider']}()")
    if not chapter:
        chapter = manga["current_chapter"]
    else:
        manga["current_chapter"] = chapter

    try:
        while True:
            offset = DYNAMIC_DL_SIZE
            current_chapter = manga["chapters"][chapter]
            print(f"Name: {manga['name']}")
            print(f"Chapter: {current_chapter['name']}\n")

            # check if current chapter is downloaded. if not, download it.
            if current_chapter["path"] == "":
                print("Downloading current chapter...")
                paths = provider.download(
                    manga["name"], [current_chapter], verbose=False
                )
                _update_chapter_paths(manga["name"], paths)

            # open current chapter
            webbrowser.get().open(f"file:///{current_chapter['path']}")

            # delete chapters outside of offset
            if manga["download_mode"] == "dynamic":
                # range for chapters outside of offset
                pre_offset = range(max(0, chapter - offset))
                post_offset = range(
                    min(len(manga["chapters"]), chapter + offset + 1),
                    len(manga["chapters"]),
                )
                offset_range = itertools.chain(pre_offset, post_offset)
                # print(list(offset_range))
                for c in offset_range:
                    try:
                        os.remove(manga["chapters"][c]["path"])
                    except Exception:
                        """do nothing"""
                    finally:
                        manga["chapters"][c]["path"] = ""
                # download chapters in offset
                chapter_downloads = [
                    c
                    for c in manga["chapters"][
                        max(0, chapter - offset) : min(
                            chapter + offset + 1, len(manga["chapters"])
                        )
                    ]
                    if c["path"] == ""
                ]
                paths = provider.download(
                    manga["name"], chapter_downloads, verbose=False
                )
                _update_chapter_paths(manga["name"], paths)
            selection = input("\nAction? ([n - Next]/p - Previous/q - Quit): ").lower()
            if selection == "q":
                manga["current_chapter"] = chapter
                break
            elif selection == "p":
                chapter = max(chapter - 1, 0)
            else:
                current_chapter["read"] = True
                chapter = min(len(manga["chapters"]), chapter + 1)
    except KeyboardInterrupt:
        return


def list_manga(new_chapters):
    """Lists the manga currently being tracked by manga_manager"""

    if len(config["manga"].items()) == 0:
        return
    for i, (name, manga) in enumerate(config["manga"].items()):
        chapters_read = len(
            [chapter for chapter in manga["chapters"] if chapter["read"]]
        )
        chapters = len(manga["chapters"])
        output = [
            f"{i}: {name}",
            f"Read: {chapters_read}/{chapters}",
            f"Current Chapter: {manga['current_chapter'] + 1}"
        ]
        if name in new_chapters:
            output.append(f"{new_chapters[name]} new chapters!")
        print(" - ".join(output))
    print("\n")


def _new_chapter_check(manga, new_chapters):
    """Checks manga for newly released chapters"""

    provider = eval(f"{manga['provider']}()")
    chapters = provider.chapter_list(manga["link"])
    chapter_names = [chapter["name"] for chapter in manga["chapters"]]
    for chapter in chapters:
        if chapter[0] not in chapter_names:
            manga["chapters"].append(
                {"name": chapter[0], "link": chapter[1], "path": "", "read": False}
            )
            if manga["name"] in new_chapters:
                new_chapters[manga["name"]] += 1
            else:
                new_chapters[manga["name"]] = 1


def print_separator():
    """Prints a separator line"""

    print("~" * 35)


def fuzzy_find_title(title):
    """Returns the title of the manga closest to the submitted title"""

    return max(config["manga"].keys(), key=lambda x: fuzz.ratio(title, x))


def print_welcome():
    """Prints the manga_manager welcome header"""

    welcome_message = "~Welcome to Manga Manager~"
    print_separator()
    print(welcome_message)
    print("-" * len(welcome_message) + "\n")


def start_menu():
    """Menu for using manga_manager"""

    try:
        new_chapters = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            for manga in config["manga"].values():
                executor.submit(_new_chapter_check, manga, new_chapters)
        while True:
            print_welcome()
            list_manga(new_chapters)
            selection = input("> ")
            print_separator()
            parser = argument_parser()
            args = parser.parse_args(selection.split())
            args.title = " ".join(args.title)
            if args.action == "add":
                add_manga(
                    title=args.title,
                    provider=eval(f"{args.provider}()"),
                    download_mode=args.download_mode,
                )
                save()
            elif args.action == "remove":
                remove_manga(fuzzy_find_title(args.title))
                save()
            elif args.action == "edit":
                edit_manga(fuzzy_find_title(args.title))
                save()
            elif args.action == "read":
                read_manga(
                    title=fuzzy_find_title(args.title),
                    chapter=int(args.chapters) - 1 if args.chapters else None,
                )
                save()
            elif args.action == "quit":
                break
    except KeyboardInterrupt:
        """do nothing"""
    except Exception as e:
        print(e)
    finally:
        save()


config = _load()
