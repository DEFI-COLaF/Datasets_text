import molyé_util as m_util
import regex as re
from bs4 import BeautifulSoup

import metadata_patterns




def extract_wiki_metadata(wiki_soup, wiki_link, idno):
    metadata= {}
    metadata["title"] = wiki_soup.find("div", class_="headertemplate-title").text
    metadata["author"] = wiki_soup.find("span", itemprop="author").text
    metadata["publisher"] = wiki_soup.find("span", itemprop="publisher").text
    metadata["date"] = wiki_soup.find(["span", "time"], itemprop="datePublished").text
    metadata["id"] = f"CRE_PROSE_{idno}"
    metadata["permalien"] = wiki_link
    metadata = {k.strip() : v.strip() for k, v in metadata.items()}
    return metadata


#Wikisource organizes documents into a main page with table of contents and several sections/chapters
def parse_wiki_table(wiki_soup, wiki_base):
    headers = wiki_soup.find_all("div", class_="tableItem")
    section_links = [wiki_base+ h.find("a")["href"] for h in headers if h.find("a")]
    return section_links


#a section corresponds roughly to a chapter but also includes things like prefaces
def parse_wiki_section(section_link):
    section_html = m_util.get_html_content(section_link)
    soup = BeautifulSoup(section_html, features="xml")
    section_header = soup.find("h3").text
    section_body = soup.find("div", id="mw-content-text").text
    section_start = section_body.find(section_header) + len(section_header)
    section_body = section_body[section_start:].strip()
    section_header = section_header.upper().replace(".", ". ").strip()
    return [section_header, section_body]


#Parse the xml into metadata (dict) and sections (pairs of header + section/chapter body)
def parse_wiki_book(wiki_link, idno, wiki_base="https://fr.wikisource.org"):
    wiki_html = m_util.get_html_content(wiki_link)
    wiki_soup = BeautifulSoup(wiki_html, features="xml")
    metadata = extract_wiki_metadata(wiki_soup, wiki_link, idno)
    section_links = parse_wiki_table(wiki_soup, wiki_base)
    sections = [parse_wiki_section(link) for link in section_links]
    return metadata, sections

def read_wiki_poems(source):
    soup = BeautifulSoup(source, features="xml")
    poems = soup.find_all("div", class_="poem")
    poems = [p.text.strip() for p in soup.find_all("div", class_="poem")]
    #title is first line, body is everything else
    titles = [p.split("\n")[0] for p in poems]
    bodies = ["\n".join(p.split("\n")[1:]) for p in poems]
    sections = list(zip(titles, bodies))
    return sections



#create a full TEI XML tree from the metadata and text body
def create_wiki_xml(metadata, sections, work_type, langs_used, main_lang):
    # TODO : need to calculate these from the texts
    root = metadata_patterns.create_tree_base(metadata, work_type, langs_used, main_lang=main_lang)
    body = m_util.get_et_node(root, "body")
    for i, section in enumerate(sections):
        metadata_patterns.add_section(body, section, i + 1, work_type)
    return root


def additional_metadata(metadata, collection_name):
    metadata["collection"] = collection_name
    metadata["online_publisher"] = "Wikisource"
    metadata["digitizer"] = "TO BE UPDATED"
    metadata["online_date"] = "2024-05-30"
    return metadata

def convert_one_wiki_prose(work_info, idno, collection_name):
    link = work_info["Link"]
    target_langs = [l.strip() for l in work_info["Lang"].split(", ")]
    meta_lang = work_info["Metalang"]
    all_langs = list(set(target_langs + [meta_lang]))
    metadata, sections = parse_wiki_book(link, idno)
    metadata = additional_metadata(metadata, collection_name)
    wiki_xml = create_wiki_xml(metadata, sections, "prose", all_langs, main_lang=meta_lang)
    return wiki_xml


def convert_wiki_work(wikisource_works, collection_name, wiki_tei_folder, work_type="prose"):
    converted_works = []
    for i, work in enumerate(wikisource_works):
        idno = f"{i + 1:0>3}"
        wiki_link = work["Link"]
        title = work["Title"]
        wiki_xml = ""
        try:
            if work_type =="prose":
                wiki_xml = convert_one_wiki_prose(work, idno, collection_name)
            elif work_type == "poetry":
                pass
            converted_works.append(wiki_xml)
            out_name = f'{wiki_tei_folder}/{m_util.format_title(title)}.xml'
            m_util.write_tree(wiki_xml, out_name)
        except AttributeError as e:
            print(f"unable to treat {title}")
    return converted_works


