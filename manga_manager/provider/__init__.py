from manga_manager.provider.mangakakalot import Mangakakalot

provider_dict = {
    "Mangakakalot": Mangakakalot
}

def find_provider(provider):
    if provider in provider_dict:
        return provider_dict[provider]
    else:
        raise Exception("Invalid provider")