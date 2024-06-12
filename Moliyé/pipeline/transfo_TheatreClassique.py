import lxml
from lxml import etree as ET
import os

import metadata_patterns

def create_metadata_xml(metadata):
    metadata = f"""
        <teiHeader>
                <fileDesc>
                    <titleStmt>
                        <idno>{metadata["id"]}</idno>
                        <title type="main">{metadata["title"]}</title>
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
                            <ptr target="{metadata["permalien"]}"/>
                            <title>{metadata["title"]}</title>
                            <author>{metadata["author"]}</author>
                            <publisher>Gallica</publisher>
                            <date when=""/>
                        </bibl>
                        <bibl type="digitalSource">
                            <ptr
                                target="{metadata["permalien"]}"/>
                            <title>{metadata["title"]}</title>
                            <author>{metadata["publisher"]}</author>
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
                            <date when=f"{metadata["date"]}"/>
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
                            {metadata["listperson_xml"]}
                        </listPerson>
                    </particDesc>
                </profileDesc>
                <revisionDesc>
                    <change when="2024-03-24" who="#JJANES">Génération du document</change>
                </revisionDesc>
            </teiHeader>
        """
    return metadata

