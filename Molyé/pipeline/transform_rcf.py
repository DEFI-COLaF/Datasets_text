import molyé_util as m_util
import regex as re
from bs4 import BeautifulSoup
from lxml import etree as ET
import metadata_patterns
import transform_wiki as wiki

#TODO handle sub-headings
def read_deux_textes():
    link = "https://creolica.net/Edition-de-deux-textes-religieux"
    source = m_util.get_html_content(link)
    start = "<p>[ms 24]</p>"
    end = '<hr class="spip" /></div>'
    start_i = source.find(start)
    end_i = source.find(end)
    content = source[start_i:end_i]
    content = re.sub(r"(&nbsp)", "", content)
    content = re.sub(r"<br>", "\n", content)
    content = re.sub(r"\b([DR]\.)", r"</p>\n<p>\1", content)
    content = re.sub(r"\n{2,}", "\n", content)
    content = re.sub(r"(</?)tr>", r"\1row>", content)

    content = m_util.remove_tag(content, "center")
    content = m_util.remove_tag(content, "hr")
    content = m_util.remove_tag(content, "sup")
    content = m_util.remove_tag(content, "a")

    content = m_util.remove_attrs(content, "h3")
    content = m_util.remove_attrs(content, "table")
    content = m_util.remove_attrs(content, "td")
    content = m_util.simple_tag_replace(content, "tr", "row")
    content = m_util.simple_tag_replace(content, "td", "cell")
    content = m_util.simple_tag_replace(content, "strong", "head")

    metadata = {"title" : "Profession de Foy, en jargon des Esclaves Nêgres » et « Petit Catechisme de l’Isle de Bourbon",
                "author" : "Philippe Caulier", "date": "1760~", "digitizer" : "Philip Baker and Annegret Bollée",
                "publisher" : "Creolica", "online_publisher" :  "Philip Baker and Annegret Bollée",
                "id": "CRE_RCF_001", "collection" : "Moliyé",
                "permalien" : "https://creolica.net/Edition-de-deux-textes-religieux", "online_date" : "2004"}

    tree = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")

    meta_xml = metadata_patterns.create_metadata_xml(metadata, "prose", ["rcf"])
    tree.append(meta_xml)
    text = ET.SubElement(tree, "text")
    body = ET.SubElement(text, "body")
    split_i = content.find("<h3")
    #profession
    body.append(ET.fromstring(f'<div type="chapter" n="1"> {content[:split_i]}</div>'))
    #catechisme
    body.append(ET.fromstring(f'<div type="chapter" n="2"> {content[split_i:]}</div>'))
    return tree


def read_fables(fables_link):
    fables_src = m_util.get_html_content(fables_link)


    metadata = {
        "title": "Fables créoles et Explorations dans l'intérieur de l'île Bourbon : esquisses africaines (Nouvelle édition)",
        "author": "Héry, Louis", "date": "1833", "digitizer": "Bibliothèque nationale de France, département Philosophie, histoire, sciences de l'homme, 4-LK11-2249",
        "publisher": "J. Rigal (Paris)", "online_publisher": "Wikisource",
        "id": "CRE_RCF_002", "collection": "Molyé",
        "permalien": "https://gallica.bnf.fr/ark:/12148/bpt6k5470315c/f21.item", "online_date": "2008"}
    poems = wiki.read_wiki_poems(fables_src)

    #There is French in the full book
    langs_used = ["rcf"]
    #TODO add poetry
    root = metadata_patterns.create_tree_base(metadata, "prose", langs_used, main_lang="rcf")
    body = m_util.get_et_node(root, "body")
    for i, poem in enumerate(poems):
        metadata_patterns.add_section(body, poem, i + 1, work_type="poetry")
    return root

def main():
    out_folder = "../dataset_colaf"
    fables_link = "https://fr.wikisource.org/wiki/Fables_cr%C3%A9oles"
    fables = read_fables(fables_link)
    deux = read_deux_textes()
    m_util.write_tree(deux, f"{out_folder}/misc_works/deux_textes.xml")
    m_util.write_tree(fables, f"{out_folder}/wikisource/fables_créoles.xml")

if __name__ == '__main__':
    main()