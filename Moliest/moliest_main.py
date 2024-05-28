import moliest_util
import moliest_util as m_util
import transfo_TheatreClassique
import csv

import requests
from bs4 import BeautifulSoup
from lxml import etree
import xml.etree.ElementTree as ET

import regex as re


def create_prose_metadata_xml(metadata):
    metadata = f"""
        <teiHeader>
                <fileDesc>
                    <titleStmt>
                        <idno>{metadata["id"]}</idno>
                        <title type="main">{metadata["title"]}</title>
                        <respStmt>
                            <resp>Encoding</resp>
                            <persName xml:id="RDENT">
                                <surname>Dent</surname>
                                <forename>Rasul</forename>
                                <idno type="orcid">0000-0002-8971-6175</idno>
                            </persName>
                        </respStmt>
                        <respStmt>
                            <resp>Encoding</resp>
                            <persName xml:id="JJANES">
                                <surname>Janes</surname>
                                <forename>Juliette</forename>
                                <idno type="orcid">0000-0002-8971-6173</idno>
                            </persName>
                        </respStmt>                       
                        <principal>
                            <persName xml:id="BSAGOT">
                                <surname>Sagot</surname>
                                <forename>Benoît</forename>
                                <idno type="orcid">0000-0001-8957-9503</idno>
                            </persName>
                        </principal>
                        <funder>Inria</funder>
                    </titleStmt>
                    <publicationStmt>
                        <publisher ref="https://colaf.huma-num.fr/">Corpus et Outils pour les Langues de
                            France (COLaF)</publisher>
                        <date when="2024-03-25"/>
                        <availability>
                            <licence target="https://creativecommons.org/licenses/by/4.0/"/>
                        </availability>
                    </publicationStmt>
                    <sourceDesc>
                        <bibl type="printSource">
                            <ptr target="{metadata["permalien"]}"/>
                            <title>{metadata["title"]}</title>
                            <author>{metadata["author"]}</author>
                            <publisher>Gallica</publisher>
                            <date when="{metadata["date"]}"/>
                        </bibl>
                        <bibl type="digitalSource">
                            <ptr
                                target="{metadata["permalien"]}"/>
                            <title>{metadata["title"]}</title>
                            <author>{metadata["publisher"]}</author>
                            <publisher>Wikisource</publisher>
                            <date when="2024"/>
                        </bibl>
                    </sourceDesc>
                </fileDesc>
                <profileDesc>
                    <langUsage>
                        <language ident="met-fr">
                            <idno type="langue">met-fr</idno>
                            <idno type="script">latin</idno>
                            <name>Français</name>
                            <location><country>Paris</country></location>
                            <date when="{metadata["date"]}"/>
                        </language>
                    </langUsage>
                    <textClass>
                        <keywords>
                            <term type="supergenre" rend="spoken">Fiction</term>
                            <term type="genre" rend="spoken-script">fiction-drama</term>
                        </keywords>
                    </textClass>
                </profileDesc>
                <revisionDesc>
                    <change when="2024-03-24" who="#JJANES">Génération du document</change>
                </revisionDesc>
            </teiHeader>
        """
    return metadata


def save_tc_works(raw_xml_folder, works):
    for work in works:
        title, link = work["Title"], work["Link"]
        html = moliest_util.get_html_content(link)
        with open(f"{raw_xml_folder}/{title}.xml", mode="w") as f:
            f.write(html)
    transfo_TheatreClassique.main(raw_xml_folder)

def extract_wiki_metadata(wiki_soup, wiki_link, idno):
    metadata= {}
    metadata["title"] = wiki_soup.find("div", class_="headertemplate-title").text
    metadata["author"] = wiki_soup.find("span", itemprop="author").text
    metadata["publisher"] = wiki_soup.find("span", itemprop="publisher").text
    metadata["date"] = wiki_soup.find("time", itemprop="datePublished").text
    metadata["id"] = f"CRE_PROSE_{idno}"
    metadata["permalien"] = wiki_link
    metadata["listperson_xml"] = "NOT APPLICABLE"
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
def parse_wiki_book(wiki_link, idno, wiki_base="https://fr.wikisource.org"):
    wiki_html = moliest_util.get_html_content(wiki_link)
    wiki_soup = BeautifulSoup(wiki_html, "html")
    metadata = extract_wiki_metadata(wiki_soup, wiki_link, idno)
    section_links = parse_wiki_table(wiki_soup, wiki_base)
    sections = [parse_wiki_section(link) for link in section_links]
    return metadata, sections

def create_wiki_xml(metadata, sections):
    xml_metadata = create_prose_metadata_xml(metadata)
    root = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    applied_metadata = root.append(etree.fromstring(xml_metadata))
    text = etree.SubElement(root, "text")
    text.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "met-fra-std"
    body = etree.SubElement(text, "body")
    for i, section in enumerate(sections):
        section_header, section_body = section
        xml_section = etree.SubElement(body, "div", n=str(i + 1), type="chapter")
        xml_section_header = etree.SubElement(xml_section, "head", )
        xml_section_header.text = section_header
        paragraphs = split_into_paragraphs(section_body)
        for p in paragraphs:
            xml_paragraph = etree.SubElement(xml_section, "p")
            xml_paragraph.text = p
    return root

def split_into_paragraphs(long_text):
    paragraphs = long_text.split("\n")
    paragraphs = [p for p in paragraphs if len(p)]
    # long_text = re.sub(r"\n{2,}", "<PARAGRAPH_BREAK>", long_text)
    # paragraphs = long_text.split("<PARAGRAPH_BREAK>")
    return paragraphs


# def parse_wiki_html(wiki_html):
#     sections = []
#     for i, section_header in enumerate(headers[:-1]):
#         section_start = main.find(section_header) + len(section_header)
#         section_end = main.find(headers[i+1])
#         section_body = main[section_start:section_end]
#         sections.append([section_header, section_body])
#
#     last_header = headers[-1]
#     last_start = main.find(last_header) + len(last_header)
#     last_body = main[last_start:]
#     sections.append([last_header, last_body])
#     sections = [[header.upper(), body.strip()] for header, body in sections]
#     return sections
#
#

def load_works(list_file):
    works = []
    with open(list_file) as f:
        lines = csv.DictReader(f, delimiter="\t", quotechar='"')
        for line in lines:
            works.append(line)
    return works
list_file = "Moliyé_list.tsv"
works = load_works(list_file)

raw_xml_folder = "theatre-classique"
classique_works = [w for w in works if w["Source"] == "theatre-classique"]




raw_wiki_folder = "wikisource"
moliest_util.create_directory(raw_wiki_folder)

wiki_tei_folder = "wikisource_TEI"
moliest_util.create_directory(wiki_tei_folder)

wiki_title = 'Une de perdue'
wiki_link = "https://fr.wikisource.org/wiki/Une_de_perdue,_deux_de_trouv%C3%A9es/Tome_I"

wikisource_works = [w for w in works if w["Source"] == "Wikisource"]

def convert_wiki_prose(wikisource_works):
    for i, work in enumerate(wikisource_works):
        idno = f"{i + 1:0>3}"
        wiki_link = work["Link"]
        title = work["Title"]
        try:
            metadata, sections = parse_wiki_book(wiki_link, idno)
            wiki_xml = create_wiki_xml(metadata, sections)
            etree.ElementTree(wiki_xml).write(f'{wiki_tei_folder}/{title}.xml', pretty_print=True, encoding="UTF-8",
                                              xml_declaration=True)
        except AttributeError as e:
            print(f"unable to treat {title}")



def read_pdf_object(pdfReader):
    all_text = ""
    for page in pdfReader.pages:
        all_text = all_text + page.extract_text()
    return all_text

def extract_web_pdf(url):
    doc_obj = requests.get(url, headers = {'User-Agent': 'Me 2.0'})
    doc_bytes = doc_obj.content
    pdfReader = PyPDF2.PdfReader(io.BytesIO(doc_bytes), "rb")
    all_text = read_pdf_object(pdfReader)
    return all_text



# with open(f"{raw_wiki_folder}/{wiki_title}.html", mode="w") as f:
#     f.write(wiki_soup.body.prettify())

import PyPDF2

#probably will change to fuzzy matching
def get_rid_of_title(page_text, book_title):
    page_lines = page_text.split("\n")
    first_line = page_lines[0]
    first_line = re.sub(book_title.upper(), "", first_line)
    first_line = re.sub(r"\d+", "", first_line)
    page_lines[0] = first_line
    page_text = "\n".join(page_lines)
    return page_text
def fix_common_pdf_errors(page_text, book_title):
    page_text = re.sub("<<", "«", page_text)
    page_text = re.sub(">>", "»", page_text)
    page_text = re.sub(r" \.", r".", page_text)
    page_text = get_rid_of_title(page_text, book_title)
    return page_text

def identify_small_roman(line):
    romans = re.findall(r"C?L?I?X{0,3}V?I{0,3}\.?", line)
    return [r for r in romans if len(r)]

def identify_section_header(page_text):
    pass

pdf_file = open("Google_books/pdf/L_autre_monde.pdf", "rb")
pdf_reader = PyPDF2.PdfReader(pdf_file)
print(len(pdf_reader.pages))
test_page = pdf_reader.pages[23].extract_text()
print(fix_common_pdf_errors(test_page, "L'autre monde"))


