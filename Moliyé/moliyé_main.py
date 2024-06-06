# -*- coding: utf-8 -*-
import os

import moliyé_util as m_util
import csv

import requests
from bs4 import BeautifulSoup
from lxml import etree as ET
import io
import regex as re

import metadata_patterns

#Basic metadata should be easy to match using html
def extract_wiki_metadata(wiki_soup, wiki_link, idno):
    metadata= {}
    metadata["title"] = wiki_soup.find("div", class_="headertemplate-title").text
    metadata["author"] = wiki_soup.find("span", itemprop="author").text
    metadata["publisher"] = wiki_soup.find("span", itemprop="publisher").text
    metadata["date"] = wiki_soup.find("time", itemprop="datePublished").text
    metadata["id"] = f"CRE_PROSE_{idno}"
    metadata["permalien"] = wiki_link
    return metadata


#Wikisource organizes documents into a main page with table of contents and several sections/chapters
def parse_wiki_table(wiki_soup, wiki_base):
    headers = wiki_soup.find_all("div", class_="tableItem")
    section_links = [wiki_base+ h.find("a")["href"] for h in headers if h.find("a")]
    return section_links


#a section corresponds roughly to a chapter but also includes things like prefaces
def parse_wiki_section(section_link):
    section_html = m_util.get_html_content(section_link)
    soup = BeautifulSoup(section_html)
    section_header = soup.find("h3").text
    section_body = soup.find("div", id="mw-content-text").text
    section_start = section_body.find(section_header) + len(section_header)
    section_body = section_body[section_start:].strip()
    section_header = section_header.upper().replace(".", ". ").strip()
    return [section_header, section_body]


#Parse the xml into metadata (dict) and sections (pairs of header + section/chapter body)
def parse_wiki_book(wiki_link, idno, wiki_base="https://fr.wikisource.org"):
    wiki_html = m_util.get_html_content(wiki_link)
    wiki_soup = BeautifulSoup(wiki_html, features="html")
    metadata = extract_wiki_metadata(wiki_soup, wiki_link, idno)
    section_links = parse_wiki_table(wiki_soup, wiki_base)
    sections = [parse_wiki_section(link) for link in section_links]
    return metadata, sections

#create a full TEI XML tree from the metadata and text body
def create_wiki_xml(metadata, sections):
    # TODO : need to calculate these from the texts
    langs_used = ['lou', 'met-fr']
    xml_metadata = metadata_patterns.create_metadata_xml(metadata, "prose", langs_used)
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


#Give basic paragraph structure to long form texts
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

def fix_tei_tag(soup):
    return str(soup).replace("tei:", "")
def tag_langs_play(file_text, roles_langs):
    soup = BeautifulSoup(file_text, features="xml")

    for role, lang in roles_langs.items():
        #For plays, tag at both <sp> and <p> levels for interoperability with prose
        matches = soup.find_all("sp", attrs={"who": role})
        for match in matches:
            match["xml:lang"] = lang
            lines = match.find_all("p")
            for line in lines:
                line["xml:lang"] = lang
    # inserts namespace unnecessarily
    out = fix_tei_tag(soup)
    return out

#insert sentence tags into prose
def tag_langs_prose(file_text, lines, lang):
    for line in lines:
        file_text = re.sub(f"{line}", fr'<s xml:lang="{lang}">{line}</s>', file_text)
    return file_text

def convert_one_wiki_prose(wiki_link, idno, collection_name):
    metadata, sections = parse_wiki_book(wiki_link, idno)
    metadata["collection"] = collection_name
    metadata["online_publisher"] = "Wikisource"
    metadata["digitizer"] = "TO BE UPDATED"
    metadata["online_date"] = "2024-05-30"
    wiki_xml = create_wiki_xml(metadata, sections)
    return wiki_xml

def convert_wiki_prose(wikisource_works, collection_name, wiki_tei_folder):
    converted_works = []
    for i, work in enumerate(wikisource_works):
        idno = f"{i + 1:0>3}"
        wiki_link = work["Link"]
        title = work["Title"]
        try:
            wiki_xml = convert_one_wiki_prose(wiki_link, idno, collection_name)
            converted_works.append(wiki_xml)
            out_name = f'{wiki_tei_folder}/{m_util.format_title(title)}.xml'
            m_util.write_tree(wiki_xml, out_name)
        except AttributeError as e:
            print(f"unable to treat {title}")
    return converted_works

def save_tc_works(raw_xml_folder, works):
    for work in works:
        title, link = work["Title"], work["Link"]
        html = m_util.get_html_content(link)
        with open(f"{raw_xml_folder}/{m_util.format_title(title)}.xml", mode="w") as f:
            f.write(html)

def create_multiple_person(item_multiple):
    metadata_list = []
    nom_list =[]
    for el in item_multiple:
        if " " in el.text or "[" in el.text or "Ô" in el.text or "'" in el.text or "," in el.text:
            nom = el.text
            nom = nom.replace(" ","_")
            nom = nom.replace("[", "")
            nom = nom.replace("Ô", "O")
            nom = nom.replace("'", "_")
            nom = nom.replace(",", "")
        else:
            nom = el.text
        if nom in " ".join(nom_list):
            nom = nom+"_2"
        else:
            nom_list.append(nom)
        metadata_list.append(f'<person xml:id="{nom}"><persName>{el.text}</persName></person>')
    xml_metadata = "".join(metadata_list)
    return xml_metadata


def parse_tree_metadata(tree):
    metadata = {}
    metadata["title"] = tree.find(".//title").text
    metadata["author"] = tree.find(".//author").text

    #new Colaf ID
    #metadata["id"] =  tree.find(".//idno").text
    metadata["date"] = tree.find(".//docDate").text
    publisher = tree.find(".//publisher")
    if publisher:
        metadata["publisher"]=publisher.text
    else:
        metadata["publisher"] = ""
    metadata["permalien"] = tree.find(".//permalien").text
    metadata["castItem"] = tree.findall(".//castItem/role")
    metadata["listperson_xml"]= create_multiple_person(metadata["castItem"])
    #TODO extract digitizer
    metadata["digitizer"] = "Gallica"
    return metadata

def transform_one_classique_play(xml_file, idno, collection="Moliyé"):
    tree = ET.parse(xml_file)
    metadata = parse_tree_metadata(tree)
    metadata["collection"] = collection
    metadata["online_publisher"] = "Theatre Classique"
    metadata["id"] = idno
    #TODO fix date
    metadata["online_date"] = "2024-05-30"
    # TODO fix permalien
    if type(metadata["permalien"]) == type(None):
        metadata["permalien"] = "https://www.theatre-classique.fr/"

    metadata_xml = metadata_patterns.create_metadata_xml(metadata,"theatre", ["met-fr"])
    xsl_file = ET.parse("html2tei.xsl")
    xsl_transform = ET.XSLT(xsl_file)
    transformed_xml = xsl_transform(tree).getroot()
    root = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    metadata_node = root.append(metadata_xml)
    text = root.append(transformed_xml)
    return root



def transform_classique(raw_dir, tei_dir):
    for i, file in enumerate(os.listdir(raw_dir)):
        try:
            #print(file)
            idno = f"CRE_TC_{i + 1:0>3}"
            xml_file = f"{raw_dir}/{file}"
            tree = transform_one_classique_play(xml_file, idno)
            out_name = f'{tei_dir}/{file}'
            m_util.write_tree(tree, out_name)
        except ET.XMLSyntaxError:
            print(f"Unable to parse {file}")
        except AttributeError:
            print(f"{file} has no text")


def test_prose():
    wiki_title = 'Une de perdue'
    wiki_link = "https://fr.wikisource.org/wiki/Une_de_perdue,_deux_de_trouv%C3%A9es/Tome_I"
    test_root = convert_one_wiki_prose(wiki_link, "000", "Moliyé")
    out= ET.tostring(test_root, encoding="unicode", pretty_print=True).replace("XMLID", "xml:id")
    ET.ElementTree(ET.fromstring(out)).write("dataset_colaf/test.xml", xml_declaration=True, encoding="UTF-8")


def find_converted_file(title, tei_folder):
    filename = f"{m_util.format_title(title)}.xml"
    if filename in os.listdir(tei_folder):
        return f"{tei_folder}/{filename}"
    else:

        print(f"{filename} not found")

def parse_play_lang_info(work_info):
    roles = work_info["Character"]
    roles = roles.upper().split(",")
    roles = [r.strip() for r in roles]

    langs = work_info["Lang"].split(",")
    #keep codes lowercase
    langs = [l.strip() for l in langs]

    roles_langs = {r: l for r, l in zip(roles, langs)}
    return roles_langs

def update_lang_usage_play(file_text, roles_langs, meta_langs):
    soup = BeautifulSoup(file_text, features="xml")
    lang_usage = soup.find("langUsage")
    #Don't add same language multiple times
    langs_used = meta_langs + list(set(roles_langs.values()))
    new_lang_usage = metadata_patterns.create_lang_usage_xml(langs_used)
    tag = BeautifulSoup(ET.tostring(new_lang_usage, pretty_print=True), features="xml")
    lang_usage.replace_with(tag)
    #turns = soup.find_all("sp", attrs={"xml:lang" :True })
    return fix_tei_tag(soup)


#Extract lines by language at either <sp> or <p> level
def get_lines_of_interest(file_text, langs, level="p"):
    soup = BeautifulSoup(file_text, features="xml")
    matches = soup.find_all(level, attrs={"xml:lang": langs})
    #inserts namespace unnecessarily
    return [ str(m).replace("tei:", "") for m in matches]

def read_file(filename, mode="r"):
    file_text = ""
    with open(filename, mode=mode) as f:
        file_text = f.read()
    return file_text
def extract_short_metadata(file_text):
    metadata = {}
    soup = BeautifulSoup(file_text, features="xml")
    titleStmt = soup.find("titleStmt")
    metadata["title"] = titleStmt.find("title").text
    metadata["author"] = titleStmt.find("author").text
    metadata["id"] = titleStmt.find("idno").text
    return metadata


def update_play(file_text, play_info):
    # TODO incorporate meta_langs
    meta_langs = ["met-fr"]
    roles_langs = parse_play_lang_info(play_info)
    # metadata = extract_short_metadata(file_text)
    tagged = tag_langs_play(file_text, roles_langs)
    updated = update_lang_usage_play(tagged, roles_langs, meta_langs)
    return updated


#Add language annotations (and possibly other kinds eventually
def annotate_all_plays(plays, folder):
    for play in plays:
        title = play["Title"]
        file = find_converted_file(title, folder)
        if file:
            file_text = read_file(file)
            updated = update_play(file_text, play)
            tree = ET.fromstring(updated.encode("utf8"))
            m_util.write_tree(tree, file)

def prep_work_extract(file_name, langs, level):
    file_text = read_file(file_name)
    metadata = extract_short_metadata(file_text)
    quotes = get_lines_of_interest(file_text, langs, level)
    return metadata,  [quotes]

def prep_all_plays(plays, folder):
    prepped_extracts = []
    all_langs = set()
    for play in plays:
        file_name = find_converted_file(play["Title"], folder)
        if file_name:
            roles_langs = parse_play_lang_info(play)
            langs = set(roles_langs.values())
            short_metadata, quote_groups = prep_work_extract(file_name, langs, "sp")
            all_langs = all_langs.union(langs)
            #Handle whitespace and repeated names in xml:ids
            roles_langs = {f"{m_util.format_title(role)}_{short_metadata['id']}" : lang for role, lang in roles_langs.items()}
            prepped_extracts.append([short_metadata, quote_groups, langs, roles_langs])
    return prepped_extracts, all_langs



def main(list_file):
    works = load_works(list_file)
    classique_works = [w for w in works if w["Source"] == "theatre-classique"]
    wikisource_works = [w for w in works if w["Source"] == "Wikisource"]
    raw_classique_folder = "theatre-classique"
    classique_tei_folder = "theatre_TEI"
    raw_wiki_folder = "wikisource"
    wiki_tei_folder = "wikisource_TEI"
    folders = [raw_classique_folder, classique_tei_folder, raw_wiki_folder, wiki_tei_folder]
    m_util.prepare_folders(folders)

    save_tc_works(raw_classique_folder, classique_works)
    transform_classique(raw_classique_folder, classique_tei_folder)
    annotate_all_plays(classique_works, classique_tei_folder)
    convert_wiki_prose(wikisource_works, "Moliyé", wiki_tei_folder)

    prepped_extracts, all_langs = prep_all_plays(classique_works, classique_tei_folder)
    corpus_metadata = {"id" : "Moliyé_000", "title": "Moliyé", "author": "Rasul Dent",
                       "publisher": "CoLAF", "online_publisher": "CoLAF",  "permalien" : "https://colaf.huma-num.fr/",
                       "online_date": "2024"}
    corpus_tree = metadata_patterns.create_corpus_xml(corpus_metadata, all_langs, prepped_extracts)
    m_util.write_tree(corpus_tree, "dataset_colaf/moliyé.xml")



list_file = "Moliyé_list.tsv"
main(list_file)

#
# works = load_works(list_file)
# classique_works = [w for w in works if w["Source"] == "theatre-classique"]
# classique_tei_folder = "theatre_TEI"
# pource = classique_works[1]
# file_name = find_converted_file(pource["Title"], classique_tei_folder)
# roles_langs = parse_play_lang_info(pource)
# langs = set(roles_langs.values())
# short_metadata, quote_groups = prep_work_extract(file_name, langs, "sp")
# play_extracts = metadata_patterns.create_extracts_xml(short_metadata, quote_groups, roles_langs)



