from lxml import etree
import xml.etree.ElementTree as ET
import os
import json
import ast
import regex as re
import pandas as pd

import requests
from bs4 import BeautifulSoup
import roman

def create_colaf_header(extracted_metadata, url):
    #<idno>{extracted_metadata["idno"]}</idno>
    colaf_header = f"""
          <teiHeader>
    <fileDesc>
        <titleStmt>
            <title type="main">{extracted_metadata["short_title"]} </title>
            <respStmt>
                <resp>Encoding</resp>
                <persName xml:id="RDENT">
                    <surname>Dent</surname>
                    <forename>Rasul</forename>
                    <idno type="orcid">0009-0004-1032-1745</idno>        
                </persName>
            </respStmt>
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
            <date when="2024-03-25"/>
            <availability>
                <licence target="https://creativecommons.org/licenses/by/4.0/"/>
            </availability>
        </publicationStmt>
        <sourceDesc>
            <bibl type="digitalSource">
                <ptr target="{url}"/>
                <title>{extracted_metadata["title"]}</title>
                <author>{extracted_metadata["author"]}</author>
                <publisher>{extracted_metadata["publisher"]} </publisher>
                <date when="{extracted_metadata["date"]}"/>
            </bibl>
            <bibl type="CorpusSource">
                <ptr target="{extracted_metadata["digital_publisher"]}"/>
                <title>{extracted_metadata["title"]}</title>
                <author>{extracted_metadata["digital_publisher"]}</author>
                <publisher>{extracted_metadata["digital_publisher"]}</publisher>
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
                {extracted_metadata["period"]}
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

def handle_web_error(response):
    # Print an error message if the request was not successful
    error_message = response.status_code
    print(f"Error: {error_message}")
    log_filename = "errors.txt"
    with open(log_filename, "a") as log_file:
        # Append the error message along with the current timestamp
        log_file.write(f"{error_message}\n")
        print(f"Error logged to '{log_filename}'.")
    return None

def get_html_content(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)

        if response.status_code == 200:
            # Return the web content
            return str(response.text)

        else:
            return handle_web_error(response)
    except Exception as e:

        # Print an error message if an exception occurs
        print(f"Exception: {str(e)}")
        return None


def divide_xml_content(full_file):
    soup = BeautifulSoup(full_file, 'xml')
    header = str(soup.find("teiHeader"))
    text = str(soup.find("text"))
    front = str(soup.find("front"))
    body = str(soup.find("body"))
    return header, text, front, body

def remove_tags(s):
    return re.sub("<.*?>", "", s)
"""Extract the tags"""

def convert_roman_year(raw_date):
    numeral_pattern = r"[MDLCXVI\.\s]+"
    roman_year = re.search(numeral_pattern, raw_date)[0]
    roman_year = re.sub(r"\W", "", roman_year)
    return roman.fromRoman(roman_year)

def extract_date(front_soup):
    date = ""
    try:
        raw_date = front_soup.find("docDate")
        if raw_date["value"]:
            date = str(raw_date["value"])
        else:
            date = str(convert_roman_year(remove_tags(str(raw_date))))
    except Exception as e:
        print(f"{front_soup.title()} has a {e}")
        date = "date_error"
    return date


def create_idno(metadata):
    idno = "_".join(
        [remove_tags(metadata["short_title"]), remove_tags(metadata["author"].split()[0]), metadata["date"]])
    idno = re.sub(r"\s+", "_", idno)
    idno = re.sub(r"\W", "", idno)
    return idno

def convert_tags(play):
    play = re.sub(r"<(\/)?strong>", "<\1hi>")
    play = re.sub(r"<(\/)em>", "", play)
    return  play

def create_tree_basis(metadata, url):
    root = None
    root = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    xml_header = create_colaf_header(metadata, url)
    tree_metadata = root.append(etree.fromstring(xml_header))
    text = etree.SubElement(root, "text")
    text.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "met-fra-std"
    return root