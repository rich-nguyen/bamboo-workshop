# Run this script as mayapy
# /Applications/Autodesk/maya2015/Maya.app/Contents/bin/mayapy /Users/noin/work/bamboo-workshop/bamboo-workshop.py "/Users/noin/Dropbox/Share/Bamboo Workshop/TestTriangle.ma"

import sys

import maya.standalone
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

class Edge:

    def __init__(self, id, startVertexId, endVertexId, length):
        self.id = id
        self.startVertexId = startVertexId
        self.endVertexId = endVertexId
        self.connectedVertices = [self.startVertexId, self.endVertexId]
        self.length = length

class Vertex:

    def __init__(self, id, position, connectedEdges):
        self.id = id
        self.position = position
        self.connectedEdges = connectedEdges

class Exporter:

    def __init__(self):
        self.edges = []
        self.vertices =[]

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
            vertexId = [vertex for vertex in edge.connectedVertices if not vertexId == vertex].pop()
            connections.append((edgeId,vertexId))
        return connections


    def extractVertices(self, dagPath):
        print("\n ---- Vertex Information ---- \n")

        vertexIterator = OpenMaya.MItMeshVertex(dagPath)

        while not vertexIterator.isDone():

            vertexId = vertexIterator.index()
            position = vertexIterator.position(OpenMaya.MSpace.kObject)

            edgeList = OpenMaya.MIntArray()
            vertexIterator.getConnectedEdges(edgeList)
            connectedEdges = [edgeList[i] for i in range(edgeList.length())]
            newVertex = Vertex(vertexId, position, connectedEdges)
            self.vertices.append(newVertex)

            vertexIterator.next()

        for vertex in self.vertices:
            print("vertex {0} has position({1},{2},{3}) and is connected to edges: {4}".format(
                vertex.id,
                vertex.position.x,
                vertex.position.y,
                vertex.position.z,
                ', '.join(map(str, vertex.connectedEdges))))

            # For each vertex, find the angle of the connected edge. Use the position of the connected vertex.
            for connections in self.findConnectedVertices(vertex.id):
                print("   - found edge {0} connected to vertex: {1}".format(connections[0], connections[1]))

    def extractEdges(self, dagPath):
        print("\n ---- Edge Information ---- \n")

        edgeIterator = OpenMaya.MItMeshEdge(dagPath)

        while not edgeIterator.isDone():

            lengthPtr = OpenMaya.MScriptUtil().asDoublePtr()
            edgeIterator.getLength(lengthPtr, OpenMaya.MSpace.kObject)
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

            dagIterator.next()

def main(argv):

    print("running my script over " + argv[1])

    # Start Maya in batch mode
    maya.standalone.initialize(name='python')

    # Open the file with the file command
    cmds.file(argv[1], force=True, open=True)

    exporter = Exporter()
    exporter.export()

main(sys.argv)
