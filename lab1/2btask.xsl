<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    version="1.0"
    xmlns="http://www.w3.org/1999/xhtml">
    
<xsl:output method="html" encoding="UTF-8" doctype-system="about:legacy-doctype"/>

<!-- Ключи для подсчета уникальных значений -->
<xsl:key name="id-values" match="id" use="."/>
<xsl:key name="name-values" match="name" use="."/>
<xsl:key name="old-name-values" match="old-name" use="."/>
<xsl:key name="term-number-values" match="term-number" use="."/>
<xsl:key name="study-year-values" match="study-year" use="."/>
<xsl:key name="created-at-values" match="created-at" use="."/>
<xsl:key name="updated-at-values" match="updated-at" use="."/>

<xsl:template match="/">
<html>
<head>
    <title>Анализ XML</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
</head>
<body>
    <h2>Результат анализа XML-файла</h2>
    
    <h3>а) Названия полей, входящих в сущность another-students-db-a-group:</h3>
    <ul>
    <xsl:for-each select="//another-students-db-a-group[1]/*">
        <li><xsl:value-of select="name()"/></li>
    </xsl:for-each>
    </ul>
    
    <h3>б) Характеристики полей:</h3>
    <table border="1" cellpadding="5">
        <tr bgcolor="#CCCCCC">
            <th>Поле</th>
            <th>Тип данных</th>
            <th>Макс. длина</th>
            <th>Ограничения</th>
        </tr>
        
        <!-- ID -->
        <tr>
            <td>id</td>
            <td>integer</td>
            <td>-</td>
            <td><xsl:call-template name="check-field">
                <xsl:with-param name="name" select="'id'"/>
                <xsl:with-param name="always" select="true()"/>
            </xsl:call-template></td>
        </tr>
        
        <!-- NAME -->
        <tr>
            <td>name</td>
            <td>string</td>
            <td><xsl:call-template name="max-len"><xsl:with-param name="nodes" select="//name"/></xsl:call-template></td>
            <td><xsl:call-template name="check-field">
                <xsl:with-param name="name" select="'name'"/>
                <xsl:with-param name="always" select="true()"/>
            </xsl:call-template></td>
        </tr>
        
        <!-- OLD-NAME -->
        <tr>
            <td>old-name</td>
            <td>string</td>
            <td><xsl:call-template name="max-len"><xsl:with-param name="nodes" select="//old-name[not(@nil='true')]"/></xsl:call-template></td>
            <td><xsl:call-template name="check-field">
                <xsl:with-param name="name" select="'old-name'"/>
                <xsl:with-param name="always" select="false()"/>
            </xsl:call-template></td>
        </tr>
        
        <!-- TERM-NUMBER -->
        <tr>
            <td>term-number</td>
            <td>integer</td>
            <td>-</td>
            <td><xsl:call-template name="check-field">
                <xsl:with-param name="name" select="'term-number'"/>
                <xsl:with-param name="always" select="true()"/>
            </xsl:call-template></td>
        </tr>
        
        <!-- STUDY-YEAR -->
        <tr>
            <td>study-year</td>
            <td>string</td>
            <td><xsl:call-template name="max-len"><xsl:with-param name="nodes" select="//study-year"/></xsl:call-template></td>
            <td><xsl:call-template name="check-field">
                <xsl:with-param name="name" select="'study-year'"/>
                <xsl:with-param name="always" select="true()"/>
            </xsl:call-template></td>
        </tr>
        
        <!-- CREATED-AT -->
        <tr>
            <td>created-at</td>
            <td>datetime</td>
            <td>-</td>
            <td>NOT NULL</td>
        </tr>
        
        <!-- UPDATED-AT -->
        <tr>
            <td>updated-at</td>
            <td>datetime</td>
            <td>-</td>
            <td>NOT NULL</td>
        </tr>
    </table>
</body>
</html>
</xsl:template>

<!-- Вычисление максимальной длины -->
<xsl:template name="max-len">
    <xsl:param name="nodes"/>
    <xsl:param name="max" select="0"/>
    <xsl:for-each select="$nodes">
        <xsl:variable name="len" select="string-length(.)"/>
        <xsl:variable name="new-max">
            <xsl:choose>
                <xsl:when test="$len > $max"><xsl:value-of select="$len"/></xsl:when>
                <xsl:otherwise><xsl:value-of select="$max"/></xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:call-template name="max-len">
            <xsl:with-param name="nodes" select="$nodes[position() > 1]"/>
            <xsl:with-param name="max" select="$new-max"/>
        </xsl:call-template>
    </xsl:for-each>
    <xsl:if test="not($nodes)"><xsl:value-of select="$max"/></xsl:if>
</xsl:template>

<!-- Проверка ограничений -->
<xsl:template name="check-field">
    <xsl:param name="name"/>
    <xsl:param name="always"/>
    
    <xsl:variable name="values" select="//*[name()=$name]"/>
    <xsl:variable name="unique" select="//*[name()=$name][
        generate-id() = generate-id(key(concat($name,'-values'), .))
    ]"/>
    <xsl:variable name="nulls" select="count($values[. = '' or @nil='true'])"/>
    <xsl:variable name="total" select="count($values)"/>
    <xsl:variable name="unique-count" select="count($unique[not(. = '' or @nil='true')])"/>
    
    <xsl:if test="$always and $nulls = 0">
        <xsl:text>NOT NULL</xsl:text>
    </xsl:if>
    
    <xsl:if test="$unique-count >= 2 and $unique-count &lt;= 5">
        <xsl:if test="$always and $nulls = 0">
            <xsl:text>, </xsl:text>
        </xsl:if>
        <xsl:text>CHECK (</xsl:text>
        <xsl:for-each select="$unique[not(. = '' or @nil='true')]">
            <xsl:if test="position() > 1">, </xsl:if>
            <xsl:value-of select="."/>
        </xsl:for-each>
        <xsl:text>)</xsl:text>
    </xsl:if>
    
    <xsl:if test="not($always and $nulls = 0) and not($unique-count >= 2 and $unique-count &lt;= 5)">
        <xsl:text>нет</xsl:text>
    </xsl:if>
</xsl:template>

</xsl:stylesheet>