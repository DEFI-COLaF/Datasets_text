<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="xml" indent="yes" encoding="UTF-8" xmlns="http://www.tei-c.org/ns/1.0"/>
    <xsl:strip-space elements="*"/>
    <xsl:template match="TEI">
        <text>
            <body>
        <xsl:apply-templates select="text"/>
                </body>
        </text>
    </xsl:template>
    <xsl:template match="sp">
        <sp>
            <xsl:attribute name="who">
                <xsl:value-of select="@who"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </sp>
    </xsl:template>
    <xsl:template match="text/front">
        <div type="liminal">
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    <!--<xsl:template match="body">
        <body>
            <xsl:apply-templates/>
        </body>
    </xsl:template>-->
    <xsl:template match="l">
        <l>
            <xsl:apply-templates/>
        </l>
    </xsl:template>
    <xsl:template match="div1">
        <div type="act">
            <xsl:attribute name="n">
                <xsl:value-of select="@n"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    <xsl:template match="div2">
        <div type="scene">
            <xsl:attribute name="n">
                <xsl:value-of select="@n"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    <xsl:template match="speaker">
        <speaker>
            <xsl:apply-templates/>
        </speaker>
    </xsl:template>
    <xsl:template match="head">
        <head>
            <xsl:apply-templates/>
        </head>
    </xsl:template>
    <xsl:template match="docTitle">
        <div type="titlepage">
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    <xsl:template match="titlePart|docDate|docAuthor|premiere|adresse|teiacheveImprime">
        <div type="liminal">
        <p>
            <xsl:apply-templates/>
        </p>
        </div>
    </xsl:template>
    <xsl:template match="privilege|div[@type='preface']">
        <div type="liminal">
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    <xsl:template match="p">
        <p>
            <xsl:apply-templates/>
        </p>
    </xsl:template>
    <xsl:template match="front|performance"><xsl:apply-templates></xsl:apply-templates></xsl:template>
    <xsl:template match="div[@type='dedicace']">
        <div type="liminal">
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    <xsl:template match="castList">
        <list>
            <xsl:apply-templates/></list>
    </xsl:template>
    <xsl:template match="castItem">
        <item><xsl:value-of select="."/></item>
    </xsl:template>
    <xsl:template match="set">
        <p><xsl:apply-templates/></p>
    </xsl:template>
    <xsl:template match="stage">
        <stage><xsl:apply-templates/></stage>
    </xsl:template>
    <xsl:template match="note">
        <note><xsl:apply-templates/></note>
    </xsl:template>
</xsl:stylesheet>
