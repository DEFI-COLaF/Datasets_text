import moliyé_util as m_utils
from lxml import etree
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import regex as re
import os


def get_local_files(folder):
    files = os.listdir(folder)
    files = [f"{folder}/{f}" for f in files]
    return files
def read_file(file):
    raw = ""
    with open(test_file) as f:
        raw = f.read()
    return raw

def parse_raw(raw):
    soup = BeautifulSoup(raw)
    header = soup.header.text
    body = soup.text.replace(header, "").strip()
    header_pairs = [line.split(" : ") for line in header.split("\n") if len(line.split(" : ")) == 2]
    metadata = {p[0].strip().lower(): p[1].strip() for p in header_pairs}
    return metadata, body

def adjust_metadata(metadata):
    metadata["publisher"] = metadata["newspaper"]
    metadata["date"] = metadata["publication date"]
    metadata["year"] = metadata["date"].split("-")[0]
    metadata["digital_publisher"] = metadata["provenance"]
    metadata["short_title"] = metadata["title"]
    metadata["period"] = metadata["year"]
    return metadata
def create_prose_poetry_xml(metadata, body, url):
    root = m_utils.create_tree_basis(metadata, url)
    text = root.find("text")
    xml_body = etree.SubElement(text, "body")
    body_lines = body.split("\n")
    for i, line in enumerate(body_lines):
        etree.SubElement(xml_body, "p", text=line, n=str(i))
    return root


transcription_folder = "/home/rdent/Datasets_text/Moliest/Transcribed_Local"
files = get_local_files(transcription_folder)
test_file = files[1]
raw = read_file(test_file)
metadata, body = parse_raw(raw)
url = "TO BE ADDED"

