# Bamboo module for modifying the scene mesh into joints.

import maya.cmds as cmds

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
            numberOfColumns=3,
            columnWidth=[(1, 100), (2, 60), (3, 60)],
            columnOffset=[(1, "right", 3)])

        # Top Row
        cmds.separator(h=10, style="none")
        cmds.separator(h=10, style="none")
        cmds.separator(h=10, style="none")

        cmds.text(label="Output File:")
        cmds.textField()
        cmds.separator(h=10, style="none")

        cmds.text(label="Lengths File:")
        cmds.textField()
        cmds.separator(h=10, style="none")

        # Blank row
        cmds.separator(h=10, style="none")
        cmds.separator(h=10, style="none")
        cmds.separator(h=10, style="none")

        cmds.separator(h=10, style="none")
        cmds.button(
            label="Export",
            command=self.actionBtnCmd
        )
        cmds.button(
            label="Cancel",
            command=self.cancelBtnCmd
        )

        cmds.showWindow()

    def actionBtnCmd(self, *args):
        cmds.deleteUI(self.window, window=True)

    def cancelBtnCmd(self, *args):
        cmds.deleteUI(self.window, window=True)