"""
TODO:
- check for new volumes (autodownload or manually download dictated by config)
"""

import warnings
warnings.filterwarnings('ignore')

import json
import os
import shutil
import webbrowser
from argparse import ArgumentParser
from pathlib import Path
from fuzzywuzzy import fuzz
import itertools
from manga_manager.driver import *


DYNAMIC_DL_SIZE = 2


def load():
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
    path = Path(__file__).parent
    try:
        data = json.dumps(config)
        with open(path / "config.json", "w") as file:
            file.write(data)
    except Exception as e:
        print(e)


def update_chapter_paths(manga_name, paths):
    for chapter in config["manga"][manga_name]["chapters"]:
        if chapter["name"] in paths:
            chapter["path"] = paths[chapter["name"]]


def add_manga(title, provider='Mangakakalot', download_mode='dynamic'):
    provider = eval(f"{provider}()")
    manga_url, manga_name, manga_authors, manga_chapters = provider.search(
        title)

    if manga_name:
        if manga_name not in config["manga"]:
            config["manga"][manga_name] = {
                "name": manga_name,
                "link": manga_url,
                "authors": manga_authors,
                "download_mode": download_mode,
                "provider": provider.name,
                "current_chapter": 0,
                "chapters": [{"name": chapter[0], "link": chapter[1], "path": "", "read": False} for chapter in manga_chapters]
            }
        if download_mode in ["dynamic", "all"]:
            paths = provider.download(
                manga_name,
                config["manga"][manga_name]["chapters"][:(
                    DYNAMIC_DL_SIZE if download_mode == "dynamic" else -1)]
            )
            update_chapter_paths(manga_name, paths)
    else:
        print("Title not found")


def remove_manga(title):
    confirmation = input(f"Are you sure you want to delete {title}? ([y]/n):").lower()
    if confirmation == "n":
        return
    shutil.rmtree(Path("manga", title))
    config["manga"].pop(title)
    print(f"{title} was successfully deleted\n")


def edit_manga(title):
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


def manga_from_selection(selection):
    selection = "0" if selection == "" else selection
    name, manga = list(config["manga"].items())[int(selection)]
    return name, manga


def read_manga(title, chapter=None):
    manga = config["manga"][title]
    provider = eval(f"{manga['provider']}()")
    if not chapter:
        chapter = manga["current_chapter"]
    else:
        manga["current_chapter"] = chapter

    while True:
        offset = DYNAMIC_DL_SIZE
        current_chapter = manga["chapters"][chapter]
        print(f"Name: {manga['name']}")
        print(f"Chapter: {current_chapter['name']}\n")

        # check if current chapter is downloaded. if not, download it.
        if current_chapter["path"] == "":
            print("Downloading current chapter...")
            paths = provider.download(
                manga["name"],
                [current_chapter],
                verbose=False
            )
            update_chapter_paths(manga["name"], paths)

        # open current chapter
        webbrowser.get().open(f"file:///{current_chapter['path']}")

        # delete chapters outside of offset
        if manga["download_mode"] in ["dynamic", "none"]:
            # range for chapters outside of offset
            pre_offset = range(max(0, chapter - offset))
            post_offset = range(min(len(manga["chapters"]), chapter + offset + 1), len(manga["chapters"]))
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
            chapter_downloads = [c for c in manga['chapters'][max(0, chapter-offset):min(chapter+offset+1, len(manga['chapters']))] if c['path'] == '']
            paths = provider.download(
                manga["name"],
                chapter_downloads,
                verbose=False
            )
            update_chapter_paths(manga["name"], paths)
        selection = input("\nAction? ([n - Next]/p - Previous/q - Quit): ").lower()
        if selection == "q":
            manga["current_chapter"] = chapter
            break
        elif selection == "p":
            chapter = max(chapter - 1, 0)
        else:
            current_chapter["read"] = True
            chapter = min(len(manga["chapters"]), chapter + 1)


def list_manga():
    if len(config["manga"].items()) == 0:
        return
    for i, (name, manga) in enumerate(config["manga"].items()):
        chapters_read = len(
            [chapter for chapter in manga["chapters"] if chapter["read"]])
        chapters = len(manga["chapters"])
        print(f"{i}: {name} - {chapters_read}/{chapters}")
    print("\n")


def new_chapter_check():
    new_chapters = {}
    for name, manga in config["manga"].items():
        provider = eval(f"{manga['provider']}()")
        chapters = provider.new_chapters(manga)
        for chapter in chapters:
            manga["chapters"].append(chapter)
            if manga["name"] not in new_chapters:
                new_chapters[manga["name"]] = [chapter]
            else:
                new_chapters[manga["name"]].append(chapter)


def print_seperator():
    print("~"*35)


def argument_parser():
    parser = ArgumentParser()
    parser.add_argument('action', choices=['add', 'remove', 'edit', 'read', 'quit'])
    parser.add_argument('title', nargs='*')
    parser.add_argument('-t', '--title', default="")
    parser.add_argument('-i', '--index', type=int, required=False)
    parser.add_argument('-c', '--chapters', required=False)
    parser.add_argument('-dm', '--download_mode',
                        choices=['dynamic', 'all', 'none'], default='dynamic')
    parser.add_argument('-p', '--provider', default='Mangakakalot')
    return parser


def fuzzy_find_title(title):
    return max(config["manga"].keys(), key=lambda x: fuzz.ratio(title, x))


def start_menu():
    try:
        # new_chapters = new_chapter_check()
        while True:
            welcome_message = "~Welcome to Manga Manager~"
            print_seperator()
            print(welcome_message)
            print("-"*len(welcome_message) + "\n")
            list_manga()
            selection = input("> ")
            print_seperator()
            parser = argument_parser()
            args = parser.parse_args(selection.split())
            args.title = " ".join(args.title)
            if args.action == "add":
                add_manga(
                    title=args.title,
                    provider=args.provider,
                    download_mode=args.download_mode
                )
            elif args.action == "remove":
                remove_manga(fuzzy_find_title(args.title))
            elif args.action == "edit":
                edit_manga(fuzzy_find_title(args.title))
            elif args.action == "read":
                read_manga(
                    title=fuzzy_find_title(args.title),
                    chapter=int(args.chapters) - 1 if args.chapters else None
                )
            elif args.action == "quit":
                break
    except KeyboardInterrupt:
        """do nothing"""
    except Exception as e:
        print(e)
    finally:
        save()


config = load()
