from bs4 import BeautifulSoup
import requests
from urllib.parse import quote_plus
import time

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
    series_name = series_div.find('a').text
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


def main():
    all_characters = get_all_characters()
    for character in all_characters:
        char = get_character(character['url'])
        urls = get_character_artworks(character['url'])


if __name__ == "__main__":
    main()
