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
        get_character(character_url)
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    info = {}
    series_div = soup.find(attrs={'data-source': 'series'})
    series_name = series_div.find('a').text
    info['series'] = series_name

    gender_div = soup.find(attrs={'data-source': 'gender'})
    gender = gender_div.find('div').text
    info['gender'] = gender

    return info


def main():
    all_characters = get_all_characters()
    for character in all_characters:
        get_character(character)


if __name__ == "__main__":
    main()
