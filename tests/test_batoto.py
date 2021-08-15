import json
import unittest
import time
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from manga_manager.manga_manager import MangaManager
from manga_manager.model import Chapter, Manga, SearchResult
from manga_manager.provider import find_provider

manga = {
    "One Piece": Manga(
        title="One Piece",
        link="https://bato.to/series/19516",
        authors="Author(s) : Oda, eiichiro",
        download_mode="dynamic",
        provider="Batoto",
        current_chapter=0,
        chapters=[
            Chapter(
                title=f"Chapter 1",
                link="https://bato.to/chapter/376339",
                path="",
                read=False,
            ),
            Chapter(
                title=f"Chapter 2",
                link="https://bato.to/chapter/376344",
                path="",
                read=False,
            ),
            Chapter(
                title=f"Chapter 3",
                link="https://bato.to/chapter/376347",
                path="",
                read=False,
            ),
            Chapter(
                title=f"Chapter 3",
                link="https://bato.to/chapter/376351",
                path="",
                read=False,
            ),
        ],
    ),
}

class TestManga_manager_Batoto(unittest.TestCase):
    """Tests for Batoto Provider"""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.manga_title = "One Piece"
        self.provider_name = "Batoto"
        self.chapter_limit = 2
        self.manga_path = Path(__file__).parent / "manga"
        self.manga = deepcopy(manga)
        self.provider = find_provider(self.provider_name)()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_batoto_exist_in_providers(self):
        find_provider(self.provider_name)()

    def test_batoto_download(self):
        self.provider.download(
            title=self.manga_title,
            chapters=self.manga[self.manga_title].chapters[:self.chapter_limit],
            dl_dir=self.manga_path / self.manga_title,
        )

    def test_batoto_chapter_list(self):
        chapters = self.provider.chapter_list(self.manga[self.manga_title].link)
        print(chapters)

    def test_batoto_search(self):
        provider = find_provider(self.provider_name)()
        results, pages = provider.search()
        print(results, pages)

if __name__ == "__main__":
    unittest.main()
