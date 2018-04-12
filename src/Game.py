class Game:
    name = ""
    provider = ""
    release_date = ""
    genres = ""
    price = ""
    platform = ""
    size = ""
    is_plus_exclusive = ""

    def __init__(self, name="", provider="", release_date="", genres="", price="", platform="", size="", is_plus_exclusive=""):
        self.name = name
        self.provider = provider
        self.release_date = release_date
        self.genres = genres
        self.price = price
        self.platform = platform
        self.size = size
        self.is_plus_exclusive = is_plus_exclusive

    def to_dict(self):
        return {
            'name': self.name,
            'provider': self.provider,
            'release_date': self.release_date,
            'genres' : self.genres,
            'price': self.price,
            'platform': self.platform,
            'size': self.size,
            'is_plus_exclusive': self.is_plus_exclusive
        }


