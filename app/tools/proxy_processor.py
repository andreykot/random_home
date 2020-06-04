from collections import deque
import requests
import re
from random import randint, shuffle
from sqlalchemy.orm import Session
from fake_useragent import UserAgent

from app import db


PROXIES_SOURCE = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt"


def get_proxies_from_source_txt():
    try:
        r = requests.get(PROXIES_SOURCE)
    except requests.ConnectionError:
        return []

    proxies = re.findall(r"\d+\.\d+\.\d+\.\d+:\d+", r.content.decode())
    shuffle(proxies)
    return proxies


def connect_to_cian(url: str, page: int = None) -> (requests.Response, None):
    session = Session(bind=db.models.engine)
    answer = None
    for current_proxy in get_proxies_from_db(session, 20):
        try:
            url_page = url + '&page={}'.format(page) if page else url
            proxy = {'http': 'http://' + current_proxy.address}

            ua = UserAgent()
            html = requests.get(url_page,
                                headers={'User-Agent': ua.random},
                                proxies=proxy,
                                timeout=5)
            if check_response(html):
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


def check_response(response: requests.Response):
    if re.search(r'[cC]aptcha', response.content.decode()):
        raise requests.exceptions.InvalidProxyURL
    elif response.status_code == 200:
        return True
    elif response.status_code == 404:
        raise requests.exceptions.InvalidURL
    else:
        raise requests.exceptions.ConnectionError


def get_proxies_from_db(session: Session, n: int = 20):
    proxies = session.query(db.models.ProxyList).\
        filter(db.models.ProxyList.available).\
        all()
    if proxies:
        start = randint(0, len(proxies) - n)
        end = start + n
        for i in range(start, end):
            yield proxies[i]
    else:
        raise ValueError("Couldn't find proxies in DB")


def test_check_response():
    import time
    while True:
        r = requests.get(r"https://spb.cian.ru/novostrojki/")
        print(check_response(r))
        #time.sleep(0.1)


if __name__ == '__main__':
    test_check_response()
