"""
This page is in the table of contents.
Export is a script to pick an export plugin and optionally print the output to a file.

The export manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Export

==Operation==
The default 'Activate Export' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===Also Send Output To===
Default is empty.

Defines the output name for sending to a file or pipe.  A common choice is sys.stdout to print the output in the shell screen.  Another common choice is sys.stderr.  With the empty default, nothing will be done.

===Delete Comments===
Default is on.

When selected, export will delete the comments.  The comments are not necessary to run a fabricator.

===Export Operations===
Export presents the user with a choice of the export plugins in the export_plugins folder.  The chosen plugin will then modify the gcode or translate it into another format.  There is also the "Do Not Change Output" choice, which will not change the output.  An export plugin is a script in the export_plugins folder which has the functions getOutput, isReplaceable and if it's output is not replaceable, writeOutput.

===File Extension===
Default is gcode.

Defines the file extension added to the name of the output file.

===Save Penultimate Gcode===
Default is off.

When selected, export will save the gcode with the suffix '_penultimate.gcode' just before it is exported.  This is useful because the code after it is exported could be in a form which the viewers can not display.

==Alterations==
Export looks for alteration files in the alterations folder in the .skeinforge folder in the home directory.  Export does not care if the text file names are capitalized, but some file systems do not handle file name cases properly, so to be on the safe side you should give them lower case names.  If it doesn't find the file it then looks in the alterations folder in the skeinforge_tools folder. If it doesn't find anything there it looks in the skeinforge_tools folder.

===replace.csv===
When export is exporting the code, if there is a file replace.csv, it will replace the word in the first column by its replacement in the second column.  There is an example file replace_example.csv to demonstrate the comma separated format, which can be edited in a text editor or a spreadsheet.

==Examples==
The following examples export the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and export.py.


> python export.py
This brings up the export dialog.


> python export.py Screw Holder Bottom.stl
The export tool is parsing the file:
Screw Holder Bottom.stl
..
The export tool has created the file:
.. Screw Holder Bottom_export.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import export
>>> export.main()
This brings up the export dialog.


>>> export.writeOutput( 'Screw Holder Bottom.stl' )
The export tool is parsing the file:
Screw Holder Bottom.stl
..
The export tool has created the file:
.. Screw Holder Bottom_export.gcode

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools import analyze
from skeinforge_tools import profile
from skeinforge_tools.meta_plugins import polyfile
from skeinforge_tools.skeinforge_utilities import consecution
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import intercircle
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools.skeinforge_utilities import settings
import cStringIO
import os
import sys
import time


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getCraftedTextFromText( gcodeText, exportRepository = None ):
	"Export a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'export' ):
		return gcodeText
	if exportRepository == None:
		exportRepository = settings.getReadRepository( ExportRepository() )
	if not exportRepository.activateExport.value:
		return gcodeText
	return ExportSkein().getCraftedGcode( exportRepository, gcodeText )

def getDistanceGcode( exportText ):
	"Get gcode lines with distance variable added.G2 X-0.148 Y-0.062 Z0.0 I-0.148 J0.148G2 X-0.148 Y-0.062 Z0.0 R0.21"
	lines = gcodec.getTextLines( exportText )
	oldLocation = None
	for line in lines:
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		firstWord = None
		if len( splitLine ) > 0:
			firstWord = splitLine[ 0 ]
		if firstWord == 'G1':
			location = gcodec.getLocationFromSplitLine( oldLocation, splitLine )
			if oldLocation != None:
				distance = location.distance( oldLocation )
				print( distance )
			oldLocation = location
	return exportText

def getNewRepository():
	"Get the repository constructor."
	return ExportRepository()

def getReplaced( exportText ):
	"Get text with words replaced according to replace.csv file."
	replaceText = settings.getFileInAlterationsOrGivenDirectory( os.path.dirname( __file__ ), 'Replace.csv' )
	if replaceText == '':
		return exportText
	lines = gcodec.getTextLines( replaceText )
	for line in lines:
		replacedLine = line.replace( ',', ' ' )
		replacedLine = replacedLine.replace( '\t', ' ' )
		splitLine = replacedLine.split()
		if len( splitLine ) > 1:
			exportText = exportText.replace( splitLine[ 0 ], splitLine[ 1 ] )
	return exportText

def getSelectedPluginModule( plugins ):
	"Get the selected plugin module."
	for plugin in plugins:
		if plugin.value:
			return gcodec.getModuleWithDirectoryPath( plugin.directoryPath, plugin.name )
	return None

def writeOutput( fileName = '' ):
	"Export a gcode linear move file."
	fileName = interpret.getFirstTranslatorFileNameUnmodified( fileName )
	if fileName == '':
		return
	exportRepository = ExportRepository()
	settings.getReadRepository( exportRepository )
	startTime = time.time()
	print( 'File ' + gcodec.getSummarizedFileName( fileName ) + ' is being chain exported.' )
	suffixFileName = fileName[ : fileName.rfind( '.' ) ] + '_export.' + exportRepository.fileExtension.value
	gcodeText = gcodec.getGcodeFileText( fileName, '' )
	procedures = consecution.getProcedures( 'export', gcodeText )
	gcodeText = consecution.getChainTextFromProcedures( fileName, procedures[ : - 1 ], gcodeText )
	if gcodeText == '':
		return
	analyze.writeOutput( suffixFileName, gcodeText )
	if exportRepository.savePenultimateGcode.value:
		penultimateFileName = fileName[ : fileName.rfind( '.' ) ] + '_penultimate.gcode'
		gcodec.writeFileText( penultimateFileName, gcodeText )
		print( 'The penultimate file is saved as ' + gcodec.getSummarizedFileName( penultimateFileName ) )
	exportChainGcode = getCraftedTextFromText( gcodeText, exportRepository )
	replaceableExportChainGcode = None
	selectedPluginModule = getSelectedPluginModule( exportRepository.exportPlugins )
	if selectedPluginModule == None:
		replaceableExportChainGcode = exportChainGcode
	else:
		if selectedPluginModule.isReplaceable():
			replaceableExportChainGcode = selectedPluginModule.getOutput( exportChainGcode )
		else:
			selectedPluginModule.writeOutput( suffixFileName, exportChainGcode )
	if replaceableExportChainGcode != None:
		replaceableExportChainGcode = getReplaced( replaceableExportChainGcode )
		gcodec.writeFileText( suffixFileName, replaceableExportChainGcode )
		print( 'The exported file is saved as ' + gcodec.getSummarizedFileName( suffixFileName ) )
	if exportRepository.alsoSendOutputTo.value != '':
		if replaceableExportChainGcode == None:
			replaceableExportChainGcode = selectedPluginModule.getOutput( exportChainGcode )
		exec( 'print >> ' + exportRepository.alsoSendOutputTo.value + ', replaceableExportChainGcode' )
	print( 'It took ' + str( int( round( time.time() - startTime ) ) ) + ' seconds to export the file.' )


class ExportRepository:
	"A class to handle the export settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge_tools.craft_plugins.export.html', '', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Export', self, '' )
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute( 'http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Export' )
		self.activateExport = settings.BooleanSetting().getFromValue( 'Activate Export', self, True )
		self.alsoSendOutputTo = settings.StringSetting().getFromValue( 'Also Send Output To:', self, '' )
		self.deleteComments = settings.BooleanSetting().getFromValue( 'Delete Comments', self, True )
		exportPluginsFolderPath = gcodec.getAbsoluteFolderPath( __file__, 'export_plugins' )
		exportStaticDirectoryPath = os.path.join( exportPluginsFolderPath, 'static_plugins' )
		exportPluginFileNames = gcodec.getPluginFileNamesFromDirectoryPath( exportPluginsFolderPath )
		exportStaticPluginFileNames = gcodec.getPluginFileNamesFromDirectoryPath( exportStaticDirectoryPath )
		self.exportLabel = settings.LabelDisplay().getFromName( 'Export Operations: ', self )
		self.exportPlugins = []
		exportLatentStringVar = settings.LatentStringVar()
		self.doNotChangeOutput = settings.RadioCapitalized().getFromRadio( exportLatentStringVar, 'Do Not Change Output', self, True )
		self.doNotChangeOutput.directoryPath = None
		allExportPluginFileNames = exportPluginFileNames + exportStaticPluginFileNames
		for exportPluginFileName in allExportPluginFileNames:
			exportPlugin = None
			if exportPluginFileName in exportPluginFileNames:
				path = os.path.join( exportPluginsFolderPath, exportPluginFileName )
				exportPlugin = settings.RadioCapitalizedButton().getFromPath( exportLatentStringVar, exportPluginFileName, path, self, False )
				exportPlugin.directoryPath = exportPluginsFolderPath
			else:
				exportPlugin = settings.RadioCapitalized().getFromRadio( exportLatentStringVar, exportPluginFileName, self, False )
				exportPlugin.directoryPath = exportStaticDirectoryPath
			self.exportPlugins.append( exportPlugin )
		self.fileExtension = settings.StringSetting().getFromValue( 'File Extension:', self, 'gcode' )
		self.savePenultimateGcode = settings.BooleanSetting().getFromValue( 'Save Penultimate Gcode', self, False )
		self.executeTitle = 'Export'

	def execute( self ):
		"Export button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


class ExportSkein:
	"A class to export a skein of extrusions."
	def __init__( self ):
		self.decimalPlacesExported = 2
		self.output = cStringIO.StringIO()

	def addLine( self, line ):
		"Add a line of text and a newline to the output."
		if line != '':
			self.output.write( line + '\n' )

	def getCraftedGcode( self, exportRepository, gcodeText ):
		"Parse gcode text and store the export gcode."
		lines = gcodec.getTextLines( gcodeText )
		for line in lines:
			self.parseLine( exportRepository, line )
		return self.output.getvalue()

	def getLineWithTruncatedNumber( self, character, line ):
		'Get a line with the number after the character truncated.'
		indexOfCharacter = line.find( character )
		if indexOfCharacter < 0:
			return line
		indexOfNumberEnd = line.find( ' ', indexOfCharacter )
		if indexOfNumberEnd < 0:
			indexOfNumberEnd = len( line )
		indexOfNumberStart = indexOfCharacter + 1
		numberString = line[ indexOfNumberStart : indexOfNumberEnd ]
		if numberString == '':
			return line
		roundedNumberString = euclidean.getRoundedToDecimalPlacesString( self.decimalPlacesExported, float( numberString ) )
		return line[ : indexOfNumberStart ] + roundedNumberString + line[ indexOfNumberEnd : ]

	def parseLine( self, exportRepository, line ):
		"Parse a gcode line."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if firstWord == '(<decimalPlacesCarried>':
			self.decimalPlacesExported = max( 1, int( splitLine[ 1 ] ) - 1 )
		if firstWord[ 0 ] == '(' and exportRepository.deleteComments.value:
			return
		if firstWord == '(</extruderInitialization>)':
			self.addLine( '(<procedureDone> export </procedureDone>)' )
		if firstWord != 'G1' and firstWord != 'G2' and firstWord != 'G3' :
			self.addLine( line )
			return
		line = self.getLineWithTruncatedNumber( 'X', line )
		line = self.getLineWithTruncatedNumber( 'Y', line )
		line = self.getLineWithTruncatedNumber( 'Z', line )
		line = self.getLineWithTruncatedNumber( 'I', line )
		line = self.getLineWithTruncatedNumber( 'J', line )
		line = self.getLineWithTruncatedNumber( 'R', line )
		self.addLine( line )


def main():
	"Display the export dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
