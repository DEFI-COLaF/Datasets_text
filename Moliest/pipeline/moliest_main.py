import os

import moliest_util
import moliest_util as m_util
import transfo_TheatreClassique
import csv

import requests
from bs4 import BeautifulSoup
from lxml import etree as ET
import io
import regex as re

import metadata_patterns

import glob
def clear_folders(folders):
    for folder in folders:
        files = glob.glob(f"{folder}/*")
        for file in files:
            os.remove(file)
def create_folders(folders):
    for folder in folders:
        moliest_util.create_directory(folder)

def format_title(title_string):
    title_string=title_string.strip()
    title_string = re.sub(r"\W", "_", title_string)
    title_string = re.sub(r"_{2,}", "_", title_string)
    return title_string

def extract_wiki_metadata(wiki_soup, wiki_link, idno):
    metadata= {}
    metadata["title"] = wiki_soup.find("div", class_="headertemplate-title").text
    metadata["author"] = wiki_soup.find("span", itemprop="author").text
    metadata["publisher"] = wiki_soup.find("span", itemprop="publisher").text
    metadata["date"] = wiki_soup.find("time", itemprop="datePublished").text
    metadata["id"] = f"CRE_PROSE_{idno}"
    metadata["permalien"] = wiki_link
    return metadata

def parse_wiki_table(wiki_soup, wiki_base):
    headers = wiki_soup.find_all("div", class_="tableItem")
    section_links = [wiki_base+ h.find("a")["href"] for h in headers if h.find("a")]
    return section_links


#a section corresponds roughly to a chapter but also includes things like prefaces
def parse_wiki_section(section_link):
    section_html = moliest_util.get_html_content(section_link)
    soup = BeautifulSoup(section_html)
    section_header = soup.find("h3").text
    section_body = soup.find("div", id="mw-content-text").text
    section_start = section_body.find(section_header) + len(section_header)
    section_body = section_body[section_start:].strip()
    section_header = section_header.upper().replace(".", ". ").strip()
    return [section_header, section_body]


#Parse the xml into metadata (dict) and sections (pairs of header + section/chapter body)
def parse_wiki_book(wiki_link, idno, wiki_base="https://fr.wikisource.org"):
    wiki_html = moliest_util.get_html_content(wiki_link)
    wiki_soup = BeautifulSoup(wiki_html, "html")
    metadata = extract_wiki_metadata(wiki_soup, wiki_link, idno)
    section_links = parse_wiki_table(wiki_soup, wiki_base)
    sections = [parse_wiki_section(link) for link in section_links]
    return metadata, sections

#create a full TEI XML tree from the metadata and text body
def create_wiki_xml(metadata, sections):
    # TODO : need to calculate these from the texts
    langs_used = ['lou', 'met-fr']
    xml_metadata = metadata_patterns.create_prose_metadata_xml(metadata, langs_used)
    root = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    applied_metadata = root.append(xml_metadata)
    text = ET.SubElement(root, "text")
    text.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "met-fra-std"
    body = ET.SubElement(text, "body")
    for i, section in enumerate(sections):
        section_header, section_body = section
        xml_section = ET.SubElement(body, "div", n=str(i + 1), type="chapter")
        xml_section_header = ET.SubElement(xml_section, "head", )
        xml_section_header.text = section_header
        paragraphs = split_into_paragraphs(section_body)
        for p in paragraphs:
            xml_paragraph = ET.SubElement(xml_section, "p")
            xml_paragraph.text = p
    return root

def split_into_paragraphs(long_text):
    paragraphs = long_text.split("\n")
    paragraphs = [p for p in paragraphs if len(p)]
    # long_text = re.sub(r"\n{2,}", "<PARAGRAPH_BREAK>", long_text)
    # paragraphs = long_text.split("<PARAGRAPH_BREAK>")
    return paragraphs

def load_works(list_file):
    works = []
    with open(list_file) as f:
        lines = csv.DictReader(f, delimiter="\t", quotechar='"')
        for line in lines:
            works.append(line)
    return works

def convert_one_wiki_prose(wiki_link, idno, collection_name):
    metadata, sections = parse_wiki_book(wiki_link, idno)
    metadata["collection"] = collection_name
    metadata["online_publisher"] = "Wikisource"
    metadata["digitizer"] = "TO BE UPDATED"
    metadata["online_date"] = "2024-05-30"
    wiki_xml = create_wiki_xml(metadata, sections)
    return wiki_xml
def convert_wiki_prose(wikisource_works, collection_name):
    converted_works = []
    for i, work in enumerate(wikisource_works):
        idno = f"{i + 1:0>3}"
        wiki_link = work["Link"]
        title = work["Title"]
        try:
            wiki_xml = convert_one_wiki_prose(wiki_link, idno, collection_name)
            converted_works.append(wiki_xml)
            out = ET.tostring(wiki_xml, encoding="unicode", pretty_print=True).replace("XMLID", "xml:id")
            ET.ElementTree(ET.fromstring(out)).write(f"{wiki_tei_folder}/{format_title(title)}.xml",
                                                     xml_declaration=True, encoding="UTF-8")
        except AttributeError as e:
            print(f"unable to treat {title}")
    return converted_works

def save_tc_works(raw_xml_folder, works):
    for work in works:
        title, link = work["Title"], work["Link"]
        html = moliest_util.get_html_content(link)
        with open(f"{raw_xml_folder}/{format_title(title)}.xml", mode="w") as f:
            f.write(html)


def transform_classique(raw_dir, tei_dir):
    for file in os.listdir(raw_dir):
        try:
            #print(file)
            xml_file = f"{raw_dir}/{file}"
            tree = ET.parse(xml_file)
            metadata_dict = transfo_TheatreClassique.parse_tree_metadata(tree)
            metadata_string = transfo_TheatreClassique.create_metadata_xml(metadata_dict)
            xsl_file = ET.parse("html2tei.xsl")
            xsl_transform = ET.XSLT(xsl_file)
            transformed_xml = xsl_transform(tree).getroot()
            root = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
            metadata = root.append(ET.fromstring(metadata_string))
            text = root.append(transformed_xml)
            ET.ElementTree(root).write(f'{tei_dir}/{file}', pretty_print=True, encoding="UTF-8",
                                       xml_declaration=True)
        except ET.XMLSyntaxError:
            print(f"Unable to parse {file}")
        except AttributeError:
            print(f"{file} has no text")




list_file = "Moliyé_list.tsv"
works = load_works(list_file)
classique_works = [w for w in works if w["Source"] == "theatre-classique"]
wikisource_works = [w for w in works if w["Source"] == "Wikisource"]

raw_classique_folder = "theatre-classique"
classique_tei_folder = "theatre_TEI"
raw_wiki_folder = "wikisource"
wiki_tei_folder = "wikisource_TEI"
folders = [raw_classique_folder, classique_tei_folder, raw_wiki_folder, wiki_tei_folder]
create_folders(folders)
clear_folders(folders)


save_tc_works(raw_classique_folder, classique_works)
#transform_classique(raw_classique_folder, classique_tei_folder)
convert_wiki_prose(wikisource_works, "Moliyé")


wiki_title = 'Une de perdue'
wiki_link = "https://fr.wikisource.org/wiki/Une_de_perdue,_deux_de_trouv%C3%A9es/Tome_I"
test_root = convert_one_wiki_prose(wiki_link, "000", "Moliyé")
out= ET.tostring(test_root, encoding="unicode", pretty_print=True).replace("XMLID", "xml:id")
ET.ElementTree(ET.fromstring(out)).write("dataset_colaf/test.xml", xml_declaration=True, encoding="UTF-8")







