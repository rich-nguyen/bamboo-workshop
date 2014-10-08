# Bamboo module for modifying the scene mesh into joints.

import maya.cmds as cmds
import functools
import bamboo.exporter

class ExporterUI():
    def __init__(self):
        ## unique window handle
        self.window = "bambooExporterUI"
    def show(self):
        # delete the window if its handle exists
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        # initialize the window
        window = cmds.window(
            self.window,
            title="Bamboo Exporter",
            sizeable=True,
            resizeToFitChildren=True,
            height=50
        )

        col1Width = 115

        cmds.columnLayout(adjustableColumn=True)

        cmds.separator(height=10, style="none")

        intSliderGrp1 = cmds.intSliderGrp(field=True, label="Grid Spacing: ", min=1, max=100, value=20, step=1,
            columnWidth=[(1, col1Width)])

        intSliderGrp2 = cmds.intSliderGrp(field=True, label="Joints per row: ", min=1, max=10, value=4, step=1,
            columnWidth=[(1, col1Width)])

        cmds.separator(height=3, style="none")

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        cmds.text("Create Instructions: ", width=col1Width, align="right")
        checkbox1 = cmds.checkBox(label="", value=True)
        cmds.setParent("..")

        cmds.separator(height=10, style="none")

        cmds.rowLayout(numberOfColumns=3)
        cmds.separator(height=10, style="none", width=col1Width)
        cmds.button(label="Export", command=functools.partial(self.actionBtnCmd,
            intSliderGrp1,
            intSliderGrp2,
            checkbox1), width=120)
        cmds.button(label="Cancel", command=self.cancelBtnCmd, width=80)
        cmds.setParent("..")

        cmds.showWindow(window)

    def actionBtnCmd(self, intSliderGrp1, intSliderGrp2, checkbox1, *args):
        multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
        outputFile = cmds.fileDialog2(fileFilter=multipleFilters,
                         fileMode=0,
                         dialogStyle=2,
                         caption="Save Output File As")[0]
        gridSpacing = cmds.intSliderGrp(intSliderGrp1, query=True, value=True)
        gridWidth = cmds.intSliderGrp(intSliderGrp2, query=True, value=True)
        createInstructions = cmds.checkBox(checkbox1, query=True, value=True)

        cmds.deleteUI(self.window, window=True)
        exporter = bamboo.exporter.Exporter(gridSpacing, gridWidth, createInstructions)
        exporter.export(outputFile)

    def cancelBtnCmd(self, *args):
        cmds.deleteUI(self.window, window=True)