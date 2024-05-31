from lxml import etree as ET
from lxml.builder import ElementMaker

fra_ger_meta = {"ident" : "fra-deu",
            "usage" : "XX",
            "script": "Latin",
            "lang_name" : "Germanic Baragouin"}

met_fra_meta = {"ident" : "met-fr",
            "usage" : "XX",
            "script": "Latin",
            "lang_name" : "French of Metropolitan France"}

lou_meta = {"ident" : "lou",
            "usage" : "XX",
            "script": "Latin",
            "lang_name" : "Louisiana Creole"}

ALL_LANGS_META = {"lou" : lou_meta,
              "met-fr" : met_fra_meta}

rasul_meta = {"xml:id" :"RDENT",
              "surname": "Dent",
              "forename" : "Rasul",
              "resp": "Encoding",
              "orcid": "0009-0004-1032-1745"}


juliette_meta = {"xml:id" :"JJANES",
              "surname": "Janes",
              "forename" : "Juliette",
              "resp": "Encoding",
              "orcid": "0000-0002-8971-6173"}


benoit_meta = {"xml:id" :"BSAGOT",
              "surname": "Sagot",
              "forename" : "Benoît",
              "resp": "Principal",
              "orcid": "0000-0001-8957-9503"}

ALL_PERSONS_META = {"RDENT" : rasul_meta,
                    "JJANES" : juliette_meta,
                    "BSAGOT" : benoit_meta}

def create_pers_name(person_meta):
    pers_name = ET.Element("persName", XMLID=person_meta["xml:id"])
    surname = ET.SubElement(pers_name, "surname")
    surname.text = person_meta["surname"]
    forename = ET.SubElement(pers_name, "forename")
    forename.text = person_meta["forename"]

    idno = ET.SubElement(pers_name, "idno", type="orcid")
    idno.text = person_meta["orcid"]
    return pers_name
def create_resp_statement(person_meta):
    respStmt = ET.Element("respStmt")
    resp = ET.SubElement(respStmt, "resp")
    resp.text = person_meta["resp"]
    pers_name = create_pers_name(person_meta)
    respStmt.append(pers_name)
    return respStmt

def create_principal_statement(person_meta):
    principal = ET.Element("principal")
    pers_name = create_pers_name(person_meta)
    principal.append(pers_name)
    return principal


def create_title_statement_xml(metadata, encoders=["RDENT", "JJANES"], principals=["BSAGOT"]):
    titleStmt = ET.Element("titleStmt")

    idno = ET.SubElement(titleStmt, "idno")
    idno.text = metadata["id"]

    title = ET.SubElement(titleStmt, "title", type="main")
    title.text = metadata["title"]

    collection = ET.SubElement(titleStmt, "title", type="collection")
    collection.text = metadata["collection"]

    author = ET.SubElement(titleStmt, "author")
    author.text = metadata["author"]

    for encoder in encoders:
        encoder_resp = create_resp_statement(ALL_PERSONS_META[encoder])
        titleStmt.append(encoder_resp)
    for principal in principals:
        principalStmt = create_principal_statement(ALL_PERSONS_META[principal])
        titleStmt.append(principalStmt)

    funder = ET.SubElement(titleStmt, "funder")
    funder.text = "Inria"
    return titleStmt


def create_publisher_xml():
    root = ET.Element("publicationStmt")
    publisher = ET.SubElement(root, "publisher", ref="https://colaf.huma-num.fr")
    publisher.text = "Corpus et Outils pour les Langues de France (COLaF)"
    date = ET.SubElement(root,"date", when="2024-05-30")
    availability = ET.SubElement(root, "availability")
    licence = ET.SubElement(availability, "licence", target="https://creativecommons.org/licenses/by/4.0/")
    return root


def create_source_desc_xml(metadata):
    root = ET.Element("sourceDesc")
    print_bibl = ET.SubElement(root, "bibl", type="PrintSource")
    #TODO
    print_ptr = ET.SubElement(print_bibl, "ptr", target=metadata["permalien"])

    print_title = ET.SubElement(print_bibl, "title")
    print_title.text = metadata["title"]

    print_author = ET.SubElement(print_bibl, "author")
    print_author.text = metadata["author"]

    print_publisher = ET.SubElement(print_bibl, "publisher")
    print_publisher.text = metadata["digitizer"]
    print_date = ET.SubElement(print_bibl, "date", when=metadata["date"])

    corpus_bibl = ET.SubElement(root, "bibl", type="CorpusSource")
    #TODO
    corpus_ptr = ET.SubElement(corpus_bibl, "ptr", target=metadata["permalien"])

    corpus_title = ET.SubElement(corpus_bibl, "title")
    corpus_title.text = metadata["title"]

    corpus_author = ET.SubElement(corpus_bibl, "author")
    corpus_author.text = metadata["author"]

    corpus_publisher = ET.SubElement(corpus_bibl, "publisher")
    corpus_publisher.text = metadata["online_publisher"]
    corpus_date = ET.SubElement(corpus_bibl, "date", when=metadata["online_date"])
    return root

def create_file_desc(metadata):
    file_desc = ET.Element("fileDesc")
    file_desc.append(create_title_statement_xml(metadata))
    file_desc.append(create_publisher_xml())
    file_desc.append(create_source_desc_xml(metadata))

    extent = ET.SubElement(file_desc, "extent")
    extent.text = "TO BE DEFINED"
    return file_desc

def create_lang_xml(lang_meta):
    lang_tree = ET.Element("language", ident=lang_meta["ident"])
    langue = ET.SubElement(lang_tree, "idno", type="langue")
    langue.text = lang_meta["ident"]

    script = ET.SubElement(lang_tree, "idno", type="script")
    script.text = lang_meta["script"]

    name = ET.SubElement(lang_tree, "name")
    name.text = lang_meta["lang_name"]
    return lang_tree

def create_lang_usage_xml(langs_used):
    lang_usage = ET.Element("langUsage")
    langs_xml = [create_lang_xml(ALL_LANGS_META[lang]) for lang in langs_used]
    for lang in langs_xml:
        lang_usage.append(lang)
    return lang_usage

#TODO integrate keywords
def create_text_class(keywords):
    text_class = ET.Element("textClass")
    keywords = ET.SubElement(text_class, "keywords")
    keywords.append(ET.fromstring('<term type="supergenre" rend="fiction">Fiction</term>'))
    keywords.append(ET.fromstring('<term type="genre" rend="fiction-prose">Drama</term>'))
    return text_class

def create_profile_desc(langs_used, keywords=""):
    profile_desc = ET.Element("profileDesc")
    profile_desc.append(create_lang_usage_xml(langs_used))
    profile_desc.append(create_text_class(keywords))
    return profile_desc

#TODO integrate date
def create_rev_desc(reviser="#RDENT", change_message="Génération du document"):
    rev_desc = ET.Element("revisionDesc")
    change = ET.SubElement(rev_desc, "change", when="2024-03-24", who=reviser)
    change.text = change_message
    return rev_desc
def create_prose_metadata_xml(metadata, langs_used):
    tei_root = ET.Element("teiHeader")
    tei_root.append(create_file_desc(metadata))
    tei_root.append(create_profile_desc(langs_used))
    tei_root.append(create_rev_desc())
    return tei_root


