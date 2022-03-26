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
    links.pop()
    return links[2:]


# copy lines  in text
def copy_lines(filename, begin, end):
    with open(filename, "r") as f:
        lines = f.readlines()[begin + 1 : end]
        string = ""
        for i in lines:
            string += i
        string = dropFirstChar(string)
        return string


# get row index of filter in text file which happens twice
def getLocations(fil, start):
    locations = []
    with open(fil, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if start in line:
                locations.append(i)
    string = copy_lines(fil, locations[0], locations[1])
    return string


# DROP FIRST character of each line of text (comments)
def dropFirstChar(string):
    lines = string.split("\n")
    for i in range(len(lines)):
        lines[i] = lines[i][1:]
    return "\n".join(lines)


# replace characters in string
def sessionReplace(string, replace):
    string = string.replace("Saturday Morning Session", replace)
    return string


def talkReplace(string, title, author, dir_name):
    string = string.replace("TITLE", title)
    string = string.replace("AUTHOR", author)
    string = string.replace("/repository/FILE", dir_name)
    string = string.replace("{{", "{")
    string = string.replace("}}", "}")
    return string


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
def createTexString(talk_lines, link_name):
    tex_string = ""
    fpath = os.getcwd()
    for fname in os.listdir(fpath):
        if link_name in fname:
            soup = TexSoup(open(f"{fpath}/{fname}"))
            title = list(soup.find_all("DocTitle"))
            author = list(soup.find_all("Author"))
            dir_name = f"{{/repository/{fname}}}"

            for i in author:
                k = i.text
                k = "".join(k)

            for i in title:
                v = i.text
                v = "".join(v)

            tex_string += talkReplace(talk_lines, v, k, dir_name)
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
    # open and find line to replace
    toc_name = "../t-general_conference.tex"
    session_lines = getLocations(toc_name, "PART HEADER START>")
    session_end_lines = getLocations(toc_name, "PART HEADER END>")
    talk_lines = getLocations(toc_name, "CHAPTER ENTRY>")

    tex_string = ""
    n = 0
    first_time = True
    for j in true_links:
        print("###########################:", j)
        session_string = "[]---"
        if session_string in str(j):
            if first_time is True:
                tex_string += sessionReplace(session_lines, sessions[n])
                n += 1
                print("first time entered")
                first_time = False
                continue
            else:
                tex_string += session_end_lines
                n += 1
                print("session_string entered")
                continue
        else:
            print("else entered")
            link_name = str(j)
            get_tex = createTexString(talk_lines, link_name)
            tex_string += get_tex

    # built final input string
    full_tex = f"{tex_string}\n{session_end_lines}"

    # fil = open(toc_name, "rt")
    lookup = "<TOC START>"

    fil = open(toc_name, "rt")
    data = fil.read()
    data = data.replace(lookup, full_tex)
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
