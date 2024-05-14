from lxml import etree as ET
import os

def create_multiple_person(item_multiple):
    metadata_list = []
    nom_list =[]
    for el in item_multiple:
        if " " in el.text or "[" in el.text or "Ô" in el.text or "'" in el.text or "," in el.text:
            nom=el.text
            nom = nom.replace(" ","_")
            nom = nom.replace("[", "")
            nom = nom.replace("Ô", "O")
            nom = nom.replace("'", "_")
            nom = nom.replace(",", "")
        else:
            nom = el.text
        if nom in " ".join(nom_list):
            nom = nom+"_2"
        else:
            nom_list.append(nom)
        metadata_list.append(f'<person xml:id="{nom}"><persName>{el.text}</persName></person>')
    xml_metadata = "".join(metadata_list)
    print(xml_metadata)
    return xml_metadata

def create_directory(directory_path):
    """
    Verify the existence of a directory. If it does not exist, create it.

    Parameters:
    - directory_path (str): The path of the directory to be checked/created.
    """
    try:
        # Check if the directory exists
        if not os.path.exists(directory_path):
            # If not, create the directory
            os.makedirs(directory_path)
        else:
            pass
    except Exception as e:
        print(f"Error: {str(e)}")


def create_metadata(tree):
    title = tree.find(".//title").text
    auteur = tree.find(".//author").text
    id = "CRE_THEATRE_" + tree.find(".//idno").text
    #date = tree.find(".//docDate").text
    publisher = tree.find(".//publisher")
    if publisher:
        publisher=publisher.text
    else:
        publisher = ""
    permalien = tree.find(".//permalien").text

    castItem = tree.findall(".//castItem/role")
    listperson_xml = create_multiple_person(castItem)

    metadata = f"""
        <teiHeader>
                <fileDesc>
                    <titleStmt>
                        <idno>{id}</idno>
                        <title type="main">{title}</title>
                        <respStmt>
                            <resp>Encoding</resp>
                            <persName xml:id="RDENT">
                                <surname>Dent</surname>
                                <forename>Rasul</forename>
                                <idno type="orcid">0000-0002-8971-6175</idno>
                            </persName>
                        </respStmt>
                        <respStmt>
                            <resp>Encoding</resp>
                            <persName xml:id="JJANES">
                                <surname>Janes</surname>
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
                        <publisher ref="https://colaf.huma-num.fr/">Corpus et Outils pour les Langues de
                            France (COLaF)</publisher>
                        <date when="2024-03-25"/>
                        <availability>
                            <licence target="https://creativecommons.org/licenses/by/4.0/"/>
                        </availability>
                    </publicationStmt>
                    <sourceDesc>
                        <bibl type="printSource">
                            <ptr target="{permalien}"/>
                            <title>{title}</title>
                            <author>{auteur}</author>
                            <publisher>Gallica</publisher>
                            <date when=""/>
                        </bibl>
                        <bibl type="digitalSource">
                            <ptr
                                target="https://www.theatre-classique.fr/pages/documents/{file}"/>
                            <title>{title}</title>
                            <author>{publisher}</author>
                            <publisher>Théâtre Classique</publisher>
                            <date when="2021"/>
                        </bibl>
                    </sourceDesc>
                    <extent>
                        <measure unit="token-colaf"/><!--A ajouter plus tard-->
                    </extent>
                </fileDesc>
                <profileDesc>
                    <langUsage>
                        <language ident="met-fr">
                            <idno type="langue">met-fr</idno>
                            <idno type="script">latin</idno>
                            <name>Français</name>
                            <date when=""/>
                            <location><country>Paris</country></location>
                        </language>
                    </langUsage>
                    <textClass>
                        <keywords>
                            <term type="supergenre" rend="spoken">Fiction</term>
                            <term type="genre" rend="spoken-script">fiction-drama</term>
                        </keywords>
                    </textClass>
                    <particDesc>
                        <listPerson>
                            {listperson_xml}
                        </listPerson>
                    </particDesc>
                </profileDesc>
                <revisionDesc>
                    <change when="2024-03-24" who="#JJANES">Génération du document</change>
                </revisionDesc>
            </teiHeader>
        """
    return metadata

for file in os.listdir("theatre"):
    print(file)
    xml_file = "theatre/"+file
    tree = ET.parse(xml_file)
    metadata_string = create_metadata(tree)
    xsl_file = ET.parse("html2tei.xsl")
    xsl_transform = ET.XSLT(xsl_file)
    transformed_xml = xsl_transform(tree).getroot()
    root = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    metadata = root.append(ET.fromstring(metadata_string))
    text = root.append(transformed_xml)
    create_directory("theatre_TEI")
    ET.ElementTree(root).write(f'theatre_TEI/{file}', pretty_print=True, encoding="UTF-8",
                               xml_declaration=True)

