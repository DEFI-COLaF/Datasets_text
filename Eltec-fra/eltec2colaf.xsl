<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="xml" indent="yes" encoding="UTF-8" xmlns="http://www.tei-c.org/ns/1.0"/>
    <xsl:strip-space elements="*"/>
    <xsl:template match="//tei:TEI">
        <TEI>
            <teiHeader>
                <fileDesc>
                    <titleStmt>
                        <idno>
                            <xsl:value-of select="//tei:TEI/@xml:id"/>
                        </idno>
                        <title type="main">
                            <xsl:value-of select="//tei:bibl[@type='digitalSource']/tei:title"/>
                        </title>
                        <title type="collection">ELTec Collection</title>
                        <author>
                            <xsl:value-of select="//tei:titleStmt/tei:author"/>
                        </author>
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
                        <date when="2023-11-24"/>
                        <availability>
                            <xsl:element name="licence">
                                <xsl:attribute name="target">
                                    <xsl:value-of select="//tei:licence/@target"/>
                                </xsl:attribute>
                            </xsl:element>
                        </availability>
                    </publicationStmt>
                    <sourceDesc>
                        <bibl type="printSource">
                            <title><xsl:value-of select="//tei:bibl[@type='printSource']/tei:title"/></title>
                            <author><xsl:value-of select="//tei:titleStmt/tei:author"/></author>
                            <pubPlace><xsl:value-of select="//tei:bibl[@type='printSource']/tei:pubPlace"/></pubPlace>
                            <publisher><xsl:value-of select="//tei:bibl[@type='printSource']/tei:publisher"/></publisher>
                            <xsl:element name="date">
                                <xsl:attribute name="when">
                                    <xsl:value-of select="//tei:bibl[@type='firstEdition']/tei:date"/>
                                </xsl:attribute>
                            </xsl:element>
                        </bibl>
                        <bibl type="digitalSource">
                            <xsl:element name="ptr">
                                <xsl:attribute name="target">
                                    <xsl:value-of select="//tei:distributor/@ref"/>
                                </xsl:attribute>
                            </xsl:element>
                            <title><xsl:value-of select="//tei:titleStmt/tei:title"/></title>
                            <author>Christof Schöch</author>
                            <publisher><xsl:value-of select="//tei:publicationStmt/tei:publisher"/></publisher>
                            <xsl:element name="date">
                                <xsl:attribute name="when">
                                    <xsl:value-of select="//tei:publicationStmt/tei:date/@when"/>
                                </xsl:attribute>
                            </xsl:element>
                        </bibl>
                    </sourceDesc>
                    <extent>
                        <xsl:apply-templates select="//tei:extent"/>      
                    </extent>
                </fileDesc>
                <profileDesc>
                    <langUsage>
                        <xsl:element name="language">
                            <xsl:attribute name="ident">met-fra-std</xsl:attribute>
                            <xsl:attribute name="usage">100</xsl:attribute>
                            <idno type="langue">met-fra-std</idno>
                            <idno type="script">latin</idno>
                          <name>Français</name>
                            <date>
                                <xsl:value-of select="//tei:bibl[@type = 'firstEdition']/tei:date"/>
                            </date>
                            <location>
                                <settlement>
                                <xsl:value-of
                                    select="//tei:bibl[@type = 'firstEdition']/tei:pubPlace"/></settlement>
                            </location>
                        </xsl:element>
                    </langUsage>
                    <textClass>
                        <keywords>
                            <term type="supergenre" rend="fiction">Fiction</term>
                            <term type="genre" rend="fiction-prose">Prose</term>
                            <term type="motclef" rend="fiction-prose-novels">Novels</term>
                        </keywords>
                    </textClass>
                </profileDesc>
                <revisionDesc>
                    <change when="2024-01-30" who="#JJANES">Génération du XML grâce à transfo_eltec.xsl</change>
                </revisionDesc>
            </teiHeader>
            <text xml:lang="met-fra-std">
                <body>
                <xsl:apply-templates select="//tei:text"/>
                </body>
            </text>
        </TEI>
    </xsl:template>
    <xsl:template match="//tei:text">
       <xsl:apply-templates/>
    </xsl:template>
    <xsl:template match="//tei:div">
        <xsl:choose>
        <xsl:when test="@type='liminal'">
            <xsl:element name="div" >
                <xsl:attribute name="type">liminal</xsl:attribute>
                <xsl:apply-templates/>
            </xsl:element>
        </xsl:when>
            <xsl:when test="@type='letter'">
                <xsl:element name="div">
                    <xsl:apply-templates/></xsl:element>
            </xsl:when>
            <xsl:when test="@type='group'">
                <xsl:element name="div">
                    <xsl:attribute name="type">part</xsl:attribute>
                    <xsl:apply-templates/></xsl:element>
            </xsl:when>
            <xsl:when test="@type='notes'">
                <div type="liminal">
                <xsl:apply-templates/>
                </div>
            </xsl:when>
        <xsl:otherwise>
                <xsl:element name="div" >
                    <xsl:attribute name="type">chapter</xsl:attribute>
                        <xsl:apply-templates/>
                </xsl:element>
        </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    <xsl:template match="//tei:trailer">
        <xsl:element name="div">
            <xsl:attribute name="type">liminal</xsl:attribute>
            <xsl:element name="p">
            <xsl:apply-templates/>
            </xsl:element>
        </xsl:element>
    </xsl:template>
    <xsl:template match="//tei:p">
        <xsl:choose>
            <xsl:when test="./tei:label">
                <sp>
                    <speaker><xsl:apply-templates/></speaker>
                </sp>
            </xsl:when>
            <xsl:otherwise>
            <p>
            <xsl:apply-templates/>
            </p>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    <xsl:template match="//tei:head">
        <xsl:element name="head">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="//tei:s">
        <xsl:element name="s">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="//tei:ref">
        <xsl:element name="ref">
            <xsl:attribute name="target">
                <xsl:value-of select="@target"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="//tei:note">
        <xsl:element name="note">
            <xsl:if test="@xml:id">
                <xsl:attribute name="xml:id">
                    <xsl:value-of select="@xml:id"/>
                </xsl:attribute>
            </xsl:if>
            
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="//tei:l">
        <xsl:choose>
            <xsl:when test="parent::tei:p"><xsl:apply-templates/></xsl:when>
            <xsl:when test="parent::tei:div"><lg><l><xsl:apply-templates/></l></lg></xsl:when>
            <xsl:otherwise>
        <xsl:element name="l">
            <xsl:apply-templates/>
        </xsl:element>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="//tei:quote">
        <xsl:choose>
        <xsl:when test="count(parent::tei:p)>0">
        </xsl:when>
            <xsl:otherwise>
                <xsl:element name="quote">
                    <xsl:apply-templates/>
                </xsl:element></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    <xsl:template match="//tei:w">
        <xsl:element name="w">
            <xsl:attribute name="pos">
                <xsl:value-of select="@pos"/>
            </xsl:attribute>
            <xsl:attribute name="lemma">
                <xsl:value-of select="@lemma"/>
            </xsl:attribute>
            <xsl:if test="@n">
                <xsl:attribute name="n">
                    <xsl:value-of select="@n"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="@*">
        <xsl:copy/>
    </xsl:template>
    <xsl:template match="//tei:front|//tei:back">
        <xsl:choose>
            <xsl:when test="child::tei:div[@type='liminal']">
                <xsl:apply-templates/>
            </xsl:when>
            <xsl:otherwise><div type="liminal">
                <xsl:apply-templates/>
            </div></xsl:otherwise>
        
        </xsl:choose>
    </xsl:template>
    <xsl:template match="//tei:body//tei:title|tei//hi|//tei:emph|//tei:corr">
        <hi><xsl:apply-templates/></hi>
    </xsl:template>
    <xsl:template match="//tei:body|//tei:milestone|//tei:gap">
        <xsl:apply-templates/></xsl:template>
    <xsl:template match="//tei:lg">
        <xsl:element name="lg" >
                <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="//tei:extent">
        <xsl:if test="//tei:measure/@unit='words'">
            <xsl:element name="measure">
                <xsl:attribute name="unit">word</xsl:attribute>
            </xsl:element>
            <xsl:value-of select="//tei:measure[@unit='words']"/>
        </xsl:if>  
    </xsl:template>
    <xsl:template match="tei:*">
        <xsl:element name="{local-name()}">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:element>
    </xsl:template>
    

</xsl:stylesheet>
