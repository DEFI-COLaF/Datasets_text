import csv
from lxml import etree
import os
import pandas as pd
import re
from bs4 import BeautifulSoup

with (open("ocr_etatdeslieux.csv", 'r', newline="") as csvfile):
    reader = csv.DictReader(csvfile, delimiter=",")
    for ligne_etat in reader:
        if "Texte" in ligne_etat['TEXTE']:
            pattern = r'Texte n°\d{1,2}'
            match = re.match(pattern, ligne_etat['TEXTE']).group()
            titre = ligne_etat['TEXTE'].replace(match, "")
        else:
            titre = ligne_etat['TEXTE']
        if "&" in titre:
            titre = titre.replace("&","et")
        titre_propre = titre.replace('"', "")
        if ligne_etat['CODE POSTAL']:
            code_postal = ligne_etat['CODE POSTAL']
            if "62" in code_postal:
                region="Pas de Calais"
                pays = "France"
            elif "59" in code_postal:
                region="Nord"
                pays = "France"
            elif "80" in code_postal:
                region="Somme"
                pays = "France"
            elif "B" in code_postal:
                pays = "Belgique"
                region = ""
            else:
                if ligne_etat["VILLE"]:
                    ville = ligne_etat['VILLE']
                    if "BELGIQUE" in ville:
                        pays = "Belgique"
                        region = ""
                    else:
                        pays="France"
                        region=""
                else:
                    pays = "France"
                    region=""

        metadata_xml = f"""    <teiHeader>
                <fileDesc>
                    <titleStmt>
                        <idno>PIC_CONCOURS__{ligne_etat['annee']}_{int(ligne_etat['n']):02d}</idno>
                        <title type="main">{titre_propre}</title>
                        <title type="collection">Picard Concours</title>
                        <author>{ligne_etat['PRENOM']}, {ligne_etat['NOM']}</author>
                        <respStmt>
                            <resp>Encoding</resp>
                            <persName xml:id="JJANES">
                                <surname>Janès</surname>
                                <forename>Juliette</forename>
                                <idno type="orcid">0000-0002-8971-6173</idno>
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
                        <publisher ref="https://colaf.huma-num.fr/">Corpus et Outils pour
                            les Langues de France (COLaF)</publisher>
                        <date when="2024-04-04"/>
                        <availability>
                            <licence target="https://creativecommons.org/licenses/by/4.0/"/>
                        </availability>
                    </publicationStmt>
                    <sourceDesc>
                        <bibl>
                            <title>{titre_propre}</title>
                            <author>{ligne_etat['PRENOM']}, {ligne_etat['NOM']}</author>
                            <pubPlace>Amiens</pubPlace>
                            <publisher>Agence régionale de la langue Picarde</publisher>
                            <date when="{ligne_etat['annee']}"/>
                        </bibl>
                    </sourceDesc>
                </fileDesc>
                <profileDesc>
                    <langUsage>
                        <language ident="met-oil-pic" usage="100">
                            <idno type="langue">met-oïl-pic</idno>
                            <idno type="script">latin</idno>
                            <name>Picard</name>
                            <date>2020</date>
                            <location>
                            <region>{region}</region>
                            <country>{pays}</country>
                            </location>
                        </language>
                    </langUsage>
                    <textClass>
                        <keywords>
                            <term type="supergenre" rend="fiction">Fiction</term>
                            <term type="genre" rend="fiction-prose">Prose</term>
                        </keywords>
                    </textClass>
                </profileDesc>
                <revisionDesc>
                    <change when="2024-04-02" who="#JJANES">Génération du XML</change>
                </revisionDesc>
            </teiHeader>"""
        root = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
        metadata = root.append(etree.fromstring(metadata_xml))
        nom_dir = ligne_etat['new_name'].replace(".pdf","")
        extracted_text=[]
        for file in sorted(os.listdir('OCR/'+nom_dir)):
            if "xml" in file:

                if "METS" in file:
                    pass
                else:
                    extracted_text.append(f"<pb n='{file[:-4]}.png'/>")
                    tree = etree.parse('OCR/'+nom_dir+'/'+file)
                    root_file = tree.getroot()
                    for string_element in root_file.findall('.//{http://www.loc.gov/standards/alto/ns-v4#}String'):
                        texte = string_element.attrib['CONTENT']
                        print(texte)
                        soup = BeautifulSoup(texte, "html.parser")
                        texte_normal = soup.text
                        if "&" in texte_normal:
                            texte_normal = texte_normal.replace("&", "et")
                        extracted_text.append("<lb/>"+texte_normal)

        extracted_text_xml = '<text xml:lang="met-oil-pic"><body><div>'+"".join(extracted_text)+'</div></body></text>'
        body = root.append(etree.fromstring(extracted_text_xml))

        etree.ElementTree(root).write(f'TEI_1/Picard_Concours_{ligne_etat["annee"]}_{int(ligne_etat["n"]):02d}.xml', pretty_print=True, encoding="UTF-8",
                                        xml_declaration=True)
