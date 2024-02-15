
from lxml import etree
import os
import json
import ast


def nettoyage_code(texte):
    dict_code = {"é":"\u00e9", "è":"\u00e8"}
    words=texte.split()
    for i in range(len(words)):
        for key in dict_code:
            if key in str(words[i]):
                words[i]= str(words[i]).replace(key, dict_code[key])
    texte_propre = b' '.join(words)
    return texte_propre

n=0
for dir in os.listdir("dataset/"):
    for file in os.listdir("dataset/" + dir + "/"):
        n+=1
        idno = f'fra-sosweet-{n:04d}'
        metadata = f"""
          <teiHeader>
            <fileDesc>
              <titleStmt>
                <idno>{idno}</idno>
                <title type="main">{file[:-5]}</title>
                <title type="collection">So Sweet</title>
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
                <publisher ref="https://colaf.huma-num.fr/">Corpus et Outils pour les Langues de
                  France (COLaF)</publisher>
                <date when="2024-01-30"/>
                <availability>
                  <licence target="https://creativecommons.org/licenses/by/4.0/"/>
                </availability>
              </publicationStmt>
              <sourceDesc>
                <bibl type="digitalSource">
                  <ptr target="https://www.ortolang.fr/market/corpora/sosweet"/>
                  <title>So Sweet</title>
                  <author>Jean-Philippe Magué</author>
                  <author>Marton Karsai</author>
                  <author>Jean-Pierre Chevrot</author>
                  <author>Djamé Seddah</author>
                  <publisher>Ortolang</publisher>
                  <date when="2024"/>
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
                  <date from="2009" to="2017"/>
                  <location/>
                </language>
              </langUsage>
              <textClass>
                <keywords>
                  <term type="supergenre" rend="web">Web</term>
                  <term type="genre" rend="web-social">Social</term>
                  <term type="motclef" rend="web-social-forum">Tweets</term>
                </keywords>
              </textClass>
              <particDesc>
                <listPerson/>
              </particDesc>
            </profileDesc>
            <revisionDesc>
              <change when="2023-11-24" who="#JJANES">Génération du 1er schema ODD COLAF</change>
            </revisionDesc>
          </teiHeader>
        """
        root=None
        print(f'Transformation du fichier {file}')
        root = etree.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
        metadata = root.append(etree.fromstring(metadata))
        text = etree.SubElement(root, "text")
        text.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "met-fra-std"
        body = etree.SubElement(text, "body")
        # parsage du doc
        file_doc = open("dataset/" + dir + "/" + file)
        str_file = file_doc.read()
        count_replace = str_file.count("}") - 1
        str_dict = "[" + str_file.replace("}", "},", count_replace) + "]"
        str_dict = str_dict.replace('"tweet": ', '"tweet": b')
        dict_tweets = ast.literal_eval(str_dict)
        div = etree.SubElement(body, "div")
        head = etree.SubElement(div, "head")
        head.text = file.replace(".data", "")
        user_list = []
        for tweet in dict_tweets:
            post = etree.SubElement(div, "post", who="#" + tweet["user"], when=tweet["date"])
            post.attrib['{http://www.w3.org/XML/1998/namespace}id'] = tweet["user"] + "-" + tweet["date"]
            p = etree.SubElement(post, "p")
            #p.text = nettoyage_code(tweet["tweet"])
            p.text = tweet["tweet"]
            user_list.append(tweet['user'])
        user_list = list(set(user_list))
        for user in user_list:
            listperson = root.find(".//listPerson")
            person = etree.SubElement(listperson, "person")
            person.attrib['{http://www.w3.org/XML/1998/namespace}id'] = user
        etree.ElementTree(root).write(f'{dir}/{file[:-5]}.xml', pretty_print=True, encoding="UTF-8",
                                      xml_declaration=True)



