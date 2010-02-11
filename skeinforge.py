#!/usr/bin/python

from __future__ import absolute_import

from skeinforge_tools import craft
from skeinforge_tools import profile
from skeinforge_tools.meta_plugins import polyfile
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import settings
from skeinforge_tools.skeinforge_utilities import interpret
import os
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = """
Adrian Bowyer <http://forums.reprap.org/profile.php?12,13>
Brendan Erwin <http://forums.reprap.org/profile.php?12,217>
Greenarrow <http://forums.reprap.org/profile.php?12,81>
Ian England <http://forums.reprap.org/profile.php?12,192>
John Gilmore <http://forums.reprap.org/profile.php?12,364>
Jonwise <http://forums.reprap.org/profile.php?12,716>
Kyle Corbitt <http://forums.reprap.org/profile.php?12,90>
Michael Duffin <http://forums.reprap.org/profile.php?12,930>
Marius Kintel <http://reprap.soup.io/>
Nophead <http://www.blogger.com/profile/12801535866788103677>
PJR <http://forums.reprap.org/profile.php?12,757>
Reece.Arnott <http://forums.reprap.org/profile.php?12,152>
Wade <http://forums.reprap.org/profile.php?12,489>
Xsainnz <http://forums.reprap.org/profile.php?12,563>
Zach Hoeken <http://blog.zachhoeken.com/>

Organizations:
Art of Illusion <http://www.artofillusion.org/>"""
__date__ = "$Date: 2008/21/11 $"
__license__ = "GPL 3.0"


def addToProfileMenu( profileSelection, profileType, repository ):
	"Add a profile menu."
	pluginFileNames = profile.getPluginFileNames()
	craftTypeName = profile.getCraftTypeName()
	pluginModule = profile.getCraftTypePluginModule()
	profilePluginSettings = settings.getReadRepository( pluginModule.getNewRepository() )
	for pluginFileName in pluginFileNames:
		profile.ProfileTypeMenuRadio().getFromMenuButtonDisplay( profileType, pluginFileName, repository, craftTypeName == pluginFileName )
	for profileName in profilePluginSettings.profileList.value:
		profile.ProfileSelectionMenuRadio().getFromMenuButtonDisplay( profileSelection, profileName, repository, profileName == profilePluginSettings.profileListbox.value )

def getPluginsDirectoryPath():
	"Get the plugins directory path."
	return gcodec.getAbsoluteFolderPath( __file__, 'skeinforge_tools' )

def getPluginFileNames():
	"Get analyze plugin fileNames."
	return gcodec.getPluginFileNamesFromDirectoryPath( getPluginsDirectoryPath() )

def getNewRepository():
	"Get the repository constructor."
	return SkeinforgeRepository()

def writeOutput( fileName = '' ):
	"Craft a gcode file."
	craft.writeOutput( fileName )


class SkeinforgeRepository:
	"A class to handle the skeinforge settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge.html', '', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Skeinforge', self, '' )
		versionText = gcodec.getFileText( gcodec.getVersionFileName() )
		self.createdOnLabel = settings.LabelDisplay().getFromName( 'Created On: ' + versionText, self )
		self.profileType = settings.MenuButtonDisplay().getFromName( 'Profile Type: ', self )
		self.profileSelection = settings.MenuButtonDisplay().getFromName( 'Profile Selection: ', self )
		addToProfileMenu( self.profileSelection, self.profileType, self )
		settings.LabelDisplay().getFromName( '', self )
		self.skeinforgeLabel = settings.LabelDisplay().getFromName( 'Open Settings: ', self )
		importantFileNames = [ 'craft', 'profile' ]
		settings.getDisplayToolButtonsRepository( gcodec.getAbsoluteFolderPath( __file__, 'skeinforge_tools' ), importantFileNames, getPluginFileNames(), self )
		self.executeTitle = 'Skeinforge'

	def execute( self ):
		"Skeinforge button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )

	def save( self ):
		"Profile has been saved and profile menu should be updated."
		self.profileType.removeMenus()
		self.profileSelection.removeMenus()
		addToProfileMenu( self.profileSelection, self.profileType, self )
		self.profileType.addRadiosToDialog( self.repositoryDialog )
		self.profileSelection.addRadiosToDialog( self.repositoryDialog )


def main():
	"Display the skeinforge dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
