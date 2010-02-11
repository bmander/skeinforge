"""
Euclidean is a collection of python utilities for complex numbers, paths, polygons & Vector3s.

To use euclidean, install python 2.x on your machine, which is avaliable from http://www.python.org/download/

Then in the folder which euclidean is in, type 'python' in a shell to run the python interpreter.  Finally type 'import euclidean' to import these utilities and 'from vector3 import Vector3' to import the Vector3 class.


Below are examples of euclidean use.

>>> from euclidean import *
>>> origin=complex()
>>> right=complex(1.0,0.0)
>>> back=complex(0.0,1.0)
>>> getMaximum(right,back)
1.0, 1.0
>>> polygon=[origin, right, back]
>>> getPolygonLength(polygon)
3.4142135623730949
>>> getPolygonArea(polygon)
0.5
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
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addCircleToPixelTable( pixelTable, point ):
	"Add circle to the pixel table."
	xStep = int( round( point.real ) )
	yStep = int( round( point.imag ) )
	for xCircleStep in xrange( xStep - 2, xStep + 3 ):
		for yCircleStep in xrange( yStep - 2, yStep + 3 ):
			stepKey = ( xCircleStep, yCircleStep )
			pixelTable[ stepKey ] = None

def addElementToListTable( element, key, listTable ):
	"Add an element to the list table."
	if key in listTable:
		listTable[ key ].append( element )
	else:
		listTable[ key ] = [ element ]

def addElementToPixelList( element, pixelTable, x, y ):
	"Add an element to the pixel list."
	stepKey = getStepKey( x, y )
	addElementToListTable( element, stepKey, pixelTable )

def addElementToPixelListFromPoint( element, pixelTable, point ):
	"Add an element to the pixel list."
	addElementToPixelList( element, pixelTable, int( round( point.real ) ), int( round( point.imag ) ) )

def addListToListTable( elementList, key, listTable ):
	"Add a list to the list table."
	if key in listTable:
		listTable[ key ] += elementList
	else:
		listTable[ key ] = elementList

def addLoopToPixelTable( loop, pixelTable, width ):
	"Add loop to the pixel table."
	for pointIndex in xrange( len( loop ) ):
		pointBegin = loop[ pointIndex ]
		pointEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		addValueSegmentToPixelTable( pointBegin, pointEnd, pixelTable, None, width )

def addPathToPixelTable( path, pixelTable, value, width ):
	"Add path to the pixel table."
	for pointIndex in xrange( len( path ) - 1 ):
		pointBegin = path[ pointIndex ]
		pointEnd = path[ pointIndex + 1 ]
		addValueSegmentToPixelTable( pointBegin, pointEnd, pixelTable, value, width )

def addPixelTableToPixelTable( fromPixelTable, intoPixelTable ):
	"Add from pixel table to the into pixel table."
	for fromPixelTableKey in fromPixelTable.keys():
		intoPixelTable[ fromPixelTableKey ] = fromPixelTable[ fromPixelTableKey ]

def addPixelToPixelTable( pixelTable, value, x, y ):
	"Add pixel to the pixel table."
	pixelTable[ getStepKey( x, y ) ] = value

def addPixelToPixelTableWithSteepness( isSteep, pixelTable, value, x, y ):
	"Add pixels to the pixel table with steepness."
	if isSteep:
		addPixelToPixelTable( pixelTable, value, y, x )
	else:
		addPixelToPixelTable( pixelTable, value, x, y )

def addPointToPath( path, pixelTable, point, value, width ):
	"Add a point to a path and the pixel table."
	path.append( point )
	if len( path ) < 2:
		return
	begin = path[ - 2 ]
	addValueSegmentToPixelTable( begin, point, pixelTable, value, width )

def addSegmentToPixelTable( beginComplex, endComplex, pixelTable, shortenDistanceBegin, shortenDistanceEnd, width ):
	"Add line segment to the pixel table."
	if abs( beginComplex - endComplex ) <= 0.0:
		return
	beginComplex /= width
	endComplex /= width
	if shortenDistanceBegin > 0.0:
		endMinusBeginComplex = endComplex - beginComplex
		endMinusBeginComplexLength = abs( endMinusBeginComplex )
		if endMinusBeginComplexLength < shortenDistanceBegin:
			return
		beginComplex = beginComplex + endMinusBeginComplex * shortenDistanceBegin / endMinusBeginComplexLength
	if shortenDistanceEnd > 0.0:
		beginMinusEndComplex = beginComplex - endComplex
		beginMinusEndComplexLength = abs( beginMinusEndComplex )
		if beginMinusEndComplexLength < shortenDistanceEnd:
			return
		endComplex = endComplex + beginMinusEndComplex * shortenDistanceEnd / beginMinusEndComplexLength
	deltaX = endComplex.real - beginComplex.real
	deltaY = endComplex.imag - beginComplex.imag
	isSteep = abs( deltaY ) > abs( deltaX )
	if isSteep:
		beginComplex = complex( beginComplex.imag, beginComplex.real )
		endComplex = complex( endComplex.imag, endComplex.real )
	if beginComplex.real > endComplex.real:
		newBeginComplex = endComplex
		endComplex = beginComplex
		beginComplex = newBeginComplex
	deltaX = endComplex.real - beginComplex.real
	deltaY = endComplex.imag - beginComplex.imag
	if deltaX > 0.0:
		gradient = deltaY / deltaX
	else:
		gradient = 0.0
		print( 'This should never happen, deltaX in addSegmentToPixelTable in euclidean is 0.' )
		print( beginComplex )
		print( endComplex )
		print( shortenDistanceBegin )
		print( shortenDistanceEnd )
		print( width )
	xBegin = int( round( beginComplex.real ) )
	xEnd = int( round( endComplex.real ) )
	yIntersection = beginComplex.imag - beginComplex.real * gradient
	addPixelToPixelTableWithSteepness( isSteep, pixelTable, None, xBegin, int( round( beginComplex.imag ) ) )
	addPixelToPixelTableWithSteepness( isSteep, pixelTable, None, xEnd, int( round( endComplex.imag ) ) )
	for x in xrange( xBegin + 1, xEnd ):
		y = int( math.floor( yIntersection + x * gradient ) )
		addPixelToPixelTableWithSteepness( isSteep, pixelTable, None, x, y )
		addPixelToPixelTableWithSteepness( isSteep, pixelTable, None, x, y + 1 )

def addSurroundingLoopBeginning( distanceFeedRate, loop, z ):
	"Add surrounding loop beginning to gcode output."
	distanceFeedRate.addLine( '(<surroundingLoop>)' )
	distanceFeedRate.addLine( '(<boundaryPerimeter>)' )
	for point in loop:
		pointVector3 = Vector3( point.real, point.imag, z )
		distanceFeedRate.addLine( distanceFeedRate.getBoundaryLine( pointVector3 ) )

def addToThreadsFromLoop( extrusionHalfWidth, gcodeType, loop, oldOrderedLocation, skein ):
	"Add to threads from the last location from loop."
	loop = getLoopStartingNearest( extrusionHalfWidth, oldOrderedLocation.dropAxis( 2 ), loop )
	oldOrderedLocation.x = loop[ 0 ].real
	oldOrderedLocation.y = loop[ 0 ].imag
	gcodeTypeStart = gcodeType
	if isWiddershins( loop ):
		skein.distanceFeedRate.addLine( '(<%s> outer )' % gcodeType )
	else:
		skein.distanceFeedRate.addLine( '(<%s> inner )' % gcodeType )
	skein.addGcodeFromThreadZ( loop + [ loop[ 0 ] ], oldOrderedLocation.z ) # Turn extruder on and indicate that a loop is beginning.
	skein.distanceFeedRate.addLine( '(</%s>)' % gcodeType )

def addToThreadsRemoveFromSurroundings( oldOrderedLocation, surroundingLoops, skein ):
	"Add to threads from the last location from surrounding loops."
	if len( surroundingLoops ) < 1:
		return
	while len( surroundingLoops ) > 0:
		getTransferClosestSurroundingLoop( oldOrderedLocation, surroundingLoops, skein )

def addValueSegmentToPixelTable( beginComplex, endComplex, pixelTable, value, width ):
	"Add line segment to the pixel table."
	if abs( beginComplex - endComplex ) <= 0.0:
		return
	beginComplex /= width
	endComplex /= width
	deltaX = endComplex.real - beginComplex.real
	deltaY = endComplex.imag - beginComplex.imag
	isSteep = abs( deltaY ) > abs( deltaX )
	if isSteep:
		beginComplex = complex( beginComplex.imag, beginComplex.real )
		endComplex = complex( endComplex.imag, endComplex.real )
	if beginComplex.real > endComplex.real:
		newBeginComplex = endComplex
		endComplex = beginComplex
		beginComplex = newBeginComplex
	deltaX = endComplex.real - beginComplex.real
	deltaY = endComplex.imag - beginComplex.imag
	if deltaX > 0.0:
		gradient = deltaY / deltaX
	else:
		gradient = 0.0
		print( 'This should never happen, deltaX in addValueSegmentToPixelTable in euclidean is 0.' )
		print( beginComplex )
		print( value )
		print( endComplex )
		print( width )
	xBegin = int( round( beginComplex.real ) )
	xEnd = int( round( endComplex.real ) )
	yIntersection = beginComplex.imag - beginComplex.real * gradient
	addPixelToPixelTableWithSteepness( isSteep, pixelTable, value, xBegin, int( round( beginComplex.imag ) ) )
	addPixelToPixelTableWithSteepness( isSteep, pixelTable, value, xEnd, int( round( endComplex.imag ) ) )
	for x in xrange( xBegin + 1, xEnd ):
		y = int( math.floor( yIntersection + x * gradient ) )
		addPixelToPixelTableWithSteepness( isSteep, pixelTable, value, x, y )
		addPixelToPixelTableWithSteepness( isSteep, pixelTable, value, x, y + 1 )

def addXIntersectionIndexesFromLoop( frontOverWidth, loop, solidIndex, xIntersectionIndexLists, width, yList ):
	"Add the x intersection indexes for a loop."
	for pointIndex in xrange( len( loop ) ):
		pointBegin = loop[ pointIndex ]
		pointEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		if pointBegin.imag > pointEnd.imag:
			pointOriginal = pointBegin
			pointBegin = pointEnd
			pointEnd = pointOriginal
		fillBegin = int( math.ceil( pointBegin.imag / width - frontOverWidth ) )
		fillBegin = max( 0, fillBegin )
		fillEnd = int( math.ceil( pointEnd.imag / width - frontOverWidth ) )
		fillEnd = min( len( xIntersectionIndexLists ), fillEnd )
		if fillEnd > fillBegin:
			secondMinusFirstComplex = pointEnd - pointBegin
			secondMinusFirstImaginaryOverReal = secondMinusFirstComplex.real / secondMinusFirstComplex.imag
			beginRealMinusImaginary = pointBegin.real - pointBegin.imag * secondMinusFirstImaginaryOverReal
			for fillLine in xrange( fillBegin, fillEnd ):
				xIntersection = yList[ fillLine ] * secondMinusFirstImaginaryOverReal + beginRealMinusImaginary
				xIntersectionIndexList = xIntersectionIndexLists[ fillLine ]
				xIntersectionIndexList.append( XIntersectionIndex( solidIndex, xIntersection ) )

def addXIntersectionIndexesFromLoops( frontOverWidth, loops, solidIndex, xIntersectionIndexLists, width, yList ):
	"Add the x intersection indexes for a loop."
	for loop in loops:
		addXIntersectionIndexesFromLoop( frontOverWidth, loop, solidIndex, xIntersectionIndexLists, width, yList )

def addXIntersectionIndexesFromLoopY( loop, solidIndex, xIntersectionIndexList, y ):
	"Add the x intersection indexes for a loop."
	for pointIndex in xrange( len( loop ) ):
		pointFirst = loop[ pointIndex ]
		pointSecond = loop[ ( pointIndex + 1 ) % len( loop ) ]
		isYAboveFirst = y > pointFirst.imag
		isYAboveSecond = y > pointSecond.imag
		if isYAboveFirst != isYAboveSecond:
			xIntersection = getXIntersection( pointFirst, pointSecond, y )
			xIntersectionIndexList.append( XIntersectionIndex( solidIndex, xIntersection ) )

def addXIntersectionIndexesFromLoopListsY( loopLists, xIntersectionIndexList, y ):
	"Add the x intersection indexes for the loop lists."
	for loopListIndex in xrange( len( loopLists ) ):
		loopList = loopLists[ loopListIndex ]
		addXIntersectionIndexesFromLoopsY( loopList, loopListIndex, xIntersectionIndexList, y )

def addXIntersectionIndexesFromLoopsY( loops, solidIndex, xIntersectionIndexList, y ):
	"Add the x intersection indexes for the loops."
	for loop in loops:
		addXIntersectionIndexesFromLoopY( loop, solidIndex, xIntersectionIndexList, y )

def addXIntersectionIndexesFromSegment( index, segment, xIntersectionIndexList ):
	"Add the x intersection indexes from the segment."
	for endpoint in segment:
		xIntersectionIndexList.append( XIntersectionIndex( index, endpoint.point.real ) )

def addXIntersectionIndexesFromSegments( index, segments, xIntersectionIndexList ):
	"Add the x intersection indexes from the segments."
	for segment in segments:
		addXIntersectionIndexesFromSegment( index, segment, xIntersectionIndexList )

def addXIntersectionIndexesFromXIntersections( index, xIntersectionIndexList, xIntersections ):
	"Add the x intersection indexes from the XIntersections."
	for xIntersection in xIntersections:
		xIntersectionIndexList.append( XIntersectionIndex( index, xIntersection ) )

def addXIntersections( loop, xIntersections, y ):
	"Add the x intersections for a loop."
	for pointIndex in xrange( len( loop ) ):
		pointFirst = loop[ pointIndex ]
		pointSecond = loop[ ( pointIndex + 1 ) % len( loop ) ]
		isYAboveFirst = y > pointFirst.imag
		isYAboveSecond = y > pointSecond.imag
		if isYAboveFirst != isYAboveSecond:
			xIntersections.append( getXIntersection( pointFirst, pointSecond, y ) )

def addXIntersectionsFromLoopForTable( loop, xIntersectionsTable, width ):
	"Add the x intersections for a loop into a table."
	for pointIndex in xrange( len( loop ) ):
		pointBegin = loop[ pointIndex ]
		pointEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		if pointBegin.imag > pointEnd.imag:
			pointOriginal = pointBegin
			pointBegin = pointEnd
			pointEnd = pointOriginal
		fillBegin = int( math.ceil( pointBegin.imag / width ) )
		fillEnd = int( math.ceil( pointEnd.imag / width ) )
		if fillEnd > fillBegin:
			secondMinusFirstComplex = pointEnd - pointBegin
			secondMinusFirstImaginaryOverReal = secondMinusFirstComplex.real / secondMinusFirstComplex.imag
			beginRealMinusImaginary = pointBegin.real - pointBegin.imag * secondMinusFirstImaginaryOverReal
			for fillLine in xrange( fillBegin, fillEnd ):
				y = fillLine * width
				xIntersection = y * secondMinusFirstImaginaryOverReal + beginRealMinusImaginary
				addElementToListTable( xIntersection, fillLine, xIntersectionsTable )

def addXIntersectionsFromLoops( loops, xIntersections, y ):
	"Add the x intersections for the loops."
	for loop in loops:
		addXIntersections( loop, xIntersections, y )

def addXIntersectionsFromLoopsForTable( loops, xIntersectionsTable, width ):
	"Add the x intersections for a loop into a table."
	for loop in loops:
		addXIntersectionsFromLoopForTable( loop, xIntersectionsTable, width )

def compareSegmentLength( endpoint, otherEndpoint ):
	"Get comparison in order to sort endpoints in ascending order of segment length."
	if endpoint.segmentLength > otherEndpoint.segmentLength:
		return 1
	if endpoint.segmentLength < otherEndpoint.segmentLength:
		return - 1
	return 0

def concatenateRemovePath( connectedPaths, pathIndex, paths, pixelTable, segments, width ):
	"Get connected paths from paths."
	bottomSegment = segments[ pathIndex ]
	path = paths[ pathIndex ]
	if bottomSegment == None:
		connectedPaths.append( path )
		return
	endpoints = getEndpointsFromSegments( segments[ pathIndex + 1 : ] )
	bottomSegmentEndpoint = bottomSegment[ 0 ]
	nextEndpoint = bottomSegmentEndpoint.getNearestMissCheckEndpointPath( endpoints, bottomSegmentEndpoint.path, pixelTable, width )
	if nextEndpoint == None:
		bottomSegmentEndpoint = bottomSegment[ 1 ]
		nextEndpoint = bottomSegmentEndpoint.getNearestMissCheckEndpointPath( endpoints, bottomSegmentEndpoint.path, pixelTable, width )
	if nextEndpoint == None:
		connectedPaths.append( path )
		return
	nextEndpoint.path.reverse()
	concatenatedPath = bottomSegmentEndpoint.path + nextEndpoint.path
	paths[ nextEndpoint.pathIndex ] = concatenatedPath
	segments[ nextEndpoint.pathIndex ] = getSegmentFromPath( concatenatedPath, nextEndpoint.pathIndex )
	addValueSegmentToPixelTable( bottomSegmentEndpoint.point, nextEndpoint.point, pixelTable, None, width )

def getAngleAroundZAxisDifference( subtractFromVec3, subtractVec3 ):
	"Get the angle around the Z axis difference between a pair of Vector3s."
	subtractVectorMirror = complex( subtractVec3.x , - subtractVec3.y )
	differenceVector = getRoundZAxisByPlaneAngle( subtractVectorMirror, subtractFromVec3 )
	return math.atan2( differenceVector.y, differenceVector.x )

def getAroundLoop( begin, end, loop ):
	"Get an arc around a loop."
	aroundLoop = []
	if end <= begin:
		end += len( loop )
	for pointIndex in xrange( begin, end ):
		aroundLoop.append( loop[ pointIndex % len( loop ) ] )
	return aroundLoop

def getAwayPoints( points, radius ):
	"Get a path with only the points that are far enough away from each other."
	away = []
	oneOverOverlapDistance = 100.0 / radius
	pixelTable = {}
	for point in points:
		x = int( point.real * oneOverOverlapDistance )
		y = int( point.imag * oneOverOverlapDistance )
		if not getSquareIsOccupied( pixelTable, x, y ):
			away.append( point )
			stepKey = getStepKey( x, y )
			pixelTable[ stepKey ] = None
	return away

def getBackOfLoops( loops ):
	"Get the back of the loops."
	negativeFloat = - 999999999.75342341
	back = negativeFloat
	for loop in loops:
		for point in loop:
			back = max( back, point.imag )
	if back == negativeFloat:
		print( "This should never happen, there are no loops for getBackOfLoops in euclidean" )
	return back

def getClippedAtEndLoopPath( clip, loopPath ):
	"Get a clipped loop path."
	if clip <= 0.0:
		return loopPath
	loopPathLength = getPathLength( loopPath )
	clip = min( clip, 0.3 * loopPathLength )
	lastLength = 0.0
	pointIndex = 0
	totalLength = 0.0
	clippedLength = loopPathLength - clip
	while totalLength < clippedLength and pointIndex < len( loopPath ) - 1:
		firstPoint = loopPath[ pointIndex ]
		secondPoint  = loopPath[ pointIndex + 1 ]
		pointIndex += 1
		lastLength = totalLength
		totalLength += abs( firstPoint - secondPoint )
	remainingLength = clippedLength - lastLength
	clippedLoopPath = loopPath[ : pointIndex ]
	ultimateClippedPoint = loopPath[ pointIndex ]
	penultimateClippedPoint = clippedLoopPath[ - 1 ]
	segment = ultimateClippedPoint - penultimateClippedPoint
	segmentLength = abs( segment )
	if segmentLength <= 0.0:
		return clippedLoopPath
	newUltimatePoint = penultimateClippedPoint + segment * remainingLength / segmentLength
	return clippedLoopPath + [ newUltimatePoint ]

def getClippedLoopPath( clip, loopPath ):
	"Get a clipped loop path."
	if clip <= 0.0:
		return loopPath
	loopPathLength = getPathLength( loopPath )
	clip = min( clip, 0.3 * loopPathLength )
	lastLength = 0.0
	pointIndex = 0
	totalLength = 0.0
	while totalLength < clip and pointIndex < len( loopPath ) - 1:
		firstPoint = loopPath[ pointIndex ]
		secondPoint  = loopPath[ pointIndex + 1 ]
		pointIndex += 1
		lastLength = totalLength
		totalLength += abs( firstPoint - secondPoint )
	remainingLength = clip - lastLength
	clippedLoopPath = loopPath[ pointIndex : ]
	ultimateClippedPoint = clippedLoopPath[ 0 ]
	penultimateClippedPoint = loopPath[ pointIndex - 1 ]
	segment = ultimateClippedPoint - penultimateClippedPoint
	segmentLength = abs( segment )
	loopPath = clippedLoopPath
	if segmentLength > 0.0:
		newUltimatePoint = penultimateClippedPoint + segment * remainingLength / segmentLength
		loopPath = [ newUltimatePoint ] + loopPath
	return getClippedAtEndLoopPath( clip, loopPath )

def getConnectedPaths( paths, pixelTable, width ):
	"Get connected paths from paths."
	if len( paths ) < 2:
		return paths
	connectedPaths = []
	segments = []
	for pathIndex in xrange( len( paths ) ):
		path = paths[ pathIndex ]
		segments.append( getSegmentFromPath( path, pathIndex ) )
	for pathIndex in xrange( 0, len( paths ) - 1 ):
		concatenateRemovePath( connectedPaths, pathIndex, paths, pixelTable, segments, width )
	connectedPaths.append( paths[ - 1 ] )
	return connectedPaths

def getCrossProduct( firstComplex, secondComplex ):
	"Get z component cross product of a pair of complexes."
	return firstComplex.real * secondComplex.imag - firstComplex.imag * secondComplex.real

def getDiagonalFlippedLoop( loop ):
	"Get loop flipped over the dialogonal, in other words with the x and y swapped."
	diagonalFlippedLoop = []
	for point in loop:
		diagonalFlippedLoop.append( complex( point.imag, point.real ) )
	return diagonalFlippedLoop

def getDiagonalFlippedLoops( loops ):
	"Get loops flipped over the dialogonal, in other words with the x and y swapped."
	diagonalFlippedLoops = []
	for loop in loops:
		diagonalFlippedLoops.append( getDiagonalFlippedLoop( loop ) )
	return diagonalFlippedLoops

def getDistanceToPlaneSegment( segmentBegin, segmentEnd, point ):
	"Get the distance squared from a point to the x & y components of a segment."
	segmentDifference = segmentEnd - segmentBegin
	pointMinusSegmentBegin = point - segmentBegin
	beginPlaneDot = getDotProduct( pointMinusSegmentBegin, segmentDifference )
	if beginPlaneDot <= 0.0:
		return abs( point - segmentBegin ) * abs( point - segmentBegin )
	differencePlaneDot = getDotProduct( segmentDifference, segmentDifference )
	if differencePlaneDot <= beginPlaneDot:
		return abs( point - segmentEnd ) * abs( point - segmentEnd )
	intercept = beginPlaneDot / differencePlaneDot
	interceptPerpendicular = segmentBegin + segmentDifference * intercept
	return abs( point - interceptPerpendicular ) * abs( point - interceptPerpendicular )

def getDotProduct( firstComplex, secondComplex ):
	"Get the dot product of a pair of complexes."
	return firstComplex.real * secondComplex.real + firstComplex.imag * secondComplex.imag

def getDotProductPlusOne( firstComplex, secondComplex ):
	"Get the dot product plus one of the x and y components of a pair of Vector3s."
	return 1.0 + getDotProduct( firstComplex, secondComplex )

def getEndpointFromPath( path, pathIndex ):
	"Get endpoint segment from a path."
	begin = path[ - 1 ]
	end = path[ - 2 ]
	endpointBegin = Endpoint()
	endpointEnd = Endpoint().getFromOtherPoint( endpointBegin, end )
	endpointBegin.getFromOtherPoint( endpointEnd, begin )
	endpointBegin.path = path
	endpointBegin.pathIndex = pathIndex
	return endpointBegin

def getEndpointsFromSegments( segments ):
	"Get endpoints from segments."
	endpoints = []
	for segment in segments:
		for endpoint in segment:
			endpoints.append( endpoint )
	return endpoints

def getEndpointsFromSegmentTable( segmentTable ):
	"Get the endpoints from the segment table."
	endpoints = []
	segmentTableKeys = segmentTable.keys()
	segmentTableKeys.sort()
	for segmentTableKey in segmentTableKeys:
		for segment in segmentTable[ segmentTableKey ]:
			for endpoint in segment:
				endpoints.append( endpoint )
	return endpoints

def getFillOfSurroundings( surroundingLoops ):
	"Get extra fill loops of surrounding loops."
	fillOfSurroundings = []
	for surroundingLoop in surroundingLoops:
		fillOfSurroundings += surroundingLoop.getFillLoops()
	return fillOfSurroundings

def getFourSignificantFigures( number ):
	"Get number rounded to four significant figures as a string."
	absoluteNumber = abs( number )
	if absoluteNumber >= 100.0:
		return getRoundedToDecimalPlacesString( 2, number )
	if absoluteNumber < 0.000000001:
		return getRoundedToDecimalPlacesString( 13, number )
	return getRoundedToDecimalPlacesString( 3 - math.floor( math.log10( absoluteNumber ) ), number )

def getFrontOfLoops( loops ):
	"Get the front of the loops."
	bigFloat = 999999999.196854654
	front = bigFloat
	for loop in loops:
		for point in loop:
			front = min( front, point.imag )
	if front == bigFloat:
		print( "This should never happen, there are no loops for getFrontOfLoops in euclidean" )
	return front

def getFrontOverWidthAddXListYList( front, loopLists, numberOfLines, xIntersectionIndexLists, width, yList ):
	"Get the front over width and add the x intersection index lists and ylist."
	frontOverWidth = getFrontOverWidthAddYList( front, numberOfLines, xIntersectionIndexLists, width, yList )
	for loopListIndex in xrange( len( loopLists ) ):
		loopList = loopLists[ loopListIndex ]
		addXIntersectionIndexesFromLoops( frontOverWidth, loopList, loopListIndex, xIntersectionIndexLists, width, yList )
	return frontOverWidth

def getFrontOverWidthAddYList( front, numberOfLines, xIntersectionIndexLists, width, yList ):
	"Get the front over width and add the x intersection index lists and ylist."
	frontOverWidth = front / width
	for fillLine in xrange( numberOfLines ):
		yList.append( front + float( fillLine ) * width )
		xIntersectionIndexLists.append( [] )
	return frontOverWidth

def getHalfSimplifiedLoop( loop, radius, remainder ):
	"Get the loop with half of the points inside the channel removed."
	if len( loop ) < 2:
		return loop
	channelRadius = radius * .01
	simplified = []
	addIndex = 0
	if remainder == 1:
		addIndex = len( loop ) - 1
	for pointIndex in xrange( len( loop ) ):
		point = loop[ pointIndex ]
		if pointIndex % 2 == remainder or pointIndex == addIndex:
			simplified.append( point )
		elif not isWithinChannel( channelRadius, pointIndex, loop ):
			simplified.append( point )
	return simplified

def getHalfSimplifiedPath( path, radius, remainder ):
	"Get the path with half of the points inside the channel removed."
	if len( path ) < 2:
		return path
	channelRadius = radius * .01
	simplified = []
	addIndex = len( path ) - 1
	for pointIndex in xrange( len( path ) ):
		point = path[ pointIndex ]
		if pointIndex % 2 == remainder or pointIndex == 0 or pointIndex == addIndex:
			simplified.append( point )
		elif not isWithinChannel( channelRadius, pointIndex, path ):
			simplified.append( point )
	return simplified

def getHorizontalSegmentListsFromLoopLists( alreadyFilledArounds, front, numberOfLines, rotatedFillLoops, width ):
	"Get horizontal segment lists inside loops."
	xIntersectionIndexLists = []
	yList = []
	frontOverWidth = getFrontOverWidthAddXListYList( front, alreadyFilledArounds, numberOfLines, xIntersectionIndexLists, width, yList )
	addXIntersectionIndexesFromLoops( frontOverWidth, rotatedFillLoops, - 1, xIntersectionIndexLists, width, yList )
	horizontalSegmentLists = []
	for xIntersectionIndexListIndex in xrange( len( xIntersectionIndexLists ) ):
		xIntersectionIndexList = xIntersectionIndexLists[ xIntersectionIndexListIndex ]
		lineSegments = getSegmentsFromXIntersectionIndexes( xIntersectionIndexList, yList[ xIntersectionIndexListIndex ] )
		horizontalSegmentLists.append( lineSegments )
	return horizontalSegmentLists

def getIncrementFromRank( rank ):
	"Get the increment from the rank which is 0 at 1 and increases by three every power of ten."
	rankZone = int( math.floor( rank / 3 ) )
	rankModulo = rank % 3
	powerOfTen = pow( 10, rankZone )
	moduloMultipliers = ( 1, 2, 5 )
	return float( powerOfTen * moduloMultipliers[ rankModulo ] )

def getInsidesAddToOutsides( loops, outsides ):
	"Add loops to either the insides or outsides."
	insides = []
	for loopIndex in xrange( len( loops ) ):
		loop = loops[ loopIndex ]
		if isInsideOtherLoops( loopIndex, loops ):
			insides.append( loop )
		else:
			outsides.append( loop )
	return insides

def getIntermediateLocation( alongWay, begin, end ):
	"Get the intermediate location between begin and end."
	return begin * ( 1.0 - alongWay ) + end * alongWay

def getIntersectionOfXIntersectionIndexes( totalSolidSurfaceThickness, xIntersectionIndexList ):
	"Get x intersections from surrounding layers."
	xIntersectionList = []
	solidTable = {}
	solid = False
	xIntersectionIndexList.sort()
	for xIntersectionIndex in xIntersectionIndexList:
		toggleHashtable( solidTable, xIntersectionIndex.index, "" )
		oldSolid = solid
		solid = len( solidTable ) >= totalSolidSurfaceThickness
		if oldSolid != solid:
			xIntersectionList.append( xIntersectionIndex.x )
	return xIntersectionList

def getIntersectionOfXIntersectionsTables( xIntersectionsTables ):
	"Get the intersection of both XIntersections tables."
	intersectionOfXIntersectionsTables = {}
	firstIntersectionTable = xIntersectionsTables[ 0 ]
	for firstIntersectionTableKey in firstIntersectionTable.keys():
		xIntersectionIndexList = []
		for xIntersectionsTableIndex in xrange( len( xIntersectionsTables ) ):
			xIntersectionsTable = xIntersectionsTables[ xIntersectionsTableIndex ]
			addXIntersectionIndexesFromXIntersections( xIntersectionsTableIndex, xIntersectionIndexList, xIntersectionsTable[ firstIntersectionTableKey ] )
		xIntersections = getIntersectionOfXIntersectionIndexes( len( xIntersectionsTables ), xIntersectionIndexList )
		if len( xIntersections ) > 0:
			intersectionOfXIntersectionsTables[ firstIntersectionTableKey ] = xIntersections
	return intersectionOfXIntersectionsTables

def getJoinOfXIntersectionIndexes( xIntersectionIndexList ):
	"Get joined x intersections from surrounding layers."
	xIntersections = []
	solidTable = {}
	solid = False
	xIntersectionIndexList.sort()
	for xIntersectionIndex in xIntersectionIndexList:
		toggleHashtable( solidTable, xIntersectionIndex.index, "" )
		oldSolid = solid
		solid = len( solidTable ) > 0
		if oldSolid != solid:
			xIntersections.append( xIntersectionIndex.x )
	return xIntersections

def getLargestLoop( loops ):
	"Get largest loop from loops."
	if len( loops ) == 1:
		return loops[ 0 ]
	largestArea = - 999999999.0
	largestLoop = None
	for loop in loops:
		loopArea = abs( getPolygonArea( loop ) )
		if loopArea > largestArea:
			largestArea = loopArea
			largestLoop = loop
	return largestLoop

def getLastExistingFillOfSurroundings( surroundingLoops ):
	"Get extra fill loops of surrounding loops."
	lastExistingFillOfSurroundings = []
	for surroundingLoop in surroundingLoops:
		lastExistingFillOfSurroundings += surroundingLoop.getLastExistingFillLoops()
	return lastExistingFillOfSurroundings

def getLeftPoint( points ):
	"Get the leftmost complex point in the points."
	leftmost = 999999999.0
	leftPointComplex = None
	for pointComplex in points:
		if pointComplex.real < leftmost:
			leftmost = pointComplex.real
			leftPointComplex = pointComplex
	return leftPointComplex

def getListTableElements( listTable ):
	"Get all the element in a list table."
	listTableElements = []
	for listTableValue in listTable.values():
		listTableElements += listTableValue
	return listTableElements

def getLoopInsideContainingLoop( containingLoop, loops ):
	"Get a loop that is inside the containing loop."
	for loop in loops:
		if loop != containingLoop:
			if isPathInsideLoop( containingLoop, loop ):
				return loop
	return None

def getLoopStartingNearest( extrusionHalfWidth, location, loop ):
	"Add to threads from the last location from loop."
	nearestIndex = getNearestDistanceIndex( location, loop ).index
	loop = getAroundLoop( nearestIndex, nearestIndex, loop )
	nearestPoint = getNearestPointOnSegment( loop[ 0 ], loop[ 1 ], location )
	if abs( nearestPoint - loop[ 0 ] ) > extrusionHalfWidth and abs( nearestPoint - loop[ 1 ] ) > extrusionHalfWidth:
		loop = [ nearestPoint ] + loop[ 1 : ] + [ loop[ 0 ] ]
	elif abs( nearestPoint - loop[ 0 ] ) > abs( nearestPoint - loop[ 1 ] ):
		loop = loop[ 1 : ] + [ loop[ 0 ] ]
	return loop

def getMaximum( firstComplex, secondComplex ):
	"Get a complex with each component the maximum of the respective components of a pair of complexes."
	return complex( max( firstComplex.real, secondComplex.real ), max( firstComplex.imag, secondComplex.imag ) )

def getMaximumFromPoints( points ):
	"Get a complex with each component the maximum of the respective components of a list of complex points."
	maximum = complex( - 999999999.0, - 999999999.0 )
	for pointComplex in points:
		maximum = getMaximum( maximum, pointComplex )
	return maximum

def getMaximumSpan( loop ):
	"Get the maximum span of the loop."
	extent = getMaximumFromPoints( loop ) - getMinimumFromPoints( loop )
	return max( extent.real, extent.imag )

def getMinimum( firstComplex, secondComplex ):
	"Get a complex with each component the minimum of the respective components of a pair of complexes."
	return complex( min( firstComplex.real, secondComplex.real ), min( firstComplex.imag, secondComplex.imag ) )

def getMinimumFromPoints( points ):
	"Get a complex with each component the minimum of the respective components of a list of complex points."
	minimum = complex( 999999999.0, 999999999.0 )
	for pointComplex in points:
		minimum = getMinimum( minimum, pointComplex )
	return minimum

def getMinimumFromVec3List( vec3List ):
	"Get a complex with each component the minimum of the respective components of a list of Vector3s."
	minimum = complex( 999999999.0, 999999999.0 )
	for point in vec3List:
		minimum = getMinimum( minimum, point.dropAxis( 2 ) )
	return minimum

def getNearestDistanceIndex( point, loop ):
	"Get the distance squared to the nearest segment of the loop and index of that segment."
	smallestDistance = 999999999999999999.0
	nearestDistanceIndex = None
	for pointIndex in xrange( len( loop ) ):
		segmentBegin = loop[ pointIndex ]
		segmentEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		distance = getDistanceToPlaneSegment( segmentBegin, segmentEnd, point )
		if distance < smallestDistance:
			smallestDistance = distance
			nearestDistanceIndex = DistanceIndex( distance, pointIndex )
	return nearestDistanceIndex

def getNearestPointOnSegment( segmentBegin, segmentEnd, point ):
	"Get the nearest point on the segment."
	segmentDifference = segmentEnd - segmentBegin
	pointMinusSegmentBegin = point - segmentBegin
	beginPlaneDot = getDotProduct( pointMinusSegmentBegin, segmentDifference )
	differencePlaneDot = getDotProduct( segmentDifference, segmentDifference )
	intercept = beginPlaneDot / differencePlaneDot
	intercept = max( intercept, 0.0 )
	intercept = min( intercept, 1.0 )
	return segmentBegin + segmentDifference * intercept

def getNormalized( complexNumber ):
	"Get the normalized complex."
	complexNumberLength = abs( complexNumber )
	if complexNumberLength > 0.0:
		return complexNumber / complexNumberLength
	return complexNumber

def getNumberOfIntersectionsToLeft( loop, point ):
	"Get the number of intersections through the loops for the line starting from the left point and going left."
	numberOfIntersectionsToLeft = 0
	for pointIndex in xrange( len( loop ) ):
		firstPointComplex = loop[ pointIndex ]
		secondPointComplex = loop[ ( pointIndex + 1 ) % len( loop ) ]
		isLeftAboveFirst = point.imag > firstPointComplex.imag
		isLeftAboveSecond = point.imag > secondPointComplex.imag
		if isLeftAboveFirst != isLeftAboveSecond:
			if getXIntersection( firstPointComplex, secondPointComplex, point.imag ) < point.real:
				numberOfIntersectionsToLeft += 1
	return numberOfIntersectionsToLeft

def getNumberOfIntersectionsToLeftOfLoops( loops, point ):
	"Get the number of intersections through the loop for the line starting from the left point and going left."
	totalNumberOfIntersectionsToLeft = 0
	for loop in loops:
		totalNumberOfIntersectionsToLeft += getNumberOfIntersectionsToLeft( loop, point )
	return totalNumberOfIntersectionsToLeft

def getOrderedSurroundingLoops( perimeterWidth, surroundingLoops ):
	"Get ordered surrounding loops from surrounding loops."
	insides = []
	orderedSurroundingLoops = []
	for loopIndex in xrange( len( surroundingLoops ) ):
		surroundingLoop = surroundingLoops[ loopIndex ]
		otherLoops = []
		for beforeIndex in xrange( loopIndex ):
			otherLoops.append( surroundingLoops[ beforeIndex ].boundary )
		for afterIndex in xrange( loopIndex + 1, len( surroundingLoops ) ):
			otherLoops.append( surroundingLoops[ afterIndex ].boundary )
		if isPathEntirelyInsideLoops( otherLoops, surroundingLoop.boundary ):
			insides.append( surroundingLoop )
		else:
			orderedSurroundingLoops.append( surroundingLoop )
	for outside in orderedSurroundingLoops:
		outside.getFromInsideSurroundings( insides, perimeterWidth )
	return orderedSurroundingLoops

def getPathLength( path ):
	"Get the length of a path ( an open polyline )."
	pathLength = 0.0
	for pointIndex in xrange( len( path ) - 1 ):
		firstPoint = path[ pointIndex ]
		secondPoint  = path[ pointIndex + 1 ]
		pathLength += abs( firstPoint - secondPoint )
	return pathLength

def getPathsFromEndpoints( endpoints, fillInset, pixelTable, width ):
	"Get paths from endpoints."
	for beginningEndpoint in endpoints[ : : 2 ]:
		beginningPoint = beginningEndpoint.point
		addSegmentToPixelTable( beginningPoint, beginningEndpoint.otherEndpoint.point, pixelTable, 0, 0, width )
	endpointFirst = endpoints[ 0 ]
	endpoints.remove( endpointFirst )
	otherEndpoint = endpointFirst.otherEndpoint
	endpoints.remove( otherEndpoint )
	nextEndpoint = None
	path = []
	paths = [ path ]
	if len( endpoints ) > 1:
		nextEndpoint = otherEndpoint.getNearestMiss( endpoints, path, pixelTable, width )
		if nextEndpoint != None:
			if abs( nextEndpoint.point - endpointFirst.point ) < abs( nextEndpoint.point - otherEndpoint.point ):
				endpointFirst = endpointFirst.otherEndpoint
				otherEndpoint = endpointFirst.otherEndpoint
	addPointToPath( path, pixelTable, endpointFirst.point, None, width )
	addPointToPath( path, pixelTable, otherEndpoint.point, len( paths ) - 1, width )
	oneOverEndpointWidth = 0.2 / fillInset
	endpointTable = {}
	for endpoint in endpoints:
		addElementToPixelListFromPoint( endpoint, endpointTable, endpoint.point * oneOverEndpointWidth )
	while len( endpointTable ) > 0:
		if len( endpointTable ) == 1:
			if len( endpointTable.values()[ 0 ] ) < 2:
				return
		endpoints = getSquareValuesFromPoint( endpointTable, otherEndpoint.point * oneOverEndpointWidth )
		nextEndpoint = otherEndpoint.getNearestMiss( endpoints, path, pixelTable, width )
		if nextEndpoint == None:
			path = []
			paths.append( path )
			endpoints = getListTableElements( endpointTable )
			nextEndpoint = otherEndpoint.getNearestEndpoint( endpoints )
# this commented code should be faster than the getListTableElements code, but it isn't, someday a spiral algorithim could be tried
#			endpoints = getSquareValuesFromPoint( endpointTable, otherEndpoint.point * oneOverEndpointWidth )
#			nextEndpoint = otherEndpoint.getNearestEndpoint( endpoints )
#			if nextEndpoint == None:
#				endpoints = []
#				for endpointTableValue in endpointTable.values():
#					endpoints.append( endpointTableValue[ 0 ] )
#				nextEndpoint = otherEndpoint.getNearestEndpoint( endpoints )
#				endpoints = getSquareValuesFromPoint( endpointTable, nextEndpoint.point * oneOverEndpointWidth )
#				nextEndpoint = otherEndpoint.getNearestEndpoint( endpoints )
		addPointToPath( path, pixelTable, nextEndpoint.point, len( paths ) - 1, width )
		removeElementFromPixelListFromPoint( nextEndpoint, endpointTable, nextEndpoint.point * oneOverEndpointWidth )
		otherEndpoint = nextEndpoint.otherEndpoint
		hop = nextEndpoint.getHop( fillInset, path )
		if hop != None:
			if len( path ) < 2:
				print( 'path of length one in getPathsFromEndpoints in euclidean, this should never happen')
				print( path )
			path = [ hop ]
			paths.append( path )
		addPointToPath( path, pixelTable, otherEndpoint.point, len( paths ) - 1, width )
		removeElementFromPixelListFromPoint( otherEndpoint, endpointTable, otherEndpoint.point * oneOverEndpointWidth )
	return paths

def getPlaneDot( vec3First, vec3Second ):
	"Get the dot product of the x and y components of a pair of Vector3s."
	return vec3First.x * vec3Second.x + vec3First.y * vec3Second.y

def getPointsRoundZAxis( planeAngle, points ):
	"Get points rotated by the plane angle"
	planeArray = []
	for point in points:
		planeArray.append( planeAngle * point )
	return planeArray

def getPointMaximum( firstPoint, secondPoint ):
	"Get a point with each component the maximum of the respective components of a pair of Vector3s."
	return Vector3( max( firstPoint.x, secondPoint.x ), max( firstPoint.y, secondPoint.y ), max( firstPoint.z, secondPoint.z ) )

def getPointMinimum( firstPoint, secondPoint ):
	"Get a point with each component the minimum of the respective components of a pair of Vector3s."
	return Vector3( min( firstPoint.x, secondPoint.x ), min( firstPoint.y, secondPoint.y ), min( firstPoint.z, secondPoint.z ) )

def getPointPlusSegmentWithLength( length, point, segment ):
	"Get point plus a segment scaled to a given length."
	return segment * length / abs( segment ) + point

def getPolygonArea( polygonComplex ):
	"Get the area of a complex polygon."
	polygonComplexArea = 0.0
	for pointIndex in xrange( len( polygonComplex ) ):
		point = polygonComplex[ pointIndex ]
		secondPointComplex  = polygonComplex[ ( pointIndex + 1 ) % len( polygonComplex ) ]
		area  = point.real * secondPointComplex.imag - secondPointComplex.real * point.imag
		polygonComplexArea += area
	return 0.5 * polygonComplexArea

def getPolygonLength( polygon ):
	"Get the length of a polygon perimeter."
	polygonLength = 0.0
	for pointIndex in xrange( len( polygon ) ):
		point = polygon[ pointIndex ]
		secondPoint  = polygon[ ( pointIndex + 1 ) % len( polygon ) ]
		polygonLength += abs( point - secondPoint )
	return polygonLength

def getRank( width ):
	"Get the rank which is 0 at 1 and increases by three every power of ten."
	return int( math.floor( 3.0 * math.log10( width ) ) )

def getRotatedWiddershinsQuarterAroundZAxis( vector3 ):
	"Get Vector3 rotated a quarter widdershins turn around Z axis."
	return Vector3( - vector3.y, vector3.x, vector3.z )

def getRoundedPoint( point ):
	"Get point with each component rounded."
	return Vector3( round( point.x ), round( point.y ), round( point.z ) )

def getRoundedToDecimalPlaces( decimalPlaces, number ):
	"Get number rounded to a number of decimal places."
	decimalPlacesRounded = max( 1, int( round( decimalPlaces ) ) )
	return round( number, decimalPlacesRounded )

def getRoundedToDecimalPlacesString( decimalPlaces, number ):
	"Get number rounded to a number of decimal places as a string."
	return str( getRoundedToDecimalPlaces( decimalPlaces, number ) )

def getRoundedToThreePlaces( number ):
	"Get number rounded to three places as a string."
	return str( round( number, 3 ) )

def getRoundZAxisByPlaneAngle( planeAngle, vector3 ):
	"Get Vector3 rotated by a plane angle."
	return Vector3( vector3.x * planeAngle.real - vector3.y * planeAngle.imag, vector3.x * planeAngle.imag + vector3.y * planeAngle.real, vector3.z )

def getSegmentFromPath( path, pathIndex ):
	"Get endpoint segment from a path."
	if len( path ) < 2:
		return None
	begin = path[ - 1 ]
	end = path[ - 2 ]
	forwardEndpoint = getEndpointFromPath( path, pathIndex )
	reversePath = path[ : ]
	reversePath.reverse()
	reverseEndpoint = getEndpointFromPath( reversePath, pathIndex )
	return ( forwardEndpoint, reverseEndpoint )

def getSegmentFromPoints( begin, end ):
	"Get endpoint segment from a pair of points."
	endpointFirst = Endpoint()
	endpointSecond = Endpoint().getFromOtherPoint( endpointFirst, end )
	endpointFirst.getFromOtherPoint( endpointSecond, begin )
	return ( endpointFirst, endpointSecond )

def getSegmentsFromXIntersections( xIntersections, y ):
	"Get endpoint segments from the x intersections."
	segments = []
	end = len( xIntersections )
	if len( xIntersections ) % 2 == 1:
		end -= 1
	for xIntersectionIndex in xrange( 0, end, 2 ):
		firstX = xIntersections[ xIntersectionIndex ]
		secondX = xIntersections[ xIntersectionIndex + 1 ]
		if firstX != secondX:
			segments.append( getSegmentFromPoints( complex( firstX, y ), complex( secondX, y ) ) )
	return segments

def getSegmentsFromXIntersectionIndexes( xIntersectionIndexList, y ):
	"Get endpoint segments from the x intersection indexes."
	xIntersections = getXIntersectionsFromIntersections( xIntersectionIndexList )
	return getSegmentsFromXIntersections( xIntersections, y )

def getSimplifiedLoop( loop, radius ):
	"Get loop with points inside the channel removed."
	if len( loop ) < 2:
		return loop
	simplificationMultiplication = 256
	simplificationRadius = radius / float( simplificationMultiplication )
	maximumIndex = len( loop ) * simplificationMultiplication
	pointIndex = 1
	while pointIndex < maximumIndex:
		oldLoopLength = len( loop )
		loop = getHalfSimplifiedLoop( loop, simplificationRadius, 0 )
		loop = getHalfSimplifiedLoop( loop, simplificationRadius, 1 )
		simplificationRadius += simplificationRadius
		if oldLoopLength == len( loop ):
			if simplificationRadius > radius:
				return getAwayPoints( loop, radius )
			else:
				simplificationRadius *= 1.5
		simplificationRadius = min( simplificationRadius, radius )
		pointIndex += pointIndex
	return getAwayPoints( loop, radius )

def getSimplifiedLoops( loops, radius ):
	"Get the simplified loops."
	simplifiedLoops = []
	for loop in loops:
		simplifiedLoops.append( getSimplifiedLoop( loop, radius ) )
	return simplifiedLoops

def getSimplifiedPath( path, radius ):
	"Get path with points inside the channel removed."
	if len( path ) < 2:
		return path
	simplificationMultiplication = 256
	simplificationRadius = radius / float( simplificationMultiplication )
	maximumIndex = len( path ) * simplificationMultiplication
	pointIndex = 1
	while pointIndex < maximumIndex:
		oldPathLength = len( path )
		path = getHalfSimplifiedPath( path, simplificationRadius, 0 )
		path = getHalfSimplifiedPath( path, simplificationRadius, 1 )
		simplificationRadius += simplificationRadius
		if oldPathLength == len( path ):
			if simplificationRadius > radius:
				return getAwayPoints( path, radius )
			else:
				simplificationRadius *= 1.5
		simplificationRadius = min( simplificationRadius, radius )
		pointIndex += pointIndex
	return getAwayPoints( path, radius )

def getSquareIsOccupied( pixelTable, x, y ):
	"Determine if a square around the x and y pixel coordinates is occupied."
	squareValues = []
	for xStep in xrange( x - 1, x + 2 ):
		for yStep in xrange( y - 1, y + 2 ):
			stepKey = getStepKey( xStep, yStep )
			if stepKey in pixelTable:
				return True
	return False

def getSquareLoop( beginComplex, endComplex ):
	"Get a square loop from the beginning to the end and back."
	loop = [ beginComplex ]
	loop.append( complex( beginComplex.real, endComplex.imag ) )
	loop.append( endComplex )
	loop.append( complex( endComplex.real, beginComplex.imag ) )
	return loop

def getSquareValues( pixelTable, x, y ):
	"Get a list of the values in a square around the x and y pixel coordinates."
	squareValues = []
	for xStep in xrange( x - 1, x + 2 ):
		for yStep in xrange( y - 1, y + 2 ):
			stepKey = getStepKey( xStep, yStep )
			if stepKey in pixelTable:
				squareValues += pixelTable[ stepKey ]
	return squareValues

def getSquareValuesFromPoint( pixelTable, point ):
	"Get a list of the values in a square around the point."
	return getSquareValues( pixelTable, int( round( point.real ) ), int( round( point.imag ) ) )

def getStepKey( x, y ):
	"Get step key for x and y."
	return ( x, y )

def getStepKeyFromPoint( point ):
	"Get step key for the point."
	return ( int( round( point.real ) ), int( round( point.imag ) ) )

def getThreeSignificantFigures( number ):
	"Get number rounded to three significant figures as a string."
	absoluteNumber = abs( number )
	if absoluteNumber >= 10.0:
		return getRoundedToDecimalPlacesString( 1, number )
	if absoluteNumber < 0.000000001:
		return getRoundedToDecimalPlacesString( 12, number )
	return getRoundedToDecimalPlacesString( 1 - math.floor( math.log10( absoluteNumber ) ), number )

def getTransferClosestSurroundingLoop( oldOrderedLocation, remainingSurroundingLoops, skein ):
	"Get and transfer the closest remaining surrounding loop."
	if len( remainingSurroundingLoops ) > 0:
		oldOrderedLocation.z = remainingSurroundingLoops[ 0 ].z
	closestDistance = 999999999999999999.0
	closestSurroundingLoop = None
	for remainingSurroundingLoop in remainingSurroundingLoops:
		distance = getNearestDistanceIndex( oldOrderedLocation.dropAxis( 2 ), remainingSurroundingLoop.boundary ).distance
		if distance < closestDistance:
			closestDistance = distance
			closestSurroundingLoop = remainingSurroundingLoop
	remainingSurroundingLoops.remove( closestSurroundingLoop )
	closestSurroundingLoop.addToThreads( oldOrderedLocation, skein )
	return closestSurroundingLoop

def getTransferredPaths( insides, loop ):
	"Get transferred paths from inside paths."
	transferredPaths = []
	for insideIndex in xrange( len( insides ) - 1, - 1, - 1 ):
		inside = insides[ insideIndex ]
		if isPathInsideLoop( loop, inside ):
			transferredPaths.append( inside )
			del insides[ insideIndex ]
	return transferredPaths

def getTransferredSurroundingLoops( insides, loop ):
	"Get transferred paths from inside surrounding loops."
	transferredSurroundings = []
	for insideIndex in xrange( len( insides ) - 1, - 1, - 1 ):
		insideSurrounding = insides[ insideIndex ]
		if isPathInsideLoop( loop, insideSurrounding.boundary ):
			transferredSurroundings.append( insideSurrounding )
			del insides[ insideIndex ]
	return transferredSurroundings

def getUnitPolar( angle ):
	"Get polar complex from counterclockwise angle from 1, 0."
	return complex( math.cos( angle ), math.sin( angle ) )

def getXIntersection( firstComplex, secondComplex, y ):
	"Get where the line crosses y."
	secondMinusFirstComplex = secondComplex - firstComplex
	yMinusFirst = y - firstComplex.imag
	return yMinusFirst * secondMinusFirstComplex.real / secondMinusFirstComplex.imag + firstComplex.real

def getXIntersectionsFromIntersections( xIntersectionIndexList ):
	"Get x intersections from the x intersection index list, in other words subtract non negative intersections from negatives."
	xIntersections = []
	fill = False
	solid = False
	solidTable = {}
	xIntersectionIndexList.sort()
	for solidX in xIntersectionIndexList:
		if solidX.index >= 0:
			toggleHashtable( solidTable, solidX.index, "" )
		else:
			fill = not fill
		oldSolid = solid
		solid = ( len( solidTable ) == 0 and fill )
		if oldSolid != solid:
			xIntersections.append( solidX.x )
	return xIntersections

def getXYComplexFromVector3( vector3 ):
	"Get an xy complex from a vector3 if it exists, otherwise return None."
	if vector3 == None:
		return None
	return vector3.dropAxis( 2 )

def getZComponentCrossProduct( vec3First, vec3Second ):
	"Get z component cross product of a pair of Vector3s."
	return vec3First.x * vec3Second.y - vec3First.y * vec3Second.x

def isInFilledRegion( loops, point ):
	"Determine if the left point is in the filled region of the loops."
	return getNumberOfIntersectionsToLeftOfLoops( loops, point ) % 2 == 1

def isInsideOtherLoops( loopIndex, loops ):
	"Determine if a loop in a list is inside another loop in that list."
	return isPathInsideLoops( loops[ : loopIndex ] + loops[ loopIndex + 1 : ], loops[ loopIndex ] )

def isLineIntersectingInsideXSegment( segmentFirstX, segmentSecondX, vector3First, vector3Second, y ):
	"Determine if the line is crossing inside the x segment."
	isYAboveFirst = y > vector3First.imag
	isYAboveSecond = y > vector3Second.imag
	if isYAboveFirst == isYAboveSecond:
		return False
	xIntersection = getXIntersection( vector3First, vector3Second, y )
	if xIntersection <= min( segmentFirstX, segmentSecondX ):
		return False
	return xIntersection < max( segmentFirstX, segmentSecondX )

def isLineIntersectingLoop( loop, pointBegin, pointEnd ):
	"Determine if the line is intersecting loops."
	normalizedSegment = pointEnd - pointBegin
	normalizedSegmentLength = abs( normalizedSegment )
	if normalizedSegmentLength > 0.0:
		normalizedSegment /= normalizedSegmentLength
		segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
		pointBeginRotated = segmentYMirror * pointBegin
		pointEndRotated = segmentYMirror * pointEnd
		if isLoopIntersectingInsideXSegment( loop, pointBeginRotated.real, pointEndRotated.real, segmentYMirror, pointBeginRotated.imag ):
			return True
	return False

def isLineIntersectingLoops( loops, pointBegin, pointEnd ):
	"Determine if the line is intersecting loops."
	normalizedSegment = pointEnd - pointBegin
	normalizedSegmentLength = abs( normalizedSegment )
	if normalizedSegmentLength > 0.0:
		normalizedSegment /= normalizedSegmentLength
		segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
		pointBeginRotated = segmentYMirror * pointBegin
		pointEndRotated = segmentYMirror * pointEnd
		if isLoopListIntersectingInsideXSegment( loops, pointBeginRotated.real, pointEndRotated.real, segmentYMirror, pointBeginRotated.imag ):
			return True
	return False

def isLoopIntersectingInsideXSegment( loop, segmentFirstX, segmentSecondX, segmentYMirror, y ):
	"Determine if the loop is intersecting inside the x segment."
	rotatedLoop = getPointsRoundZAxis( segmentYMirror, loop )
	for pointIndex in xrange( len( rotatedLoop ) ):
		pointFirst = rotatedLoop[ pointIndex ]
		pointSecond = rotatedLoop[ ( pointIndex + 1 ) % len( rotatedLoop ) ]
		if isLineIntersectingInsideXSegment( segmentFirstX, segmentSecondX, pointFirst, pointSecond, y ):
			return True
	return False

def isLoopIntersectingLoop( loop, otherLoop ):
	"Determine if the loop is intersecting the other loop."
	for pointIndex in xrange( len( loop ) ):
		pointBegin = loop[ pointIndex ]
		pointEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		if isLineIntersectingLoop( otherLoop, pointBegin, pointEnd ):
			return True
	return False

def isLoopIntersectingLoops( loop, otherLoops ):
	"Determine if the loop is intersecting other loops."
	for pointIndex in xrange( len( loop ) ):
		pointBegin = loop[ pointIndex ]
		pointEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		if isLineIntersectingLoops( otherLoops, pointBegin, pointEnd ):
			return True
	return False

def isLoopListIntersectingInsideXSegment( loopList, segmentFirstX, segmentSecondX, segmentYMirror, y ):
	"Determine if the loop list is crossing inside the x segment."
	for alreadyFilledLoop in loopList:
		if isLoopIntersectingInsideXSegment( alreadyFilledLoop, segmentFirstX, segmentSecondX, segmentYMirror, y ):
			return True
	return False

def isPathEntirelyInsideLoop( loop, path ):
	"Determine if a path is entirely inside another loop."
	leftPoint = getLeftPoint( path )
	if not isPointInsideLoop( loop, leftPoint ):
		return False
	for point in path:
		if not isPointInsideLoop( loop, point ):
			return False
	return True

def isPathEntirelyInsideLoops( loops, path ):
	"Determine if a path is entirely inside another loop in a list."
	for loop in loops:
		if isPathEntirelyInsideLoop( loop, path ):
			return True
	return False

def isPathInsideLoop( loop, path ):
	"Determine if a path is inside another loop."
	leftPoint = getLeftPoint( path )
	return isPointInsideLoop( loop, leftPoint )

def isPathInsideLoops( loops, path ):
	"Determine if a path is inside another loop in a list."
	for loop in loops:
		if isPathInsideLoop( loop, path ):
			return True
	return False

def isPixelTableIntersecting( bigTable, littleTable, maskTable = {} ):
	"Add path to the pixel table."
	littleTableKeys = littleTable.keys()
	for littleTableKey in littleTableKeys:
		if littleTableKey not in maskTable:
			if littleTableKey in bigTable:
				return True
	return False

def isPointInsideLoop( loop, point ):
	"Determine if a point is inside another loop."
	return getNumberOfIntersectionsToLeft( loop, point ) % 2 == 1

def isPointInsideLoops( loops, point ):
	"Determine if a point is inside a loop list."
	for loop in loops:
		if isPointInsideLoop( loop, point ):
			return True
	return False

def isSegmentCompletelyInX( segment, xFirst, xSecond ):
	"Determine if the segment overlaps within x."
	segmentFirstX = segment[ 0 ].point.real
	segmentSecondX = segment[ 1 ].point.real
	if max( segmentFirstX, segmentSecondX ) > max( xFirst, xSecond ):
		return False
	return min( segmentFirstX, segmentSecondX ) >= min( xFirst, xSecond )

def isWiddershins( polygonComplex ):
	"Determine if the complex polygon goes round in the widdershins direction."
	return getPolygonArea( polygonComplex ) > 0.0

def isWithinChannel( channelRadius, pointIndex, loop ):
	"Determine if the the point is within the channel between two adjacent points."
	point = loop[ pointIndex ]
	behindSegmentComplex = loop[ ( pointIndex + len( loop ) - 1 ) % len( loop ) ] - point
	behindSegmentComplexLength = abs( behindSegmentComplex )
	if behindSegmentComplexLength < channelRadius:
		return True
	aheadSegmentComplex = loop[ ( pointIndex + 1 ) % len( loop ) ] - point
	aheadSegmentComplexLength = abs( aheadSegmentComplex )
	if aheadSegmentComplexLength < channelRadius:
		return True
	behindSegmentComplex /= behindSegmentComplexLength
	aheadSegmentComplex /= aheadSegmentComplexLength
	absoluteZ = getDotProductPlusOne( aheadSegmentComplex, behindSegmentComplex )
	if behindSegmentComplexLength * absoluteZ < channelRadius:
		return True
	return aheadSegmentComplexLength * absoluteZ < channelRadius

def isXSegmentIntersectingPath( path, segmentFirstX, segmentSecondX, segmentYMirror, y ):
	"Determine if a path is crossing inside the x segment."
	rotatedPath = getPointsRoundZAxis( segmentYMirror, path )
	for pointIndex in xrange( len( rotatedPath ) - 1 ):
		pointFirst = rotatedPath[ pointIndex ]
		pointSecond = rotatedPath[ pointIndex + 1 ]
		if isLineIntersectingInsideXSegment( segmentFirstX, segmentSecondX, pointFirst, pointSecond, y ):
			return True
	return False

def isXSegmentIntersectingPaths( paths, segmentFirstX, segmentSecondX, segmentYMirror, y ):
	"Determine if a path list is crossing inside the x segment."
	for path in paths:
		if isXSegmentIntersectingPath( path, segmentFirstX, segmentSecondX, segmentYMirror, y ):
			return True
	return False

def joinSegmentTables( fromTable, intoTable ):
	"Join both segment tables and put the join into the intoTable."
	intoTableKeys = intoTable.keys()
	fromTableKeys = fromTable.keys()
	joinedKeyTable = {}
	concatenatedTableKeys = intoTableKeys + fromTableKeys
	for concatenatedTableKey in concatenatedTableKeys:
		joinedKeyTable[ concatenatedTableKey ] = None
	joinedKeys = joinedKeyTable.keys()
	joinedKeys.sort()
	for joinedKey in joinedKeys:
		xIntersectionIndexList = []
		if joinedKey in intoTable:
			addXIntersectionIndexesFromSegments( 0, intoTable[ joinedKey ], xIntersectionIndexList )
		if joinedKey in fromTable:
			addXIntersectionIndexesFromSegments( 1, fromTable[ joinedKey ], xIntersectionIndexList )
		xIntersections = getJoinOfXIntersectionIndexes( xIntersectionIndexList )
		lineSegments = getSegmentsFromXIntersections( xIntersections, joinedKey )
		if len( lineSegments ) > 0:
			intoTable[ joinedKey ] = lineSegments
		else:
			print( "This should never happen, there are no line segments in joinSegments in euclidean" )

def joinXIntersectionsTables( fromTable, intoTable ):
	"Join both XIntersections tables and put the join into the intoTable."
	joinedKeyTable = {}
	concatenatedTableKeys = fromTable.keys() + intoTable.keys()
	for concatenatedTableKey in concatenatedTableKeys:
		joinedKeyTable[ concatenatedTableKey ] = None
	for joinedKey in joinedKeyTable.keys():
		xIntersectionIndexList = []
		if joinedKey in intoTable:
			addXIntersectionIndexesFromXIntersections( 0, xIntersectionIndexList, intoTable[ joinedKey ] )
		if joinedKey in fromTable:
			addXIntersectionIndexesFromXIntersections( 1, xIntersectionIndexList, fromTable[ joinedKey ] )
		xIntersections = getJoinOfXIntersectionIndexes( xIntersectionIndexList )
		if len( xIntersections ) > 0:
			intoTable[ joinedKey ] = xIntersections
		else:
			print( "This should never happen, there are no line segments in joinSegments in euclidean" )

def removeElementFromListTable( element, key, listTable ):
	"Remove an element from the list table."
	if key not in listTable:
		return
	elementList = listTable[ key ]
	if len( elementList ) < 2:
		del listTable[ key ]
		return
	if element in elementList:
		elementList.remove( element )

def removeElementFromPixelListFromPoint( element, pixelTable, point ):
	"Remove an element from the pixel list."
	stepKey = getStepKeyFromPoint( point )
	removeElementFromListTable( element, stepKey, pixelTable )

def removePixelTableFromPixelTable( pixelTableToBeRemoved, pixelTableToBeRemovedFrom ):
	"Remove pixel from the pixel table."
	pixelTableToBeRemovedKeys = pixelTableToBeRemoved.keys()
	for pixelTableToBeRemovedKey in pixelTableToBeRemovedKeys:
		if pixelTableToBeRemovedKey in pixelTableToBeRemovedFrom:
			del pixelTableToBeRemovedFrom[ pixelTableToBeRemovedKey ]

def subtractXIntersectionsTable( subtractFromTable, subtractTable ):
	"Subtract the subtractTable from the subtractFromTable."
	subtractFromTableKeys = subtractFromTable.keys()
	subtractFromTableKeys.sort()
	for subtractFromTableKey in subtractFromTableKeys:
		xIntersectionIndexList = []
		addXIntersectionIndexesFromXIntersections( - 1, xIntersectionIndexList, subtractFromTable[ subtractFromTableKey ] )
		if subtractFromTableKey in subtractTable:
			addXIntersectionIndexesFromXIntersections( 0, xIntersectionIndexList, subtractTable[ subtractFromTableKey ] )
		xIntersections = getXIntersectionsFromIntersections( xIntersectionIndexList )
		if len( xIntersections ) > 0:
			subtractFromTable[ subtractFromTableKey ] = xIntersections
		else:
			del subtractFromTable[ subtractFromTableKey ]

def toggleHashtable( hashtable, key, value ):
	"Toggle a hashtable between having and not having a key."
	if key in hashtable:
		del hashtable[ key ]
	else:
		hashtable[ key ] = value

def transferClosestFillLoop( extrusionHalfWidth, oldOrderedLocation, remainingFillLoops, skein ):
	"Transfer the closest remaining fill loop."
	closestDistance = 999999999999999999.0
	closestFillLoop = None
	for remainingFillLoop in remainingFillLoops:
		distance = getNearestDistanceIndex( oldOrderedLocation.dropAxis( 2 ), remainingFillLoop ).distance
		if distance < closestDistance:
			closestDistance = distance
			closestFillLoop = remainingFillLoop
	newClosestFillLoop = getLoopInsideContainingLoop( closestFillLoop, remainingFillLoops )
	while newClosestFillLoop != None:
		closestFillLoop = newClosestFillLoop
		newClosestFillLoop = getLoopInsideContainingLoop( closestFillLoop, remainingFillLoops )
	remainingFillLoops.remove( closestFillLoop )
	addToThreadsFromLoop( extrusionHalfWidth, 'loop', closestFillLoop[ : ], oldOrderedLocation, skein )

def transferClosestPath( oldOrderedLocation, remainingPaths, skein ):
	"Transfer the closest remaining path."
	closestDistance = 999999999999999999.0
	closestPath = None
	oldOrderedLocationComplex = oldOrderedLocation.dropAxis( 2 )
	for remainingPath in remainingPaths:
		distance = min( abs( oldOrderedLocationComplex - remainingPath[ 0 ] ), abs( oldOrderedLocationComplex - remainingPath[ - 1 ] ) )
		if distance < closestDistance:
			closestDistance = distance
			closestPath = remainingPath
	remainingPaths.remove( closestPath )
	skein.addGcodeFromThreadZ( closestPath, oldOrderedLocation.z )
	oldOrderedLocation.x = closestPath[ - 1 ].real
	oldOrderedLocation.y = closestPath[ - 1 ].imag

def transferClosestPaths( oldOrderedLocation, remainingPaths, skein ):
	"Transfer the closest remaining paths."
	while len( remainingPaths ) > 0:
		transferClosestPath( oldOrderedLocation, remainingPaths, skein )

def transferPathsToSurroundingLoops( paths, surroundingLoops ):
	"Transfer paths to surrounding loops."
	for surroundingLoop in surroundingLoops:
		surroundingLoop.transferPaths( paths )


class DistanceIndex:
	"A class to hold the distance and the index of the loop."
	def __init__( self, distance, index ):
		self.distance = distance
		self.index = index

	def __repr__( self ):
		"Get the string representation of this distance index."
		return '%s, %s' % ( self.distance, self.index )


class Endpoint:
	"The endpoint of a segment."
	def __repr__( self ):
		"Get the string representation of this Endpoint."
		return 'Endpoint %s, %s' % ( self.point, self.otherEndpoint.point )

	def getFromOtherPoint( self, otherEndpoint, point ):
		"Initialize from other endpoint."
		self.otherEndpoint = otherEndpoint
		self.point = point
		return self

	def getHop( self, fillInset, path ):
		"Get a hop away from the endpoint if the other endpoint is doubling back."
		if len( path ) < 2:
			return None
		penultimateMinusPoint = path[ - 2 ] - self.point
		if abs( penultimateMinusPoint ) == 0.0:
			return None
		penultimateMinusPoint /= abs( penultimateMinusPoint )
		normalizedComplexSegment = self.otherEndpoint.point - self.point
		normalizedComplexSegmentLength = abs( normalizedComplexSegment )
		if normalizedComplexSegmentLength == 0.0:
			return None
		normalizedComplexSegment /= normalizedComplexSegmentLength
		if getDotProduct( penultimateMinusPoint, normalizedComplexSegment ) < 0.9:
			return None
		alongRatio = 0.8
		hop = self.point * alongRatio + self.otherEndpoint.point * ( 1.0 - alongRatio )
		normalizedSegment = self.otherEndpoint.point - self.point
		normalizedSegmentLength = abs( normalizedSegment )
		absoluteCross = abs( getCrossProduct( penultimateMinusPoint, normalizedComplexSegment ) )
		reciprocalCross = 1.0 / max( absoluteCross, 0.01 )
		alongWay = min( fillInset * reciprocalCross, normalizedSegmentLength )
		return self.point + normalizedSegment * alongWay / normalizedSegmentLength

	def getNearestEndpoint( self, endpoints ):
		"Get nearest endpoint."
		smallestDistance = 999999999999999999.0
		nearestEndpoint = None
		for endpoint in endpoints:
			distance = abs( self.point - endpoint.point )
			if distance < smallestDistance:
				smallestDistance = distance
				nearestEndpoint = endpoint
		return nearestEndpoint

	def getNearestMiss( self, endpoints, path, pixelTable, width ):
		"Get the nearest endpoint which the segment to that endpoint misses the other extrusions."
		pathMaskTable = {}
		smallestDistance = 9999999999.0
		penultimateMinusPoint = complex( 0.0, 0.0 )
		if len( path ) > 1:
			penultimatePoint = path[ - 2 ]
			addSegmentToPixelTable( penultimatePoint, self.point, pathMaskTable, 0, 0, width )
			penultimateMinusPoint = penultimatePoint - self.point
			if abs( penultimateMinusPoint ) > 0.0:
				penultimateMinusPoint /= abs( penultimateMinusPoint )
		for endpoint in endpoints:
			endpoint.segment = endpoint.point - self.point
			endpoint.segmentLength = abs( endpoint.segment )
			if endpoint.segmentLength <= 0.0:
#				print( 'This should never happen, the endpoints are touching' )
#				print( endpoint )
#				print( path )
				return endpoint
		endpoints.sort( compareSegmentLength )
		for endpoint in endpoints[ : 15 ]: # increasing the number of searched endpoints increases the search time, with 20 fill took 600 seconds for cilinder.gts, with 10 fill took 533 seconds
			normalizedSegment = endpoint.segment / endpoint.segmentLength
			isOverlappingSelf = getDotProduct( penultimateMinusPoint, normalizedSegment ) > 0.9
			if not isOverlappingSelf:
				if len( path ) > 2:
					segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
					pointRotated = segmentYMirror * self.point
					endpointPointRotated = segmentYMirror * endpoint.point
					if isXSegmentIntersectingPath( path[ max( 0, len( path ) - 21 ) : - 1 ], pointRotated.real, endpointPointRotated.real, segmentYMirror, pointRotated.imag ):
						isOverlappingSelf = True
			if not isOverlappingSelf:
				totalMaskTable = pathMaskTable.copy()
				addSegmentToPixelTable( endpoint.point, endpoint.otherEndpoint.point, totalMaskTable, 0, 0, width )
				segmentTable = {}
				addSegmentToPixelTable( self.point, endpoint.point, segmentTable, 0, 0, width )
				if not isPixelTableIntersecting( pixelTable, segmentTable, totalMaskTable ):
					return endpoint
		return None

	def getNearestMissCheckEndpointPath( self, endpoints, path, pixelTable, width ):
		"Get the nearest endpoint which the segment to that endpoint misses the other extrusions, also checking the path of the endpoint."
		pathMaskTable = {}
		smallestDistance = 9999999999.0
		penultimateMinusPoint = complex( 0.0, 0.0 )
		if len( path ) > 1:
			penultimatePoint = path[ - 2 ]
			addSegmentToPixelTable( penultimatePoint, self.point, pathMaskTable, 0, 0, width )
			penultimateMinusPoint = penultimatePoint - self.point
			if abs( penultimateMinusPoint ) > 0.0:
				penultimateMinusPoint /= abs( penultimateMinusPoint )
		for endpoint in endpoints:
			endpoint.segment = endpoint.point - self.point
			endpoint.segmentLength = abs( endpoint.segment )
			if endpoint.segmentLength <= 0.0:
#				print( 'This should never happen, the endpoints are touching' )
#				print( endpoint )
#				print( path )
				return endpoint
		endpoints.sort( compareSegmentLength )
		for endpoint in endpoints[ : 15 ]: # increasing the number of searched endpoints increases the search time, with 20 fill took 600 seconds for cilinder.gts, with 10 fill took 533 seconds
			normalizedSegment = endpoint.segment / endpoint.segmentLength
			isOverlappingSelf = getDotProduct( penultimateMinusPoint, normalizedSegment ) > 0.9
			if not isOverlappingSelf:
				if len( path ) > 2:
					segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
					pointRotated = segmentYMirror * self.point
					endpointPointRotated = segmentYMirror * endpoint.point
					if isXSegmentIntersectingPath( path[ max( 0, len( path ) - 21 ) : - 1 ], pointRotated.real, endpointPointRotated.real, segmentYMirror, pointRotated.imag ):
						isOverlappingSelf = True
				endpointPath = endpoint.path
				if len( endpointPath ) > 2:
					segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
					pointRotated = segmentYMirror * self.point
					endpointPointRotated = segmentYMirror * endpoint.point
					if isXSegmentIntersectingPath( endpointPath, pointRotated.real, endpointPointRotated.real, segmentYMirror, pointRotated.imag ):
						isOverlappingSelf = True
			if not isOverlappingSelf:
				totalMaskTable = pathMaskTable.copy()
				addSegmentToPixelTable( endpoint.point, endpoint.otherEndpoint.point, totalMaskTable, 0, 0, width )
				segmentTable = {}
				addSegmentToPixelTable( self.point, endpoint.point, segmentTable, 0, 0, width )
				if not isPixelTableIntersecting( pixelTable, segmentTable, totalMaskTable ):
					return endpoint
		return None


class LoopLayer:
	"Loops with a z."
	def __init__( self, z ):
		self.loops = []
		self.z = z

	def __repr__( self ):
		"Get the string representation of this loop layer."
		return '%s, %s' % ( self.z, self.loops )


class PathZ:
	"Complex path with a z."
	def __init__( self, z ):
		self.path = []
		self.z = z

	def __repr__( self ):
		"Get the string representation of this path z."
		return '%s, %s' % ( self.z, self.path )


class RotatedLoopLayer:
	"A rotated layer."
	def __init__( self, z ):
		self.loops = []
		self.rotation = None
		self.z = z

	def __repr__( self ):
		"Get the string representation of this rotated loop layer."
		return '%s, %s, %s' % ( self.z, self.rotation, self.loops )

	def getCopyAtZ( self, z ):
		"Get a raised copy."
		raisedRotatedLoopLayer = RotatedLoopLayer( z )
		for loop in self.loops:
			raisedRotatedLoopLayer.loops.append( loop[ : ] )
		raisedRotatedLoopLayer.rotation = self.rotation
		return raisedRotatedLoopLayer


class SurroundingLoop:
	"A loop that surrounds paths."
	def __init__( self, threadSequence ):
		self.addToThreadsFunctions = []
		self.boundary = []
		self.extraLoops = []
		self.infillPaths = []
		self.innerSurroundings = None
		self.lastExistingFillLoops = None
		self.lastFillLoops = None
		self.loop = None
		self.perimeterPaths = []
		self.z = None
		threadFunctionTable = { 'infill' : self.transferInfillPaths, 'loops' : self.transferClosestFillLoops, 'perimeter' : self.addPerimeterInner }
		for threadType in threadSequence:
			self.addToThreadsFunctions.append( threadFunctionTable[ threadType ] )

	def __repr__( self ):
		"Get the string representation of this surrounding loop."
		stringRepresentation = 'boundary\n%s\n' % self.boundary
		stringRepresentation += 'loop\n%s\n' % self.loop
		stringRepresentation += 'inner surroundings\n%s\n' % self.innerSurroundings
		stringRepresentation += 'infillPaths\n'
		for infillPath in self.infillPaths:
			stringRepresentation += 'infillPath\n%s\n' % infillPath
		stringRepresentation += 'perimeterPaths\n'
		for perimeterPath in self.perimeterPaths:
			stringRepresentation += 'perimeterPath\n%s\n' % perimeterPath
		return stringRepresentation + '\n'

	def addToBoundary( self, vector3 ):
		"Add vector3 to boundary."
		self.boundary.append( vector3.dropAxis( 2 ) )
		self.z = vector3.z

	def addToLoop( self, vector3 ):
		"Add vector3 to loop."
		if self.loop == None:
			self.loop = []
		self.loop.append( vector3.dropAxis( 2 ) )
		self.z = vector3.z

	def addPerimeterInner( self, oldOrderedLocation, skein ):
		"Add to the perimeter and the inner island."
		if self.loop == None:
			transferClosestPaths( oldOrderedLocation, self.perimeterPaths[ : ], skein )
		else:
			addToThreadsFromLoop( self.extrusionHalfWidth, 'perimeter', self.loop[ : ], oldOrderedLocation, skein )
		skein.distanceFeedRate.addLine( '(</boundaryPerimeter>)' )
		addToThreadsRemoveFromSurroundings( oldOrderedLocation, self.innerSurroundings[ : ], skein )

	def addToThreads( self, oldOrderedLocation, skein ):
		"Add to paths from the last location. perimeter>inner >fill>paths or fill> perimeter>inner >paths"
		addSurroundingLoopBeginning( skein.distanceFeedRate, self.boundary, self.z )
		for addToThreadsFunction in self.addToThreadsFunctions:
			addToThreadsFunction( oldOrderedLocation, skein )
		skein.distanceFeedRate.addLine( '(</surroundingLoop>)' )

	def getFillLoops( self ):
		"Get last fill loops from the outside loop and the loops inside the inside loops."
		fillLoops = self.getLoopsToBeFilled()[ : ]
		for surroundingLoop in self.innerSurroundings:
			fillLoops += getFillOfSurroundings( surroundingLoop.innerSurroundings )
		return fillLoops

	def getFromInsideSurroundings( self, inputSurroundingInsides, perimeterWidth ):
		"Initialize from inside surrounding loops."
		self.extrusionHalfWidth = 0.5 * perimeterWidth
		self.perimeterWidth = perimeterWidth
		transferredSurroundings = getTransferredSurroundingLoops( inputSurroundingInsides, self.boundary )
		self.innerSurroundings = getOrderedSurroundingLoops( perimeterWidth, transferredSurroundings )
		return self

	def getLastExistingFillLoops( self ):
		"Get last existing fill loops."
		lastExistingFillLoops = self.lastExistingFillLoops[ : ]
		for surroundingLoop in self.innerSurroundings:
			lastExistingFillLoops += getLastExistingFillOfSurroundings( surroundingLoop.innerSurroundings )
		return lastExistingFillLoops

	def getLoopsToBeFilled( self ):
		"Get last fill loops from the outside loop and the loops inside the inside loops."
		if self.lastFillLoops != None:
			return self.lastFillLoops
		loopsToBeFilled = self.fillBoundaries
		for surroundingLoop in self.innerSurroundings:
			loopsToBeFilled += surroundingLoop.fillBoundaries
		return loopsToBeFilled

	def transferClosestFillLoops( self, oldOrderedLocation, skein ):
		"Transfer closest fill loops."
		if len( self.extraLoops ) < 1:
			return
		remainingFillLoops = self.extraLoops[ : ]
		while len( remainingFillLoops ) > 0:
			transferClosestFillLoop( self.extrusionHalfWidth, oldOrderedLocation, remainingFillLoops, skein )

	def transferInfillPaths( self, oldOrderedLocation, skein ):
		"Transfer the infill paths."
		transferClosestPaths( oldOrderedLocation, self.infillPaths[ : ], skein )

	def transferPaths( self, paths ):
		"Transfer paths."
		for surroundingLoop in self.innerSurroundings:
			transferPathsToSurroundingLoops( paths, surroundingLoop.innerSurroundings )
		self.infillPaths = getTransferredPaths( paths, self.boundary )


class XIntersectionIndex:
	"A class to hold the x intersection position and the index of the loop which intersected."
	def __init__( self, index, x ):
		self.index = index
		self.x = x

	def __cmp__( self, other ):
		"Get comparison in order to sort x intersections in ascending order of x."
		if self.x > other.x:
			return 1
		if self.x < other.x:
			return - 1
		return 0

	def __repr__( self ):
		"Get the string representation of this x intersection."
		return 'XIntersectionIndex index %s; x %s ' % ( self.index, self.x )
