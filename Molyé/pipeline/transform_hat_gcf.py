import requests
import regex as re
from docx import Document
import io
from bs4 import BeautifulSoup
import molyé_util as m_util
from lxml import etree as ET


def cache_jeannot():
    url = "http://creoles.free.fr/Attente/Textes-anciens/Jeannot%20et%20Th.%20corrig%E92.doc"
    response = requests.get(url)
    raw = response.text
    start = raw.find("Dans")
    end = raw.find("\r\r\x13PAGE ")
    raw = raw[start:end]
    raw = re.sub(r"\n", "", raw)
    raw = re.sub(r"\xa0", " ", raw)
    clean = re.sub(r"\x02", "", raw)

    out_fname = "../source/misc_works/jeannot.xml"
    with open(out_fname, mode="w", encoding="utf8") as f:
        f.write(clean)

def cache_passion(passion_file):
    passion_url = "http://creoles.free.fr/Cours/passion.htm"
    response = requests.get(passion_url)
    raw = response.text
    text = BeautifulSoup(raw, features="xml").text
    with open(passion_file, mode="w", encoding="utf8") as f:
        f.write(text)

# def cache_triton():
#     link = "https://web.archive.org/web/20000917220151/http://www.ling.su.se/Creole/Archive/French-Martinique-1671.html"
#     response = requests.get(link, encoding="utf8")
#     raw = str(response.content)
#     start = raw.find("<!-- begin content -->")
#     end = raw.find("<!-- end content -->")
#     truncated = raw[start:end]
#     soup = BeautifulSoup(truncated, features="xml")
#     citations = soup.find_all("p")[:3]
#
#
#     info = soup.find("i").text
#     basic_tree = ET.Element("TEI")
#
#     h = ET.SubElement(basic_tree, "header")
#     h.text = soup.find("h2").text
#     text = ET.SubElement("")

def tei_passion(passion_file):
    text = m_util.read_file(passion_file)
    title = "La passion de Notre Seigneur selon St Jean en Langage Negre"
    first_header = "La passion de notre S. selon St Jean"
    second_header = "La Passion de Notre Seigneur selon St Jean\n(traduction de G. Hazaël-Massieux)"
    start_gcf = text.find(first_header)
    start_trad = text.find(second_header)
    intro = text[:start_gcf].strip()
    #skip some bad html
    intro  = intro[intro.find("Pour"):]
    gcf_text = text[:start_gcf:start_trad]
    trad = text[start_trad:]
    metadata = {
        "title": title,
        "author": "anonymous", "date": "1730~",
        "digitizer": "Guy Hazaël-Massieux and Marie- Christine Hazaël-Massieux",
        "publisher": "Etudes Créoles, vol.XVII, n° 2, 1994",
        "online_publisher": "Groupe Européen de Recherches en Langues Créoles",
        "id": "CRE_HAT_001", "collection": "Molyé",
        "permalien": "http://creoles.free.fr/Cours/passion.htm", "online_date": "2008"}


def main():
    cache_jeannot()
    cache_passion("../source/misc_works/passion.txt")


jeannot_file = "../source/misc_works/jeannot.txt"
jeannot_local = m_util.read_file(jeannot_file)
passion_file = "../source/misc_works/passion.txt"

if __name__ == '__main__':
    #main()
    cache_passion("../source/misc_works/passion.txt")