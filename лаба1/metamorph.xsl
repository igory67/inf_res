<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="UTF-8"/>

<xsl:key name="unique" match="another-students-db-a-group" 
         use="concat(name, '|', term-number, '|', study-year, '|', 
                substring(created-at,1,10), '|', substring(updated-at,1,10), '|', old-name)" />

<xsl:template match="/">
<pre>
CREATE TABLE another_students_db_a_group (
    id INTEGER,
    name VARCHAR(50),
    old_name VARCHAR(50),
    term_number INTEGER,
    study_year VARCHAR(9),
    created_at DATE,
    updated_at DATE
);

INSERT ALL
<xsl:for-each select="//another-students-db-a-group[
    generate-id() = generate-id(key('unique', 
        concat(name, '|', term-number, '|', study-year, '|',
               substring(created-at,1,10), '|', substring(updated-at,1,10), '|', old-name))[1])]">

    INTO another_students_db_a_group VALUES (<xsl:value-of select="id + 10000"/>, '<xsl:value-of select="name"/>', 
    <xsl:choose>
        <xsl:when test="old-name/@nil='true' or old-name=''">NULL</xsl:when>
        <xsl:otherwise>'<xsl:value-of select="old-name"/>'</xsl:otherwise>
    </xsl:choose>
    , <xsl:value-of select="term-number"/>, '<xsl:value-of select="study-year"/>', 
    '<xsl:value-of select="substring(created-at,1,10)"/>', 
    '<xsl:value-of select="substring(updated-at,1,10)"/>')
</xsl:for-each>
SELECT * FROM dual;
</pre>
</xsl:template>

</xsl:stylesheet>