from bs4 import BeautifulSoup
import requests
from urllib.parse import quote_plus
import time
import mongo
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

base_url = 'https://mudae.fandom.com'


def get_all_characters():
    characters = []
    while True:
        if len(characters) == 0:
            char_list_url = 'https://mudae.fandom.com/wiki/Category:Characters'
        else:
            char_list_url = 'https://mudae.fandom.com/wiki/Category:Characters?from=' + quote_plus(
                characters[-1]['name'])
        response = requests.get(char_list_url)
        if response.status_code != 200:
            print('Failed to get the page. Status code:', response.status_code)
            print('Retrying in 5 seconds...')
            time.sleep(5)
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        for name in soup.find_all(class_='category-page__member-link'):
            character = {'name': name.text, 'url': base_url + name['href']}
            if character not in characters:
                characters.append(character)
        print('Amount of characters:', len(characters))
        if len(characters) == 3602:
            print('All characters have been fetched.')
            break

    return characters


def get_character(character_url):
    response = requests.get(character_url)
    if response.status_code != 200:
        print('Failed to get the page. Status code:', response.status_code)
        time.sleep(5)
        return get_character(character_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    info = {}
    series_div = soup.find(attrs={'data-source': 'series'})
    try:
        series_name = series_div.find('a').text
    except AttributeError:
        series_name = series_div.find('span').text
    info['series'] = series_name

    gender_div = soup.find(attrs={'data-source': 'gender'})
    gender = gender_div.find('div').text
    info['gender'] = gender

    return info


def get_character_artworks(character_url):
    response = requests.get(character_url)
    if response.status_code != 200:
        print('Failed to get the page. Status code:', response.status_code)
        time.sleep(5)
        return get_character_artworks(character_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    artworks = []
    character_aside = soup.find('aside', class_='type-character')
    for img_container in character_aside.find_all(class_='pi-image'):
        img_tag = img_container.find('a')
        img_url = img_tag['href']
        artworks.append(img_url)
    return artworks


def process_character(character):
    charUrl = character['url']
    charName = character['name']
    char = get_character(charUrl)
    charGender = char['gender']
    charSeries = char['series']
    artworksUrl = get_character_artworks(character['url'])

    mongo.add_character(charName, charSeries, charGender, charUrl)
    for artwork in artworksUrl:
        mongo.add_artwork(charName, artwork)


def main():
    mongo.create_indexes()
    all_characters = get_all_characters()

    with ThreadPoolExecutor(max_workers=5) as executor:
        list(tqdm(executor.map(process_character, all_characters), total=len(all_characters)))


if __name__ == "__main__":
    main()
