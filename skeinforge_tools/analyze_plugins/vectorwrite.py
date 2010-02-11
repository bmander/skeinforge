"""
This page is in the table of contents.
Vectorwrite is a script to write Scalable Vector Graphics for a gcode file.

The vectorwrite manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Vectorwrite

Vectorwrite generates a Scalable Vector Graphics file which can be opened by an SVG viewer or an SVG capable browser like Mozilla:
http://www.mozilla.com/firefox/

==Operation==
The default 'Activate Vectorwrite' checkbox is on.  When it is on, the functions described below will work when called from the skeinforge toolchain, when it is off, the functions will not be called from the toolchain.  The functions will still be called, whether or not the 'Activate Vectorwrite' checkbox is on, when vectorwrite is run directly.

==Settings==

===Layers===

====Layers From====
Default is zero.

The "Layers From" is the index of the bottom layer that will be displayed.  If the layer from is the default zero, the display will start from the lowest layer.  If the the layer from index is negative, then the display will start from the layer from index below the top layer.

====Layers To====
Default is a huge number, which will be limited to the highest index layer.

The "Layers To" is the index of the top layer that will be displayed.  If the layer to index is a huge number like the default, the display will go to the top of the model, at least until we model habitats:)  If the layer to index is negative, then the display will go to the layer to index below the top layer.  The layer from until layer to index is a python slice.

==Examples==

Below are examples of vectorwrite being used.  These examples are run in a terminal in the folder which contains Screw Holder_penultimate.gcode and vectorwrite.py.


> python vectorwrite.py
This brings up the vectorwrite dialog.


> python vectorwrite.py Screw Holder_penultimate.gcode
The vectorwrite file is saved as Screw_Holder_penultimate_vectorwrite.svg


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import vectorwrite
>>> vectorwrite.main()
This brings up the vectorwrite dialog.


>>> vectorwrite.analyzeFile( 'Screw Holder_penultimate.gcode' )
The vectorwrite file is saved as Screw_Holder_penultimate_vectorwrite.svg

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities.vector3 import Vector3
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import settings
from skeinforge_tools.skeinforge_utilities import svg_codec
from skeinforge_tools.meta_plugins import polyfile
import cStringIO
import os
import sys
import time

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


#maybe add open webbrowser first time file is created choice
def analyzeFile( fileName ):
	"Write scalable vector graphics for a gcode file."
	gcodeText = gcodec.getFileText( fileName )
	analyzeFileGivenText( fileName, gcodeText )

def analyzeFileGivenText( fileName, gcodeText, repository = None ):
	"Write scalable vector graphics for a gcode file given the settings."
	if gcodeText == '':
		return ''
	if repository == None:
		repository = settings.getReadRepository( VectorwriteRepository() )
	startTime = time.time()
	vectorwriteGcode = VectorwriteSkein().getSVG( fileName, gcodeText, repository )
	if vectorwriteGcode == '':
		return
	suffixFileName = fileName[ : fileName.rfind( '.' ) ] + '_vectorwrite.svg'
	suffixDirectoryName = os.path.dirname( suffixFileName )
	suffixReplacedBaseName = os.path.basename( suffixFileName ).replace( ' ', '_' )
	suffixFileName = os.path.join( suffixDirectoryName, suffixReplacedBaseName )
	gcodec.writeFileText( suffixFileName, vectorwriteGcode )
	print( 'The vectorwrite file is saved as ' + gcodec.getSummarizedFileName( suffixFileName ) )
	print( 'It took ' + str( int( round( time.time() - startTime ) ) ) + ' seconds to vectorwrite the file.' )
	settings.openWebPage( suffixFileName )

def getNewRepository():
	"Get the repository constructor."
	return VectorwriteRepository()

def writeOutput( fileName, gcodeText = '' ):
	"Write scalable vector graphics for a skeinforge gcode file, if activate vectorwrite is selected."
	repository = settings.getReadRepository( VectorwriteRepository() )
	if not repository.activateVectorwrite.value:
		return
	gcodeText = gcodec.getTextIfEmpty( fileName, gcodeText )
	analyzeFileGivenText( fileName, gcodeText, repository )


class ThreadLayer:
	"Threads with a z."
	def __init__( self, z ):
		self.boundaryLoops = []
		self.innerPerimeters = []
		self.loops = []
		self.outerPerimeters = []
		self.paths = []
		self.z = z

	def __repr__( self ):
		"Get the string representation of this loop layer."
		return '%s, %s' % ( self.innerLoops, self.innerPerimeters, self.outerLoops, self.outerPerimeters, self.paths, self.z )


class VectorwriteRepository:
	"A class to handle the vectorwrite settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge_tools.analyze_plugins.vectorwrite.html', '', self )
		self.activateVectorwrite = settings.BooleanSetting().getFromValue( 'Activate Vectorwrite', self, False )
		self.fileNameInput = settings.FileNameInput().getFromFileName( [ ( 'Gcode text files', '*.gcode' ) ], 'Open File to Write Vector Graphics for', self, '' )
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute( 'http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Vectorwrite' )
		self.layersFrom = settings.IntSpin().getFromValue( 0, 'Layers From (index):', self, 20, 0 )
		self.layersTo = settings.IntSpin().getSingleIncrementFromValue( 0, 'Layers To (index):', self, 912345678, 912345678 )
		#Create the archive, title of the execute button, title of the dialog & settings fileName.
		self.executeTitle = 'Vectorwrite'

	def execute( self ):
		"Write button has been clicked."
		fileNames = polyfile.getFileOrGcodeDirectory( self.fileNameInput.value, self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			analyzeFile( fileName )


class VectorwriteSkein( svg_codec.SVGCodecSkein ):
	"A class to vectorwrite a carving."
	def addLoops( self, loops, pathStart ):
		"Add loops to the output."
		loopString = ''
		for loop in loops:
			loopString += self.getSVGLoopString( loop ) + ' '
		if len( loopString ) > 0:
			self.addLine( pathStart + loopString[ : - 1 ] + '"/>' )

	def addPaths( self, colorName, paths, pathStart ):
		"Add paths to the output."
		pathString = ''
		for path in paths:
			pathString += self.getSVGPathString( path ) + ' '
		if len( pathString ) > 0:
			self.addLine( pathStart + pathString[ : - 1 ] + '" fill="none" stroke="%s"/>' % colorName )

	def addRotatedLoopLayer( self, z ):
		"Add rotated loop layer."
		self.rotatedBoundaryLayer = ThreadLayer( z )
		self.rotatedBoundaryLayers.append( self.rotatedBoundaryLayer )

	def addRotatedLoopLayerToOutput( self, layerIndex, rotatedBoundaryLayer ):
		"Add rotated boundary layer to the output."
		self.addLayerBegin( layerIndex, rotatedBoundaryLayer.z )
		pathStart = '\t\t\t<path transform="scale(%s, %s) translate(%s, %s)" d="' % ( self.unitScale, - self.unitScale, self.getRounded( - self.cornerMinimum.x ), self.getRounded( - self.cornerMinimum.y ) )
		self.addLoops( rotatedBoundaryLayer.boundaryLoops, pathStart )
		self.addPaths( '#fa0', rotatedBoundaryLayer.innerPerimeters, pathStart ) #orange
		self.addPaths( '#ff0', rotatedBoundaryLayer.loops, pathStart ) #yellow
		self.addPaths( '#f00', rotatedBoundaryLayer.outerPerimeters, pathStart ) #red
		self.addPaths( '#f5c', rotatedBoundaryLayer.paths, pathStart ) #light violetred
		self.addLine( '\t\t</g>' )

	def addToLoops( self ):
		"Add the thread to the loops."
		self.isLoop = False
		if len( self.thread ) < 1:
			return
		self.rotatedBoundaryLayer.loops.append( self.thread )
		self.thread = []

	def addToPerimeters( self ):
		"Add the thread to the perimeters."
		self.isPerimeter = False
		if len( self.thread ) < 1:
			return
		if self.isOuter:
			self.rotatedBoundaryLayer.outerPerimeters.append( self.thread )
		else:
			self.rotatedBoundaryLayer.innerPerimeters.append( self.thread )
		self.thread = []

	def getSVG( self, fileName, gcodeText, repository ):
		"Parse gnu triangulated surface text and store the vectorwrite gcode."
		self.boundaryLoop = None
		self.cornerMaximum = Vector3( - 999999999.0, - 999999999.0, - 999999999.0 )
		self.cornerMinimum = Vector3( 999999999.0, 999999999.0, 999999999.0 )
		self.extruderActive = False
		self.isLoop = False
		self.isOuter = False
		self.isPerimeter = False
		self.lines = gcodec.getTextLines( gcodeText )
		self.oldLocation = None
		self.thread = []
		self.rotatedBoundaryLayers = []
		self.repository = repository
		self.parseInitialization()
		for line in self.lines[ self.lineIndex : ]:
			self.parseLine( line )
		return self.getReplacedSVGTemplate( fileName, 'vectorwrite', self.rotatedBoundaryLayers )

	def linearMove( self, splitLine ):
		"Get statistics for a linear move."
		location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
		self.cornerMaximum = euclidean.getPointMaximum( self.cornerMaximum, location )
		self.cornerMinimum = euclidean.getPointMinimum( self.cornerMinimum, location )
		if self.extruderActive:
			if len( self.thread ) == 0:
				self.thread = [ self.oldLocation.dropAxis( 2 ) ]
			self.thread.append( location.dropAxis( 2 ) )
		self.oldLocation = location

	def parseInitialization( self ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			if firstWord == '(<decimalPlacesCarried>':
				self.decimalPlacesCarried = int( splitLine[ 1 ] )
			elif firstWord == '(<layerThickness>':
				self.layerThickness = float( splitLine[ 1 ] )
			elif firstWord == '(<extrusion>)':
				return
			elif firstWord == '(<perimeterWidth>':
				self.perimeterWidth = float( splitLine[ 1 ] )

	def parseLine( self, line ):
		"Parse a gcode line and add it to the outset skein."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if firstWord == 'G1':
			self.linearMove( splitLine )
		elif firstWord == 'M101':
			self.extruderActive = True
		elif firstWord == 'M103':
			self.extruderActive = False
			if self.isLoop:
				self.addToLoops()
				return
			if self.isPerimeter:
				self.addToPerimeters()
				return
			self.rotatedBoundaryLayer.paths.append( self.thread )
			self.thread = []
		elif firstWord == '(</boundaryPerimeter>)':
			self.boundaryLoop = None
		elif firstWord == '(<boundaryPoint>':
			location = gcodec.getLocationFromSplitLine( None, splitLine )
			if self.boundaryLoop == None:
				self.boundaryLoop = []
				self.rotatedBoundaryLayer.boundaryLoops.append( self.boundaryLoop )
			self.boundaryLoop.append( location.dropAxis( 2 ) )
		elif firstWord == '(<layer>':
			self.addRotatedLoopLayer( float( splitLine[ 1 ] ) )
		elif firstWord == '(</loop>)':
			self.addToLoops()
		elif firstWord == '(<loop>':
			self.isLoop = True
		elif firstWord == '(<perimeter>':
			self.isPerimeter = True
			self.isOuter = ( splitLine[ 1 ] == 'outer' )
		elif firstWord == '(</perimeter>)':
			self.addToPerimeters()


def main():
	"Display the vectorwrite dialog."
	if len( sys.argv ) > 1:
		analyzeFile( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
