import regex as re
import os
from bs4 import BeautifulSoup
import metadata_patterns
import molyé_util as m_util
from lxml import etree as ET




def extract_metadata(soup):
    header = soup.find("header").text.strip()
    header_lines = [h.split(" : ") for h in header.split("\n")]
    metadata = {h[0].strip().lower(): h[1].strip() for h in header_lines}
    metadata["id"] = "FRA_FLA_000"
    metadata["collection"] = "Moliyé"
    metadata["permalien"] = metadata["relationship"]
    metadata["digitizer"] = metadata["source"]
    if metadata["newspaper"]:
        metadata["publisher"] = metadata["newspaper"]
    metadata["online_publisher"] = metadata["provenance"]
    metadata["online_date"] = metadata["online date"]
    metadata["date"] = metadata["publication date"]
    return metadata

def extract_text(soup):
    text = soup.find("text").text.strip()
    return text


#TODO update main language tags at creation time
def treat_local(local_file, work_type, langs_used, main_lang):
    text = ""
    with open(local_file) as f:
        text = f.read()
        soup = BeautifulSoup(text, features="lxml")
        metadata = extract_metadata(soup)
        root = metadata_patterns.create_tree_base(metadata, "prose", langs_used, main_lang=main_lang)
        body_node = m_util.get_et_node(root, "body")
        text = extract_text(soup)
        section_info = [metadata["title"], text]
        metadata_patterns.add_section(body_node, section_info, 1, work_type=work_type)
    return root
def main():
    local_folder = "../source/transcribed_gallica"
    out_folder = "../dataset_colaf/misc_works"
    files = os.listdir(local_folder)
    for file in files:
        print(file)
        full_file = f"{local_folder}/{file}"
        root = treat_local(full_file, "poetry", ["fra-deu"], "fra-deu")
        m_util.write_tree(root, f"{out_folder}/{file}")

if __name__ == '__main__':
    main()
