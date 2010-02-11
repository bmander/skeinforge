"""
Svg_codec is a class and collection of utilities to read from and write to an svg file.

Svg_codec uses the svg_layer.template file in the same folder as svg_codec, to output an svg file.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools.skeinforge_utilities import triangle_mesh
import cStringIO
import math
import os


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getCarving( fileName ):
	"Get a carving for the file using an import plugin."
	importPluginFileNames = interpret.getImportPluginFileNames()
	for importPluginFileName in importPluginFileNames:
		fileTypeDot = '.' + importPluginFileName
		if fileName[ - len( fileTypeDot ) : ].lower() == fileTypeDot:
			importPluginsDirectoryPath = gcodec.getAbsoluteFolderPath( os.path.dirname( __file__ ), 'import_plugins' )
			pluginModule = gcodec.getModuleWithDirectoryPath( importPluginsDirectoryPath, importPluginFileName )
			if pluginModule != None:
				return pluginModule.getCarving( fileName )
	print( 'Could not find plugin to handle ' + fileName )
	return None

def getParameterFromJavascript( lines, parameterName, parameterValue ):
	"Get a parameter from lines of javascript."
	for line in lines:
		strippedLine = line.replace( ';', ' ' ).lstrip()
		splitLine = strippedLine.split()
		firstWord = gcodec.getFirstWord( splitLine )
		if firstWord == parameterName:
			return float( splitLine[ 2 ] )
	return parameterValue

def getReplacedInQuotes( original, replacement, text ):
	"Replace what follows in quotes after the word."
	wordAndQuote = original + '="'
	originalIndexStart = text.find( wordAndQuote )
	if originalIndexStart == - 1:
		return text
	originalIndexEnd = text.find( '"', originalIndexStart + len( wordAndQuote ) )
	if originalIndexEnd == - 1:
		return text
	wordAndBothQuotes = text[ originalIndexStart : originalIndexEnd + 1 ]
	return text.replace( wordAndBothQuotes, wordAndQuote + replacement + '"' )

def getReplaceWithLine( line, replaceWithTable ):
	"Parse the line and replace it a table key is in the line."
	for replaceWithTableKey in replaceWithTable.keys():
		if line.find( replaceWithTableKey ) > - 1:
			return line.replace( replaceWithTableKey, replaceWithTable[ replaceWithTableKey ] )
	return line

def getReplacedWordAndInQuotes( original, replacement, text ):
	"Replace the word in the text and replace what follows in quotes after the word."
	text = text.replace( 'replaceWith_' + original, replacement )
	return getReplacedInQuotes( original, replacement, text )

def parseLineReplaceWithTable( firstWordTable, line, output, replaceWithTable ):
	"Parse the line and replace it if the first word of the line is in the first word table."
	firstWord = gcodec.getFirstWordFromLine( line )
	if firstWord in firstWordTable:
		line = firstWordTable[ firstWord ]
	elif line.find( 'replaceWith' ) > - 1:
		line = getReplaceWithLine( line, replaceWithTable )
	gcodec.addLineAndNewlineIfNecessary( line, output )


class SVGCodecSkein:
	"A base class to get an svg skein from a carving."
	def __init__( self ):
		self.margin = 20
		self.output = cStringIO.StringIO()
		self.textHeight = 22.5
		self.unitScale = 3.7

	def addLayerBegin( self, layerIndex, z ):
		"Add the start lines for the layer."
#		y = (1 * i + 1) * ( margin + sliceDimY * unitScale) + i * txtHeight
		layerTranslateY = layerIndex * self.textHeight + ( layerIndex + 1 ) * ( self.extent.y * self.unitScale + self.margin )
		zRounded = self.getRounded( z )
		self.addLine( '\t\t<g id="z %s" transform="translate(%s, %s)">' % ( zRounded, self.getRounded( self.margin ), self.getRounded( layerTranslateY ) ) )
		self.addLine( '\t\t\t<text y="15" fill="#000" stroke="none">Layer %s, z %s</text>' % ( layerIndex, zRounded ) )
#		<g id="z 0.1" transform="translate(20, 242)">
#			<text y="15" fill="#000" stroke="none">Layer 1, z 0.1</text>
#	unit scale (mm=3.7, in=96)
#	
#	g transform
#		x = margin
#		y = (layer + 1) * ( margin + (slice height * unit scale)) + (layer * 20)
#
#	text
#		y = text height
#
#	path transform
#		scale = (unit scale) (-1 * unitscale)
#		translate = (-1 * minX) (-1 * minY)

	def addLayerEnd( self, rotatedBoundaryLayer ):
		"Add the path and end lines for the layer."
		pathString = '\t\t\t<path transform="scale(%s, %s) translate(%s, %s)" d="' % ( self.unitScale, - self.unitScale, self.getRounded( - self.cornerMinimum.x ), self.getRounded( - self.cornerMinimum.y ) )
		if len( rotatedBoundaryLayer.loops ) > 0:
			pathString += self.getSVGLoopString( rotatedBoundaryLayer.loops[ 0 ] )
		for loop in rotatedBoundaryLayer.loops[ 1 : ]:
			pathString += ' ' + self.getSVGLoopString( loop )
		pathString += '"/>'
		self.addLine( pathString )
		self.addLine( '\t\t</g>' )

	def addRotatedLoopLayerToOutput( self, layerIndex, rotatedBoundaryLayer ):
		"Add rotated boundary layer to the output."
		self.addLayerBegin( layerIndex, rotatedBoundaryLayer.z )
		self.addLayerEnd( rotatedBoundaryLayer )

	def addRotatedLoopLayersToOutput( self, rotatedBoundaryLayers ):
		"Add rotated boundary layers to the output."
		truncatedRotatedBoundaryLayers = rotatedBoundaryLayers[ self.repository.layersFrom.value : self.repository.layersTo.value ]
		for truncatedRotatedBoundaryLayerIndex in xrange( len( truncatedRotatedBoundaryLayers ) ):
			truncatedRotatedBoundaryLayer = truncatedRotatedBoundaryLayers[ truncatedRotatedBoundaryLayerIndex ]
			self.addRotatedLoopLayerToOutput( truncatedRotatedBoundaryLayerIndex, truncatedRotatedBoundaryLayer )

	def addLine( self, line ):
		"Add a line of text and a newline to the output."
		self.output.write( line + "\n" )

	def addLines( self, lines ):
		"Add lines of text to the output."
		for line in lines:
			self.addLine( line )

	def getInitializationForOutputSVG( self, procedureName ):
		"Get initialization gcode for the output."
		canvasInitializationOutput = cStringIO.StringIO()
		canvasInitializationOutput.write( '\tdecimalPlacesCarried = %s\n' % self.decimalPlacesCarried ) # Set decimal places carried.
		canvasInitializationOutput.write( '\tlayerThickness = %s\n' % self.getRounded( self.layerThickness ) ) # Set layer thickness.
		canvasInitializationOutput.write( '\tperimeterWidth = %s\n' % self.getRounded( self.perimeterWidth ) ) # Set perimeter width.
		canvasInitializationOutput.write( '\tprocedureDone = "%s"\n' % procedureName ) # The procedure done one this svg file.
		canvasInitializationOutput.write( '\textrusionStart = 1\n' ) # Initialization is finished, extrusion is starting.
		return canvasInitializationOutput.getvalue()

	def getReplacedSVGTemplate( self, fileName, procedureName, rotatedBoundaryLayers ):
		"Get the lines of text from the svg_layer.template file."
#( layers.length + 1 ) * (margin + sliceDimY * unitScale + txtHeight) + margin + txtHeight + margin + 110
		self.extent = self.cornerMaximum - self.cornerMinimum
		self.addRotatedLoopLayersToOutput( rotatedBoundaryLayers )
		svgTemplateText = gcodec.getFileTextInFileDirectory( __file__, 'svg_layer.template' )
		svgTemplateText = getReplacedWordAndInQuotes( 'layerThickness', self.getRounded( self.layerThickness ), svgTemplateText )
		svgTemplateText = getReplacedWordAndInQuotes( 'maxX', self.getRounded( self.cornerMaximum.x ), svgTemplateText )
		svgTemplateText = getReplacedWordAndInQuotes( 'minX', self.getRounded( self.cornerMinimum.x ), svgTemplateText )
		svgTemplateText = getReplacedWordAndInQuotes( 'maxY', self.getRounded( self.cornerMaximum.y ), svgTemplateText )
		svgTemplateText = getReplacedWordAndInQuotes( 'minY', self.getRounded( self.cornerMinimum.y ), svgTemplateText )
		svgTemplateText = getReplacedWordAndInQuotes( 'maxZ', self.getRounded( self.cornerMaximum.z ), svgTemplateText )
		svgTemplateText = getReplacedWordAndInQuotes( 'minZ', self.getRounded( self.cornerMinimum.z ), svgTemplateText )
		lines = gcodec.getTextLines( svgTemplateText )
		self.margin = getParameterFromJavascript( lines, 'margin', self.margin )
		self.textHeight = getParameterFromJavascript( lines, 'textHeight', self.textHeight )
		javascriptControlsWidth = getParameterFromJavascript( lines, 'javascripControlBoxX', 510.0 )
		noJavascriptControlsHeight = getParameterFromJavascript( lines, 'noJavascriptControlBoxY', 110.0 )
		controlTop = len( rotatedBoundaryLayers ) * ( self.margin + self.extent.y * self.unitScale + self.textHeight ) + 2.0 * self.margin + self.textHeight
#	width = margin + (sliceDimX * unitScale) + margin;
		width = 2.0 * self.margin + max( self.extent.x * self.unitScale, javascriptControlsWidth )
		summarizedFileName = gcodec.getSummarizedFileName( fileName ) + ' SVG Slice File'
		noJavascriptControlsTagString = '	<g id="noJavascriptControls" fill="#000" transform="translate(%s, %s)">' % ( self.getRounded( self.margin ), self.getRounded( controlTop ) )
		firstWordTable = {}
		firstWordTable[ 'height="999px"' ] = '	height="%spx"' % self.getRounded( controlTop + noJavascriptControlsHeight + self.margin )
		firstWordTable[ 'width="999px"' ] = '	width="%spx"' % self.getRounded( width )
		firstWordTable[ '<!--replaceLineWith_boundaryLayerLines-->' ] = self.output.getvalue()
		firstWordTable[ '<!--replaceLineWith_emptyString-->' ] = ''
		firstWordTable[ '<!--replaceLineWith_noJavascriptControls-->' ] = noJavascriptControlsTagString
		firstWordTable[ '<!--replaceLineWith_sliceVariableLines-->' ] = self.getInitializationForOutputSVG( procedureName )
		replaceWithTable = {}
		replaceWithTable[ 'replaceWith_Title' ] = summarizedFileName
		replaceWithTable[ 'replaceWith_dimX' ] = self.getRounded( self.extent.x )
		replaceWithTable[ 'replaceWith_dimY' ] = self.getRounded( self.extent.y )
		replaceWithTable[ 'replaceWith_dimZ' ] = self.getRounded( self.extent.z )
		output = cStringIO.StringIO()
		for line in lines:
			parseLineReplaceWithTable( firstWordTable, line, output, replaceWithTable )
		return output.getvalue()

	def getRounded( self, number ):
		"Get number rounded to the number of carried decimal places as a string."
		return euclidean.getRoundedToDecimalPlacesString( self.decimalPlacesCarried, number )

	def getRoundedComplexString( self, point ):
		"Get the rounded complex string."
		return self.getRounded( point.real ) + ' ' + self.getRounded( point.imag )

	def getSVGLoopString( self, loop ):
		"Get the svg loop string."
		if len( loop ) < 1:
			return ''
		return self.getSVGPathString( loop ) + ' z'

	def getSVGPathString( self, path ):
		"Get the svg path string."
		svgLoopString = ''
		for point in path:
			stringBeginning = 'M '
			if len( svgLoopString ) > 0:
				stringBeginning = ' L '
			svgLoopString += stringBeginning + self.getRoundedComplexString( point )
		return svgLoopString
