"""
This page is in the table of contents.
Polyfile is a script to choose whether the skeinforge toolchain will operate on one file or all the files in a directory.

==Settings==
===Polyfile Choice===
Default is 'Execute File',

====Execute File====
When selected, the toolchain will operate on only the chosen file.

====Execute All Unmodified Files in a Directory'====
When selected, the toolchain will operate on all the unmodifed files in the directory that the chosen file is in.

==Examples==
Examples of using polyfile follow below.


> python polyfile.py
This brings up the polyfile dialog.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import polyfile
>>> polyfile.main()
This brings up the polyfile dialog.


>>> polyfile.isDirectorySetting()
This returns true if 'Execute All Unmodified Files in a Directory' is chosen and returns false if 'Execute File' is chosen.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import settings


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getFileOrGcodeDirectory( fileName, wasCancelled, words = [] ):
	"Get the gcode files in the directory the file is in if directory setting is true.  Otherwise, return the file in a list."
	if isEmptyOrCancelled( fileName, wasCancelled ):
		return []
	if isDirectorySetting():
		return gcodec.getFilesWithFileTypeWithoutWords( 'gcode', words, fileName )
	return [ fileName ]

def getFileOrDirectoryTypes( fileName, fileTypes, wasCancelled ):
	"Get the gcode files in the directory the file is in if directory setting is true.  Otherwise, return the file in a list."
	if isEmptyOrCancelled( fileName, wasCancelled ):
		return []
	if isDirectorySetting():
		return gcodec.getFilesWithFileTypesWithoutWords( fileTypes, [], fileName )
	return [ fileName ]

def getFileOrDirectoryTypesUnmodifiedGcode( fileName, fileTypes, wasCancelled ):
	"Get the gcode files in the directory the file is in if directory setting is true.  Otherwise, return the file in a list."
	if isEmptyOrCancelled( fileName, wasCancelled ):
		return []
	if isDirectorySetting():
		return gcodec.getFilesWithFileTypesWithoutWords( fileTypes, [], fileName ) + gcodec.getUnmodifiedGCodeFiles( fileName )
	return [ fileName ]

def getNewRepository():
	"Get the repository constructor."
	return PolyfileRepository()

def isDirectorySetting():
	"Determine if the directory setting is true."
	return settings.getReadRepository( PolyfileRepository() ).directorySetting.value

def isEmptyOrCancelled( fileName, wasCancelled ):
	"Determine if the fileName is empty or the dialog was cancelled."
	return str( fileName ) == '' or str( fileName ) == '()' or wasCancelled


class PolyfileRepository:
	"A class to handle the polyfile settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge_tools.meta_plugins.polyfile.html', '', self )
		self.directoryOrFileChoiceLabel = settings.LabelDisplay().getFromName( 'Directory or File Choice: ', self )
		directoryLatentStringVar = settings.LatentStringVar()
		self.directorySetting = settings.Radio().getFromRadio( directoryLatentStringVar, 'Execute All Unmodified Files in a Directory', self, False )
		self.fileSetting = settings.Radio().getFromRadio( directoryLatentStringVar, 'Execute File', self, True )


def main():
	"Display the file or directory dialog."
	settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
