# route.py
# --------
# This code was written by Prof. Jaeyong Chung for educational purposes, especially sys4106 at Yonsei University.
# Some codes are borrowed from cs188 at UC Berkely
# TritonRoute was developed by UCSD.

import cppyy
import os
import code
import traceback
from game import *

import argparse

from searchAgents import RoutingProblem
from search import *
from plotGraph import *

stopAfterFirstNet = False
plotGraph = False

def parseAgentArgs(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key,val = p, 1
        opts[key] = val
    return opts


def loadAgent(pacman, nographics):
    # Looks through all pythonPath Directories for the right module,
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir): continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if pacman in dir(module):
                if nographics and modulename == 'keyboardAgents.py':
                    raise Exception('Using the keyboard requires graphics (not text display)')
                return getattr(module, pacman)
    raise Exception('The agent ' + pacman + ' is not specified in any *Agents.py.')




def solveRoutingProblem(graph, connComps, nextPin, path, ccMazeIdx1, ccMazeIdx2, centerPt):

    
    #problem = RoutingProblem(graph, goal=destinations[0], start=sources[0])
    #actions = bfs(problem)
    agent = agentType(**agentArgs)
    agent.registerInitialState(graph)
    problem = agent.problem
    actions = agent.actions
    if len(actions)==0: # a path not found
        return False 

    state = problem.getStartState()
    cost = 0

    pathList = []
    prevAction = frDirEnum.UNKNOWN
    for action in actions:
        if prevAction!=action:
            pathList.append(state)
        state = problem.nextState(state, action)
        prevAction = action
        if problem.isGoalState(state):
            pathList.append(state)
        mi = FlexMazeIdx(state[0], state[1], state[2])
        if mi not in connComps:
            connComps.push_back(mi)
            
    for state in reversed(pathList): # from dst to # src
        mi = FlexMazeIdx(state[0], state[1], state[2])
        path.push_back(mi)

    return True


def routeNet(worker, net):

    if net.getPins().size()<=1:
        return True

    unConnPins = std.set[drPinPtr, frBlockObjectComp]()
    # another way to do above
    # unConnPins = std.set["fr:drPin*", frBlockObjectComp]()

    mazeIdx2unConnPins = std.map[FlexMazeIdx, std.set[drPinPtr, frBlockObjectComp]]()
    apMazeIdx = std.set[FlexMazeIdx]()
    realPinAPMazeIdx = std.set[FlexMazeIdx]()

    worker.routeNet_prep(net, unConnPins, mazeIdx2unConnPins, apMazeIdx, realPinAPMazeIdx)

    areaMap = std.map[FlexMazeIdx, frCoord]()
    if gbl.ENABLE_BOUNDARY_MAR_FIX:
        worker.routeNet_prepAreaMap(net, areaMap)

    ccMazeIdx1 = FlexMazeIdx()
    ccMazeIdx2 = FlexMazeIdx()
    centerPt = frPoint()
    connComps = std.vector[FlexMazeIdx]()

    # first pin selection algorithm
    worker.routeNet_setSrc(unConnPins, mazeIdx2unConnPins, connComps, ccMazeIdx1, ccMazeIdx2, centerPt)

    path = std.vector[FlexMazeIdx]() #  astar must return with >= 1 idx
    isFirstConn = True
    while not unConnPins.empty():
        
        worker.mazePinInit()
        nextPin = worker.routeNet_getNextDst(ccMazeIdx1, ccMazeIdx2, mazeIdx2unConnPins)
        path.clear()

        #if worker.gridGraph.search(connComps, nextPin, path, ccMazeIdx1, ccMazeIdx2, centerPt):
        #if search(worker.gridGraph, connComps, nextPin, path, ccMazeIdx1, ccMazeIdx2, centerPt):
        if plotGraph:
            plotMyGridGraph(worker.gridGraph)

        if solveRoutingProblem(worker.gridGraph, connComps, nextPin, path, ccMazeIdx1, ccMazeIdx2, centerPt):
          worker.routeNet_postAstarUpdate(path, connComps, unConnPins, mazeIdx2unConnPins, isFirstConn) # remove nextPin from unConnPins
          worker.routeNet_postAstarWritePath(net, path, realPinAPMazeIdx)
          worker.routeNet_postAstarPatchMinAreaVio(net, path, areaMap)
          isFirstConn = False
        else:
          return False
    worker.routeNet_postRouteAddPathCost(net)
    return True


def routeNets(worker, nets):
    try:
        for n in nets:
            net = cppyy.bind_object(n, 'fr::drNet')
            worker.mazeNetInit(net)
            routeNet(worker, net)
            worker.mazeNetEnd(net)
            if stopAfterFirstNet:
                break
    except Exception as e:
        traceback.print_exc()
        os.exit_(1)

if __name__ == "__main__":
     # Create the parser
    parser = argparse.ArgumentParser(description="Set global variables for the program.")

    # Add arguments with default values
    parser.add_argument("--lef_file", default="./designs/ispd18.lef", help="Path to the LEF file")
    parser.add_argument("--def_file", default="./designs/toy1.def", help="Path to the DEF file")
    parser.add_argument("--guide_file", default="./designs/toy1.guide", help="Path to the GUIDE file")
    parser.add_argument("--out_file", default="out.def", help="Path for the output DEF file")
    parser.add_argument("--out_maze_file", default="maze.log", help="Path for the output maze log file")
    parser.add_argument("--agent_type", default="SearchAgent", help="the agent type to use")
    parser.add_argument("--agent_args", default="fn=dfs,prob=RoutingProblem", help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_argument("--plot_graph", action="store_true", help='show graph')

    # Parse the arguments
    args = parser.parse_args()

    gbl.LEF_FILE = args.lef_file
    gbl.DEF_FILE = args.def_file
    gbl.GUIDE_FILE = args.guide_file
    gbl.OUT_FILE = args.out_file
    gbl.OUT_MAZE_FILE = args.out_maze_file
   
    agentType = loadAgent(args.agent_type, True)
    agentArgs = parseAgentArgs(args.agent_args)

    fr.FlexDRWorker.routeNetsExt = routeNets
    if args.plot_graph:
        plotGraph = True

    tr = fr.FlexRoute()
    #tr.main()
    tr.init()
    tr.prep()
    tr.ta()
    #tr.dr();
    dr = fr.FlexDR(tr.getDesign())
    dr.init()
    stopAfterFirstNet = True
    dr.searchRepair(0, 7, 0, 1, gbl.DRCCOST, 0,  0, 0, True, 1, True, 0);
    tr.endFR()

