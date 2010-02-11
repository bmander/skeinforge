"""
This page is in the table of contents.
Carve is a script to carve a shape into svg slice layers.

The carve manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Carve

On the Arcol Blog a method of deriving the layer thickness is posted.  That article "Machine Calibrating" is at:
http://blog.arcol.hu/?p=157

==Settings==
===Bridge Thickness Multiplier===
Default is one.

Defines the the ratio of the thickness on the bridge layers over the thickness of the typical non bridge layers.

===Extra Decimal Places===
Default is one.

Defines the number of extra decimal places export will output compared to the number of decimal places in the layer thickness.  The higher the 'Extra Decimal Places', the more significant figures the output numbers will have.

===Import Coarseness===
Default is one.

When a triangle mesh has holes in it, the triangle mesh slicer switches over to a slow algorithm that spans gaps in the mesh.  The higher the 'Import Coarseness' setting, the wider the gaps in the mesh it will span.  An import coarseness of one means it will span gaps of the perimeter width.

===Infill in Direction of Bridges===
Default is on.

When selected, the infill will be in the direction of bridges across gaps, so that the fill will be able to span a bridge easier.

===Layer Thickness===
Default is 0.4 mm.

Defines the thickness of the extrusion layer at default extruder speed, this is the most important carve setting.

===Layers===
Carve slices from bottom to top.  To get a single layer, set the "Layers From" to zero and the "Layers To" to one.  The layer from until layer to range is a python slice.

====Layers From====
Default is zero.

Defines the index of the bottom layer that will be carved.  If the layer from is the default zero, the carving will start from the lowest layer.  If the the layer from index is negative, then the carving will start from the layer from index below the top layer.

====Layers To====
Default is a huge number, which will be limited to the highest index layer.

Defines the index of the top layer that will be carved.  If the layer to index is a huge number like the default, the carving will go to the top of the model.  If the layer to index is negative, then the carving will go to the layer to index below the top layer.

===Mesh Type===
Default is 'Correct Mesh'.

====Correct Mesh====
When selected, the mesh will be accurately carved, and if a hole is found, carve will switch over to the algorithm that spans gaps.

====Unproven Mesh====
When selected, carve will use the gap spanning algorithm from the start.  The problem with the gap spanning algothm is that it will span gaps, even if there is not actually a gap in the model.

===Perimeter Width over Thickness===
Default is 1.8.

Defines the ratio of the extrusion perimeter width to the layer thickness.  The higher the value the more the perimeter will be inset, the default is 1.8.  A ratio of one means the extrusion is a circle, a typical ratio of 1.8 means the extrusion is a wide oval.  These values should be measured from a test extrusion line.

==Examples==
The following examples carve the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and carve.py.


> python carve.py
This brings up the carve dialog.


> python carve.py Screw Holder Bottom.stl
The carve tool is parsing the file:
Screw Holder Bottom.stl
..
The carve tool has created the file:
.. Screw Holder Bottom_carve.svg


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import carve
>>> carve.main()
This brings up the carve dialog.


>>> carve.writeOutput( 'Screw Holder Bottom.stl' )
The carve tool is parsing the file:
Screw Holder Bottom.stl
..
The carve tool has created the file:
.. Screw Holder Bottom_carve.svg

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
from skeinforge_tools.skeinforge_utilities import triangle_mesh
import math
import os
import sys
import time


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getCraftedText( fileName, text = '', repository = None ):
	"Get carved text."
	if gcodec.getHasSuffix( fileName, '.svg' ):
		text = gcodec.getTextIfEmpty( fileName, text )
		return text
	return getCraftedTextFromFileName( fileName, repository = None )

def getCraftedTextFromFileName( fileName, repository = None ):
	"Carve a shape file."
	carving = svg_codec.getCarving( fileName )
	if carving == None:
		return ''
	if repository == None:
		repository = CarveRepository()
		settings.getReadRepository( repository )
	return CarveSkein().getCarvedSVG( carving, fileName, repository )

def getNewRepository():
	"Get the repository constructor."
	return CarveRepository()

def writeOutput( fileName = '' ):
	"Carve a GNU Triangulated Surface file."
	startTime = time.time()
	print( 'File ' + gcodec.getSummarizedFileName( fileName ) + ' is being carved.' )
	carveGcode = getCraftedText( fileName )
	if carveGcode == '':
		return
	suffixFileName = gcodec.getFilePathWithUnderscoredBasename( fileName, '_carve.svg' )
	gcodec.writeFileText( suffixFileName, carveGcode )
	print( 'The carved file is saved as ' + gcodec.getSummarizedFileName( suffixFileName ) )
	print( 'It took ' + str( int( round( time.time() - startTime ) ) ) + ' seconds to carve the file.' )
	settings.openWebPage( suffixFileName )


class CarveRepository:
	"A class to handle the carve settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		profile.addListsToCraftTypeRepository( 'skeinforge_tools.craft_plugins.carve.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( interpret.getTranslatorFileTypeTuples(), 'Open File for Carve', self, '' )
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute( 'http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Carve' )
		self.bridgeThicknessMultiplier = settings.FloatSpin().getFromValue( 0.8, 'Bridge Thickness Multiplier (ratio):', self, 1.2, 1.0 )
		self.extraDecimalPlaces = settings.IntSpin().getFromValue( 0, 'Extra Decimal Places (integer):', self, 2, 1 )
		self.importCoarseness = settings.FloatSpin().getFromValue( 0.5, 'Import Coarseness (ratio):', self, 2.0, 1.0 )
		self.infillDirectionBridge = settings.BooleanSetting().getFromValue( 'Infill in Direction of Bridges', self, True )
		self.layerThickness = settings.FloatSpin().getFromValue( 0.1, 'Layer Thickness (mm):', self, 1.0, 0.4 )
		self.layersFrom = settings.IntSpin().getFromValue( 0, 'Layers From (index):', self, 20, 0 )
		self.layersTo = settings.IntSpin().getSingleIncrementFromValue( 0, 'Layers To (index):', self, 912345678, 912345678 )
		self.meshTypeLabel = settings.LabelDisplay().getFromName( 'Mesh Type: ', self )
		importLatentStringVar = settings.LatentStringVar()
		self.correctMesh = settings.Radio().getFromRadio( importLatentStringVar, 'Correct Mesh', self, True )
		self.unprovenMesh = settings.Radio().getFromRadio( importLatentStringVar, 'Unproven Mesh', self, False )
		self.perimeterWidthOverThickness = settings.FloatSpin().getFromValue( 1.4, 'Perimeter Width over Thickness (ratio):', self, 2.2, 1.8 )
		self.executeTitle = 'Carve'

	def execute( self ):
		"Carve button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypes( self.fileNameInput.value, interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


class CarveSkein( svg_codec.SVGCodecSkein ):
	"A class to carve a carving."
	def addRotatedLoopLayerToOutput( self, layerIndex, rotatedBoundaryLayer ):
		"Add rotated boundary layer to the output."
		self.addLayerBegin( layerIndex, rotatedBoundaryLayer.z )
		if rotatedBoundaryLayer.rotation != None:
			self.addLine('\t\t\t<!--bridgeRotation--> %s' % rotatedBoundaryLayer.rotation ) # Indicate the bridge rotation.
		self.addLayerEnd( rotatedBoundaryLayer )

	def getCarvedSVG( self, carving, fileName, repository ):
		"Parse gnu triangulated surface text and store the carved gcode."
		self.carving = carving
		self.repository = repository
		self.layerThickness = repository.layerThickness.value
		self.setExtrusionDiameterWidth( repository )
		if repository.infillDirectionBridge.value:
			carving.setCarveBridgeLayerThickness( self.bridgeLayerThickness )
		carving.setCarveLayerThickness( self.layerThickness )
		importRadius = 0.5 * repository.importCoarseness.value * abs( self.perimeterWidth )
		carving.setCarveImportRadius( max( importRadius, 0.01 * self.layerThickness ) )
		carving.setCarveIsCorrectMesh( repository.correctMesh.value )
		rotatedBoundaryLayers = carving.getCarveRotatedBoundaryLayers()
		if len( rotatedBoundaryLayers ) < 1:
			return ''
		self.cornerMaximum = carving.getCarveCornerMaximum()
		self.cornerMinimum = carving.getCarveCornerMinimum()
		self.layerThickness = self.carving.layerThickness
		self.decimalPlacesCarried = max( 0, 1 + self.repository.extraDecimalPlaces.value - int( math.floor( math.log10( self.layerThickness ) ) ) )
		self.setExtrusionDiameterWidth( repository )
		return self.getReplacedSVGTemplate( fileName, 'carve', rotatedBoundaryLayers )

	def setExtrusionDiameterWidth( self, repository ):
		"Set the extrusion diameter & width and the bridge thickness & width."
		self.bridgeLayerThickness = self.layerThickness * repository.bridgeThicknessMultiplier.value
		self.perimeterWidth = repository.perimeterWidthOverThickness.value * self.layerThickness


def main():
	"Display the carve dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
