"""
World - Central class driving the simulation

Created on 01.04.2011

@author: eckhartarnold

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import random

from Agent import PublicInfo, SI, SFI
from Statistics import RoundStatistics
from Institution import SanctioningInstitution, SanctionFreeInstitution


class WorldInfo(object):
    """Contains publically available information about the world as well as
    some abstract methods to query information about other agents.
    
    Variables:
        game           - PublicGoodsGameBase object: that defines the game
                         to be played        
        roundNr        - int: number of current round, starting with one
        maxRounds      - int: maximal number of rounds
        numAgents      - int: total number of agents/persons 
                              in the simulation/experiment
        contribTokens  - int: maximum number of tokens that can be contributed
                         every round
        sanctionTokens - int: maximum number of tokens that can be used for
                         sanctioning every round.
        anonymizedInfos - tuple of PublicInfo objects. Contains the publically 
                          acessible information about the agents from the 
                          previous round. The order of the list is randomly
                          changed during each round so that agents cannot be
                          tracked by other agents.
        statistics      - RoundStatistics object: gives access to statistical
                          data about the anonymized agent info list.
    """
    
    def __init__(self):
        self.game = None        
        self.roundNr = 0
        self.maxRounds = 0  # are agents supposed to know this?
        self.numAgents = 0
        self.contribTokens = 0
        self.sanctionTokens = 0
        self.anonymizedInfos = tuple()
        self.statistics = RoundStatistics(tuple(), -2)

    def asHTMLSnippet(self):
        """Returns a human readably HTML representation of the data."""
        assert False, "Not yet implemented!"
           
    def anonymizedIndex(self, agent):
        """Returns the index of the 'agent' in the anonymized list for 
        this round.
        """
        raise NotImplementedError



class World(WorldInfo):
    """The world object ties the other objects (agents, institutions, game) 
    together and runs the simulation.
    
    Variables:
        agents              - list of AgentBase objects: the agents in the game.
                              these can be either humans or different computer 
                              strategies  
        anonymized          - list of AgentBase objects: the same agents as in
                              the 'agents' list, but in randomly sorted order.
                              The order of the 'anonymized' list is re-shuffled
                              before every new round of the game
        __anonymizedIndices   - dictionary agent->int: a dictionary that tells
                              the index of an agent in the 'anonymized' list
        SI                  - SanctioningInstitution object: the sanctioning
                              institution
        SFI                 - SanctionFreeInstitution object: the sanctioning 
                              free institution
        chronicles          - ChroniclesInterface object: writing of the
                              simulation history and evaluating of the 
                              simulation data
    """

    def __init__(self, chronicles):
        WorldInfo.__init__(self)

        self.roundNr = -1
        self.agents = []
        self.anonymized = [] # randomly ordered list of agents
        self.__anonymizedIndices = {}    
        self.SI = SanctioningInstitution()
        self.SFI = SanctionFreeInstitution()
        self.chronicles = chronicles

    def setup(self, agents, game, maxRounds, contribTokens, sanctionTokens):
        """Sets the simulation up."""
        assert self.roundNr < 0, "Simulation has already started!"
        assert maxRounds >= 1
        assert contribTokens >= 1
        assert sanctionTokens >= 1
        assert len(agents) >= 2, "need at least two agents!"
        
        self.game = game
        self.agents = agents
        self.anonymized = agents[:] # shallow copy of agents
        for agent in self.agents:           
            agent.connect(self)
        self.SI.connect(self)
        self.SFI.connect(self)        
            
        self.numAgents = len(self.agents)
        self.maxRounds = maxRounds
        self.roundNr = -1
        self.contribTokens = contribTokens
        self.sanctionTokens = sanctionTokens
        
        self.chronicles.setupComplete(self)
        
        
    def run(self):
        """Runs the simulation."""
        assert self.roundNr < 0 , "Simulation is already running, " \
                + "already finished or was never set up properly!"
        
        self.roundNr = 0
        while self.roundNr < self.maxRounds:
            self.nextRound()

        
    def nextRound(self):
        """Runs one complete round of the simulation and increses the 
        round counter  A full round includes all three stages: institution
        choice, voluntary contribution and stanctioning."""
        assert self.roundNr < self.maxRounds
        
        random.shuffle(self.anonymized)
        for i, agent in enumerate(self.anonymized):
            self.__anonymizedIndices[agent] = i
        self.anonymizedInfos = tuple(PublicInfo(agent) for agent in self.anonymized)            
        self.statistics = RoundStatistics(self.anonymizedInfos, self.roundNr-1)
            
        self.institutionChoiceStage()
        self.contributionStage()
        self.sanctioningStage()
        
        # notify agents that the round is completed
        for agent in self.agents: 
            agent.roundComplete()  
            
        self.chronicles.roundComplete()        
        
        self.roundNr += 1

    
    def institutionChoiceStage(self):
        """Performs the institution choice stage: Agents are asked to choose
        either the sanctioning or the sanction free institution and are added
        into the respective lists."""
        self.SI.members = []
        self.SFI.members = []
        for agent in self.agents:
            institution = agent.chooseInstitution()
            if institution == SI:
                self.SI.members.append(agent)
                agent.allegiance = SI
            elif institution == SFI:
                self.SFI.members.append(agent)
                agent.allegiance = SFI
            else:
                raise ValueError


    def contributionStage(self):
        """Performs the contribution stage: Agents are asked to make a 
        contribution.
        """
        self.SI.contributionStage()
        self.SFI.contributionStage()
        
    
    def sanctioningStage(self):
        """Performs the sanctioning stage.
        """
        self.SI.sanctioningStage()
        self.SFI.sanctioningStage()
                   
    
    def anonymizedIndex(self, agent):
        """Returns the index of the 'agent' in the anonymized list for 
        this round.
        """
        return self.__anonymizedIndices[agent]

