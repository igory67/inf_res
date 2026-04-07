<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="data">
<xsl:variable name="longest">
<xsl:for-each select="option">
<xsl:sort data-type="number" select="string-length()"
order="descending"/>
<xsl:if test="position()=1">
<xsl:value-of select="."/>
</xsl:if>
</xsl:for-each>
</xsl:variable>
Longest string is '<xsl:value-of select="$longest"/>'
</xsl:template>
</xsl:stylesheet>
