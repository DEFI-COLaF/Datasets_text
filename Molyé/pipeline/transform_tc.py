import molyé_util as m_util
import regex as re
from bs4 import BeautifulSoup
from lxml import etree as ET
import metadata_patterns
import os

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


def parse_tree_metadata(xml_file):
    soup = BeautifulSoup(open(xml_file), features="xml")
    metadata = {}
    metadata["title"] = soup.find("title").text
    metadata["author"]  = soup.find("author").text
    metadata["date"] = m_util.extract_date(soup.find("docDate"))
    #new Colaf ID
    #metadata["id"] =  tree.find(".//idno").text

    publisher = soup.find("publisher")
    if publisher:
        metadata["publisher"]=publisher.text
    else:
        metadata["publisher"] = ""
    metadata["permalien"] = soup.find("permalien").text
    metadata["castItem"] = soup.find_all("role")
    metadata["listperson_xml"]= create_multiple_person(metadata["castItem"])
    #TODO extract digitizer
    metadata["digitizer"] = "Gallica"
    return metadata

def transform_one_classique_play(xml_file, idno, collection="Moliyé"):
    #print(f"converting {xml_file} to CoLAF schema")
    metadata = parse_tree_metadata(xml_file)
    metadata["collection"] = collection
    metadata["online_publisher"] = "Theatre Classique"
    metadata["id"] = idno
    #TODO fix date
    metadata["online_date"] = "2024-05-30"
    # TODO fix permalien
    if type(metadata["permalien"]) == type(None):
        metadata["permalien"] = "https://www.theatre-classique.fr/"

    metadata_xml = metadata_patterns.create_metadata_xml(metadata,"theatre", ["met-fr"])
    tree = ET.parse(xml_file)
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
        except TypeError:
            print(f"{file} generated Type Error")
