"""
Intercircle is a collection of utilities for intersecting circles, used to get smooth loops around a collection of points and inset & outset loops.

"""

from __future__ import absolute_import
try:
	import psyco
	psyco.full()
except:
	pass
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities.vector3 import Vector3
from skeinforge_tools.skeinforge_utilities import euclidean
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addCircleIntersectionLoop( circleIntersectionPaths, circleIntersections ):
	"Add a circle intersection loop."
	firstCircleIntersection = circleIntersectionPaths[ 0 ]
	circleIntersectionAhead = firstCircleIntersection
	for circleIntersectionIndex in xrange( len( circleIntersections ) + 1 ):
		circleIntersectionAhead = circleIntersectionAhead.getCircleIntersectionAhead()
		if circleIntersectionAhead.index == firstCircleIntersection.index:
			firstCircleIntersection.steppedOn = True
			return
		if circleIntersectionAhead.steppedOn == True:
			print( 'circleIntersectionAhead.steppedOn == True in intercircle.' )
			print( circleIntersectionAhead )
		circleIntersectionAhead.addToList( circleIntersectionPaths )
	firstCircleIntersection.steppedOn = True
	print( "addCircleIntersectionLoop would have gone into an endless loop, this should never happen." )
	print( "circleIntersectionPaths" )
	for circleIntersection in circleIntersectionPaths:
		print( circleIntersection )
		print( circleIntersection.circleNodeAhead )
		print( circleIntersection.circleNodeBehind )
	print( "firstCircleIntersection" )
	print( firstCircleIntersection )
	print( "circleIntersections" )
	for circleIntersection in circleIntersections:
		print( circleIntersection )

def addOrbits( distanceFeedRate, loop, orbitalFeedRatePerSecond, temperatureChangeTime, z ):
	"Add orbits with the extruder off."
	timeInOrbit = 0.0
	while timeInOrbit < temperatureChangeTime:
		for point in loop:
			distanceFeedRate.addGcodeMovementZWithFeedRate( 60.0 * orbitalFeedRatePerSecond, point, z )
		timeInOrbit += euclidean.getPolygonLength( loop ) / orbitalFeedRatePerSecond

def addOrbitsIfLarge( distanceFeedRate, loop, orbitalFeedRatePerSecond, temperatureChangeTime, z ):
	"Add orbits with the extruder off if the orbits are large enough."
	if orbitsAreLarge( loop, temperatureChangeTime ):
		addOrbits( distanceFeedRate, loop, orbitalFeedRatePerSecond, temperatureChangeTime, z )

def addPointsFromSegment( pointBegin, pointEnd, points, radius, thresholdRatio = 0.9 ):
	"Add point complexes between the endpoints of a segment."
	if radius <= 0.0:
		print( 'This should never happen, radius should never be zero or less in addPointsFromSegment in intercircle.' )
	thresholdRadius = radius * thresholdRatio # a higher number would be faster but would leave bigger dangling loops and extra dangling loops.
	thresholdDiameter = thresholdRadius + thresholdRadius
	segment = pointEnd - pointBegin
	segmentLength = abs( segment )
	extraCircles = int( math.floor( segmentLength / thresholdDiameter ) )
	if extraCircles < 1:
		return
	if segmentLength == 0.0:
		print( 'This should never happen, segmentLength = 0.0 in intercircle.' )
		print( 'pointBegin' )
		print( pointBegin )
		print( pointEnd )
		return
	if extraCircles < 2:
		lengthIncrement = segmentLength / ( float( extraCircles ) + 1.0 )
		segment *= lengthIncrement / segmentLength
		pointBegin += segment
	else:
		pointBegin += segment * thresholdDiameter / segmentLength
		remainingLength = segmentLength - thresholdDiameter - thresholdDiameter
		lengthIncrement = remainingLength / ( float( extraCircles ) - 1.0 )
		segment *= lengthIncrement / segmentLength
	for circleIndex in xrange( extraCircles ):
		points.append( pointBegin )
		pointBegin += segment

def getAroundsFromLoop( loop, radius, thresholdRatio = 0.9 ):
	"Get the arounds from the loop, later combine with get arounds."
	slightlyGreaterThanRadius = 1.01 * abs( radius )
	points = getPointsFromLoop( loop, slightlyGreaterThanRadius, thresholdRatio )
	return getAroundsFromPoints( points, radius )

def getAroundsFromLoops( loops, radius, thresholdRatio = 0.9 ):
	"Get the arounds from the loops."
	slightlyGreaterThanRadius = 1.01 * abs( radius )
	points = getPointsFromLoops( loops, slightlyGreaterThanRadius, thresholdRatio )
	return getAroundsFromPoints( points, radius )

def getAroundsFromPoints( points, radius ):
	"Get the arounds from the points."
	arounds = []
	radius = abs( radius )
	centers = getCentersFromPoints( points, radius )
	for center in centers:
		inset = getSimplifiedInsetFromClockwiseLoop( center, radius )
		if isLargeSameDirection( inset, center, radius ):
			arounds.append( inset )
	return arounds

def getCentersFromCircleNodes( circleNodes, radius ):
	"Get the complex centers of the circle intersection loops from circle nodes."
	if len( circleNodes ) < 2:
		return []
	circleIntersections = getCircleIntersectionsFromCircleNodes( circleNodes )
	circleIntersectionLoops = getCircleIntersectionLoops( circleIntersections )
	return getCentersFromIntersectionLoops( circleIntersectionLoops, radius )

def getCentersFromIntersectionLoop( circleIntersectionLoop, radius ):
	"Get the centers from the intersection loop."
	loop = []
	for circleIntersection in circleIntersectionLoop:
		loop.append( circleIntersection.circleNodeAhead.circle * radius )
	return loop

def getCentersFromIntersectionLoops( circleIntersectionLoops, radius ):
	"Get the centers from the intersection loops."
	centers = []
	for circleIntersectionLoop in circleIntersectionLoops:
		centers.append( getCentersFromIntersectionLoop( circleIntersectionLoop, radius ) )
	return centers

def getCentersFromLoop( loop, radius ):
	"Get the centers of the loop."
	circleNodes = getCircleNodesFromLoop( loop, radius )
	return getCentersFromCircleNodes( circleNodes, radius )

def getCentersFromLoopDirection( isWiddershins, loop, radius ):
	"Get the centers of the loop which go around in the given direction."
	centers = getCentersFromLoop( loop, radius )
	return getLoopsFromLoopsDirection( isWiddershins, centers )

def getCentersFromPoints( points, radius ):
	"Get the centers from the points."
	circleNodes = getCircleNodesFromPoints( points, abs( radius ) )
	return getCentersFromCircleNodes( circleNodes, abs( radius ) )

def getCircleIntersectionsFromCircleNodes( circleNodes ):
	"Get all the circle intersections which exist between all the circle nodes."
	if len( circleNodes ) < 1:
		return []
	circleIntersections = []
	index = 0
	pixelTable = {}
	for circleNode in circleNodes:
		euclidean.addElementToPixelListFromPoint( circleNode, pixelTable, circleNode.circle )
	accumulatedCircleNodeTable = {}
	for circleNodeIndex in xrange( len( circleNodes ) ):
		circleNodeBehind = circleNodes[ circleNodeIndex ]
		circleNodeIndexMinusOne = circleNodeIndex - 1
		if circleNodeIndexMinusOne >= 0:
			circleNodeAdditional = circleNodes[ circleNodeIndexMinusOne ]
			euclidean.addElementToPixelListFromPoint( circleNodeAdditional, accumulatedCircleNodeTable, 0.5 * circleNodeAdditional.circle )
		withinNodes = circleNodeBehind.getWithinNodes( accumulatedCircleNodeTable )
		for circleNodeAhead in withinNodes:
			circleIntersectionForward = CircleIntersection( circleNodeAhead, index, circleNodeBehind )
			if not circleIntersectionForward.isWithinCircles( pixelTable ):
				circleIntersections.append( circleIntersectionForward )
				circleNodeBehind.circleIntersections.append( circleIntersectionForward )
				index += 1
			circleIntersectionBackward = CircleIntersection( circleNodeBehind, index, circleNodeAhead )
			if not circleIntersectionBackward.isWithinCircles( pixelTable ):
				circleIntersections.append( circleIntersectionBackward )
				circleNodeAhead.circleIntersections.append( circleIntersectionBackward )
				index += 1
	return circleIntersections

def getCircleIntersectionLoops( circleIntersections ):
	"Get all the loops going through the circle intersections."
	circleIntersectionLoops = []
	for circleIntersection in circleIntersections:
		if not circleIntersection.steppedOn:
			circleIntersectionLoop = [ circleIntersection ]
			circleIntersectionLoops.append( circleIntersectionLoop )
			addCircleIntersectionLoop( circleIntersectionLoop, circleIntersections )
	return circleIntersectionLoops

def getCircleNodesFromLoop( loop, radius, thresholdRatio = 0.9 ):
	"Get the circle nodes from every point on a loop and between points."
	radius = abs( radius )
	points = getPointsFromLoop( loop, radius, thresholdRatio )
	return getCircleNodesFromPoints( points, radius )

def getCircleNodesFromPoints( points, radius ):
	"Get the circle nodes from a path."
	circleNodes = []
	oneOverRadius = 1.0 / radius
	points = euclidean.getAwayPoints( points, 0.001 * radius )
	for point in points:
		circleNodes.append( CircleNode( point * oneOverRadius, len( circleNodes ) ) )
	return circleNodes

def getInsetFromClockwiseTriple( aheadAbsolute, behindAbsolute, center, radius ):
	"Get loop inset from clockwise triple, out from widdershins loop."
	originalCenterMinusBehind = euclidean.getNormalized( center - behindAbsolute )
	reverseRoundZAngle = complex( originalCenterMinusBehind.real, - originalCenterMinusBehind.imag )
	rotatedAheadAbsolute = aheadAbsolute * reverseRoundZAngle
	rotatedBehindAbsolute = behindAbsolute * reverseRoundZAngle
	rotatedCenter = center * reverseRoundZAngle
	aheadIntersection = getIntersectionAtInset( rotatedAheadAbsolute, rotatedCenter, radius )
	behindIntersection = getIntersectionAtInset( rotatedCenter, rotatedBehindAbsolute, radius )
	centerMinusAhead = rotatedCenter - rotatedAheadAbsolute
	if abs( centerMinusAhead.imag ) < abs( 0.00001 * centerMinusAhead.real ):
		between = 0.5 * ( aheadIntersection + behindIntersection )
		return originalCenterMinusBehind * between
	yMinusAhead = behindIntersection.imag - aheadIntersection.imag
	x = aheadIntersection.real + yMinusAhead * centerMinusAhead.real / centerMinusAhead.imag
	insetFromClockwiseTriple = originalCenterMinusBehind * complex( x, behindIntersection.imag )
	insetMinusOriginal = insetFromClockwiseTriple - center
	distance = abs( insetMinusOriginal )
	maximumDistance = 2.0 * radius
	if distance < maximumDistance:
		return insetFromClockwiseTriple
	return center + maximumDistance / distance * insetMinusOriginal

def getInsetFromClockwiseLoop( loop, radius ):
	"Get loop inset from clockwise loop, out from widdershins loop."
	insetLoop = []
	for pointIndex in xrange( len( loop ) ):
		behindAbsolute = loop[ ( pointIndex + len( loop ) - 1 ) % len( loop ) ]
		center = loop[ pointIndex ]
		aheadAbsolute = loop[ ( pointIndex + 1 ) % len( loop ) ]
		insetLoop.append( getInsetFromClockwiseTriple( aheadAbsolute, behindAbsolute, center, radius ) )
	return insetLoop

def getInsetLoopsFromLoop( inset, loop, thresholdRatio = 0.9 ):
	"Get the inset loops, which might overlap."
	isInset = inset > 0
	insetLoops = []
	isLoopWiddershins = euclidean.isWiddershins( loop )
	arounds = getAroundsFromLoop( loop, inset, thresholdRatio )
	for around in arounds:
		leftPoint = euclidean.getLeftPoint( around )
		shouldBeWithin = ( isInset == isLoopWiddershins )
		if euclidean.isPointInsideLoop( loop, leftPoint ) == shouldBeWithin:
			if isLoopWiddershins != euclidean.isWiddershins( around ):
				around.reverse()
			insetLoops.append( around )
	return insetLoops

def getInsetLoopsFromLoops( inset, loops ):
	"Get the inset loops, which might overlap."
	insetLoops = []
	for loop in loops:
		insetLoops += getInsetLoopsFromLoop( inset, loop )
	return insetLoops

def getInsetSeparateLoopsFromLoops( inset, loops, thresholdRatio = 0.9 ):
	"Get the separate inset loops."
	isInset = inset > 0
	insetSeparateLoops = []
	radius = abs( inset )
	arounds = getAroundsFromLoops( loops, radius, thresholdRatio )
	for around in arounds:
		leftPoint = euclidean.getLeftPoint( around )
		if isInset == euclidean.isInFilledRegion( loops, leftPoint ):
			if isInset:
				around.reverse()
			insetSeparateLoops.append( around )
	return insetSeparateLoops

def getIntersectionAtInset( ahead, behind, inset ):
	"Get circle intersection loop at inset from segment."
	aheadMinusBehind = 0.5 * ( ahead - behind )
	rotatedClockwiseQuarter = complex( aheadMinusBehind.imag, - aheadMinusBehind.real )
	rotatedClockwiseQuarter *= inset / abs( rotatedClockwiseQuarter )
	return aheadMinusBehind + behind + rotatedClockwiseQuarter

def getLargestInsetLoopFromLoop( loop, radius ):
	"Get the largest inset loop from the loop."
	loops = getInsetLoopsFromLoop( radius, loop )
	return euclidean.getLargestLoop( loops )

def getLargestInsetLoopFromLoopNoMatterWhat( loop, radius ):
	"Get the largest inset loop from the loop, even if the radius has to be shrunk and even if there is still no inset loop."
	largestInsetLoop = getLargestInsetLoopFromLoop( loop, radius )
	if largestInsetLoop != None:
		return largestInsetLoop
	largestInsetLoop = getLargestInsetLoopFromLoop( loop, 0.55 * radius )
	if largestInsetLoop != None:
		return largestInsetLoop
	largestInsetLoop = getLargestInsetLoopFromLoop( loop, 0.35 * radius )
	if largestInsetLoop != None:
		return largestInsetLoop
	largestInsetLoop = getLargestInsetLoopFromLoop( loop, 0.2 * radius )
	if largestInsetLoop != None:
		return largestInsetLoop
	print( 'This should never happen, there should always be a largestInsetLoop in getLargestInsetLoopFromLoopNoMatterWhat in intercircle.' )
	print( loop )
	return loop

def getLoopsFromLoopsDirection( isWiddershins, loops ):
	"Get the loops going round in a given direction."
	directionalLoops = []
	for loop in loops:
		if euclidean.isWiddershins( loop ) == isWiddershins:
			directionalLoops.append( loop )
	return directionalLoops

def getPointsFromLoop( loop, radius, thresholdRatio = 0.9 ):
	"Get the points from every point on a loop and between points."
	radius = abs( radius )
	points = []
	for pointIndex in xrange( len( loop ) ):
		pointBegin = loop[ pointIndex ]
		pointEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		points.append( pointBegin )
		addPointsFromSegment( pointBegin, pointEnd, points, radius, thresholdRatio )
	return points

def getPointsFromLoops( loops, radius, thresholdRatio = 0.9 ):
	"Get the points from every point on a loop and between points."
	points = []
	for loop in loops:
		points += getPointsFromLoop( loop, radius, thresholdRatio )
	return points

def getSimplifiedInsetFromClockwiseLoop( loop, radius ):
	"Get loop inset from clockwise loop, out from widdershins loop."
	return getWithoutIntersections( euclidean.getSimplifiedLoop( getInsetFromClockwiseLoop( loop, radius ), radius ) )

def getWithoutIntersections( loop ):
	"Get loop without intersections."
	lastLoopLength = len( loop )
	while lastLoopLength > 3:
		removeIntersection( loop )
		if len( loop ) == lastLoopLength:
			return loop
		lastLoopLength = len( loop )
	return loop

def isLargeSameDirection( inset, loop, radius ):
	"Determine if the inset is in the same direction as the loop and it is large enough."
	if euclidean.isWiddershins( inset ) != euclidean.isWiddershins( loop ):
		return False
	return euclidean.getMaximumSpan( inset ) > 2.01 * abs( radius )

def isLoopIntersectingLoop( anotherLoop, loop ):
	"Determine if the a loop is intersecting another loop."
	for pointIndex in xrange( len( loop ) ):
		pointFirst = loop[ pointIndex ]
		pointSecond = loop[ ( pointIndex + 1 ) % len( loop ) ]
		segment = pointFirst - pointSecond
		normalizedSegment = euclidean.getNormalized( segment )
		segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
		segmentFirstPoint = segmentYMirror * pointFirst
		segmentSecondPoint = segmentYMirror * pointSecond
		if euclidean.isLoopIntersectingInsideXSegment( anotherLoop, segmentFirstPoint.real, segmentSecondPoint.real, segmentYMirror, segmentFirstPoint.imag ):
			return True
	return False

def orbitsAreLarge( loop, temperatureChangeTime ):
	"Determine if the orbits are large enough."
	if len( loop ) < 1:
		print( 'Zero length loop which was skipped over, this should never happen.' )
		return False
	return temperatureChangeTime > 1.5

def removeIntersection( loop ):
	"Get loop without the first intersection."
	withoutIntersection = []
	for pointIndex in xrange( len( loop ) ):
		behind = loop[ ( pointIndex + len( loop ) - 1 ) % len( loop ) ]
		behindEnd = loop[ ( pointIndex + len( loop ) - 2 ) % len( loop ) ]
		behindMidpoint = 0.5 * ( behind + behindEnd )
		ahead = loop[ pointIndex ]
		aheadEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		aheadMidpoint = 0.5 * ( ahead + aheadEnd )
		normalizedSegment = behind - behindMidpoint
		normalizedSegmentLength = abs( normalizedSegment )
		if normalizedSegmentLength > 0.0:
			normalizedSegment /= normalizedSegmentLength
			segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
			behindRotated = segmentYMirror * behind
			behindMidpointRotated = segmentYMirror * behindMidpoint
			aheadRotated = segmentYMirror * ahead
			aheadMidpointRotated = segmentYMirror * aheadMidpoint
			y = behindRotated.imag
			isYAboveFirst = y > aheadRotated.imag
			isYAboveSecond = y > aheadMidpointRotated.imag
			if isYAboveFirst != isYAboveSecond:
				xIntersection = euclidean.getXIntersection( aheadRotated, aheadMidpointRotated, y )
				if xIntersection > min( behindMidpointRotated.real, behindRotated.real ) and xIntersection < max( behindMidpointRotated.real, behindRotated.real ):
					intersectionPoint = normalizedSegment * complex( xIntersection, y )
					loop[ ( pointIndex + len( loop ) - 1 ) % len( loop ) ] = intersectionPoint
					del loop[ pointIndex ]
					return


class BoundingLoop:
	"A class to hold a bounding loop composed of a minimum complex, a maximum complex and an outset loop."
	def __eq__( self, other ):
		"Determine whether this bounding loop is identical to other one."
		if other == None:
			return False
		return self.minimum == other.minimum and self.maximum == other.maximum and self.loop == other.loop

	def __repr__( self ):
		"Get the string representation of this bounding loop."
		return '%s, %s, %s' % ( self.minimum, self.maximum, self.loop )

	def getFromLoop( self, loop ):
		"Get the bounding loop from a path."
		self.loop = loop
		self.maximum = euclidean.getMaximumFromPoints( loop )
		self.minimum = euclidean.getMinimumFromPoints( loop )
		return self

	def getOutsetBoundingLoop( self, outsetDistance ):
		"Outset the bounding rectangle and loop by a distance."
		outsetBoundingLoop = BoundingLoop()
		outsetBoundingLoop.maximum = self.maximum + complex( outsetDistance, outsetDistance )
		outsetBoundingLoop.minimum = self.minimum - complex( outsetDistance, outsetDistance )
		greaterThanOutsetDistance = 1.1 * outsetDistance
		centers = getCentersFromLoopDirection( True, self.loop, greaterThanOutsetDistance )
		outsetBoundingLoop.loop = getSimplifiedInsetFromClockwiseLoop( centers[ 0 ], outsetDistance )
		return outsetBoundingLoop

	def isEntirelyInsideAnother( self, anotherBoundingLoop ):
		"Determine if this bounding loop is entirely inside another bounding loop."
		if self.minimum.imag < anotherBoundingLoop.minimum.imag or self.minimum.real < anotherBoundingLoop.minimum.real:
			return False
		if self.maximum.imag > anotherBoundingLoop.maximum.imag or self.maximum.real > anotherBoundingLoop.maximum.real:
			return False
		for point in self.loop:
			if euclidean.getNumberOfIntersectionsToLeft( anotherBoundingLoop.loop, point ) % 2 == 0:
				return False
		return not isLoopIntersectingLoop( anotherBoundingLoop.loop, self.loop ) #later check for intersection on only acute angles

	def isOverlappingAnother( self, anotherBoundingLoop ):
		"Determine if this bounding loop is intersecting another bounding loop."
		if self.isRectangleMissingAnother( anotherBoundingLoop ):
			return False
		for point in self.loop:
			if euclidean.getNumberOfIntersectionsToLeft( anotherBoundingLoop.loop, point ) % 2 == 1:
				return True
		for point in anotherBoundingLoop.loop:
			if euclidean.getNumberOfIntersectionsToLeft( self.loop, point ) % 2 == 1:
				return True
		return isLoopIntersectingLoop( anotherBoundingLoop.loop, self.loop ) #later check for intersection on only acute angles

	def isOverlappingAnotherInList( self, boundingLoops ):
		"Determine if this bounding loop is intersecting another bounding loop in a list."
		for boundingLoop in boundingLoops:
			if self.isOverlappingAnother( boundingLoop ):
				return True
		return False

	def isRectangleMissingAnother( self, anotherBoundingLoop ):
		"Determine if the rectangle of this bounding loop is missing the rectangle of another bounding loop."
		if self.maximum.imag < anotherBoundingLoop.minimum.imag or self.maximum.real < anotherBoundingLoop.minimum.real:
			return True
		return self.minimum.imag > anotherBoundingLoop.maximum.imag or self.minimum.real > anotherBoundingLoop.maximum.real


class CircleIntersection:
	"An intersection of two complex circles."
	def __init__( self, circleNodeAhead, index, circleNodeBehind ):
		self.aheadMinusBehind = 0.5 * ( circleNodeAhead.circle - circleNodeBehind.circle )
		self.circleNodeAhead = circleNodeAhead
		self.circleNodeBehind = circleNodeBehind
		self.index = index
		self.steppedOn = False
		demichordWidth = math.sqrt( 1.0 - self.aheadMinusBehind.real * self.aheadMinusBehind.real - self.aheadMinusBehind.imag * self.aheadMinusBehind.imag )
		rotatedClockwiseQuarter = complex( self.aheadMinusBehind.imag, - self.aheadMinusBehind.real )
		rotatedClockwiseQuarterLength = abs( rotatedClockwiseQuarter )
		if rotatedClockwiseQuarterLength == 0:
			print( 'this should never happen, rotatedClockwiseQuarter in getDemichord in intercircle is 0' )
			print( circleNodeAhead.circle )
			print( circleNodeBehind.circle )
			self.demichord = 0.0
		else:
			self.demichord = rotatedClockwiseQuarter * demichordWidth / rotatedClockwiseQuarterLength
		self.positionRelativeToBehind = self.aheadMinusBehind + self.demichord

	def __repr__( self ):
		"Get the string representation of this CircleIntersection."
		return '%s, %s, %s, %s, %s' % ( self.index, self.getAbsolutePosition(), self.circleNodeBehind.index, self.circleNodeAhead.index, self.getCircleIntersectionAhead().index )

	def addToList( self, circleIntersectionPath ):
		"Add this to the circle intersection path, setting stepped on to be true."
		self.steppedOn = True
		circleIntersectionPath.append( self )

	def getAbsolutePosition( self ):
		"Get the absolute position."
		return self.positionRelativeToBehind + self.circleNodeBehind.circle

	def getCircleIntersectionAhead( self ):
		"Get the first circle intersection on the circle node ahead."
		circleIntersections = self.circleNodeAhead.circleIntersections
		circleIntersectionAhead = None
		largestDot = - 999999999.0
		for circleIntersection in circleIntersections:
			if not circleIntersection.steppedOn:
				circleIntersectionRelativeToMidpoint = euclidean.getNormalized( circleIntersection.positionRelativeToBehind + self.aheadMinusBehind )
				dot = euclidean.getDotProduct( self.demichord, circleIntersectionRelativeToMidpoint )
				if dot > largestDot:
					largestDot = dot
					circleIntersectionAhead = circleIntersection
		if circleIntersectionAhead == None:
			print( 'this should never happen, circleIntersectionAhead in intercircle is None' )
			print( self.circleNodeAhead.circle )
			for circleIntersection in circleIntersections:
				print( circleIntersection.circleNodeAhead.circle )
		return circleIntersectionAhead

	def isWithinCircles( self, pixelTable ):
		"Determine if this circle intersection is within the circle node circles."
		absolutePosition = self.getAbsolutePosition()
		squareValues = euclidean.getSquareValuesFromPoint( pixelTable, absolutePosition )
		for squareValue in squareValues:
			if abs( squareValue.circle - absolutePosition ) < 1.0:
				if squareValue != self.circleNodeAhead and squareValue != self.circleNodeBehind:
					return True
		return False


class CircleNode:
	"A complex node of complex circle intersections."
	def __init__( self, circle, index ):
		self.circle = circle
		self.circleIntersections = []
		self.index = index

	def __repr__( self ):
		"Get the string representation of this CircleNode."
		return '%s, %s' % ( self.index, self.circle )

	def getWithinNodes( self, pixelTable ):
		"Get the nodes this circle node is within."
		withinNodes = []
		squareValues = euclidean.getSquareValuesFromPoint( pixelTable, 0.5 * self.circle )
		for squareValue in squareValues:
			if abs( self.circle - squareValue.circle ) < 2.0:
				withinNodes.append( squareValue )
		return withinNodes
