import requests
from bs4 import BeautifulSoup


def search_wiki(search_query):
    url = 'https://ru.wikipedia.org/w/index.php?search={}&title=%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F%3A%D0%9F%D0%BE%D0%B8%D1%81%D0%BA&profile=advanced&fulltext=1&advancedSearch-current=%7B%7D&ns0=1&wprov=acrw1_-1'.format(
        search_query)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    data = soup.find_all('li', attrs={'class': 'mw-search-result'})
    results = {}
    counter = 0
    for i in data:
        search_title = str(i).split('title="')[1].split('"')[0].strip()
        search_link = 'https://ru.wikipedia.org' + \
            str(i).split('href="')[1].split('"')[0].strip()
        results[counter] = {'search_title': search_title, 'search_link': search_link}
        counter += 1
    return results
