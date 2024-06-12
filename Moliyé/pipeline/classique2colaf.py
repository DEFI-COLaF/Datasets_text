#sudo chown -R $(whoami) my-project-folder - pycharm fix
import moliyé_util as m_utils
from lxml import etree
from bs4 import BeautifulSoup
import regex as re

def get_tc_metadata(header, front):
    metadata = {}
    header_soup = BeautifulSoup(header, "xml")
    front_soup = BeautifulSoup(front, "xml")
    metadata["title"] = m_utils.remove_tags(str(header_soup.find("title")))
    metadata["short_title"] = re.sub("<.*?>", "", metadata["title"]).split(",")[0].replace(" ", "_")
    metadata["author"] = m_utils.remove_tags(str(header_soup.find("author")))
    metadata["publisher"] = m_utils.remove_tags(str(header_soup.find("publisher")))
    metadata["period"] =  m_utils.remove_tags(str(header_soup.find("periode")))
    raw_date = m_utils.remove_tags(str(front_soup.find("docDate")))

    metadata["date"] = m_utils.extract_date(front_soup)
    metadata["setting"] = m_utils.remove_tags(str(front_soup.find("set")))
    metadata["idno"] = m_utils.create_idno(metadata)
    metadata["digital_publisher"] = "https://www.theatre-classique.fr/"
    return metadata

#sometimes the <text> isn't recognized
def simple_xml_transfer(xml_header, front, body):
    root = None
    root = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    metadata = root.append(etree.fromstring(xml_header))
    text = etree.SubElement(root, "text")
    text.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "met-fra-std"
    text.append(etree.fromstring(front))
    text.append(etree.fromstring(body))
    return root, metadata

def convert_tc_play(web_file, url):
    header, play_text, front, body = m_utils.divide_xml_content(web_file)
    extracted_metadata = get_tc_metadata(header, front)
    colaf_header = m_utils.create_colaf_header_play(extracted_metadata, url)
    tree, _ = simple_xml_transfer(colaf_header, front, body)
    return tree, extracted_metadata

#add poem tag

url2 = "http://théâtre-documentation.com/content/les-trois-cousines-dancourt"

