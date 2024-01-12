

import cppyy
import os
import code
import traceback

cppyy.add_include_path("./TritonRoute/src/")
cppyy.include("FlexRoute.h")
cppyy.include("dr/FlexGridGraph.h")
cppyy.include("dr/FlexWavefront.h")
cppyy.include("dr/FlexDR.h")


cppyy.load_library("./TritonRoute/build/libflexroute.so")

from cppyy import gbl as gbl
from cppyy.gbl import fr as fr
from cppyy.gbl import std


import ctypes
cppyy.cppdef("namespace fr { typedef drPin* drPinPtr; }")
from cppyy.gbl.fr import drPin, drPinPtr, frBlockObjectComp, FlexMazeIdx, frCoord, frPoint
from cppyy.gbl.fr import frDirEnum, frMIdx, FlexWavefrontGrid, frCost, frBox


class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # inspects the starting state
    """
    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
        must return an action from Directions.{North, South, East, West, Stop}
        """
        raiseNotDefined()
