"""
This page is in the table of contents.
Help has buttons and menu items to open help, blog and forum pages in your primary browser.


==Link Buttons==
===Announcements===
====Fabmetheus Blog====
The skeinforge announcements blog and the place to post questions, bugs and skeinforge requests.

===Documentation===
====Index of Local Documentation====
The list of the pages in the documentation folder.

====Wiki Manual====
The skeinforge wiki with pictures and charts.  It is the best and most readable source of skeinforge information and you are welcome to contribute.

====Skeinforge Overview====
A general description of skeinforge, has answers to frequently asked questions and has many links to skeinforge, fabrication and python pages.  It is also the help page of the skeinforge tool.

===Forums===
====Bits from Bytes Printing Board====
Board about printing questions, problems and solutions.  Most of the people on that forum use the rapman, but many of the solutions apply to any reprap.

====Bits from Bytes Software Board====
Board about software, and has some skeinforge threads.

====Skeinforge Contributions Thread====
Forum thread about how to contribute to skeinforge development.

====Skeinforge Settings Thread====
Forum thread for people to post, download and discuss skeinforge settings.

==Settings==
===Wiki Manual Primary===
Default is on.

The help menu has an item for each button on the help page.  Also, at the very top, it has a link to the local documentation and if there is a separate page for that tool in the wiki manual, a link to that page on the manual.  If the 'Wiki Manual Primary' checkbutton is selected and there is a separate wiki manual page, the wiki page will be the primary document page, otherwise the local page will be primary.  The help button (? symbol button) on the tool page will open the primary page, as will pressing <F1>.  For example, if you click the the help button from the chamber tool, which has a separate page in the wiki, and 'Wiki Manual Primary' is selected, the wiki manual chamber page will be opened.  Clicking F1 will also open the wiki manual chamber page.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import settings
import os


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addToMenu( master, menu, repository, window ):
	"Add a tool plugin menu."
	path = settings.getPathFromFileNameHelp( repository.fileNameHelp )
	capitalizedBasename = os.path.basename( path ).capitalize()
	helpRepository = settings.getReadRepository( HelpRepository() )
	if repository.openWikiManualHelpPage != None and helpRepository.wikiManualPrimary.value:
		menu.add_command( label = 'Local ' + capitalizedBasename, command = repository.openLocalHelpPage )
	else:
		settings.addAcceleratorCommand( '<F1>', repository.openLocalHelpPage, master, menu, 'Local ' + capitalizedBasename )
	if repository.openWikiManualHelpPage != None:
		if helpRepository.wikiManualPrimary.value:
			settings.addAcceleratorCommand( '<F1>', repository.openWikiManualHelpPage, master, menu, 'Wiki Manual ' + capitalizedBasename )
		else:
			menu.add_command( label = 'Wiki Manual ' + capitalizedBasename, command = repository.openWikiManualHelpPage )
	menu.add_separator()
	settings.addMenuEntitiesToMenu( menu, helpRepository.menuEntities )

def getNewRepository():
	"Get the repository constructor."
	return HelpRepository()


class HelpRepository:
	"A class to handle the help settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge_tools.help.html', '', self )
		settings.LabelDisplay().getFromName( '- Announcements -', self )
		settings.LabelDisplay().getFromName( 'Fabmetheus Blog, Announcements & Questions:', self )
		settings.HelpPage().getFromNameAfterHTTP( 'fabmetheus.blogspot.com/', 'Fabmetheus Blog', self )
		settings.LabelSeparator().getFromRepository( self )
		settings.LabelDisplay().getFromName( '- Documentation -', self )
		settings.LabelDisplay().getFromName( 'Index of Local Documentation: ', self )
		settings.HelpPage().getFromNameSubName( 'Index', self )
		settings.LabelDisplay().getFromName( 'Wiki Manual with Pictures & Charts: ', self )
		settings.HelpPage().getFromNameAfterWWW( 'bitsfrombytes.com/wiki/index.php?title=Skeinforge', 'Wiki Manual', self )
		settings.LabelDisplay().getFromName( 'Skeinforge Overview: ', self )
		settings.HelpPage().getFromNameSubName( 'Skeinforge Overview', self, 'skeinforge.html' )
		settings.LabelSeparator().getFromRepository( self )
		settings.LabelDisplay().getFromName( '- Forums -', self )
		settings.LabelDisplay().getFromName( 'Bits from Bytes Printing Board:', self )
		settings.HelpPage().getFromNameAfterWWW( 'bitsfrombytes.com/fora/user/index.php?board=5.0', 'Bits from Bytes Printing Board', self )
		settings.LabelDisplay().getFromName( 'Bits from Bytes Software Board:', self )
		settings.HelpPage().getFromNameAfterWWW( 'bitsfrombytes.com/fora/user/index.php?board=4.0', 'Bits from Bytes Software Board', self )
		settings.LabelDisplay().getFromName( 'Skeinforge Contributions Thread:', self )
		settings.HelpPage().getFromNameAfterHTTP( 'dev.forums.reprap.org/read.php?12,27562', 'Skeinforge Contributions Thread', self )
		settings.LabelDisplay().getFromName( 'Skeinforge Settings Thread:', self )
		settings.HelpPage().getFromNameAfterHTTP( 'dev.forums.reprap.org/read.php?12,27434', 'Skeinforge Settings Thread', self )
		settings.LabelSeparator().getFromRepository( self )
		self.wikiManualPrimary = settings.BooleanSetting().getFromValue( 'Wiki Manual Primary', self, True )
		self.wikiManualPrimary.setUpdateFunction( self.save )

	def save( self ):
		"Write the entities."
		settings.writeSettingsPrintMessage( self )

def main():
	"Display the help dialog."
	settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
