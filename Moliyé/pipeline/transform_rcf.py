import moliyé_util as m_util
import regex as re
import bs4 as BeautifulSoup
import xml.etree.ElementTree as ET
import metadata_patterns

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
                "id": "CRE_CRE_001", "collection" : "Moliyé",
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
    poems = m_util.read_wiki_poems(fables_src)
    return poems

def main():
    fables_link = "https://fr.wikisource.org/wiki/Fables_cr%C3%A9oles"
    deux = read_deux_textes()
    m_util.write_tree(deux, "deux_textes.xml")