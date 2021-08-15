from manga_manager.provider.mangakakalot import Mangakakalot
from manga_manager.provider.batoto import Batoto

provider_dict = {
    "Mangakakalot": Mangakakalot,
    "Batoto": Batoto
}

def find_provider(provider):
    if provider in provider_dict:
        return provider_dict[provider]
    else:
        raise Exception("Invalid provider")
