from collections import namedtuple
import re
import requests
from bs4 import BeautifulSoup

from app.CianParser.apartment import Apartment


CianFlat = namedtuple('CianFlat', ['link', 'title'])


class CianParser:
    def __init__(self, query):
        self.query = query

    def get_flats(self, page):
        html = requests.get(self.query + '&page={}'.format(page))
        check_status_code(html)
        soup = BeautifulSoup(html.content, 'lxml')
        offers = soup.find('div', attrs={'data-name': "Offers"})

        flats = list()
        for i in offers:
            flat = i.find('a', attrs={'target': "_blank", 'class': re.compile('--header--')})
            if flat:
                link = flat['href']
                if '--title--' in flat.div['class'][0] or '--single_title--' in flat.div['class'][0]:
                    title = flat.div.text
                elif '--title_wrapper--' in flat.div['class'][0]:
                    title = flat.find('div', class_=re.compile('--subtitle--')).text

                flats.append(CianFlat(link=link, title=title))

        return flats


def check_status_code(response):
    if response.status_code == 200:
        return
    else:
        print('Status: {}'.format(response.status_code))
        raise ConnectionError


def get_flats_by_query():
    apartment_link = Apartment(region='Saint Petersburg',
                               deal=(False, True, False, False),
                               rooms=(1, 2),
                               apartment_type=(False, True),
                               price=(0, 30000))
    parser = CianParser(query=apartment_link.create_link())
    page = 2
    return parser.get_flats(page)


if __name__ == '__main__':
    parser = CianParser(r'https://cian.ru/cat.php?&deal_type=rent&type=3&region=2&room1=1&room2=1&minprice=0&maxprice=49900')
    flats = parser.get_flats(5)
    print(*flats, sep='\n')
