import re
from argparse import ArgumentParser


def argument_parser():
    parser = ArgumentParser()
    parser.add_argument("action", choices=["add", "remove", "edit", "read", "quit"])
    parser.add_argument("title", nargs="*")
    parser.add_argument("-c", "--chapters", required=False)
    parser.add_argument(
        "-dm", "--download_mode", choices=["dynamic", "all", "none"], default="dynamic"
    )
    parser.add_argument("-p", "--provider", default="Mangakakalot")
    return parser


def clean_text(chapter_name):
    return re.sub(" +", " ", re.sub("\n", "", chapter_name)).strip()

def chapter_filename(chapter_name):
    return re.sub(' ', '-', re.sub('[^a-zA-Z0-9 ]', '', clean_text(chapter_name)))[:240] + ".pdf"
