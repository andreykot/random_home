from collections import deque
import requests
import re
from random import randint, shuffle
import time
from sqlalchemy.orm import Session
from fake_useragent import UserAgent

from app import db, tools


PROXIES_SOURCE = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt"


def get_proxies_from_source_txt():
    try:
        r = requests.get(PROXIES_SOURCE)
    except requests.ConnectionError:
        return []

    proxies = re.findall(r"(\d+\.\d+\.\d+\.\d+:\d+).*-S", r.content.decode())
    shuffle(proxies)
    return proxies


def get_cian(url: str, page: int = None) -> (requests.Response, None):
    session = Session(bind=db.models.engine)
    answer = None
    for current_proxy in get_proxies_from_db(session, 5):
        try:
            url_page = url + '&page={}'.format(page) if page else url
            proxy = {'https': 'https://' + current_proxy.address}

            ua = UserAgent()
            html = requests.get(url_page,
                                headers={'User-Agent': ua.random},
                                proxies=proxy,
                                timeout=5)
            if check_response_get(html):
                answer = html
                break

        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidProxyURL,
                requests.exceptions.ReadTimeout):
            session.query(db.models.ProxyList).\
                filter(db.models.ProxyList.id == current_proxy.id).\
                update({'available': False})
            print(f"{current_proxy} is not available.")
            session.commit()

    session.close()
    return answer


def post_cian(json_query) -> (requests.Response, None):
    session = Session(bind=db.models.engine)
    answer = None
    for current_proxy in get_proxies_from_db(session, max=5):
        try:
            proxy = {'http': 'http://' + current_proxy.address,
                     'https': 'https://' + current_proxy.address}
            print(proxy)

            ua = UserAgent()
            html = requests.post(tools.CianApiParser.parser.API,
                                 headers={'User-Agent': ua.random},
                                 timeout=10,
                                 proxies=proxy,
                                 data=json_query)
            print(html.status_code)
            if check_response_post(html):
                answer = html
                break

        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidProxyURL,
                requests.exceptions.ReadTimeout, ConnectionError) as e:
            print(e)
            session.query(db.models.ProxyList).\
                filter(db.models.ProxyList.id == current_proxy.id).\
                update({'available': False})
            print(f"{current_proxy.address} is not available.")
            session.commit()
            time.sleep(5)

    session.close()
    return answer


def check_response_get(response: requests.Response):
    if re.search(r'[cC]aptcha', response.content.decode()):
        raise requests.exceptions.InvalidProxyURL
    elif response.status_code == 200:
        return True
    elif response.status_code == 404:
        raise requests.exceptions.InvalidURL
    else:
        raise requests.exceptions.ConnectionError


def check_response_post(response: requests.Response):
    if re.search(r'[cC]aptcha', response.content.decode()):
        raise requests.exceptions.InvalidProxyURL
    elif response.status_code == 200:
        return True
    elif response.status_code == 404:
        raise requests.exceptions.InvalidURL
    else:
        raise requests.exceptions.ConnectionError


def get_proxies_from_db(session: Session, max: int = 5):
    proxies = session.query(db.models.ProxyList).\
        filter(db.models.ProxyList.available).\
        all()
    if proxies:
        for i in range(0, len(proxies)):
            yield proxies[i]
            if max <= i:
                break
    else:
        raise ValueError("Couldn't find proxies in DB")


def test():
    post_cian({'jsonQuery': {'page': {'type': 'term', 'value': 3},
  'region': {'type': 'terms', 'value': [2]},
  '_type': 'flatsale',
  'for_day': {'type': 'terms', 'value': '!1'},
  'price': {'type': 'range', 'value': {'gte': 0, 'lte': 4000000}},
  'room': {'type': 'terms', 'value': [1]},
  'currency': {'type': 'term', 'value': 2},
  'engine_version': {'type': 'term', 'value': 2}}})


if __name__ == '__main__':
    #test()
    print(get_proxies_from_source_txt())
