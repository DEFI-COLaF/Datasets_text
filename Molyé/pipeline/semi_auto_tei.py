import os
from lxml import etree as ET
import bs4
import molyé_util as m_util
from bs4 import BeautifulSoup

def ignore_tag(turn, tag_name, lines, out_tag, soup):
    tag = turn.find(tag_name)
    if tag:
        new_special_tag = soup.new_tag(tag_name)
        out_tag.append(new_special_tag)
        new_special_tag.string = tag.text
        lines = lines[1:]
    return lines
def add_line_tags(turn, new_soup):
    new_tag = new_soup.new_tag(turn.name, attrs=turn.attrs)
    lines = [line for line in turn.text.strip().split("\n") if len(line)]
    lines = ignore_tag(turn, "head", lines, new_tag, new_soup)
    lines = ignore_tag(turn, "speaker", lines, new_tag, new_soup)
    for line in lines:
        line_tag = new_soup.new_tag("l")
        line_tag.string = line
        new_tag.append(line_tag)
    return new_tag


test_file = "/home/rdent/Datasets_text/Molyé/source/transcribed/poetry/testament_escossois.xml"
soup = BeautifulSoup(open(test_file), features="xml")
turns = soup.find_all("lg")


new_soup = BeautifulSoup()
new_text = new_soup.new_tag("text")
new_soup.append(new_text)
for turn in turns:
    new_tag = add_line_tags(turn, new_soup)
    new_text.append(new_tag)



out = ET.fromstring(str(new_soup))
m_util.write_tree(out, "/home/rdent/Datasets_text/Molyé/source/transcribed/poetry/testament_escossois2.xml")




