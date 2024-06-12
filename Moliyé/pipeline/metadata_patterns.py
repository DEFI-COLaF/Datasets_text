from lxml import etree as ET
from lxml.builder import ElementMaker
from bs4 import BeautifulSoup

fra_deu_meta = {"ident": "fra-deu", "script": "Latin", "lang_name": "Germanic Baragouin"}

fra_ang_meta = {"ident": "fra-ang", "script": "Latin", "lang_name": "Anglo-French Baragouin"}

fra_dia_meta = {"ident": "fra-dia", "script": "Latin", "lang_name": "Early Modern Dialectal French"}


met_fra_meta = {"ident": "met-fr", "script": "Latin", "lang_name": "French of Metropolitan France"}
lou_meta = {"ident": "lou", "script": "Latin", "lang_name": "Louisiana Creole"}
rcf_meta = {"ident": "rcf", "script": "Latin", "lang_name": "Réunion Creole"}
gcf_meta = {"ident": "gcf", "script": "Latin", "lang_name": "Antillean Creole"}
gcr_meta = {"ident": "gcr", "script": "Latin", "lang_name": "French Guianese Creole"}

ALL_LANGS_META = {"met-fr": met_fra_meta, "fra-dia": fra_dia_meta, "fra-deu": fra_deu_meta, "fra-ang": fra_ang_meta,
                  "lou": lou_meta, "rcf": rcf_meta, "gcf": gcf_meta, "gcr": gcr_meta}

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


def create_corpus_title_statement(metadata, encoders, principals):
    titleStmt = ET.Element("titleStmt")

    idno = ET.SubElement(titleStmt, "idno")
    idno.text = metadata["id"]

    title = ET.SubElement(titleStmt, "title", type="main")
    title.text = metadata["title"]

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


def create_source_desc_xml(metadata, work_or_corpus="work"):
    root = ET.Element("sourceDesc")
    #only have a print source for individual works
    if work_or_corpus == "work":
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


def create_file_desc(metadata, encoders, principals, work_or_corpus="work"):
    file_desc = ET.Element("fileDesc")
    title_statement = None
    source_desc =None
    if work_or_corpus == "work":
        title_statement = create_title_statement_xml(metadata, encoders=encoders, principals=principals)
    elif work_or_corpus== "corpus":
        title_statement = create_corpus_title_statement(metadata, encoders=encoders, principals=principals)
    file_desc.append(title_statement)
    file_desc.append(create_publisher_xml())
    file_desc.append(create_source_desc_xml(metadata, work_or_corpus))

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
def create_text_class(work_type):
    text_class = ET.Element("textClass")
    keywords = ET.SubElement(text_class, "keywords")

    if work_type == "theatre":
        keywords.append(ET.fromstring('<term type="supergenre" rend="spoken">Fiction</term>'))
        keywords.append(ET.fromstring('<term type="genre" rend="spoken-script">fiction-drama</term>'))

    if work_type == "prose":
        keywords.append(ET.fromstring('<term type="supergenre" rend="fiction">Fiction</term>'))
        keywords.append(ET.fromstring('<term type="genre" rend="fiction-prose">Drama</term>'))
    return text_class

def create_theatre_part_desc(metadata):
    partic_desc = ET.Element("particDesc")
    partic_desc.append(ET.fromstring(f"<listPerson>{metadata['listperson_xml']}</listPerson>"))
    return partic_desc

def create_profile_desc(metadata, work_type, langs_used):
    profile_desc = ET.Element("profileDesc")
    profile_desc.append(create_lang_usage_xml(langs_used))
    profile_desc.append(create_text_class(work_type))
    if work_type=="theatre":
        profile_desc.append(create_theatre_part_desc(metadata))
    return profile_desc


#TODO integrate date
def create_rev_desc(reviser="#RDENT", change_message="Génération du document"):
    rev_desc = ET.Element("revisionDesc")
    change = ET.SubElement(rev_desc, "change", when="2024-05-30", who=reviser)
    change.text = change_message
    return rev_desc
def create_metadata_xml(metadata, work_type, langs_used, encoders=["RDENT", "JJANES"], principals=["BSAGOT"], work_or_corpus="work"):
    tei_root = ET.Element("teiHeader")
    tei_root.append(create_file_desc(metadata, encoders=encoders,
                                     principals=principals, work_or_corpus=work_or_corpus))
    tei_root.append(create_profile_desc(metadata, work_type, langs_used))
    tei_root.append(create_rev_desc())
    return tei_root



#Short file desc for use with excerpts
def create_short_file_desc(metadata):
    file_desc = ET.Element("fileDesc")
    title_statement = ET.SubElement(file_desc, "titleStmt")
    title = ET.SubElement(title_statement, "title")
    title.text = metadata["title"]
    author = ET.SubElement(title_statement, "author")
    author.text = metadata["author"]

    publication_stmt = create_publisher_xml()
    file_desc.append(publication_stmt)

    source_desc = ET.SubElement(file_desc, "sourceDesc")
    bibl = ET.SubElement(source_desc, "bibl")
    bibl_title = ET.SubElement(bibl, "title")
    bibl_title.text = metadata["title"]
    bibl_author = ET.SubElement(bibl, "author")
    bibl_author.text = metadata["author"]

    return file_desc

#TODO add languages
#
def create_short_prof_desc(langs, roles_langs=None):
    profile_desc = ET.Element("profileDesc")
    profile_desc.append(create_lang_usage_xml(langs))
    partic_desc = ET.SubElement(profile_desc, "particDesc")
    if roles_langs:
        for spk, lg in roles_langs.items():
            #TODO fix xmlid namespace issue
            person = ET.SubElement(partic_desc, "person", XMLID=spk)
    return partic_desc

#TODO
def create_extracts_xml(metadata, quote_groups, langs_used, roles_langs=None):
    root = ET.Element("TEI")
    #root = ET.Element("TEI", correspond=metadata["id"])
    header = ET.SubElement(root, "teiHeader")
    header.append(create_short_file_desc(metadata))
    profile_desc = create_short_prof_desc(langs_used, roles_langs)

    text = ET.SubElement(root, "text")
    for quote_group in quote_groups:
        group_node = ET.SubElement(text, "group")
        group_text = ET.SubElement(group_node, "text")
        body = ET.SubElement(group_text, "body")
        #The quotes should already be in XML
        for quote in quote_group:
            body.append(ET.fromstring(quote))
    return root


#each prepped extract is a a tuple of the metadata for the work and a list of groups of quotes
def create_corpus_xml(corpus_metadata, langs_used, prepped_extracts, encoders=["RDENT", "JJANES"], principals=["BSAGOT"]):
    corpus_root = ET.Element("teiCorpus", xmlns="http://www.tei-c.org/ns/1.0")
    tei_header = create_metadata_xml(corpus_metadata, work_type="N/A", langs_used=langs_used,
                                     encoders=encoders, principals=principals, work_or_corpus="corpus")
    corpus_root.append(tei_header)
    for metadata, quote_groups, langs, role_langs in prepped_extracts:
        extract_xml = create_extracts_xml(metadata, quote_groups, langs, role_langs)
        corpus_root.append(extract_xml)
    return corpus_root

#TODO remove idno, extent, keywords
