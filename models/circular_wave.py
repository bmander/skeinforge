"""
This page is in the table of contents.
The py.py script is an import translator plugin to get a carving from a python script.

An explanation of the SLC format can be found at:
http://rapid.lpt.fi/archives/rp-ml-1999/0713.html

An import plugin is a script in the import_plugins folder which has the function getCarving.  It is meant to be run from the interpret tool.  To ensure that the plugin works on platforms which do not handle file capitalization properly, give the plugin a lower case name.

The getCarving function takes the file name of a python script and returns the carving.

This example gets a carving for the python script circular_wave.py.  This example is run in a terminal in the folder which contains circular_wave.py and py.py.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import py
>>> py.getCarving()
0.20000000298, 999999999.0, -999999999.0, [8.72782748851e-17, None
..
many more lines of the carving
..


"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

import math

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getLoopLayers( layerThickness ):
	"Get the loop layers."
	return CircularWave( layerThickness ).getLoopLayers()


class LoopLayer:
	"Loops with a z."
	def __init__( self, z ):
		self.loops = []
		self.z = z

	def __repr__( self ):
		"Get the string representation of this loop layer."
		return '%s, %s' % ( self.z, self.loops )


class CircularWave:
	"A twisted circular wave."
	def __init__( self, layerThickness ):
		"Initialize."
		self.layerThickness = layerThickness
		self.loopLayers = []
		self.setRootParameters()
		self.setDerivedParameters()
		for layerIndex in xrange( self.numberOfLayers ):
			self.addLoopLayer( layerIndex )
	
	def __repr__( self ):
		"Get the string representation of this carving."
		return '%s, %s, %s, %s' % ( self.layerThickness, self.minimumZ, self.maximumZ, self.rotatedBoundaryLayers )

	def addLoopLayer( self, layerIndex ):
		"Add a loop layer."
		z = self.halfLayerThickness + layerIndex * self.layerThickness
		loopLayer = LoopLayer( z )
		loop = []
		for pointIndex in xrange( self.numberOfPoints ):
			twist = self.twist * z / self.height
			self.addPoint( loop, pointIndex, twist )
		loopLayer.loops.append( loop )
		self.loopLayers.append( loopLayer )

	def addPoint( self, loop, pointIndex, twist ):
		"Add a point."
		rotation = - self.rotationIncrement * pointIndex
		waveRotation = rotation * float( self.numberOfWaves )
		radius = self.midRadius + math.sin( waveRotation ) * self.halfRingWidth
		twistedRotation = rotation + twist
		point = complex( math.cos( twistedRotation ), - math.sin( twistedRotation ) ) * radius
		loop.append( point )

	def getLoopLayers( self ):
		"Get the loop layers."
		return self.loopLayers

	def setDerivedParameters( self ):
		"Set the derived parameters."
		self.halfLayerThickness = 0.5 * self.layerThickness
		self.innerRadius = self.innerRadiusRatio * self.radius
		self.midRadius = 0.5 * ( self.innerRadius + self.radius )
		self.halfRingWidth = self.radius - self.midRadius
		self.numberOfLayers = max( 1, int( round( self.height / self.layerThickness ) ) )
		self.rotationIncrement = 2.0 * math.pi / float( self.numberOfPoints )

	def setRootParameters( self ):
		"Set the root parameters."
		self.height = 10.0
		self.innerRadiusRatio = 0.5
		self.numberOfPoints = 40
		self.numberOfWaves = 3
		self.radius = 10.0
		self.twist = math.radians( 30.0 )


def main():
	"Display the inset dialog."
	if len( sys.argv ) > 1:
		getCarving( ' '.join( sys.argv[ 1 : ] ) )

if __name__ == "__main__":
	main()
