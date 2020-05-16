import os
import aiohttp

API_TOKEN = os.environ['RANDOM_HOME_BOT']

PROXY_AUTH = aiohttp.BasicAuth(login='kotovsky', password='C5efAGKhROFKSUBfpe6W3hm9iAMF6')
PROXY_URL = 'socks5://3.19.218.232:2323'
