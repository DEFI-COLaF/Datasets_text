from lxml import etree
import os
import json
import ast
import re
import requests
from bs4 import BeautifulSoup

def get_idno(file):
    pattern = r'^(\d+)_\d+_\d+_\w+'

    # Use re.match to find the pattern at the beginning of the string
    match = re.match(pattern, file)

    if match:
        # Extract and return the first number
        return int(match.group(1))
    else:
        # Return None if no match is found
        return None

def get_html_content(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the HTML content
            resultat = response.text
            soup = BeautifulSoup(resultat, 'html.parser')
            # Extract title information and remove "Français sous-titres"
            title_tag = soup.find('span', {'itemprop': 'name'})
            title = title_tag.text.strip().replace('Français', '').replace('sous-titres','').strip()

            # Extract the first director (realisateur) name
            director_tag = soup.find('p', {'itemprop': 'director'})
            director_name = director_tag.find('span', {'itemprop': 'name'}).text.strip()

            # Extract the first publisher (distribution) name
            publisher_tag = soup.find('p', {'itemprop': 'actor'})
            publisher_name = publisher_tag.find('span', {'itemprop': 'name'}).text.strip()
            return title, director_name, publisher_name
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code}")
            with open("erreurs.txt", "a") as log_file:
                # Append the error message along with the current timestamp
                log_file.write(f"{error_message}\n")
                print(f"Error logged to '{log_filename}'.")
            return None
    except Exception as e:
        # Print an error message if an exception occurs
        print(f"Exception: {str(e)}")
        return None


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
        
        
for dir_domaine in os.listdir("xml/fr"):
    for dir_annee in os.listdir("xml/fr/" + dir_domaine + "/"):
        for file in os.listdir(f'xml/fr/{dir_domaine}/{dir_annee}'):
            if "xml" in file:
                print(file)
                idno = get_idno(file)
                try:
                    title, author, publisher = get_html_content(f'https://www.opensubtitles.org/fr/search/sublanguageid-fre/idmovie-{idno}')
                except Exception as e:
                    with open("erreurs.txt", "a") as log_file:
                        # Append the error message along with the current timestamp
                        log_file.write(f"{dir_domaine} {dir_annee} {file}\n")
                    continue

                metadata = f"""
                      <teiHeader>
                <fileDesc>
                    <titleStmt>
                        <idno>fra-opensubtitles-{idno}</idno> 
                        <title type="main">{title}</title>
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
                        <publisher ref="https://colaf.huma-num.fr/">Corpus et Outils pour les Langues de France
                            (COLaF)</publisher>
                        <date when="2024-01-30"/>
                        <availability>
                            <licence target="https://creativecommons.org/licenses/by/4.0/"/>
                        </availability>
                    </publicationStmt>
                    <sourceDesc>
                        <bibl type="digitalSource">
                            <ptr target="https://www.opensubtitles.org/fr/ssearch/sublanguageid-fre/idmovie-{idno}"/>
                            <title>{title}</title>
                            <author>{author}</author>
                            <publisher>{publisher}</publisher>
                            <date when="{dir_annee}"/>
                        </bibl>
                        <bibl type="CorpusSource">
                            <ptr target="https://opus.nlpl.eu/OpenSubtitles/corpus/version/OpenSubtitles"/>
                            <title>{title}</title>
                            <author>OpenSubtitle</author>
                            <publisher>Opus</publisher>
                            <date when="2018"/>
                        </bibl>
                    </sourceDesc>
                    <extent>
                        <measure unit="token-colaf"/><!--A ajouter plus tard-->
                    </extent>
                </fileDesc>
                <profileDesc>
                    <langUsage>
                        <language ident="met-fra-std">
                            <idno type="langue">met-fra-std</idno>
                            <idno type="script">latin</idno>
                            <name>Français</name>
                            <date when="{dir_annee}"/>
                            <location/>
                        </language>
                    </langUsage>
                    <textClass>
                        <keywords>
                            <term type="supergenre" rend="spoken">Spoken</term>
                            <term type="genre" rend="spoken-script">TV/movie script</term>
                            <term type="motclef" rend="spoken-script-movie">Movie</term>
                            <term type="motclef">{dir_domaine}</term>
                        </keywords>
                    </textClass>
                </profileDesc>
                <revisionDesc>
                    <change when="2023-11-24" who="#JJANES">Génération du document</change>
                </revisionDesc>
                </teiHeader>
                """
                root = None
                root = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
                metadata = root.append(etree.fromstring(metadata))
                text = etree.SubElement(root, "text")
                text.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "met-fra-std"
                body = etree.SubElement(text, "body")
                # parsage du doc
                xml = etree.parse(f'xml/fr/{dir_domaine}/{dir_annee}/{file}')
                div = etree.SubElement(body, "div")
                for s_xml in xml.xpath("//s"):
                    s = etree.SubElement(div, "s")
                    for w_xml in s_xml.xpath("w"):
                        w = etree.SubElement(s, "w")
                        w.text = w_xml.text
                create_directory("resultat/"+dir_domaine)
                create_directory(f'resultat/{dir_domaine}/{dir_annee}')
                etree.ElementTree(root).write(f'resultat/{dir_domaine}/{dir_annee}/{file[:-4]}.xml', pretty_print=True, encoding="UTF-8",
                                              xml_declaration=True)


































