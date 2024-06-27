# -*- coding: utf-8 -*-
import os

import molyé_util as m_util


import requests
from bs4 import BeautifulSoup
from lxml import etree as ET
import io
import regex as re
import transform_tc as tc
import transform_wiki as wiki
import metadata_patterns
import annotation

import transform_hat_gcf as hat
import transform_gcr as gcr
import transform_gal_local as gal
import transform_rcf as rcf
import transform_lou as lou

def extract_short_metadata(file_text):
    metadata = {}
    soup = BeautifulSoup(file_text, features="xml")
    titleStmt = soup.find("titleStmt")
    metadata["title"] = titleStmt.find("title").text
    metadata["author"] = titleStmt.find("author").text
    metadata["id"] = titleStmt.find("idno").text
    metadata["date"] = soup.find("bibl", type="PrintSource").find("date")["when"]
    return metadata


def prep_work_extract(file_name, langs, level):
    file_text = m_util.read_file(file_name)
    metadata = extract_short_metadata(file_text)
    quotes = m_util.get_lines_of_interest(file_text, langs, level)
    return metadata,  [quotes]

def prep_all_plays(plays, folder):
    prepped_extracts = []
    all_langs = set()
    for play in plays:
        file_name = m_util.find_converted_file(play["Title"], folder)
        if file_name:
            roles_langs = annotation.parse_play_lang_info(play)
            langs = set(roles_langs.values())
            short_metadata, quote_groups = prep_work_extract(file_name, langs, "sp")
            all_langs = all_langs.union(langs)
            #Handle whitespace and repeated names in xml:ids
            roles_langs = {f"{m_util.format_title(role)}_{short_metadata['id']}" : lang for role, lang in roles_langs.items()}
            prepped_extracts.append([short_metadata, quote_groups, langs, roles_langs])
    return prepped_extracts, all_langs


#TODO fix tags in manually added works
def get_all_lines(soup, lang, primary_tags, secondary_tags):
    quotes = [q for q in soup.find_all(primary_tags) if not "xml:lang" in q.attrs or q["xml:lang"] != "met-fr"]
    for q in quotes:
        q["xml:lang"] = lang
    quotes = [str(q).replace("tei:", "") for q in quotes]
    secondary_quotes = [str(q).replace("tei:", "") for q in soup.find_all(secondary_tags)
                        if not "xml:lang" in q.attrs or q["xml:lang"] != "met-fr"]
    quotes += [q for q in secondary_quotes if q not in " ".join(quotes)]
    return quotes

#TODO finish
def prep_wiki_works(wiki_works, folder):
    prepped_extracts = []
    all_langs = set()
    for work in wiki_works:
        file_name = m_util.find_converted_file(work["Title"], folder)
        if file_name:
            langs = [work["Lang"]]
            file_text = m_util.read_file(file_name)
            soup = BeautifulSoup(file_text, features="xml")
            main_lang = soup.find("text")["xml:lang"]
            short_metadata = {}
            quote_groups = []
            if "met-fr" in main_lang:
                short_metadata, quote_groups = prep_work_extract(file_name, langs, "s")

            else:
                short_metadata = extract_short_metadata(file_text)
                quote_groups = [get_all_lines(soup, main_lang, ["p"], ["NA"])]

            langs = langs + [main_lang]
            all_langs = all_langs.union(set(langs))
            prepped_extracts.append([short_metadata, quote_groups, langs, None])

    return prepped_extracts, all_langs


def prep_misc_works(folder):
    prepped_extracts = []
    all_langs = set()
    file_names = [f"{folder}/{file}" for file in os.listdir(folder)]
    for file in file_names:
        file_text = m_util.read_file(file)
        soup = BeautifulSoup(file_text, features="xml")
        main_lang =  [soup.find("language")["ident"]]
        short_metadata = extract_short_metadata(file_text)
        all_langs = all_langs.union(set(main_lang))
        quote_groups = [get_all_lines(soup, main_lang, ["sp", "p"], ["lg"])]
        prepped_extracts.append([short_metadata, quote_groups, main_lang, None])
    return prepped_extracts, all_langs



def test_prose():
    wiki_title = 'Une de perdue'
    wiki_link = "https://fr.wikisource.org/wiki/Une_de_perdue,_deux_de_trouv%C3%A9es/Tome_I"
    test_root = wiki.convert_one_wiki_prose(wiki_link, "000", "Moliyé")
    out = ET.tostring(test_root, encoding="unicode").replace("XMLID", "xml:id")
    ET.ElementTree(ET.fromstring(out)).write("dataset_colaf/test.xml", xml_declaration=True, encoding="UTF-8",  pretty_print=True)

def arrange_timeline(file):
    soup = BeautifulSoup(open(file), features="xml")
    docs = soup.find_all("TEI")
    docs_sorted = sorted(docs, key=lambda x: x.find("bibl").find("date")["when"][:4])
    corpus_root = ET.Element("teiCorpus", xmlns="http://www.tei-c.org/ns/1.0")
    header = m_util.fix_tei_tag(soup.find("teiHeader"))
    corpus_root.append(ET.fromstring(header))
    for doc in docs_sorted:
        corrected = m_util.fix_tei_tag(doc)
        corpus_root.append(ET.fromstring(corrected))
        m_util.write_tree(corpus_root, file)

def main(list_file, recache=False):
    works = m_util.load_works(list_file)
    classique_works = [w for w in works if w["Source"] == "theatre-classique"]
    wikisource_works = [w for w in works if w["Source"] == "Wikisource"]
    src_dir = "../source"
    fin_dir = "../dataset_colaf"
    tc_dir = "theatre_classique"
    wiki_dir = "wikisource"
    raw_classique_folder = f"{src_dir}/{tc_dir}"
    classique_tei_folder = f"{fin_dir}/{tc_dir}"
    raw_wiki_folder = f"{src_dir}/{wiki_dir}"
    wiki_tei_folder = f"{fin_dir}/{wiki_dir}"
    if recache:
        folders = [raw_classique_folder, classique_tei_folder, raw_wiki_folder, wiki_tei_folder]
        m_util.prepare_folders(folders)
        tc.save_tc_works(raw_classique_folder, classique_works)
        tc.transform_classique(raw_classique_folder, classique_tei_folder)
    # annotation.annotate_all_plays(classique_works, classique_tei_folder)
    #
    # hat.main()
    # gal.main()
    # rcf.main()
    # wiki.convert_wiki_work(wikisource_works, "Molyé", wiki_tei_folder)
    # lou.main()
    prepped_extracts, all_langs = prep_all_plays(classique_works, classique_tei_folder)
    wiki_extracts, wiki_langs = prep_wiki_works(wikisource_works, wiki_tei_folder)
    misc_extracts, misc_langs = prep_misc_works("../dataset_colaf/misc_works")


    all_extracts = prepped_extracts + wiki_extracts + misc_extracts
    all_langs = all_langs.union(wiki_langs).union(misc_langs)

    print(all_langs)
    corpus_file_name = "../dataset_colaf/molyé.xml"
    corpus_metadata = {"id" : "Molyé_000", "title": "Molyé", "author": "Rasul Dent",
                       "publisher": "CoLAF", "online_publisher": "CoLAF",  "permalien" : "https://colaf.huma-num.fr/",
                       "online_date": "2024"}
    corpus_tree = metadata_patterns.create_corpus_xml(corpus_metadata, all_langs, all_extracts)
    m_util.write_tree(corpus_tree, corpus_file_name)
    arrange_timeline(corpus_file_name)

if __name__ == '__main__':
    list_file = "Molyé_list.tsv"
    main(list_file)
    m_soup = BeautifulSoup(open("..//dataset_colaf/molyé.xml"), features="xml")
    text = m_soup.text
    print(len(text.split()))

