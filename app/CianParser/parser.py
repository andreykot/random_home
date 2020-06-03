from collections import namedtuple, deque
from random import randint
import re
import requests
import traceback
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app import db
from .proxy_processor import connect_to_cian


CianFlat = namedtuple('CianFlat', ['link', 'title'])


FLATS_PER_PAGE = 28


class Parser:
    def __init__(self, url: str):
        self.url = url

    @staticmethod
    def get_amount(content: str, soup: BeautifulSoup = None) -> (int, None):
        try:
            if not soup:
                soup = BeautifulSoup(content, 'lxml')
            summary_header = soup.find('div', attrs={'data-name': "SummaryHeader"})
            pattern = re.compile("Найдено\s(.+)\sобъявлений")
            summary_header_text = summary_header.find('h3', text=pattern).text
            sum_int = int(re.search(pattern, summary_header_text)[1].replace(' ', ''))
            return sum_int
        except Exception:
            print(traceback.print_exc())

    def process(self, page=None):
        html = connect_to_cian(url=self.url, page=page)

        if not html:
            raise requests.exceptions.ConnectionError

        soup = self.create_parse_soup(html)

        estimated_pages = self.get_amount(content=html.content, soup=soup) // FLATS_PER_PAGE
        pages = estimated_pages if estimated_pages <= 54 else 54
        page = page if page <= pages else 54

        flats_from_page = self.get_flats_from_page(soup)
        random_flat = self.get_random_flat(flats_from_page)
        return random_flat, pages

    @staticmethod
    def create_parse_soup(html: requests.Response):
        return BeautifulSoup(html.content, 'lxml')

    def get_flats_from_page(self, soup: BeautifulSoup) -> list:
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

    def get_random_flat(self, flats: list) -> CianFlat:
        return flats[randint(0, FLATS_PER_PAGE - 1)]


class Apartment:
    """Class to initialize apartment with his special parameters."""

    def __init__(self, region: str, deal: int, rooms: tuple = None, apartment_type: int = None,
                 price: tuple = None):
        """
        Args:
            region (:str): Name of region for search.
                Available: 'Москва', 'Санкт-Петербург'.
            deal (:int): Deal type of apartment. There are four options:
                Available: 1 - for sale, 2 - for rent 1year+, 3 - rent 1year, 4 - per-day rent.
            rooms (:tuple of :int): List of available number of rooms for apartment.
                Available: 9 - studios, 1 - 1-room, 2 - 2-room, 3 - 3-room, 4 - 4-room+.
                Example: (1,2) - apartment with 1 or 2 rooms.
            apartment_type (:int): Apartment type.
                Available: 0 - all apartments, 1 - new apartments, 2 - secondary apartments.
            price (:tuple of :int or Nonetype): Min and max price of apartment.
                Example: (None, 3000000) - min price is None, max price is 3000000.
        """

        self.region = region
        self.deal = deal
        self.rooms = rooms
        self.apartment_type = apartment_type
        self.price = price
        self.region = region

    def create_link(self):
        query = r'https://cian.ru/cat.php?'
        for func in self.get_deal, self.get_region, self.get_rooms, self.get_apartment_type, self.get_price:
            query = func(query)
        return query

    def get_deal(self, query):
        if self.deal not in [1, 2, 3, 4]:
            raise ValueError('Incompatible arguments for Apartment.deal')

        if self.deal == 1:
            return query + '&' + 'deal_type=sale'
        else:
            if self.deal == 2:
                return query + '&' + 'deal_type=rent' + '&' + 'type=4'
            elif self.deal == 3:
                return query + '&' + 'deal_type=rent' + '&' + 'type=3'
            elif self.deal == 4:
                return query + '&' + 'deal_type=rent' + '&' + 'type=2'
            else:
                raise ValueError('No arguments for deal type.')

    def get_rooms(self, query):
        if self.rooms:
            for n in self.rooms:
                if isinstance(n, int):
                    query += '&' + 'room{}=1'.format(n)
                else:
                    raise ValueError('Incompatible type of arguments for "rooms". Need iterable of int.')
        return query

    def get_apartment_type(self, query):
        if self.apartment_type:
            if self.deal != 1 or self.apartment_type == 0:
                return query
            elif self.apartment_type == 1:
                return query + '&' + 'object_type=2'
            elif self.apartment_type == 2:
                return query + '&' + 'object_type=1'
            else:
                raise RuntimeError

        return query

    def get_price(self, query):
        if self.price:
            if self.price[0]:
                query += '&' + 'minprice=' + str(int(self.price[0]))

            if self.price[1]:
                query += '&' + 'maxprice=' + str(int(self.price[1]))

        return query

    def get_region(self, query):
        if self.region == 'Москва':
            return query + '&' + 'region=1'
        elif self.region == 'Санкт-Петербург':
            return query + '&' + 'region=2'
        else:
            raise ValueError('Unsupported region.')


def safe_commit(session):
    try:
        session.commit()
    except Exception:
        print(traceback.format_exc())
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    parser = Parser(r'https://cian.ru/cat.php?&deal_type=rent&type=3&region=2&room1=1&room2=1&minprice=0&maxprice=49900')
    flats = parser.get_flats(5)
    print(*flats, sep='\n')
