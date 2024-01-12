import argparse
from game import *

def printGraph(graph):

    gridBBox = frBox()

    graph.getBBox(gridBBox)

    print(f"printing Maze grid ({gridBBox.left()},{gridBBox.bottom()}) ... ({gridBBox.right(),gridBBox.top()})")

    xDim = ctypes.c_int()
    yDim = ctypes.c_int()
    zDim = ctypes.c_int()
    graph.getDim(xDim, yDim, zDim)
    xDim = xDim.value
    yDim = yDim.value
    zDim = zDim.value

    print(f"extBBox (xDim, yDim, zDim) = ({xDim},{yDim},{zDim})")

    v = frPoint()
    w = frPoint()
    for xIdx in range(xDim):
        for yIdx in range(yDim):
            for zIdx in range(zDim):
                if graph.isSrc(xIdx, yIdx, zIdx):
                    print(f"({xIdx}, {yIdx}, {zIdx}) is a source node.")
                if graph.isDst(xIdx, yIdx, zIdx):
                    print(f"({xIdx}, {yIdx}, {zIdx}) is a destination node.")

                if (graph.hasEdge(xIdx, yIdx, zIdx, frDirEnum.N)):
                    v = graph.getPoint(v, xIdx, yIdx)
                    w = graph.getPoint(w, xIdx, yIdx+1)
                    print(f"The x,y coordinates of node ({xIdx}, {yIdx}, {zIdx}) is ({v.x()}, {v.y()}).")
                    print(f"The x,y coordinates of node ({xIdx}, {yIdx+1}, {zIdx}) is ({w.x()}, {w.y()}).")
                if (graph.hasEdge(xIdx, yIdx, zIdx, frDirEnum.E)):
                    v = graph.getPoint(v, xIdx, yIdx)
                    w = graph.getPoint(w, xIdx+1, yIdx)
                    print(f"The x,y coordinates of node ({xIdx}, {yIdx}, {zIdx}) is ({v.x()}, {v.y()}).")
                    print(f"The x,y coordinates of node ({xIdx+1}, {yIdx}, {zIdx}) is ({w.x()}, {w.y()}).")
                if (graph.hasEdge(xIdx, yIdx, zIdx, frDirEnum.U)):
                    v = graph.getPoint(v, xIdx, yIdx)
                    print(f"The x,y coordinates of node ({xIdx}, {yIdx}, {zIdx}) is ({v.x()}, {v.y()}).")
                    print(f"The x,y coordinates of node ({xIdx}, {yIdx}, {zIdx+1}) is ({v.x()}, {v.y()}).") 


def plotMyGridGraph(graph):
    """
    Using a python plot library, visualize the given 3D grid graph using the API
    """
    "*** YOUR CODE HERE ***"
    try:
        printGraph(graph)
    except Exception as e:
        traceback.print_exec()
        os.exit_(1)

    
