<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.12.3-București" hasScaleBasedVisibilityFlag="0" maxScale="0" minScale="1e+08" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>0</Searchable>
  </flags>
  <customproperties>
    <property key="WMSBackgroundLayer" value="false"/>
    <property key="WMSPublishDataSourceUrl" value="false"/>
    <property key="embeddedWidgets/count" value="0"/>
  </customproperties>
  <pipe>
    <rasterrenderer alphaBand="-1" nodataColor="" type="singlebandpseudocolor" band="1" opacity="0.5" classificationMin="7" classificationMax="inf">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader classificationMode="2" colorRampType="DISCRETE" clip="0">
          <colorramp type="cpt-city" name="[source]">
            <prop v="0" k="inverted"/>
            <prop v="cpt-city" k="rampType"/>
            <prop v="cb/qual/Set3" k="schemeName"/>
            <prop v="_08" k="variantName"/>
          </colorramp>
          <item label="&lt;= 7" alpha="255" color="#d0d0d0" value="7"/>
          <item label="7 - 10" alpha="255" color="#bebada" value="10"/>
          <item label="10 - 20" alpha="255" color="#80b1d3" value="20"/>
          <item label="20 - 48" alpha="255" color="#b3de69" value="48"/>
          <item label="> 48" alpha="255" color="#e31a1c" value="inf"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast contrast="0" brightness="0"/>
    <huesaturation saturation="0" colorizeBlue="128" grayscaleMode="0" colorizeOn="0" colorizeGreen="128" colorizeRed="255" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
