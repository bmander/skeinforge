"""
This page is in the table of contents.
Craft is a script to access the plugins which craft a gcode file.

The plugin buttons which are commonly used are bolded and the ones which are rarely used have normal font weight.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools import profile
from skeinforge_tools.meta_plugins import polyfile
from skeinforge_tools.skeinforge_utilities import consecution
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools.skeinforge_utilities import settings
import os
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addSubmenus( menu, pluginFileName, pluginFolderPath, pluginPath ):
	"Add a tool plugin menu."
	submenu = settings.Tkinter.Menu( menu, tearoff = 0 )
	menu.add_cascade( label = pluginFileName.capitalize(), menu = submenu )
	settings.ToolDialog().addPluginToMenu( submenu, pluginPath )
	submenu.add_separator()
	submenuFileNames = gcodec.getPluginFileNamesFromDirectoryPath( pluginFolderPath )
	for submenuFileName in submenuFileNames:
		settings.ToolDialog().addPluginToMenu( submenu, os.path.join( pluginFolderPath, submenuFileName ) )

def addToCraftMenu( menu ):
	"Add a craft plugin menu."
	settings.ToolDialog().addPluginToMenu( menu, gcodec.getUntilDot( os.path.abspath( __file__ ) ) )
	menu.add_separator()
	directoryPath = getPluginsDirectoryPath()
	directoryFolders = settings.getFolders( directoryPath )
	pluginFileNames = getPluginFileNames()
	for pluginFileName in pluginFileNames:
		pluginFolderName = pluginFileName + '_plugins'
		pluginPath = os.path.join( directoryPath, pluginFileName )
		if pluginFolderName in directoryFolders:
			addSubmenus( menu, pluginFileName, os.path.join( directoryPath, pluginFolderName ), pluginPath )
		else:
			settings.ToolDialog().addPluginToMenu( menu, pluginPath )

def addToMenu( master, menu, repository, window ):
	"Add a tool plugin menu."
	CraftMenuSaveListener( menu, window )

def getPluginsDirectoryPath():
	"Get the plugins directory path."
	return gcodec.getAbsoluteFolderPath( __file__, 'craft_plugins' )

def getPluginFileNames():
	"Get craft plugin fileNames."
	craftSequence = consecution.getReadCraftSequence()
	craftSequence.sort()
	return craftSequence

def getNewRepository():
	"Get the repository constructor."
	return CraftRepository()

def writeOutput( fileName = '' ):
	"Craft a gcode file.  If no fileName is specified, comment the first gcode file in this folder that is not modified."
	pluginModule = consecution.getLastModule()
	if pluginModule != None:
		pluginModule.writeOutput( fileName )


class CraftMenuSaveListener:
	"A class to update a craft menu."
	def __init__( self, menu, window ):
		"Set the menu."
		self.menu = menu
		addToCraftMenu( menu )
		settings.addElementToListTableIfNotThere( self, window, settings.globalProfileSaveListenerListTable )

	def save( self ):
		"Profile has been saved and profile menu should be updated."
		settings.deleteMenuItems( self.menu )
		addToCraftMenu( self.menu )


class CraftRadioButtonsSaveListener:
	"A class to update the craft radio buttons."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		settings.addElementToListTableIfNotThere( self, self.repository.repositoryDialog, settings.globalProfileSaveListenerListTable )
		self.gridPosition = gridPosition.getCopy()
		self.gridPosition.increment()
		self.gridPosition.row = gridPosition.rowStart
		self.setRadioButtons()

	def getFromRadioPlugins( self, radioPlugins, repository ):
		"Initialize."
		self.name = 'CraftRadioButtonsSaveListener'
		self.radioPlugins = radioPlugins
		self.repository = repository
		repository.displayEntities.append( self )
		return self

	def save( self ):
		"Profile has been saved and craft radio plugins should be updated."
		self.setRadioButtons()

	def setRadioButtons( self ):
		"Profile has been saved and craft radio plugins should be updated."
		craftSequence = profile.getCraftTypePluginModule().getCraftSequence()
		gridPosition = self.gridPosition.getCopy()
		maximumValue = False
		activeRadioPlugins = []
		for radioPlugin in self.radioPlugins:
			if radioPlugin.name in craftSequence:
				activeRadioPlugins.append( radioPlugin )
				radioPlugin.incrementGridPosition( gridPosition )
				maximumValue = max( radioPlugin.value, maximumValue )
			else:
				radioPlugin.radiobutton.grid_remove()
		if not maximumValue:
			selectedRadioPlugin = settings.getSelectedRadioPlugin( self.repository.importantFileNames + [ activeRadioPlugins[ 0 ].name ], activeRadioPlugins ).setSelect()
		self.repository.pluginFrame.update()


class CraftRepository:
	"A class to handle the craft settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge_tools.craft.html', '', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Craft', self, '' )
		self.importantFileNames = [ 'carve', 'chop', 'feed', 'flow', 'lift', 'raft', 'speed' ]
		allCraftNames = gcodec.getPluginFileNamesFromDirectoryPath( getPluginsDirectoryPath() )
		radioPlugins = settings.getRadioPluginsAddPluginFrame( getPluginsDirectoryPath(), self.importantFileNames, allCraftNames, self )
		CraftRadioButtonsSaveListener().getFromRadioPlugins( radioPlugins, self )
		self.executeTitle = 'Craft'

	def execute( self ):
		"Craft button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, [], self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


def main():
	"Display the craft dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
