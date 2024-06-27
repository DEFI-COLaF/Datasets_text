import molyé_util as m_util
import regex as re
from bs4 import BeautifulSoup
from lxml import etree as ET
import metadata_patterns



def parse_play_lang_info(work_info):
    roles = work_info["Character"]
    roles = roles.upper().split(",")
    roles = [r.strip() for r in roles]

    langs = work_info["Lang"].split(",")
    #keep codes lowercase
    langs = [l.strip() for l in langs]

    roles_langs = {r: l for r, l in zip(roles, langs)}
    return roles_langs

def tag_langs_play(file_text, roles_langs):
    soup = BeautifulSoup(file_text, features="xml")

    for role, lang in roles_langs.items():
        #For plays, tag at both <sp> and <p> levels for interoperability with prose
        matches = soup.find_all("sp", attrs={"who": role})
        for match in matches:
            match["xml:lang"] = lang
            lines = match.find_all("p")
            for line in lines:
                line["xml:lang"] = lang
    # inserts namespace unnecessarily
    out = m_util.fix_tei_tag(soup)
    return out

#insert sentence tags into prose
def tag_langs_prose(file_text, lines, lang):
    for line in lines:
        file_text = file_text.replace(line, fr'<s xml:lang="{lang}">{line}</s>')
    return file_text

def tag_all_paragraphs(file_text, lang):
    soup = BeautifulSoup(file_text, features="xml")
    for match in soup.find_all("p"):
        match["xml:lang"] = lang
    return m_util.fix_tei_tag(soup)

def update_lang_usage_play(file_text, roles_langs, meta_langs):
    soup = BeautifulSoup(file_text, features="xml")
    lang_usage = soup.find("langUsage")
    #Don't add same language multiple times
    langs_used = meta_langs + list(set(roles_langs.values()))
    new_lang_usage = metadata_patterns.create_lang_usage_xml(langs_used)
    tag = BeautifulSoup(ET.tostring(new_lang_usage, pretty_print=True), features="xml")
    lang_usage.replace_with(tag)
    #turns = soup.find_all("sp", attrs={"xml:lang" :True })
    return m_util.fix_tei_tag(soup)



def update_play(file_text, play_info):
    # TODO incorporate meta_langs
    meta_langs = ["met-fr"]
    roles_langs = parse_play_lang_info(play_info)
    # metadata = extract_short_metadata(file_text)
    tagged = tag_langs_play(file_text, roles_langs)
    updated = update_lang_usage_play(tagged, roles_langs, meta_langs)
    return updated


#Add language annotations (and possibly other kinds eventually
def annotate_all_plays(plays, folder):
    for play in plays:
        title = play["Title"]
        file = m_util.find_converted_file(title, folder)
        if file:
            file_text = m_util.read_file(file)
            updated = update_play(file_text, play)
            root = ET.fromstring(updated.encode("utf8"))
            #print(ET.dump(root))
            m_util.write_tree(root, file)