import molyé_util as m_util
import transform_wiki as wiki
import annotation
import metadata_patterns
from bs4 import BeautifulSoup
from lxml import etree as ET

def main():
    list_file = "Molyé_list.tsv"
    works = m_util.load_works(list_file)
    gcr_works = [w for w in works if w["Lang"] == "gcr"]

    atipa = gcr_works[0]
    idno = "006"

    tree = wiki.convert_one_wiki_prose(atipa, idno, "Molyé")
    m_util.write_tree(tree, "../dataset_colaf/wikisource/Atipa.xml")

if __name__ == '__main__':
    main()