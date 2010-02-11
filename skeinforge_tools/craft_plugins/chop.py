"""
This page is in the table of contents.
Chop is a script to chop a shape into svg slice layers.

==Settings==

===Extra Decimal Places===
Default is one.

Defines the number of extra decimal places export will output compared to the number of decimal places in the layer thickness.  The higher the 'Extra Decimal Places', the more significant figures the output numbers will have.

===Import Coarseness===
Default is one.

When a triangle mesh has holes in it, the triangle mesh slicer switches over to a slow algorithm that spans gaps in the mesh.  The higher the 'Import Coarseness' setting, the wider the gaps in the mesh it will span.  An import coarseness of one means it will span gaps of the perimeter width.

===Layer Thickness===
Default is 0.4 mm.

Defines the thickness of the layer, this is the most important chop setting.

===Layers===
Chop slices from top to bottom.  To get only the bottom layer, set the "Layers From" to minus one.  The layer from until layer to range is a python slice.

====Layers From====
Default is zero.

Defines the index of the top layer that will be chopped.  If the layer from is the default zero, the carving will start from the top layer.  If the the layer from index is negative, then the carving will start from the layer from index above the bottom layer.

====Layers To====
Default is a huge number, which will be limited to the highest index number.

Defines the index of the bottom layer that will be carved.  If the layer to index is a huge number like the default, the carving will go to the bottom of the model.  If the layer to index is negative, then the carving will go to the layer to index above the bottom layer.

===Mesh Type===
Default is 'Correct Mesh'.

====Correct Mesh====
When selected, the mesh will be accurately chopped, and if a hole is found, chop will switch over to the algorithm that spans gaps.

====Unproven Mesh====
When selected, chop will use the gap spanning algorithm from the start.  The problem with the gap spanning algothm is that it will span gaps, even if there is not actually a gap in the model.

===Perimeter Width===
Default is 2 mm.

Defines the width of the perimeter.

==Examples==

The following examples chop the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and chop.py.


> python chop.py
This brings up the chop dialog.


> python chop.py Screw Holder Bottom.stl
The chop tool is parsing the file:
Screw Holder Bottom.stl
..
The chop tool has created the file:
.. Screw Holder Bottom_chop.svg


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import chop
>>> chop.main()
This brings up the chop dialog.


>>> chop.writeOutput( 'Screw Holder Bottom.stl' )
The chop tool is parsing the file:
Screw Holder Bottom.stl
..
The chop tool has created the file:
.. Screw Holder Bottom_chop.svg

"""

from __future__ import absolute_import
try:
	import psyco
	psyco.full()
except:
	pass
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools import profile
from skeinforge_tools.meta_plugins import polyfile
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools.skeinforge_utilities import settings
from skeinforge_tools.skeinforge_utilities import svg_codec
import math
import os
import sys
import time


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getCraftedText( fileName, text = '', repository = None ):
	"Get chopped text."
	if gcodec.getHasSuffix( fileName, '.svg' ):
		if text == '':
			text = gcodec.getFileText( fileName )
		return text
	return getCraftedTextFromFileName( fileName, repository = None )

def getCraftedTextFromFileName( fileName, repository = None ):
	"Chop a shape file."
	carving = svg_codec.getCarving( fileName )
	if carving == None:
		return ''
	if repository == None:
		repository = ChopRepository()
		settings.getReadRepository( repository )
	return ChopSkein().getCarvedSVG( carving, fileName, repository )

def getNewRepository():
	"Get the repository constructor."
	return ChopRepository()

def writeOutput( fileName = '' ):
	"Chop a GNU Triangulated Surface file.  If no fileName is specified, chop the first GNU Triangulated Surface file in this folder."
	if fileName == '':
		unmodified = gcodec.getFilesWithFileTypesWithoutWords( interpret.getImportPluginFileNames() )
		if len( unmodified ) == 0:
			print( "There are no carvable files in this folder." )
			return
		fileName = unmodified[ 0 ]
	startTime = time.time()
	print( 'File ' + gcodec.getSummarizedFileName( fileName ) + ' is being chopped.' )
	chopGcode = getCraftedText( fileName )
	if chopGcode == '':
		return
	suffixFileName = fileName[ : fileName.rfind( '.' ) ] + '_chop.svg'
	suffixDirectoryName = os.path.dirname( suffixFileName )
	suffixReplacedBaseName = os.path.basename( suffixFileName ).replace( ' ', '_' )
	suffixFileName = os.path.join( suffixDirectoryName, suffixReplacedBaseName )
	gcodec.writeFileText( suffixFileName, chopGcode )
	print( 'The chopped file is saved as ' + gcodec.getSummarizedFileName( suffixFileName ) )
	print( 'It took ' + str( int( round( time.time() - startTime ) ) ) + ' seconds to chop the file.' )
	settings.openWebPage( suffixFileName )


class ChopRepository:
	"A class to handle the chop settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		profile.addListsToCraftTypeRepository( 'skeinforge_tools.craft_plugins.chop.html', self )
		self.addExtraTopLayerIfNecessary = settings.BooleanSetting().getFromValue( 'Add Extra Top Layer if Necessary', self, True )
		self.fileNameInput = settings.FileNameInput().getFromFileName( interpret.getTranslatorFileTypeTuples(), 'Open File to be Chopped', self, '' )
		self.extraDecimalPlaces = settings.IntSpin().getFromValue( 0, 'Extra Decimal Places (integer):', self, 2, 1 )
		self.importCoarseness = settings.FloatSpin().getFromValue( 0.5, 'Import Coarseness (ratio):', self, 2.0, 1.0 )
		self.layerThickness = settings.FloatSpin().getFromValue( 0.1, 'Layer Thickness (mm):', self, 1.0, 0.4 )
		self.layersFrom = settings.IntSpin().getFromValue( 0, 'Layers From (index):', self, 20, 0 )
		self.layersTo = settings.IntSpin().getSingleIncrementFromValue( 0, 'Layers To (index):', self, 912345678, 912345678 )
		self.meshTypeLabel = settings.LabelDisplay().getFromName( 'Mesh Type: ', self, )
		importLatentStringVar = settings.LatentStringVar()
		self.correctMesh = settings.Radio().getFromRadio( importLatentStringVar, 'Correct Mesh', self, True )
		self.unprovenMesh = settings.Radio().getFromRadio( importLatentStringVar, 'Unproven Mesh', self, False )
		self.perimeterWidth = settings.FloatSpin().getFromValue( 0.4, 'Perimeter Width (mm):', self, 4.0, 2.0 )
		self.executeTitle = 'Chop'

	def execute( self ):
		"Chop button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypes( self.fileNameInput.value, interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


class ChopSkein( svg_codec.SVGCodecSkein ):
	"A class to chop a carving."
	def addExtraTopLayerIfNecessary( self, rotatedBoundaryLayers ):
		"Add extra top layer if necessary."
		topRotatedBoundaryLayer = rotatedBoundaryLayers[ - 1 ]
		cuttingSafeHeight = topRotatedBoundaryLayer.z + 0.5001 * self.layerThickness
		if cuttingSafeHeight > self.cornerMaximum.z:
			return
		extraTopRotatedBoundaryLayer = topRotatedBoundaryLayer.getCopyAtZ( topRotatedBoundaryLayer.z + self.layerThickness )
		rotatedBoundaryLayers.append( extraTopRotatedBoundaryLayer )

	def getCarvedSVG( self, carving, fileName, repository ):
		"Parse gnu triangulated surface text and store the chopped gcode."
		self.carving = carving
		self.repository = repository
		self.layerThickness = repository.layerThickness.value
		self.perimeterWidth = repository.perimeterWidth.value
		carving.setCarveLayerThickness( self.layerThickness )
		importRadius = 0.5 * repository.importCoarseness.value * abs( self.perimeterWidth )
		carving.setCarveImportRadius( max( importRadius, 0.01 * self.layerThickness ) )
		carving.setCarveIsCorrectMesh( repository.correctMesh.value )
		rotatedBoundaryLayers = carving.getCarveRotatedBoundaryLayers()
		if len( rotatedBoundaryLayers ) < 1:
			return ''
		self.cornerMaximum = carving.getCarveCornerMaximum()
		self.cornerMinimum = carving.getCarveCornerMinimum()
		if repository.addExtraTopLayerIfNecessary.value:
			self.addExtraTopLayerIfNecessary( rotatedBoundaryLayers )
		rotatedBoundaryLayers.reverse()
		self.layerThickness = self.carving.layerThickness
		self.decimalPlacesCarried = max( 0, 1 + self.repository.extraDecimalPlaces.value - int( math.floor( math.log10( self.layerThickness ) ) ) )
		return self.getReplacedSVGTemplate( fileName, 'chop', rotatedBoundaryLayers )


def main():
	"Display the chop dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
