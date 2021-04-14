import re

from fuzzywuzzy import fuzz


class Manga:
    """Class representing a manga"""

    def __init__(
        self,
        title,
        link,
        authors="",
        download_mode="dynamic",
        provider="Mangakakalot",
        current_chapter=0,
        chapters=[],
    ):
        self.title = title
        self.link = link
        self.authors = authors
        self.download_mode = download_mode
        self.provider = provider
        self.current_chapter = current_chapter
        self.chapters = chapters

    def __getitem__(self, accessor):
        if isinstance(accessor, (int, slice)):
            return self.chapters[accessor]
        elif isinstance(accessor, tuple):
            return [self.chapters[i] for i in [int(c) for c in accessor]]
        else:
            return max(self.chapters, key=lambda x: fuzz.ratio(x.title))

    @classmethod
    def _parse(cls, data):
        return cls(
            title=data["title"],
            link=data["link"],
            authors=data["authors"],
            download_mode=data["download_mode"],
            provider=data["provider"],
            current_chapter=data["current_chapter"],
            chapters=[Chapter._parse(chapter) for chapter in data["chapters"]],
        )

    def _to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "authors": self.authors,
            "download_mode": self.download_mode,
            "provider": self.provider,
            "current_chapter": self.current_chapter,
            "chapters": [chapter._to_dict() for chapter in self.chapters],
        }


class Chapter:
    """Class representing a manga chapter"""

    def __init__(self, title, link, path="", read=False):
        self.title = title
        self.link = link
        self.path = path
        self.read = read

    @classmethod
    def _parse(cls, data):
        return cls(
            title=data["title"], link=data["link"], path=data["path"], read=data["read"]
        )

    def _to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "path": self.path,
            "read": self.read,
        }


class SearchResult:
    """Result from searching a provider site"""

    def __init__(self, title, link, authors=None, updates=None, chapters=None):
        self.title = title
        self.link = link
        self.authors = authors
        self.updates = updates
        self.chapters = chapters

    def format(self):
        outputs = [self.title]
        if self.authors:
            outputs.append(self.authors)
        if self.updates:
            outputs.append(self.updates)
        if self.chapters:
            outputs.append(self.chapters)
        return " - ".join(outputs)
