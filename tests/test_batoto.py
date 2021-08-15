import json
import unittest
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
                title=f"Chapter {i}",
                link=f"https://ww.mangakakalot.tv/chapter/kxqh9261558062112/chapter_{i}",
                path="",
                read=False,
            )
            for i in range(20)
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
        self.manager = MangaManager(
            save=False,
            manga=self.manga
        )

    def tearDown(self) -> None:
        return super().tearDown()

    def test_batoto_exist_in_providers(self):
        find_provider(self.provider_name)()

    def test_batoto_download(self):
        provider = find_provider(self.provider_name)()
        provider.download(
            title=self.manga_title,
            chapters=self.manga[self.manga_title].chapters[:self.chapter_limit],
            dl_dir=self.manga_path / self.manga_title,
        )

    def test_batoto_search(self):
        provider = find_provider(self.provider_name)()
        results, pages = provider.search()
        print(results, pages)

if __name__ == "__main__":
    unittest.main()
