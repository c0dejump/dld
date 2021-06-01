# -*- coding: utf-8 -*-

import requests
import sys
import argparse
import sys
from bs4 import BeautifulSoup


requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)



class check_file:

    def file_triage(self, req_link, s):
        #print(req_link.text)
        exclude_extension = [".jpg", ".png", "jpeg", "gif"]
        soup = BeautifulSoup(req_link.text, "html.parser")
        links = soup.find_all('a')
        if links:
            for l in links:
                link = l.get("href")
                #print(link)
                if "?C=" not in link and "wp-content" not in link and not any(e in link for e in exclude_extension):
                    print("{}{}".format(req_link.url, link))


class directory_structur:

    check_file = check_file()

    def check_link_content(self, url_link, s, dty):
        req_link = s.get(url_link, verify=False)
        if dty:
            directory_structur().search_file(url_link, s, req_link.text)
        else:
            check_file.file_triage(self, req_link, s)


    def search_file(self, url_link, s, content):
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all('a')
        if links:
            for l in links:
                link = l.get("href")
                if "/" in link and "wp-content" not in link:
                    file_link = "{}{}".format(url_link, link)
                    #print(file_link)
                    directory_structur().check_link_content(file_link, s, dty=False)
    

    def structure_file(self, url, s, content):
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all('a')
        if links:
            for l in links:
                link = l.get("href")
                if "/" in link and not "wp-content" in link:
                    url_link = "{}{}".format(url, link)
                    print("==========")
                    print(url_link)
                    print("==========")
                    directory_structur().check_link_content(url_link, s, dty=True)


def bf_dateFile(url, s):
    for file_number in range(0,13):
        url_file = "{}{}".format(url, file_number)
        req_file = s.get(url_file, verify=False, allow_redirects=False)
        if req_file.status_code not in [403, 401, 503, 404, 301, 500, 302]:
            print("[+] wp-upload directory file is open: {} [{}]".format(url_file, req_file.status_code))
            return True


def bf_date(url, s, ds):
    dir_found = False
    for date in range(2000,2022):
        url_date = "{}{}/".format(url, date)
        req_date = s.get(url_date, verify=False, allow_redirects=False)
        if req_date.status_code not in [403, 401, 503, 404, 301, 500, 302]:
            print("[+] wp-upload directory date is open: {} [{}]".format(url_date, req_date.status_code))
        else:
            bf_dateFile(url_date, s)
    if not dir_found:
        print("[-] Nothing directory upload found ")


def default_test(url, ds):
    s = requests.session()
    s.verify=False
    req = s.get(url, verify=False, allow_redirects=False)
    if req.status_code not in [403, 401, 503, 404, 301, 500, 302]:
        print("[+] wp-upload directory is open: {} [{}]".format(url, req.status_code))
        content = req.text
        ds.structure_file(url, s, content)
    elif req.status_code in [403, 401]:
        print("[!] wp-upload directory is forbidden [{}]".format(req.status_code))
        bf_date(url, s, ds)
    else:
        bf_date(url, s, ds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="URL to scan [required]", dest='url')
    parser.add_argument("-t", help="Number of threads to use for URL Fuzzing. \033[32mDefault: 20\033[0m", dest='thread', type=int, default=20, required=False)
    results = parser.parse_args()
                                     
    url = results.url
    thread = results.thread

    ds = directory_structur()

    url = "{}/wp-content/uploads/".format(url) if url[-1] != "/" else "{}wp-content/uploads/".format(url)
    default_test(url, ds)
