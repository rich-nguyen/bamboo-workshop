# Run this script as mayapy
# /Applications/Autodesk/maya2015/Maya.app/Contents/bin/mayapy /Users/noin/work/bamboo-workshop/bamboo-workshop.py "/Users/noin/Dropbox/Share/Bamboo Workshop/TestTriangle.ma"

import sys

import maya.standalone
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

# Maya Edge model class, that will be converted into a rod.
class Edge:

    def __init__(self, id, startVertexId, endVertexId, length):
        self.id = id
        self.startVertexId = startVertexId
        self.endVertexId = endVertexId
        self.connectedVertices = [self.startVertexId, self.endVertexId]
        self.length = length

# Maya Vertex model class, that will be converted into a Joint.
class Vertex:

    def __init__(self, id, position, normal, connectedEdges):
        self.id = id
        self.position = position
        self.normal = normal
        self.connectedEdges = connectedEdges

    def negatedNormal(self):
        return -self.normal

# A Vertex-based class with detailed plug information.
class Joint:

    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    def __init__(self, id):
        # the corresponding vertex that this joint was constructed from.
        self.vertexId = id
        self.plugs = []

    def addPlug(self, plug):
        self.plugs.append(plug)

    def name(self):
        return self.alphabet[self.vertexId]

# A Plug represents a single socket on a Joint. It can accomodate an edge.
class Plug:

    shapeMap = ['circle', 'triangle', 'square', 'pentagon', 'hexagon']

    def __init__(self, shapeId, rotation):
        # the unique shape that identifies the plug.
        self.shape = self.shapeMap[shapeId]
        # the angle of rotation is the transformation from the yAxis to the angle of the edge.
        self.rotation = rotation

class Exporter:

    # This needs to be incremented if a new version of the template is made.
    version = 'v1'

    def __init__(self):
        self.edges = []
        self.vertices = []
        self.joints = []

    # Find a Vertex instance from its id.
    def findVertex(self, id):
        return [vertex for vertex in self.vertices if vertex.id == id].pop()

    # Find an Edge instance from its id.
    def findEdge(self, id):
        return [edge for edge in self.edges if edge.id == id].pop()

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
        print("\n ---- Vertex Information ---- \n")

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

        for vertex in self.vertices:
            print("vertex {0} has position({1},{2},{3}), normal ({5},{6},{7}) and is connected to edges: {4}".format(
                vertex.id,
                vertex.position.x,
                vertex.position.y,
                vertex.position.z,
                ', '.join(map(str, vertex.connectedEdges)),
                vertex.normal.x,
                vertex.normal.y,
                vertex.normal.z))

    # Create all the Edge objects from the dag path shape.
    def extractEdges(self, dagPath):
        print("\n ---- Edge Information ---- \n")

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

        for edge in self.edges:
            print("edge {0} connects vertex {1} to vertex {2} and has length {3}".format(
                edge.id,
                edge.startVertexId,
                edge.endVertexId,
                edge.length))

    # Calculate rotations from the Vertex connections, and create a Joint with Plugs.
    def constructJoints(self):

        for vertex in self.vertices:
            # Create the Joint object.
            joint = Joint(vertex.id)
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

                plug = Plug(i, rotationYaxisToNormal * rotationNormalToEdge * rotationNormalToYaxis)

                print("   - Plug for vertex {0}, shape {1}".format(vertex.id, plug.shape))
                print("   -    found edge {0} connected vertex {2} to vertex: {1}".format(connection[0], connection[1], vertex.id))
                print("   -    and the direction of the edge is ({0},{1},{2})".format(
                    directionOfEdge.x,
                    directionOfEdge.y,
                    directionOfEdge.z))

                joint.addPlug(plug)

            self.joints.append(joint)

    # Takes a string path and returns an equivalent MDagPath.
    def getDagPathFromPath(self, path):
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(path)
        dagPath = OpenMaya.MDagPath()
        selectionList.getDagPath(0, dagPath)
        return dagPath

    # Takes a string template object name (eg. joint) and returns the object name.
    def getTemplateObjectName(self, objectName):
        return "template_{0}_:{1}".format(self.version, objectName)

    # Add a joint into the scene.
    def insertJoints(self):

        # copy joint object
        # copy plug object
        # run mesh difference
        # delete the layers
        # delete the groups
        # rename the cutout.

        for joint in self.joints:
            print('adding joint {0} (letter {1})'.format(joint.vertexId, joint.name()))

            # Copy joint object from the template object.
            newJoint = cmds.duplicate(self.getTemplateObjectName("joint"))[0]

            for plug in joint.plugs:

                # Copy plug object from the template object, and rotate it.
                newPlug = cmds.duplicate(self.getTemplateObjectName("square"))[0]
                plugDagPath = self.getDagPathFromPath(newPlug)
                mfnTransform = OpenMaya.MFnTransform(plugDagPath)

                #mfnTransform.setRotateOrientation(plug.baseRotation, OpenMaya.MSpace.kTransform, False)
                mfnTransform.rotateBy(plug.rotation, OpenMaya.MSpace.kTransform)

                # Mesh boolean combine, with 'difference' operator.
                boolOp = cmds.polyBoolOp(newJoint, newPlug, op=2)

                # Update the joint copy name and remove history.
                newJoint = boolOp[0]
                cmds.delete(newJoint, constructionHistory=True)

            cmds.rename(newJoint, "joint_{0}_{1}".format(joint.name(), joint.vertexId))

    def export(self):
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

        self.constructJoints()
        self.insertJoints()

def main(argv):

    print("running my script over " + argv[1])

    # Start Maya in batch mode
    maya.standalone.initialize(name='python')

    # Open the file with the file command
    cmds.file(argv[1], force=True, open=True)

    exporter = Exporter()
    exporter.export()

    cmds.file(rename="/Users/noin/Desktop/output.ma")
    cmds.file(save=True, type="mayaAscii")

main(sys.argv)