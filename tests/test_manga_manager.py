#!/usr/bin/env python

"""Tests for `manga_manager` package."""


import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from manga_manager.manga_manager import MangaManager
from manga_manager.model import Chapter, Manga, SearchResult


manga = {
    "Attack On Titan": Manga(
        title="Attack On Titan",
        link="https://ww.mangakakalot.tv/manga/kxqh9261558062112",
        authors="Author(s) : Isayama Hajime",
        download_mode="dynamic",
        provider="Mangakakalot",
        current_chapter=11,
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
    "Oyasumi Punpun": Manga(
        title="Oyasumi Punpun",
        link="https://ww.mangakakalot.tv/manga/oyasumi_punpun",
        authors="Author(s) : Asano Inio",
        download_mode="all",
        provider="Mangakakalot",
        current_chapter=5,
        chapters=[
            Chapter(
                title=f"Chapter {i}",
                link=f"https://ww.mangakakalot.tv/chapter/oyasumi_punpun/chapter_{i}",
                path="",
                read=False,
            )
            for i in range(20)
        ],
    ),
}

read_data = json.dumps(
    {"manga": {title: manga._to_dict() for title, manga in manga.items()}}
)

search_results = [
    SearchResult(
        f"Fake Title {i}",
        link=f"https://fakelink.com/{i}",
        authors=f"Fake Author {i}",
    )
    for i in range(20)
]


def chapters(start=0, stop=20):
    return [
        [f"Fake Title {i}", f"https://fakelink.com/c/{i}"] for i in range(start, stop)
    ]


class TestManga_manager(unittest.TestCase):
    """Tests for `manga_manager` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.manga = deepcopy(manga)
        self.read_data = deepcopy(read_data)
        self.search_results = deepcopy(search_results)
        self.manager = MangaManager(
            manga=self.manga,
            save=False,
        )

    def tearDown(self):
        """Tear down test fixtures, if any."""

    # load
    @patch(
        "manga_manager.manga_manager.open", new_callable=mock_open, read_data=read_data
    )
    def test_manga_manager__load(self, open_mock):
        """Tests that data is loaded correctly"""

        data = self.manager.load()
        self.assertEqual(
            {title: manga._to_dict() for title, manga in data.items()},
            {t: m._to_dict() for t, m in self.manga.items()},
        )
        open_mock.assert_called_with(self.manager.data_path, "r")

    @patch(
        "manga_manager.manga_manager.open", new_callable=mock_open, read_data=read_data
    )
    def test_manga_manager__load_nonexistent_file(self, open_mock):
        self.manager.data_path = Path("fake_path")
        self.assertEqual({}, self.manager.load())
        open_mock.assert_called_with(self.manager.data_path, "w")

    # save
    @patch(
        "manga_manager.manga_manager.open", new_callable=mock_open, read_data=read_data
    )
    def test_manga_manager__save(self, open_mock):
        self.manager.save_data = True
        self.manager.save()
        open_mock.assert_called_with(self.manager.data_path, "w")
        handle = open_mock()
        handle.write.assert_called_once_with(read_data)

    @patch(
        "manga_manager.manga_manager.open", new_callable=mock_open, read_data=read_data
    )
    def test_manga_manager__disable_save(self, open_mock):
        self.manager.save()
        open_mock.assert_not_called()

    # add manga
    @patch("manga_manager.manga_manager.input")
    @patch("manga_manager.manga_manager.find_provider")
    def test_manga_manager__add_manga(self, find_provider_mock, input_mock):
        input_mock.return_value("0")
        provider_mock = MagicMock()
        provider_mock.search.return_value = (
            self.search_results,
            len(self.search_results),
        )
        provider_mock.chapter_list.return_value = chapters()
        provider_mock.download.return_value = {
            chapter[0]: chapter[1] for chapter in chapters()
        }
        provider_mock.name.return_value = "Mangakakalot"
        find_provider_mock().return_value = provider_mock

        self.manager.add_manga("attack on titan")
        input_mock.assert_called()
        provider_mock.search.assert_called_with("attack on titan")
        provider_mock.chapter_list.assert_called_with("https://fakelink.com/1")
        provider_mock.download.assert_called()
        find_provider_mock.assert_called_with("Mangakakalot")