# quiver-mutation
play around with quiver mutation
You will need to install python, pip, and tkinter.
Based on the rules in https://arxiv.org/abs/1608.05735
----------------------------------
There are four modes: set nodes, move nodes, edges, and mutate.

1. Set Nodes:
Here, you can choose which nodes will be frozen and which nodes will be mutable.
Click once to make it frozen (displays an F), click again to make it mutable (displays an M), and click again to make it empty.
In all other modes, the empty nodes will disappear.

2. Move Nodes:
Self explanatory; you can move nodes around by left clicking and dragging.

3. Edges:
Currently a bit buggy (and needs a visual fix for the edge multiplicity).
Edges are oriented.
Click one node; that will be the initial node of an edge. Then, click another node; that will be the final node of the edge.
Since I am following the conventions in https://arxiv.org/abs/1608.05735, loops and oriented 2-cycles are not allowed.
In other words, you cannot have an edge from a node to itself, and you cannot have edges in different directions between the same two nodes.
There can be multiple edges in the same direction between the same two nodes.
To increase the edge multiplicity, left click the number in the middle of an edge.
To decrease the edge multiplicity, right click the number in the middle of an edge.
If you right click on an edge of multiplicity one, it will remove the edge.

4. Mutate:
Left click on a mutable node to perform the quiver mutation at that node.
