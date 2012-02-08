"""Institution - Classes that model tha sanctioning and the sanction 
free institution.

Created on 05.04.2011

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

from Agent import validateSanctions


class Institution(object):
    """Abstract base class for institutions.
    
    Variables:
        membersList     - list of Agent objects: the current members 
                          of this institutions. This variable is
                          manipulated by the world object directly
    """
    
    def __str__(self):
        return self.__class__.__name__
    
    def __init__(self):
        self.members = []
        self.world = None
        
    def connect(self, worldInfo):
        self.world = worldInfo
    
    def contributionStage(self):
        """Asks the members for contributions. Records the
        contributions in the agent's info record. Determines the agent's
        profits."""
        assert self.world, "Institution not connected to a world!"
        if len(self.members) == 0: return
        
        contribsList = []
        for agent in self.members:
            contrib = agent.contribute(self.world.contribTokens)
            if contrib < 0 or contrib > self.world.contribTokens:
                raise ValueError(contrib, str(agent))
            agent.contribution = contrib
            contribsList.append(contrib)
            
        pcr = self.world.game.perCapitaReturn(contribsList, 
                                              self.world.contribTokens)
        for agent in self.members:
            agent.profit = pcr + self.world.contribTokens - agent.contribution
            agent.account += agent.profit

    def sanctioningStage(self):
        """Abstract method for the sanctioning stage of the experiment/
        simulation."""
        raise NotImplementedError
    


class SanctionFreeInstitution(Institution):
    """Class for the sanction free institution."""
    
    def sanctioningStage(self):
        """Simply add the sanctioning tokens to the agent's
        account (sanction free).
        """
        assert self.world, "Institution not connected to a world!"
        
        for agent in self.members:
            agent.sanctPositive = {}
            agent.sanctNegative = {}
            agent.receivedSanct = 0
            agent.commendations = 0
            agent.punishments = 0         
            agent.account += self.world.sanctionTokens
        
        

class SanctioningInstitution(SanctionFreeInstitution):
    """Class for the sanction free institution."""
    
    @staticmethod
    def punishment(tokens):
        """Returns the punishment impact for the given number of tokens."""
        return -3 * tokens
    
    @staticmethod
    def commendation(tokens):
        """Returns the commendation impact for the given number tokens."""
        return tokens
    
    def sanctioningStage(self):
        """Ask the members who they'd like to sanction and
        then sanction members accordingly.
        """
        assert self.world, "Institution not connected to a world!"
        if len(self.members) == 0: return
        if self.world.roundNr <= 0:
            super(SanctioningInstitution, self).sanctioningStage()
            return
                        
        # mapping from anonymized agent index to agent object
        anonymizedMembersDict = dict([(self.world.anonymizedIndex(ag), ag) \
                                      for ag in self.members])
        indexMap = dict([(self.world.anonymizedIndex(ag), i) \
                         for i,ag in enumerate(self.world.agents)])
        
        for agent in self.members:
            agent.receivedSanct = 0
            agent.commendations = 0
            agent.punishments = 0
            agent.account += self.world.sanctionTokens
        
        for agent in self.members:
            otherAgentIndices = list(anonymizedMembersDict.keys())
            otherAgentIndices.remove(self.world.anonymizedIndex(agent))
            
            positive, negative = agent.sanction(self.world.sanctionTokens, 
                                                otherAgentIndices)
            if not validateSanctions(positive, negative, 
                                self.world.sanctionTokens, otherAgentIndices): 
                raise ValueError(positive, negative, otherAgentIndices, 
                               sum(positive.values()) + sum(negative.values()))    
            agent.account += self.world.sanctionTokens - agent.sanctioning
            agent.sanctPositive = dict([(indexMap[i], v) \
                                        for i,v in positive.items()])
            agent.sanctNegative = dict([(indexMap[i], v) \
                                        for i,v in negative.items()])           

            for k,v in negative.items():
                ag = anonymizedMembersDict[k]          
                ag.punishments += v
                impact = self.punishment(v)
                ag.receivedSanct += impact
                ag.account += impact 
                
            for k,v in positive.items():
                ag = anonymizedMembersDict[k]
                ag.commendations += v
                impact = self.commendation(v)
                ag.receivedSanct += impact
                ag.account += impact
