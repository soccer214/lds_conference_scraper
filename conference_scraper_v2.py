#!/usr/bin/python3
"""
Created on Wed Jan 26

@author: Aaron
"""


from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
import sys
import argparse
from lxml import etree
import requests
import os


global base

base = "https://www.churchofjesuschrist.org/"

year = 0
month = 0
count = 0
test = None


def readCommandLine():
    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", type=str, help="year: -y four digit")
    parser.add_argument("-m", type=str, help="month: two digit")
    parser.add_argument("-t", type=str, required=False, help="test: -t True")
    parser.add_argument(
        "-c", type=str, required=False, help="count: -c digit, only valid in testing"
    )
    args = parser.parse_args()

    if args.y is None or args.m is None:
        raise argparse.ArgumentError(
            'Must input -y as year ("2020") and -m as month ("04", "10")'
        )
    global year, month, count, test
    # designate args to values
    year = args.y
    month = args.m
    count = args.c
    t_first = args.t
    if t_first:
        test = True
    else:
        test = False
    return


def grab_conf():
    # grab conference page
    url = Request(f"{base}/study/general-conference/{year}/{month}?lang=eng")
    html_page = urlopen(url)
    soup = bs(html_page, "html.parser")
    links = []

    # get all talk links
    for link in soup.findAll("a"):
        links.append(link.get("href"))

    # filter duplicates
    approved = ["?lang=eng"]
    links[:] = [url for url in links if any(sub in url for sub in approved)]

    return links[2:]


# scrape, filter, and store each file
def build_file(i, fpath):

    try:

        # get url
        url = f"{base}{i}"
        page = requests.get(url)

        # get title and speaker
        soup = bs(page.content, "html.parser")
        tree = etree.HTML(str(soup))
        if int(year) > 2019:
            name = tree.xpath('//*[@id="author1"]/text()')
        else:
            name = tree.xpath('//*[@id="p1"]/text()')

        # speaker filter
        for k in name:
            name = str(name)
            if int(year) > 2011:
                name = k[3:]
            else:
                name = k[:]
            name = name.replace("President ", "")
            name = name.replace("Elder ", "")
            name = name.replace("Bishop ", "")
            name = name.replace(" ", "_")
            name = name.replace("\xa0", "_")
            name = name.replace(".", "")
            name = name.lower()

        # title filter
        title = tree.xpath('//*[@id="title1"]/text()')
        for k in title:
            title = str(title)
            title = k[:]
            title = title.replace("'", "")
            title = title.replace(",", "")
            title = title.replace("?", "")
            title = title.replace("#", "")
            title = title.replace("=", "")
            title = title.replace("(", "")
            title = title.replace(")", "")
            title = title.replace("&", "")
            title = title.replace(";", "")
            title = title.replace(":", "")
            title = title.replace("-", "")
            title = title.replace('"', "")
            title = title.replace(
                " ",
                "_",
            )
            title = title.encode("ascii", "ignore")
            title = title.decode("utf-8")
            title = title.lower()

        if test:
            file_name = f"test---{name}---{title}"
            # c+=1
        else:
            file_name = f"{name}---{title}"

        # scrape data
        with open(f"{fpath}/{file_name}.html", "w") as file:
            file.write(str(soup))

        print(f"{file_name} done")

    except Exception as e:

        print(f"{file_name}-{e}!!!!!!!!!!!!!!!! Not Completed")

    return


# if a test run this definition first
def testScript(links, fpath):
    # check for count
    if count is None:
        print('when testing enter "-t True -c (number)"')
        sys.exit()

    num = int(count)
    print(f"############### WE ARE TESTING {count} FILES ########################")
    # designate list length
    links = links[:num]
    for i in links:
        build_file(i, fpath)

    print("test completed")
    sys.exit()
    return


def delete_file(fpath):
    for fname in os.listdir(fpath):
        if "[]---[]" in fname:
            os.remove(os.path.join(fpath, fname))

    return


# begin file
if __name__ == "__main__":
    readCommandLine()

# get links to all talks
links = grab_conf()


# file placement prep
fpath = os.getcwd()
curr_dir = os.path.basename(fpath)
print("NEW & IMPROVED PATH: ", fpath)

# building test files
if test:
    # check if count is filled in
    testScript(links, fpath)

# build real file
for i in links:
    build_file(i, fpath)

# delete extraneous files that may be picked up
delete_file(fpath)
