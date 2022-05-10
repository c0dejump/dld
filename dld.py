# -*- coding: utf-8 -*-

import requests
import sys
import argparse
from bs4 import BeautifulSoup
from config import *


requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


exclude_extension = [".jpg", ".png", ".jpeg", ".gif", "css", "svg"]


class check_file:

    def file_triage(self, req_link, s):
        #print(req_link.text)
        soup = BeautifulSoup(req_link.text, "html.parser")
        links = soup.find_all('a')
        if links:
            for l in links:
                link = l.get("href")
                #print(link)
                if "?C=" not in link and "wp-content" not in link and not any(e in link for e in exclude_extension):
                    print("\t\u251c {}{}".format(req_link.url, link))


class directory_structure:

    check_file = check_file()

    def check_link_content(self, url_link, s, dty):
        try:
            req_link = s.get(url_link, verify=False)
            if dty:
                self.search_file(url_link, s, req_link.text)
            else:
                check_file.file_triage(self, req_link, s)
        except:
            pass

    def search_file(self, url_link, s, content):
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all('a')
        if links:
            for l in links:
                link = l.get("href")
                if "/" in link and "wp-content" not in link:
                    file_link = "{}{}".format(url_link, link)
                    #print(file_link)
                    directory_structure().check_link_content(file_link, s, dty=False)
                elif "?C=" not in link and "wp-content" not in link and not any(e in link for e in exclude_extension):
                    print("\t\u251c {}{}".format(url_link, link))
    

    def structure_file(self, url, s, content):
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all('a')
        files_found = []
        if links:
            for l in links:
                link = l.get("href")
                if "?C=" not in link and "wp-content" not in link and not any(e in link for e in exclude_extension):
                    if not "/" in link:
                        files_found.append(link)
                if "/" in link and not "wp-content" in link and len(link) > 1:
                    url_link = "{}{}".format(url, link)
                    print(LINE)
                    print("\033[32m[D] {}\033[0m".format(url_link))
                    print(LINE)
                    directory_structure().check_link_content(url_link, s, dty=True)
        print(LINE)
        print("{} Check files".format(INFO))
        if files_found:
            print("\t\033[33mPotential files found: {}\033[0m\n".format(files_found))
            for ff in files_found:
                url_file = "{}{}".format(url, ff)
                req_file = requests.get(url_file, verify=False, allow_redirects=False)
                print("\t\u251c {} [{}b]".format(url_file, len(req_file.content)))
        else:
            print("{} Nothing file found".format(LESS))


def bf_dateFile(url, s):
    for file_number in range(1,13):
        if file_number < 10:
            file_number = "0{}".format(file_number)
        url_file = "{}{}".format(url, file_number)
        req_file = s.get(url_file, verify=False, allow_redirects=False)
        if req_file.status_code not in [403, 401, 503, 404, 301, 500, 302, 502]:
            print("{} Directory file is open: {} [{}]".format(PLUS, url_file, req_file.status_code))
            return True
        sys.stdout.write("\033[34m [i] {}\033[0m\r".format(url_file))
        sys.stdout.flush()


def bf_date(url, s, ds):
    dir_found = False
    for date in range(2000,2022):
        url_date = "{}{}/".format(url, date)
        req_date = s.get(url_date, verify=False, allow_redirects=False)
        if req_date.status_code not in [403, 401, 503, 404, 301, 500, 302, 502]:
            print("{} Directory date is open: {} [{}]".format(PLUS, url_date, req_date.status_code))
        else:
            bf_dateFile(url_date, s)
    if not dir_found:
        print("{} Nothing directory upload found".format(LESS))


def default_test(url, ds):
    s = requests.session()
    s.verify=False
    req = s.get(url, verify=False, allow_redirects=False)
    if req.status_code not in [403, 401, 503, 404, 301, 500, 302, 502] and not "Forbidden" in req.text:
        print("\n{} Directory listing is open: {} [{}]".format(PLUS, url, req.status_code))
        content = req.text
        if len(req.content) > 1:
            ds.structure_file(url, s, content)
        else:
            bf_date(url, s, ds)
    elif req.status_code in [403, 401] or "Forbidden" in req.text:
        print("\n{} Directory listing is forbidden [{}]".format(WARNING, req.status_code))
        if "wp" in url:
            print("{} Bruteforce started...".format(INFO))
            bf_date(url, s, ds)
    else:
        print("{} Directory return [{}]".format(INFO, req.status_code))
        print("{} Bruteforce started...".format(INFO))
        bf_date(url, s, ds)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="URL to scan [required]", dest='url')
    results = parser.parse_args()
                                     
    url = results.url

    ds = directory_structure()

    #url = "{}/wp-content/uploads/".format(url) if url[-1] != "/" else "{}wp-content/uploads/".format(url)
    default_test(url, ds)
