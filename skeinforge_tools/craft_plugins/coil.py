"""
This page is in the table of contents.
Coil is a script to coil the outlines.

The default 'Activate Coil' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.

If the 'Add Inner Loops' checkbox is on, inner coiling loops will be added, the default is on.  If the 'Add Outer Loops' checkbox is on, outer coiling loops will be added, the default is on.  If the 'Cross Hatch' checkbox is on, there will be alternating horizontal and vertical coiling paths, if it is off there will only be horizontal coiling paths, the default is on.

The 'Loop Inner Outset over Perimeter Width' times the perimeter width is the amount the inner coiling loop will be outset, the default is 0.5.  The 'Loop Outer Outset over Perimeter Width' times the perimeter width is the amount the outer coiling loop will be outset, the default is 1.0.  The 'Loop Outer Outset over Perimeter Width' ratio should be greater than the 'Loop Inner Outset over Perimeter Width' ratio.

The 'Coil Width over Perimeter Width' times the perimeter width is the width of the coil lines, the default is 1.0.  If the ratio is one, all the material will be coiled.  The greater the 'Coil Width over Perimeter Width' the farther apart the coil lines will be and so less of the material will be directly coiled, the remaining material might still be removed in chips if the ratio is not much greater than one.

The following examples coil the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and coil.py.


> python coil.py
This brings up the coil dialog.


> python coil.py Screw Holder Bottom.stl
The coil tool is parsing the file:
Screw Holder Bottom.stl
..
The coil tool has created the file:
Screw Holder Bottom_coil.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import coil
>>> coil.main()
This brings up the coil dialog.


>>> coil.writeOutput( 'Screw Holder Bottom.stl' )
Screw Holder Bottom.stl
The coil tool is parsing the file:
Screw Holder Bottom.stl
..
The coil tool has created the file:
Screw Holder Bottom_coil.gcode


"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools import profile
from skeinforge_tools.meta_plugins import polyfile
from skeinforge_tools.skeinforge_utilities import consecution
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import intercircle
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools.skeinforge_utilities import settings
from skeinforge_tools.skeinforge_utilities import triangle_mesh
from skeinforge_tools.skeinforge_utilities.vector3 import Vector3
import os
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getCraftedText( fileName, gcodeText = '', repository = None ):
	"Coil the file or gcodeText."
	return getCraftedTextFromText( gcodec.getTextIfEmpty( fileName, gcodeText ), repository )

def getCraftedTextFromText( gcodeText, repository = None ):
	"Coil a gcode linear move gcodeText."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'coil' ):
		return gcodeText
	if repository == None:
		repository = settings.getReadRepository( CoilRepository() )
	if not repository.activateCoil.value:
		return gcodeText
	return CoilSkein().getCraftedGcode( gcodeText, repository )

def getNewRepository():
	"Get the repository constructor."
	return CoilRepository()

def writeOutput( fileName = '' ):
	"Coil a gcode linear move file."
	fileName = interpret.getFirstTranslatorFileNameUnmodified( fileName )
	if fileName == '':
		return
	consecution.writeChainTextWithNounMessage( fileName, 'coil' )


class CoilRepository:
	"A class to handle the coil settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		profile.addListsToCraftTypeRepository( 'skeinforge_tools.craft_plugins.coil.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Coil', self, '' )
		self.activateCoil = settings.BooleanSetting().getFromValue( 'Activate Coil', self, True )
		self.minimumToolDistance = settings.FloatSpin().getFromValue( 10.0, 'Minimum Tool Distance (millimeters):', self, 50.0, 20.0 )
		self.executeTitle = 'Coil'

	def execute( self ):
		"Coil button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )



class CoilSkein:
	"A class to coil a skein of extrusions."
	def __init__( self ):
		self.boundaryLayers = []
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.lineIndex = 0
		self.lines = None
		self.oldLocationComplex = complex()
		self.perimeterWidth = 0.6
		self.shutdownLines = []

	def addCoilLayer( self, boundaryLayers, radius, z ):
		"Add a coil layer."
		self.distanceFeedRate.addLine( '(<layer> %s )' % z ) # Indicate that a new layer is starting.
		self.distanceFeedRate.addLine( '(<surroundingLoop>)' )
		thread = []
		for boundaryLayerIndex in xrange( 1, len( boundaryLayers ) - 1 ):
			boundaryLayer = boundaryLayers[ boundaryLayerIndex ]
			boundaryLayerBegin = boundaryLayers[ boundaryLayerIndex - 1 ]
			boundaryLayerEnd = boundaryLayers[ boundaryLayerIndex + 1 ]
			beginLocation = Vector3( 0.0, 0.0, 0.5 * ( boundaryLayerBegin.z + boundaryLayer.z ) )
			outsetLoop = intercircle.getLargestInsetLoopFromLoop( boundaryLayer.loops[ 0 ], - radius )
			self.addCoilToThread( beginLocation, 0.5 * ( boundaryLayer.z + boundaryLayerEnd.z ), outsetLoop, thread )
		self.addGcodeFromThread( thread )
		self.distanceFeedRate.addLine( '(</surroundingLoop>)' )
		self.distanceFeedRate.addLine( '(</layer>)' )

	def addCoilLayers( self ):
		"Add the coil layers."
		numberOfLayersFloat = round( self.perimeterWidth / self.layerThickness )
		numberOfLayers = int( numberOfLayersFloat )
		halfLayerThickness = 0.5 * self.layerThickness
		startOutset = self.repository.minimumToolDistance.value + halfLayerThickness
		startZ = self.boundaryLayers[ 0 ].z + halfLayerThickness
		zRange = self.boundaryLayers[ - 1 ].z - self.boundaryLayers[ 0 ].z
		zIncrement = 0.0
		if zRange >= 0.0:
			zIncrement = zRange / numberOfLayersFloat
		for layerIndex in xrange( numberOfLayers ):
			boundaryLayers = self.boundaryLayers
			if layerIndex % 2 == 1:
				boundaryLayers = self.boundaryReverseLayers
			radius = startOutset + layerIndex * self.layerThickness
			z = startZ + layerIndex * zIncrement
			self.addCoilLayer( boundaryLayers, radius, z )

	def addCoilToThread( self, beginLocation, endZ, loop, thread ):
		"Add a coil to the thread."
		if len( loop ) < 1:
			return
		loop = euclidean.getLoopStartingNearest( self.halfPerimeterWidth, self.oldLocationComplex, loop )
		length = euclidean.getPolygonLength( loop )
		if length <= 0.0:
			return
		oldPoint = loop[ 0 ]
		pathLength = 0.0
		for point in loop[ 1 : ]:
			pathLength += abs( point - oldPoint )
			along = pathLength / length
			z = ( 1.0 - along ) * beginLocation.z + along * endZ
			location = Vector3( point.real, point.imag, z )
			thread.append( location )
			oldPoint = point
		self.oldLocationComplex = loop[ - 1 ]

	def addGcodeFromThread( self, thread ):
		"Add a thread to the output."
		if len( thread ) > 0:
			firstLocation = thread[ 0 ]
			self.distanceFeedRate.addGcodeMovementZ( firstLocation.dropAxis( 2 ), firstLocation.z )
		else:
			print( "zero length vertex positions array which was skipped over, this should never happen" )
		if len( thread ) < 2:
			print( "thread of only one point in addGcodeFromThread in coil, this should never happen" )
			print( thread )
			return
		self.distanceFeedRate.addLine( "M101" ) # Turn extruder on.
		for location in thread[ 1 : ]:
			self.distanceFeedRate.addGcodeMovementZ( location.dropAxis( 2 ), location.z )
		self.distanceFeedRate.addLine( "M103" ) # Turn extruder off.

	def getCraftedGcode( self, gcodeText, repository ):
		"Parse gcode text and store the coil gcode."
		self.repository = repository
		self.lines = gcodec.getTextLines( gcodeText )
		self.parseInitialization()
		self.parseBoundaries()
		self.parseUntilLayer()
		self.addCoilLayers()
		self.distanceFeedRate.addLines( self.shutdownLines )
		return self.distanceFeedRate.output.getvalue()

	def parseBoundaries( self ):
		"Parse the boundaries and add them to the boundary layers."
		boundaryLoop = None
		boundaryLayer = None
		for line in self.lines[ self.lineIndex : ]:
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			if len( self.shutdownLines ) > 0:
				self.shutdownLines.append( line )
			if firstWord == '(</boundaryPerimeter>)':
				boundaryLoop = None
			elif firstWord == '(<boundaryPoint>':
				location = gcodec.getLocationFromSplitLine( None, splitLine )
				if boundaryLoop == None:
					boundaryLoop = []
					boundaryLayer.loops.append( boundaryLoop )
				boundaryLoop.append( location.dropAxis( 2 ) )
			elif firstWord == '(<layer>':
				boundaryLayer = euclidean.LoopLayer( float( splitLine[ 1 ] ) )
				self.boundaryLayers.append( boundaryLayer )
			elif firstWord == '(</extrusion>)':
				self.shutdownLines = [ line ]
		for boundaryLayer in self.boundaryLayers:
			if not euclidean.isWiddershins( boundaryLayer.loops[ 0 ] ):
				boundaryLayer.loops[ 0 ].reverse()
		self.boundaryReverseLayers = self.boundaryLayers[ : ]
		self.boundaryReverseLayers.reverse()

	def parseInitialization( self ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine( '(<procedureDone> coil </procedureDone>)' )
				return
			elif firstWord == '(<layerThickness>':
				self.layerThickness = float( splitLine[ 1 ] )
			elif firstWord == '(<perimeterWidth>':
				self.perimeterWidth = float( splitLine[ 1 ] )
				self.halfPerimeterWidth = 0.5 * self.perimeterWidth
			self.distanceFeedRate.addLine( line )

	def parseUntilLayer( self ):
		"Parse until the layer line and add it to the coil skein."
		for self.lineIndex in xrange( self.lineIndex, len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == '(<layer>':
				return
			self.distanceFeedRate.addLine( line )


def main():
	"Display the coil dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
