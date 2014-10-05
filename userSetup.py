import maya.utils
import maya.cmds as cmds
import maya.mel as mel
import bamboo.ui

maya.utils.executeDeferred("setup()", lowestPriority=True)

def setup():
    print ("bamboo user setup")

    mainFileMenu = mel.eval("string $f=$gMainFileMenu")
    mel.eval("buildFileMenu")
    cmds.menuItem(dividerLabel="Bamboo Tools", divider=True)
    cmds.menuItem(label="Export...", parent=mainFileMenu, command="openExporterUI()")

def openExporterUI():
    bamboo.ui.ExporterUI().show()

def reload():
    print ("reloading bamboo exporter")
    # reload the file to make sure its up to date
    exec 'reload(bamboo.exporter)' in globals()