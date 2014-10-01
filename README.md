bamboo-workshop
===============

A collection of tools for rendering polygonal meshes into real physical structures. This repo contains a Maya script that can be executed on a scene containing a Mesh shape. The aim is to turn a Maya mesh into a real-world structure, where edges (in the form of some kind of rod) are connected together to resemble the original mesh.

The Mesh shape will be processed into a number of 'Joints'. A Joint represents a mesh vertex. In contrast to a vertex, it is not a point in 3D space, it is a shape volume that has plug-like sockets aligned to the edges that connect to the corresponding vertex. The Joint is oriented along the vertex normal. The rods can be inserted into the plugs. The plug-like sockets have different shapes to make assembly slightly easier.

Requirements
------------

- Maya 2015 was used to develop this tool.
- To use the provided bash scripts that help Maya locate the scripts, Maya 2015 on MacOsX is required. The bash file can easily be ported to other OSs and versions of Maya. See the script [mayaenv](./mayaenv.sh)

Running the Exporter
--------------------

1. Open Maya using [mayaenv](./mayaenv.sh). This installs the script path, and installs a menu group in Maya->File called Bamboo Tools.
2. Create a Mesh in the scene.
3. Add the templates scene as a reference node using the Maya Reference Editor.
4. Export the scene by clicking Maya->(Bamboo Tools) Export...

Things To Do
------------
[x] Basic exporter that creates Joints.
[ ] Automate the reference part.
[ ] Create the instructions file which will contain the rod lengths and connections.