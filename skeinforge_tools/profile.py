"""
This page is in the table of contents.
Profile is a script to set the craft types setting for the skeinforge chain.

Profile presents the user with a choice of the craft types in the profile_plugins folder.  The chosen craft type is used to determine the craft type profile for the skeinforge chain.  The default craft type is extrusion.

The setting is the selection.  If you hit 'Save and Close' the selection will be saved, if you hit 'Cancel' the selection will not be saved.

To change the profile setting, in a shell in the profile folder type:
> python profile.py

An example of using profile from the python interpreter follows below.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import profile
>>> profile.main()
This brings up the profile setting dialog.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import settings
import os


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addListsToCraftTypeRepository( fileNameHelp, repository ):
	"Add the value to the lists."
	craftTypeName = getCraftTypeName()
	craftTypeProfileDirectory = os.path.join( craftTypeName, getProfileName( craftTypeName ) )
	settings.addListsToRepository( fileNameHelp, craftTypeProfileDirectory, repository )
	dotsMinusOne = fileNameHelp.count( '.' ) - 1
	x = 0
	xAddition = 400
	for step in xrange( dotsMinusOne ):
		x += xAddition
		xAddition /= 2
	repository.windowPosition.value = '%s+0' % x

def addSubmenus( craftTypeName, menu, pluginFileName, pluginPath, profileRadioVar ):
	"Add a tool plugin menu."
	submenu = settings.Tkinter.Menu( menu, tearoff = 0 )
	menu.add_cascade( label = pluginFileName.capitalize(), menu = submenu )
	settings.ToolDialog().addPluginToMenu( submenu, pluginPath )
	submenu.add_separator()
	pluginModule = getCraftTypePluginModule( pluginFileName )
	profilePluginSettings = settings.getReadRepository( pluginModule.getNewRepository() )
	isSelected = ( craftTypeName == pluginFileName )
	for profileName in profilePluginSettings.profileList.value:
		value = isSelected and profileName == profilePluginSettings.profileListbox.value
		ProfileMenuRadio( pluginFileName, submenu, profileName, profileRadioVar, value )

def addToProfileMenu( menu ):
	"Add a profile menu."
	settings.ToolDialog().addPluginToMenu( menu, __file__[ : __file__.rfind( '.' ) ] )
	menu.add_separator()
	directoryPath = getPluginsDirectoryPath()
	pluginFileNames = getPluginFileNames()
	craftTypeName = getCraftTypeName()
	profileRadioVar = settings.Tkinter.StringVar()
	for pluginFileName in pluginFileNames:
		addSubmenus( craftTypeName, menu, pluginFileName, os.path.join( directoryPath, pluginFileName ), profileRadioVar )

def addToMenu( master, menu, repository, window ):
	"Add a tool plugin menu."
	ProfileMenuSaveListener( menu, window )

def getCraftTypeName( subName = '' ):
	"Get the craft type from the profile."
	profileSettings = getReadProfileRepository()
	craftTypeName = settings.getSelectedPluginName( profileSettings.craftRadios )
	if subName == '':
		return craftTypeName
	return os.path.join( craftTypeName, subName )

def getCraftTypePluginModule( craftTypeName = '' ):
	"Get the craft type plugin module."
	if craftTypeName == '':
		craftTypeName = getCraftTypeName()
	profilePluginsDirectoryPath = getPluginsDirectoryPath()
	return gcodec.getModuleWithDirectoryPath( profilePluginsDirectoryPath, craftTypeName )

def getNewRepository():
	"Get the repository constructor."
	return ProfileRepository()

def getPluginFileNames():
	"Get analyze plugin fileNames."
	return gcodec.getPluginFileNamesFromDirectoryPath( getPluginsDirectoryPath() )

def getPluginsDirectoryPath():
	"Get the plugins directory path."
	return gcodec.getAbsoluteFolderPath( __file__, 'profile_plugins' )

def getProfileName( craftTypeName ):
	"Get the profile name from the craft type name."
	craftTypeSettings = getCraftTypePluginModule( craftTypeName ).getNewRepository()
	settings.getReadRepository( craftTypeSettings )
	return craftTypeSettings.profileListbox.value

def getReadProfileRepository():
	"Get the read profile repository.	from skeinforge_tools import profile"
	return settings.getReadRepository( getNewRepository() )


class ProfileMenuRadio:
	"A class to display a profile menu radio button."
	def __init__( self, profilePluginFileName, menu, name, radioVar, value ):
		"Create a profile menu radio."
		self.activate = False
		self.menu = menu
		self.name = name
		self.profileJoinName = profilePluginFileName + '.& /' + name
		self.profilePluginFileName = profilePluginFileName
		self.radioVar = radioVar
		menu.add_radiobutton( label = name.replace( '_', ' ' ), command = self.clickRadio, value = self.profileJoinName, variable = self.radioVar )
		self.menuLength = menu.index( settings.Tkinter.END )
		if value:
			self.radioVar.set( self.profileJoinName )
			self.menu.invoke( self.menuLength )
		self.activate = True

	def clickRadio( self ):
		"Workaround for Tkinter bug, invoke and set the value when clicked."
		if not self.activate:
			return
		self.radioVar.set( self.profileJoinName )
		pluginModule = getCraftTypePluginModule( self.profilePluginFileName )
		profilePluginSettings = settings.getReadRepository( pluginModule.getNewRepository() )
		profilePluginSettings.profileListbox.value = self.name
		settings.writeSettings( profilePluginSettings )
		profileSettings = getReadProfileRepository()
		plugins = profileSettings.craftRadios
		for plugin in plugins:
			plugin.value = ( plugin.name == self.profilePluginFileName )
		settings.writeSettings( profileSettings )
		settings.updateProfileSaveListeners()


class ProfileMenuSaveListener:
	"A class to update a profile menu."
	def __init__( self, menu, window ):
		"Set the menu."
		self.menu = menu
		addToProfileMenu( menu )
		settings.addElementToListTableIfNotThere( self, window, settings.globalProfileSaveListenerListTable )

	def save( self ):
		"Profile has been saved and profile menu should be updated."
		settings.deleteMenuItems( self.menu )
		addToProfileMenu( self.menu )


class ProfilePluginRadioButtonsSaveListener:
	"A class to update the profile radio buttons."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		settings.addElementToListTableIfNotThere( self, self.repository.repositoryDialog, settings.globalProfileSaveListenerListTable )

	def getFromRadioPlugins( self, radioPlugins, repository ):
		"Initialize."
		self.name = 'ProfilePluginRadioButtonsSaveListener'
		self.radioPlugins = radioPlugins
		self.repository = repository
		repository.displayEntities.append( self )
		return self

	def save( self ):
		"Profile has been saved and profile radio plugins should be updated."
		craftTypeName = getCraftTypeName()
		for radioPlugin in self.radioPlugins:
			if radioPlugin.name == craftTypeName:
				radioPlugin.setSelect()
				self.repository.pluginFrame.update()
				return


class ProfileRepository:
	"A class to handle the profile entities."
	def __init__( self ):
		"Set the default entities, execute title & repository fileName."
		settings.addListsToRepository( 'skeinforge_tools.profile.html', '', self )
		importantFileNames = [ 'extrusion' ]
		self.craftRadios = settings.getRadioPluginsAddPluginFrame( getPluginsDirectoryPath(), importantFileNames, getPluginFileNames(), self )
		ProfilePluginRadioButtonsSaveListener().getFromRadioPlugins( self.craftRadios, self )
		for craftRadio in self.craftRadios:
			craftRadio.updateFunction = self.updateRelay
		directoryName = settings.getProfilesDirectoryPath()
		settings.makeDirectory( directoryName )
		self.windowPosition.value = '0+200'

	def updateRelay( self ):
		"Update the plugin frame then the ProfileSaveListeners."
		self.pluginFrame.update()
		settings.updateProfileSaveListeners()


class ProfileSelectionMenuRadio:
	"A class to display a profile selection menu radio button."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		self.activate = False
		self.menuButtonDisplay.setToNameAddToDialog( self.valueName, gridPosition )
		self.menuButtonDisplay.menu.add_radiobutton( label = self.valueName, command = self.clickRadio, value = self.valueName, variable = self.menuButtonDisplay.radioVar )
		self.menuLength = self.menuButtonDisplay.menu.index( settings.Tkinter.END )
		if self.value:
			self.menuButtonDisplay.radioVar.set( self.valueName )
			self.menuButtonDisplay.menu.invoke( self.menuLength )
		settings.addElementToListTableIfNotThere( self.repository, self.repository.repositoryDialog, settings.globalProfileSaveListenerListTable )
		self.activate = True

	def clickRadio( self ):
		"Workaround for Tkinter bug, invoke and set the value when clicked."
		if not self.activate:
			return
		self.menuButtonDisplay.radioVar.set( self.valueName )
		pluginModule = getCraftTypePluginModule()
		profilePluginSettings = settings.getReadRepository( pluginModule.getNewRepository() )
		profilePluginSettings.profileListbox.value = self.name
		settings.writeSettings( profilePluginSettings )
		settings.updateProfileSaveListeners()

	def getFromMenuButtonDisplay( self, menuButtonDisplay, name, repository, value ):
		"Initialize."
		self.setToMenuButtonDisplay( menuButtonDisplay, name, repository, value )
		self.valueName = name.replace( '_', ' ' )
		return self

	def setToMenuButtonDisplay( self, menuButtonDisplay, name, repository, value ):
		"Initialize."
		self.menuButtonDisplay = menuButtonDisplay
		self.menuButtonDisplay.menuRadios.append( self )
		self.name = name
		self.repository = repository
		self.value = value
		repository.displayEntities.append( self )


class ProfileTypeMenuRadio( ProfileSelectionMenuRadio ):
	"A class to display a profile type menu radio button."
	def clickRadio( self ):
		"Workaround for Tkinter bug, invoke and set the value when clicked."
		if not self.activate:
			return
		self.menuButtonDisplay.radioVar.set( self.valueName )
		profileSettings = getReadProfileRepository()
		plugins = profileSettings.craftRadios
		for plugin in plugins:
			plugin.value = ( plugin.name == self.name )
		settings.writeSettings( profileSettings )
		settings.updateProfileSaveListeners()

	def getFromMenuButtonDisplay( self, menuButtonDisplay, name, repository, value ):
		"Initialize."
		self.setToMenuButtonDisplay( menuButtonDisplay, name, repository, value )
		self.valueName = settings.getEachWordCapitalized( name )
		return self


def main():
	"Display the profile dialog."
	settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
