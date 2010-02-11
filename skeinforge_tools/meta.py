"""
This page is in the table of contents.
Meta is a script to access the plugins which handle meta information.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import settings


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addToMenu( master, menu, repository, window ):
	"Add a tool plugin menu."
	settings.addPluginsParentToMenu( getPluginsDirectoryPath(), menu, __file__, getPluginFileNames() )

def getPluginFileNames():
	"Get meta plugin file names."
	return gcodec.getPluginFileNamesFromDirectoryPath( getPluginsDirectoryPath() )

def getPluginsDirectoryPath():
	"Get the plugins directory path."
	return gcodec.getAbsoluteFolderPath( __file__, 'meta_plugins' )

def getNewRepository():
	"Get the repository constructor."
	return MetaRepository()


class MetaRepository:
	"A class to handle the meta settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge_tools.meta.html', '', self )
		importantFileNames = [ 'polyfile' ]
		settings.getRadioPluginsAddPluginFrame( getPluginsDirectoryPath(), importantFileNames, getPluginFileNames(), self )


def main():
	"Display the meta dialog."
	settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
