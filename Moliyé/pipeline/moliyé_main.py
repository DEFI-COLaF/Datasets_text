# -*- coding: utf-8 -*-
import os

import moliyé_util as m_util
import csv

import requests
from bs4 import BeautifulSoup
from lxml import etree as ET
import io
import regex as re
import transform_tc
import metadata_patterns

#Basic metadata should be easy to match using html


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





def test_prose():
    wiki_title = 'Une de perdue'
    wiki_link = "https://fr.wikisource.org/wiki/Une_de_perdue,_deux_de_trouv%C3%A9es/Tome_I"
    test_root = m_util.convert_one_wiki_prose(wiki_link, "000", "Moliyé")
    out = ET.tostring(test_root, encoding="unicode", pretty_print=True).replace("XMLID", "xml:id")
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
            file_text = m_util.read_file(file)
            updated = update_play(file_text, play)
            tree = ET.fromstring(updated.encode("utf8"))
            m_util.write_tree(tree, file)

def prep_work_extract(file_name, langs, level):
    file_text = m_util.read_file(file_name)
    metadata = extract_short_metadata(file_text)
    quotes = m_util.get_lines_of_interest(file_text, langs, level)
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



def main(list_file, recache=False):
    works = load_works(list_file)
    classique_works = [w for w in works if w["Source"] == "theatre-classique"]
    wikisource_works = [w for w in works if w["Source"] == "Wikisource"]
    src = "../source"
    fin = "../dataset_colaf"
    tc = "theatre_classique"
    wiki = "wikisource"
    raw_classique_folder = f"{src}/{tc}"
    classique_tei_folder = f"{fin}/{tc}"
    raw_wiki_folder = f"{src}/{wiki}"
    wiki_tei_folder = f"{fin}/{wiki}"
    if recache:
        folders = [raw_classique_folder, classique_tei_folder, raw_wiki_folder, wiki_tei_folder]
        m_util.prepare_folders(folders)
        transform_tc.save_tc_works(raw_classique_folder, classique_works)
        transform_tc.transform_classique(raw_classique_folder, classique_tei_folder)
    annotate_all_plays(classique_works, classique_tei_folder)
    m_util.convert_wiki_prose(wikisource_works, "Moliyé", wiki_tei_folder)

    prepped_extracts, all_langs = prep_all_plays(classique_works, classique_tei_folder)
    corpus_metadata = {"id" : "Moliyé_000", "title": "Moliyé", "author": "Rasul Dent",
                       "publisher": "CoLAF", "online_publisher": "CoLAF",  "permalien" : "https://colaf.huma-num.fr/",
                       "online_date": "2024"}
    corpus_tree = metadata_patterns.create_corpus_xml(corpus_metadata, all_langs, prepped_extracts)
    m_util.write_tree(corpus_tree, "../dataset_colaf/moliyé.xml")



list_file = "Moliyé_list.tsv"
main(list_file)


# works = load_works(list_file)
# classique_works = [w for w in works if w["Source"] == "theatre-classique"]
# raw_classique_folder = "theatre-classique"
# classique_tei_folder = "theatre_TEI"
# pource = classique_works[1]
# file_name = find_converted_file(pource["Title"], raw_classique_folder)



