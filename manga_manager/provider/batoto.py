import re
from concurrent.futures import ThreadPoolExecutor
import traceback

import requests
from bs4 import BeautifulSoup

from manga_manager.provider.provider import Provider
from manga_manager.model import SearchResult
from manga_manager.util import chapter_filename, clean_text

class Batoto(Provider):
    name = "Batoto"
