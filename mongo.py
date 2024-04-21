from pymongo import MongoClient
import hashlib

client = MongoClient('localhost', 27017)

db = client['MudaeScraper']

characters = db['Characters']
artworks = db['Artworks']


def create_indexes():
    artworks.create_index([('characterId', 1)])
    artworks.create_index([('artworkId', 1)], unique=True)
    artworks.create_index([('artworkUrl', 1)], unique=True)
    characters.create_index([('name', 1), ('series', 1)])
    characters.create_index([('characterId', 1)], unique=True)
    characters.create_index([('gender', 1)])
    characters.create_index([('name', -1), ('series', 1)])
    characters.create_index([('series', 1), ('name', 1)])
    characters.create_index([('series', -1), ('name', 1)])


def add_character(name, series, gender, url):
    char_id = hashlib.md5(str.encode(name)).hexdigest()
    char = characters.find_one({'characterId': char_id})
    if char is None:
        characters.insert_one({'characterId': char_id, 'name': name, 'series': series, 'gender': gender, 'charUrl': url})


def add_artwork(charName, url):
    character_id = hashlib.md5(str.encode(charName)).hexdigest()
    artwork_id = hashlib.md5(str.encode(url)).hexdigest()
    artwork = artworks.find_one({'artworkId': artwork_id})
    if artwork is None:
        artworks.insert_one({'artworkId': artwork_id, 'characterId': character_id, 'artworkUrl': url})