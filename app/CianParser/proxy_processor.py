from collections import deque
import requests
import re
import random
from sqlalchemy.orm import Session
from fake_useragent import UserAgent

from app import db


PROXIES_SOURCE = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt"


def get_proxies_from_source():
    try:
        r = requests.get(PROXIES_SOURCE)
    except requests.ConnectionError:
        return []

    proxies = re.findall(r"\d+\.\d+\.\d+\.\d+:\d+", r.content.decode())
    random.shuffle(proxies)
    return proxies


def connect_to_cian(session: Session, query: db.models.Query, page: int = None) -> (requests.Response, None):
    proxies = deque(get_proxies_from_db(session))
    connection_attempts = 0
    while connection_attempts < 15:
        connection_attempts += 1
        current_proxy = proxies.popleft()
        try:
            url = query.url + '&page={}'.format(page) if page else query.url
            proxy = {'http': 'http://' + current_proxy.address}

            ua = UserAgent()
            html = requests.get(url,
                                headers={'User-Agent': ua.random},
                                proxies=proxy,
                                timeout=5)
            if check_response(html):
                return html

        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidProxyURL,
                requests.exceptions.ReadTimeout):
            current_proxy.available = False
            print(f"{current_proxy} is not available.")
            session.commit()


def check_response(response: requests.Response):
    if re.search(r'[cC]aptcha', response.content.decode()):
        raise requests.exceptions.InvalidProxyURL
    elif response.status_code == 200:
        return True
    elif response.status_code == 404:
        raise requests.exceptions.InvalidURL
    else:
        raise requests.exceptions.ConnectionError


def get_proxies_from_db(session: Session) -> list:
    proxies = session.query(db.models.ProxyList).\
        filter(db.models.ProxyList.available).\
        all()
    if proxies:
        return proxies
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
