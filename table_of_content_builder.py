#!/usr/bin/python3
#
# _*_ coding: utf-8
"""

@author: Aaron
"""
from TexSoup import TexSoup
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
import os
from lxml import etree
import sys
import argparse
from lxml import etree

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


def create_title(i):

    url = Request(f"{base}{i}")
    page = urlopen(url)
    # get url

    # get title and speaker
    soup = bs(page, "html.parser")
    tree = etree.HTML(str(soup))
    if int(year) > 2019:
        name = tree.xpath('//*[@id="author1"]/text()')
    else:
        name = tree.xpath('//*[@id="p1"]/text()')
    # speaker filter
    for k in name:
        name = str(name)
        if int(year) > 2011:
            name = k[2:]
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

    file_name = f"{name}---{title}"

    return file_name


# create string input for each talk
def createTexString(link_name):
    tex_string = ""
    fpath = os.getcwd()
    for fname in os.listdir(fpath):
        if link_name in fname:
            soup = TexSoup(open(f"{fpath}/{fname}"))
            title = list(soup.find_all("DocTitle"))
            author = list(soup.find_all("Author"))
            dir_name = f"{{/repository/{fname}}}"

            for i in author:
                k = i.args

            for i in title:
                v = i.args
            tex_string += f"  \\aosachapter{v}{{s:distsys}}{k}\n  \\input{dir_name}\n\n"
            print(tex_string)
    return tex_string


if __name__ == "__main__":
    readCommandLine()
    print("###################################start:")

# session list (##### WILL NEED TO UPDATE BASED ON CONFERENCE #########)
sessions = [
    "Saturday Morning Session",
    "Saturday Afternoon Session",
    "Priesthood Session",
    "Sunday Morning Session",
    "Sunday Afternoon Session",
    "General Relief Society Session",
]

# create final table of contents string and insert into tex file
def createContentTable(true_links, sessions):
    tex_string = ""
    n = 0
    for j in true_links:
        print("###########################:", j)
        session_string = "[]---"
        if session_string in str(j):
            tex_string += f" \\end{{multicols}}\n\n%-------------------------------------------------\n% {{{sessions[n]}}}\n%-------------------------------------------------\n\\part{{{sessions[n]}}}\n \\begin{{multicols}}{{2}}\n\n\n"
            n += 1
            print("session_string entered")
            continue
        else:
            print("else entered")
            link_name = str(j)
            get_tex = createTexString(link_name)
            tex_string += get_tex

    # built final input string
    full_tex = f"{tex_string}\n\n\\end{{multicols}}\n\n"

    # open and find line to replace
    toc_name = "t-general_conference--notepad.tex"
    fil = open(toc_name, "rt")
    data = fil.read()
    data = data.replace("\end{mulitcols}", full_tex)
    fil.close()
    # open and write data to toc file
    fil = open(toc_name, "wt")
    fil.write(data)
    fil.close()

    return


links = grab_conf()

if test:
    if count:
        num = int(count)
        links = links[:num]
    else:
        print("please enter count number for test")
        sys.exit()

true_links = []

for i in links:
    file_name = create_title(i)
    true_links.append(file_name)

createContentTable(true_links, sessions)

# delete last item from list(it's always a repeat value)
true_links.pop()
