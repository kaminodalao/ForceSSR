import requests
import time
import bs4
import logging
import hashlib
import redis
import json
import os

from flask import Flask, request
from selenium import webdriver
from urllib.parse import urlparse

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
r = redis.Redis(host='127.0.0.1', port=6379)

WHITELIST = []
CHECK_DOMAIN = True

if os.getenv('DOMAINS') is not None:
    for domain in os.getenv('DOMAINS').split(','):
        if len(domain) > 0 and domain not in WHITELIST:
            WHITELIST.append(domain)

if os.getenv('DOMAINS') == '*':
    CHECK_DOMAIN = False


def record(url, method, status_code, client_ip, client_ua):
    text = "[%s]%s %s %s %s %s" % (time.strftime("%Y-%m-%d %H:%M:%S",
                                                 time.localtime()), url, method, status_code, client_ip, client_ua)
    print(text)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def load_page(path=""):
    url = request.url
    url_data = urlparse(url)
    if CHECK_DOMAIN and url_data.netloc not in WHITELIST:
        return "Request Error", 400
    url = url.replace(url_data.scheme, request.headers['X-Scheme'])
    hash = hashlib.md5(url.encode('utf8')).hexdigest()
    content = ""
    status_code = 200
    method = ""
    if r.exists(hash):
        cache = json.loads(r.get(hash).decode('utf8'))
        content = cache['content']
        status_code = cache['status_code']
        method = "cached"
    else:
        response = requests.head(url)
        if response.status_code != 200:
            content = ""
            status_code = response.status_code
            method = "http"
        elif response.headers['Content-Type'] == 'text/html':
            opt = webdriver.EdgeOptions()
            opt.add_argument("--no-sandbox")
            driver = webdriver.Edge(options=opt)
            driver.get(url)
            html = driver.find_element_by_xpath(
                "//*").get_attribute("outerHTML")
            driver.close()
            soup = bs4.BeautifulSoup(html, 'html.parser')
            content = soup.prettify()
            status_code = response.status_code
            method = "webview"
        else:
            response = requests.get(url)
            content = response.text
            status_code = response.status_code
            method = "http"

        r.set(hash, json.dumps({
            'content': content,
            'status_code': status_code
        }), ex=86400)

    record(url, method, status_code,
           request.headers['X-Real-IP'], request.headers['User-Agent'])

    return content, status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
