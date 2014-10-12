bamboo-workshop
===============

A collection of tools for rendering polygonal meshes into real physical structures. This repo contains a Maya script that can be executed on a scene containing a mesh shape. The aim is to turn a Maya mesh into a real-world structure, where edges (in the form of some kind of rod) are connected together to resemble the original mesh.

The mesh shape will be processed into a number of 'Joints'. A Joint represents a mesh vertex. In contrast to a vertex, it is not a point in 3D space, it is a shape volume that has plug-like sockets aligned to the edges that connect to the corresponding vertex. The Joint is oriented along the vertex normal. The rods can be inserted into the plugs. The plug-like sockets have different shapes to make assembly slightly easier.

Requirements
------------

- Maya 2015 was used to develop this tool.
- To use the provided bash scripts that help Maya locate the scripts, Maya 2015 on MacOsX is required. The bash file can easily be ported to other OSs and versions of Maya. See the script [mayaenv](./mayaenv.sh)

Running the Exporter
--------------------

1. Open Maya using [mayaenv](./mayaenv.sh). This installs the script path, and installs a menu group in Maya->File called Bamboo Tools.
2. Create a mesh in the scene (limitations apply).
3. Add the templates scene as a reference node using the Maya Reference Editor.
4. Export the scene by clicking Maya->(Bamboo Tools) Export...

Terminology
-----------
 - A Maya edge is converted into a Stick. Sticks are made from bamboo.
 - A Maya vertex is converted into a Dot. Dots are made from PLA plastic.
 - A Dot is made from subtracting one or more Cutouts from a Sphere. A Dot contains a corresponding numerical label (formatted 'dot_XXX').
 - A Cutout is a Maya mesh that is used to subtract a hole from a Sphere.
 - A Sphere is a Maya mesh with a numerical label (formatted 'sphere_XXX').
 - A Sculpture is a Maya mesh which will be converted into Dots and Sticks.

Mesh limitations
----------------
 - 25 vertices in the shape. Don't think we can fit anymore on our 3D printer without pagination.
 - 5 edges per vertex.
 - no extreme acute angles. The sockets will just merge together.
 - There must be a region of the vertex that has no edge connections, located near the normal. This is so the Joint can have a readable identifier imprinted.

Things To Do
------------
- [x] Basic exporter that creates Joints.
- [x] Remove alphabet
- [x] Submit the first version of the templates reference scene, with numbered joints.
- [ ] Automate the reference node bit.
- [x] Create the instructions file which will contain the rod lengths and connections.
- [ ] Add error checking.
- [ ] Export to stl.