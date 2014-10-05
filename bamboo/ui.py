# Bamboo module for modifying the scene mesh into joints.

import maya.cmds as cmds
import bamboo.exporter

class ExporterUI():
    def __init__(self):
        ## unique window handle
        self.window = "bambooExporterUI"
    def show(self):
        """Draw the window"""
        # delete the window if its handle exists
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)
        # initialize the window
        cmds.window(
            self.window,
            title="Bamboo Exporter",
            sizeable=False,
            resizeToFitChildren=True
        )
        # main form for the window
        cmds.rowColumnLayout(
            numberOfColumns=4,
            columnWidth=[(1, 10), (2, 150), (3, 10), (4, 60)])

        # Top Row
        cmds.separator(h=10, style="none")
        cmds.separator(h=10, style="none")
        cmds.separator(h=10, style="none")
        cmds.separator(h=10, style="none")

        cmds.separator(h=10, style="none")
        cmds.checkBox(label="Create instructions file", value=True)
        cmds.separator(h=10, style="none")
        cmds.separator(h=10, style="none")

        # Blank row
        cmds.separator(h=20, style="none")
        cmds.separator(h=20, style="none")
        cmds.separator(h=20, style="none")
        cmds.separator(h=20, style="none")

        cmds.separator(h=10, style="none")
        cmds.button(
            label="Export",
            command=self.actionBtnCmd  #functools and partial and textfield with query mode to extract params
        )
        cmds.separator(h=10, style="none")
        cmds.button(
            label="Cancel",
            command=self.cancelBtnCmd
        )
        # Add import reference nodes thing, menu/button

        cmds.showWindow()

    def actionBtnCmd(self, *args):
        multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
        outputFile = cmds.fileDialog2(fileFilter=multipleFilters,
                         fileMode=0,
                         dialogStyle=2,
                         caption="Save Output File As")[0]
        cmds.deleteUI(self.window, window=True)
        bamboo.exporter.Exporter().export(outputFile)

    def cancelBtnCmd(self, *args):
        cmds.deleteUI(self.window, window=True)