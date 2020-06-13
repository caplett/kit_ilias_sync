import browser_cookie3
import requests
import time
import os
import shutil
import yaml
import threading
from queue import Queue, LifoQueue
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

cj = browser_cookie3.firefox()

with open("config.yml", "r") as config_file:
    cfg = yaml.load(config_file)

base_url = cfg["credentials"]["base_url"]
url = cfg["credentials"]["url"]

base_path = cfg["credentials"]["base_path"]

login_url = cfg["credentials"]["login_url"]
uname = cfg["credentials"]["uname"]
password = cfg["credentials"]["password"]

seen_urls = []

def create_browser(options, url, uname, password):
    print("Setup Browser")
    browser = webdriver.Firefox(options=options)
    browser.get(url)

    elem = browser.find_element_by_name("home_organization_selection")
    elem.click()

    time.sleep(1)

    elem_uname = browser.find_element_by_name("j_username")
    elem_uname.clear()
    elem_uname.send_keys(uname)

    elem_pw = browser.find_element_by_name("j_password")
    elem_pw.clear()
    elem_pw.send_keys(password)

    time.sleep(1)

    elem_login = browser.find_elements_by_name("_eventId_proceed")[1]
    elem_login.click()

    time.sleep(1)
    return browser


def download_file(dq):
    url, name = dq.get()
    print("New Download Started")
    local_filename = name
    with requests.get(url, stream=True) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)


def crawl_url(q, dq, browser, cj):
    next_url, path, expect_video = q.get()
    (f"Some test")

    global seen_urls

    if next_url in seen_urls:
        print(f"Skipping {next_url}. already seen")
    else:    
    
        print(f"Processing {path}")

        r_head = requests.get(base_url + next_url, cookies=cj, stream=True)
        if r_head.status_code != 200:
            print(f": error code {r_head.status_code} on: {base_url + next_url}")

        if r_head.headers["Content-Type"] != "application/pdf":

            if expect_video == False:
                r = requests.get(base_url + next_url, cookies=cj)
                soup = BeautifulSoup(r.text, "lxml")
                items = soup.find_all("a", class_="il_ContainerItemTitle")
                if items:
                    if not os.path.exists(path):
                        os.makedirs(path)

                list_containers = soup.find_all(class_="ilContainerListItemOuter")

                for container in list_containers:
                    # Check if opencast logo is on page
                    container_items = container.find_all(
                        "a", class_="il_ContainerItemTitle"
                    )
                    if container.find_all(title="Symbol Opencast"):

                        for item in container_items:
                            q.put(
                                [
                                    item.attrs["href"].replace(base_url, ""),
                                    path
                                    + "/"
                                    + item.string.replace(" ", "_").translate(
                                        {ord(i): None for i in '/,"{}()[]'}
                                    ),
                                    True,
                                ]
                            )
                    else:
                        for item in container_items:
                            q.put(
                                [
                                    item.attrs["href"].replace(base_url, ""),
                                    path
                                    + "/"
                                    + item.string.replace(" ", "_").translate(
                                        {ord(i): None for i in '/,"{}()[]'}
                                    ),
                                    False,
                                ]
                            )

            if expect_video == True:
                try:
                    browser.get(base_url + next_url)
                    time.sleep(20)
                    name = (
                        browser.title.replace(" ", "")
                        .replace(",", "")
                        .replace(".mp4", "")
                        .replace("/", "")
                        + ".mp4"
                    )
                    soup = BeautifulSoup(browser.page_source, "lxml")
                    items = soup.find_all("source")
                    if items:
                        video_url = items[0].attrs["src"]
                        if not os.path.isfile(path + "/" + name):
                            print(f"Downloading {path}/{name}")
                            dq.put([video_url, path + "/" + name])
                        else:
                            print(f"Skipped {path}/{name}")

                    items = soup.find_all("a", class_="btn btn-info")
                    if items:
                        if not os.path.exists(path):
                            os.makedirs(path)

                    for item in items:
                        if item.string == "Abspielen":
                            q.put(
                                [item.attrs["href"].replace(base_url, ""), path, True,]
                            )
                        else:
                            print("Skipped Download button")
                except selenium.common.exceptions.TimeoutException:
                    print(f"Timeout at {path}/{next_url}")
                    # q.put([next_url, path, True])


def crawl_worker_loop(q, dq, browser, cj):
    while True:
        print(f"{q.qsize()} Items in broser queue")
        crawl_url(q, dq, browser, cj)
        q.task_done()


def downloader_worker_loop(dq):
    while True:
        print(f"{dq.qsize()} Items in download queue")
        download_file(dq)
        dq.task_done()


options = Options()
options.headless = True

num_threads = cfg["credentials"]["num_threads"]
num_download_threads = cfg["credentials"]["num_download_threads"]
browsers = [
    create_browser(options, login_url, uname, password) for _ in range(num_threads)
]

browser_cookies = browsers[0].get_cookies()
login_cookies = dict()

for c in browser_cookies:
    login_cookies[str(c["name"])] = str(c["value"])

# q = Queue()
q = LifoQueue()
q.put([url, base_path, False])

dq = Queue()

# Check if user is logged in
r_login_check = requests.get(base_url + url, cookies=login_cookies)
soup_login_check = BeautifulSoup(r_login_check.text, "lxml")

login_check = soup_login_check.find_all("a", string="Anmelden")

if login_check:
    print("Not logged in")

else:
    for i in range(num_threads):
        worker = threading.Thread(
            target=crawl_worker_loop, args=(q, dq, browsers[i], login_cookies)
        )
        worker.setDaemon(True)
        worker.start()

    for i in range(num_download_threads):
        worker = threading.Thread(target=downloader_worker_loop, args=(dq,))
        worker.setDaemon(True)
        worker.start()

    # crawl_worker_loop(q, dq, browsers[0], cj)
    # downloader_worker_loop(dq)

    q.join()
    dq.join()
