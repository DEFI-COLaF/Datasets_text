import moliyé_util as m_utils
import classique2colaf
import td2colaf
from lxml import etree
from bs4 import BeautifulSoup
import regex as re
def create_colaf_header_corpus():
    colaf_header = f"""
          <teiHeader>
    <fileDesc>
        <titleStmt>
            <title type="main">Mo liest Corpus </title>
            <respStmt>
                <resp>Encoding</resp>
                <persName xml:id="RDENT">
                    <surname>Dent</surname>
                    <forename>Rasul</forename>
                    <idno type="orcid">0000-0002-8971-6175</idno>
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
            <publisher ref="https://colaf.huma-num.fr/">Corpus et Outils pour les Langues de France
                (COLaF)</publisher>
            <date when="2024-03-26"/>
            <availability>
                <licence target="https://creativecommons.org/licenses/by/4.0/"/>
            </availability>
        </publicationStmt>
        <sourceDesc>
            <bibl type="CorpusSource">
                <ptr target="https://colaf.huma-num.fr/"/>
                <title>Mo liest Corpus </title>
                <author>Rasul Dent</author>
                <publisher>CoLAF</publisher>
                <date when="2024"/>
            </bibl>
        </sourceDesc>
    </fileDesc>
    <profileDesc>
        <langUsage>
            <language ident="met-fra-std">
                <idno type="langue">met-fra-std</idno>
                <idno type="script">latin</idno>
                <name>Français</name>
                <location/>
            </language>
        </langUsage>
        <textClass>
            <keywords>
                <term type="supergenre" rend="spoken">Fiction</term>
                <term type="genre" rend="spoken-script">fiction-drama</term>
                <term type="motclef" rend="spoken-script-movie">fiction-drama</term>
            </keywords>
        </textClass>
    </profileDesc>
    <revisionDesc>
        <change when="2024-03-24" who="#RDENT">Génération du document</change>
    </revisionDesc>
    </teiHeader>
    """
    return colaf_header


def convert_play(url, source, raw_folder, colaf_folder):
    web_file = m_utils.get_html_content(url)
    tree = None
    metadata = {}
    if source == "theatre-classique":
        tree, metadata = classique2colaf.convert_tc_play(web_file, url)
    elif source == "theatre-documentation":
        tree, metadata = td2colaf.convert_td_play(web_file, url)

    with open(f"{raw_folder}/{url.split('/')[-1]}", mode="w") as f:
        f.write(web_file)
    out_filename = f"{colaf_folder}/{source}/{metadata['idno']}.xml"
    etree.ElementTree(tree).write(out_filename, pretty_print=True, encoding="UTF-8", xml_declaration=True)
    with open(out_filename, encoding="utf8") as f:
        return f.read(), metadata

def get_lines_of_interest(body, targets):
    soup = BeautifulSoup(body, "xml")
    matches = soup.find_all("sp", attrs={"who": targets})
    return [ str(m) for m in matches ]




def new_bibliography_entry(metadata):
    entry = etree.Element("bibl")
    #needs a :
    entry.set("xmlid", metadata["idno"])

    title = etree.SubElement(entry, "title")
    title.text = metadata["title"]

    author = etree.SubElement(entry, "author")
    author.text = metadata["author"]

    date = etree.SubElement(entry, "date")
    date.text = metadata["date"]
    return entry


def clean_superflous_attr(xml_string):
    anything_between_quotes = r'\".*?\"'
    stage_pattern = f'stage={anything_between_quotes}'
    part_pattern = f'part={anything_between_quotes}'
    syll_pattern = f'syll={anything_between_quotes}'
    for pattern in [stage_pattern, part_pattern, syll_pattern]:
        xml_string = re.sub(pattern, "", xml_string)
    return xml_string

def fix_ids(xml_string):
    xml_string = xml_string.replace("id=", "n=")
    xml_string = re.sub(r"xml:?n=", "xml:id=", xml_string)
    return xml_string

def fix_misc_errors(xml_string):
    xml_string = re.sub(" rte", "", xml_string)
    xml_string = re.sub("wtage", "stage", xml_string)
    xml_string = re.sub("note tyepe?", "note type", xml_string)
    #< poem type = "chanson" >

    pass

def corpus_xml_out(corpus, corpus_metadata, out_file):
    corpus_header = create_colaf_header_corpus()
    root = None
    root = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    xml_header = root.append(etree.fromstring(corpus_header))
    text = etree.SubElement(root, "text")

    corpus_front = etree.SubElement(text, "front")
    corpus_bib = etree.SubElement(corpus_front, "listBibl")
    corpus_group = etree.SubElement(text, "group")

    for play, metadata in zip(corpus, corpus_metadata):
        corpus_bib.append(new_bibliography_entry(metadata))

        idno = metadata["idno"]
        work_section = etree.SubElement(corpus_group, "text", n=idno)
        #may add a header but not necessary rn
        work_body = etree.SubElement(work_section, "body")
        for line in play:
            line = work_body.append(etree.fromstring(line))
    etree.ElementTree(root).write(out_file, pretty_print=True, encoding="UTF-8", xml_declaration=True)
    first_draft = ""
    with open(out_file, encoding="utf8") as f:
        first_draft = f.read()
    cleaned_draft = first_draft
    cleaned_draft = clean_superflous_attr(first_draft)
    cleaned_draft = fix_ids(cleaned_draft)
    with open(out_file, mode="w") as f:
        f.write(cleaned_draft)
def cycle_through_texts(texts_list, raw_folder=None, colaf_folder=None):
    df = pd.read_csv(texts_list)
    relevant = df.loc[df["Source"].isin(["theatre-classique", "theatre-documentation"])]
    #  |  df["Source"] ==  "theatre-documentation"
    sources = relevant["Source"]
    links = relevant["Link"]
    characters = relevant["Character"]
    characters = [c.upper().split(",") for c in characters]
    characters = [[c.strip() for c in s ] for s in characters]
    triplets = list(zip(sources, links, characters))
    corpus_metadata = []
    corpus = []
    #no zero
    n = 1
    for triplet in triplets:
        try:
            colaf_xml, metadata = convert_play(triplet[1], triplet[0], raw_folder, colaf_folder)
            body = m_utils.divide_xml_content(colaf_xml)[-1]
            lines = get_lines_of_interest(body, triplet[2])
            #section = prepare_play_extracts(metadata, lines, n)
            corpus.append(lines)
            corpus_metadata.append(metadata)
            n += 1
        except:
            print(f"unable to process{triplet[1]}")
    return corpus, corpus_metadata

def main():
    raw_folder = "xml/fr"
    colaf_folder = "dataset_colaf"
    source = "theatre-classique"
    m_utils.create_directory(raw_folder)
    m_utils.create_directory(colaf_folder)
    m_utils.create_directory(f"{raw_folder}/{source}")
    m_utils.create_directory(f"{colaf_folder}/{source}")

    project_folder= "/home/rdent/Datasets_text/Moliest"
    spreadsheet_name = "Historic_L2_and_Popular_French_Representations.csv"
    tc_texts_list = f"{project_folder}/{spreadsheet_name}"
    corpus, corpus_metadata = cycle_through_texts(tc_texts_list, raw_folder, colaf_folder)
    corpus_xml_out(corpus, corpus_metadata, "moliest_v04.xml")

main()