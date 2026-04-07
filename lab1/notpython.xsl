<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="UTF-8"/>

  <xsl:template match="/">
    <xsl:variable name="longest">
      <xsl:for-each select="//name">
        <xsl:sort select="string-length()" data-type="number" order="descending"/>
        <xsl:if test="position()=1">
          <xsl:copy-of select="."/>
        </xsl:if>
      </xsl:for-each>
    </xsl:variable>

    Longest string is '<xsl:value-of select="$longest"/>'
  </xsl:template>
</xsl:stylesheet>
