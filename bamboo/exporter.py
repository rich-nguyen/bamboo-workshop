# Bamboo module for modifying the scene mesh into joints.

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.standalone
import os
import sys

# Maya Edge model class, that will be converted into a Stick.
class Edge:

    def __init__(self, id, startVertexId, endVertexId, length):
        self.id = id
        self.startVertexId = startVertexId
        self.endVertexId = endVertexId
        self.connectedVertices = [self.startVertexId, self.endVertexId]
        self.length = length

    def name(self):
        # Use a 1-based naming convention.
        return "%03d" % (self.id + 1)

# Maya Vertex model class, that will be converted into a Dot.
class Vertex:

    def __init__(self, id, position, normal, connectedEdges):
        self.id = id
        self.position = position
        self.normal = normal
        self.connectedEdges = connectedEdges

    def negatedNormal(self):
        return -self.normal

# A Vertex-based class with detailed cutout information.
class Dot:

    def __init__(self, id):
        # the corresponding vertex that this dot was constructed from.
        self.vertexId = id
        self.cutouts = []

    def addCutout(self, cutout):
        self.cutouts.append(cutout)

    def name(self):
        # Use a 1-based naming convention.
        return "%03d" % (self.vertexId + 1)

    def findCutout(self, edgeId):
        return [cutout for cutout in self.cutouts if cutout.edgeId == edgeId].pop()

    def templateName(self):
        # this used to be dynamic, but now all dots share the same template name.
        return "dot"

# A Cutout represents a single socket on a Dot. It can accomodate a Stick.
class Cutout:

    shapeMap = ['cutoutTriangle', 'cutoutSquare', 'cutoutPentagon', 'cutoutCircle']
    friendlyName = ['triangle', 'square', 'pentagon', 'circle']

    def __init__(self, shapeId, rotation, edgeId):
        # the unique shape that identifies the cutout.
        self.shape = self.shapeMap[shapeId]
        # the angle of rotation is the transformation from the yAxis to the angle of the edge.
        self.rotation = rotation
        self.edgeId = edgeId
        self.name = self.friendlyName[shapeId]

class Exporter:

    # This needs to be incremented if a new version of the template is made.
    version = 'v1'

    def __init__(self, gridSpacing, gridWidth, createInstructions):
        self.dotGridSpacing = gridSpacing
        self.dotGridWidth = gridWidth
        self.createInstructions = createInstructions
        self.edges = []
        self.vertices = []
        self.dots = []

    # Find a Vertex instance from its id.
    def findVertex(self, id):
        return [vertex for vertex in self.vertices if vertex.id == id].pop()

    # Find an Edge instance from its id.
    def findEdge(self, id):
        return [edge for edge in self.edges if edge.id == id].pop()

    # Find a Dot instance from its id.
    def findDot(self, id):
        return [dot for dot in self.dots if dot.vertexId == id].pop()

    # Find a list of (edgeId, vertexId) pairs which are connected to a specified vertex.
    def findConnectedVertices(self, vertexId):
        connections = []
        for edgeId in self.findVertex(vertexId).connectedEdges:
            edge = self.findEdge(edgeId)
            oppositeVertexId = [vertex for vertex in edge.connectedVertices if not vertexId == vertex].pop()
            connections.append((edgeId, oppositeVertexId))
        return connections

    # Create all the Vertex objects from the dag path shape.
    def extractVertices(self, dagPath):
        vertexIterator = OpenMaya.MItMeshVertex(dagPath)

        while not vertexIterator.isDone():

            vertexId = vertexIterator.index()
            position = vertexIterator.position(OpenMaya.MSpace.kWorld)

            normal = OpenMaya.MVector()
            vertexIterator.getNormal(normal, OpenMaya.MSpace.kWorld)

            edgeList = OpenMaya.MIntArray()
            vertexIterator.getConnectedEdges(edgeList)
            connectedEdges = [edgeList[i] for i in range(edgeList.length())]
            newVertex = Vertex(vertexId, position, normal, connectedEdges)
            self.vertices.append(newVertex)

            vertexIterator.next()

    # Create all the Edge objects from the dag path shape.
    def extractEdges(self, dagPath):

        edgeIterator = OpenMaya.MItMeshEdge(dagPath)

        while not edgeIterator.isDone():

            lengthPtr = OpenMaya.MScriptUtil().asDoublePtr()
            edgeIterator.getLength(lengthPtr, OpenMaya.MSpace.kWorld)
            length = OpenMaya.MScriptUtil.getDouble(lengthPtr)
            startVertexId = edgeIterator.index(0)
            endVertexId = edgeIterator.index(1)
            edgeId = edgeIterator.index()

            newEdge = Edge(edgeId, startVertexId, endVertexId, length)
            self.edges.append(newEdge)

            edgeIterator.next()

    # Calculate rotations from the Vertex connections, and create a Dot with Cutouts.
    def constructDots(self):

        for vertex in self.vertices:
            # Create the Dot object.
            dot = Dot(vertex.id)
            negatedNormal = vertex.negatedNormal()
            position = OpenMaya.MVector(vertex.position)

            # For each vertex, find the angle of the connected edge. Use the position of the connected vertex.
            connectedVertices = self.findConnectedVertices(vertex.id)
            for i in range(len(connectedVertices)):
                connection = connectedVertices[i]

                oppositeVertex = self.findVertex(connection[1])
                oppositeVertexPosition = OpenMaya.MVector(oppositeVertex.position)

                directionOfEdge = oppositeVertexPosition - position
                directionOfEdge.normalize()
                rotationNormalToEdge = OpenMaya.MQuaternion(negatedNormal, directionOfEdge)
                rotationYaxisToNormal = OpenMaya.MQuaternion(OpenMaya.MVector.yAxis, negatedNormal)
                rotationNormalToYaxis = rotationYaxisToNormal.inverse()

                cutout = Cutout(i, rotationYaxisToNormal * rotationNormalToEdge * rotationNormalToYaxis, connection[0])

                dot.addCutout(cutout)

            self.dots.append(dot)

    # Takes a string path and returns an equivalent MDagPath.
    def getDagPathFromPath(self, path):
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(path)
        dagPath = OpenMaya.MDagPath()
        selectionList.getDagPath(0, dagPath)
        return dagPath

    # Takes a string template object name (eg. cutoutTriangle) and returns the object name.
    def getTemplateObjectName(self, objectName):
        return "template_{0}_:{1}".format(self.version, objectName)

    # Add a Dot into the scene.
    def insertDots(self):

        # copy dot object
        # copy cutout object
        # run mesh difference
        # delete the layers
        # delete the groups
        # rename the cutout.

        for dot in self.dots:
            # Copy sphere object from the template object.
            newDot = cmds.duplicate(self.getTemplateObjectName(dot.templateName()))[0]

            for cutout in dot.cutouts:

                # Copy cutout object from the template object, and rotate it.
                newCutout = cmds.duplicate(self.getTemplateObjectName(cutout.shape))[0]
                cutoutDagPath = self.getDagPathFromPath(newCutout)
                mfnTransform = OpenMaya.MFnTransform(cutoutDagPath)

                mfnTransform.rotateBy(cutout.rotation, OpenMaya.MSpace.kTransform)

                # Mesh boolean combine, with 'difference' operator.
                boolOp = cmds.polyBoolOp(newDot, newCutout, op=2)

                # Update the dot copy name and remove history.
                newDot = boolOp[0]
                cmds.delete(newDot, constructionHistory=True)

            dotPath = "dot_{0}".format(dot.name())
            cmds.rename(newDot, dotPath)

            # Move the new dot onto the final grid for printing.
            self.positionDot(dotPath, dot.vertexId)

    def positionDot(self, dotPath, vertexId):
        # Given the vertex id and the num vertex id, work out the world position of the dot.

        xPosition = (vertexId % self.dotGridWidth) * self.dotGridSpacing
        zPosition = (vertexId // self.dotGridWidth) * self.dotGridSpacing

        dotDagPath = self.getDagPathFromPath(dotPath)
        mfnTransform = OpenMaya.MFnTransform(dotDagPath)
        mfnTransform.setTranslation(OpenMaya.MVector(xPosition, 0.0, zPosition), OpenMaya.MSpace.kTransform)

    def printStickInformation(self):
        print("\n ---- Stick Information ---- \n")

        for edge in self.edges:
            startDot = self.findDot(edge.startVertexId)
            endDot = self.findDot(edge.endVertexId)
            print("Stick {0} connects dot_{1} {2} hole to dot_{3} {4} hole and has length {5}".format(
                edge.name(),
                startDot.name(),
                startDot.findCutout(edge.id).name,
                endDot.name(),
                endDot.findCutout(edge.id).name,
                edge.length))

    def export(self, outputFile):

        cmds.file(rename=outputFile)

        # Traverse the scene.
        dagIterator = OpenMaya.MItDag(OpenMaya.MItDag.kDepthFirst)

        while not dagIterator.isDone():

            dagPath = OpenMaya.MDagPath()
            dagIterator.getPath(dagPath)

            dagNode = OpenMaya.MFnDagNode(dagPath)

            if (not dagNode.isIntermediateObject() and
                    dagPath.hasFn(OpenMaya.MFn.kMesh) and
                    not dagPath.hasFn(OpenMaya.MFn.kTransform)):

                print(dagPath.fullPathName() + " mesh found")

                self.extractEdges(dagPath)

                self.extractVertices(dagPath)

                break

            dagIterator.next()

        self.constructDots()

        self.printStickInformation()

        self.insertDots()

        fileName, fileExtension = os.path.splitext(outputFile)
        fileType = ""
        if fileExtension == ".mb":
            fileType = "mayaBinary"
        elif fileExtension == ".ma":
            fileType = "mayaAscii"

        cmds.file(save=True, type=fileType)

# Run the exporter in console mode, good for testing.
# /Applications/Autodesk/maya2015/Maya.app/Contents/bin/mayapy "~/work/bamboo-workshop/bamboo/exporter.py" "~/Dropbox/Share/Bamboo Workshop/Noins testing Sandbox/TestTriangle.ma" "~/Desktop/output.ma"
def main(argv):

    print("running bamboo exporter in console mode")

    # Start Maya in batch mode
    maya.standalone.initialize(name='python')

    # Open the file with the file command
    cmds.file(argv[1], force=True, open=True)

    # Pass the output file.
    Exporter(20, 5, False).export(argv[2])

if __name__ == "__main__":
    main(sys.argv)