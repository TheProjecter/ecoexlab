"""AgentInterface - The questions that an agent (human or computer) 
must answer.

The agent interface can be implementes by computer agent classes 
with a programmed strategy or it can be implemented by a class
conntecting to a user interface that asks a human agent for her or
his choices.

Created on 30.03.2011

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


# agent allegiance keys:
SI, SFI, ALL = "SI", "SFI", "ALL"

#SANCTION = "SI"         # sanction institution
#SANCTION_FREE = "SFI"   # sanction free institution


###############################################################################
#
#  sanctioning support functions
#
###############################################################################

def validateSanctions(positive, negative, maxTokens, indices):
    """Returns true, if not more than 'maxTokens' have been
    used for sanctioning and only agents listed in indices have 
    been sanctioned."""
    indexError = ( ( set(negative.keys()) \
                   | set(positive.keys()) ) - set(indices)) != set() 
    return not indexError and \
           sum(positive.values()) + sum(negative.values()) <= maxTokens



###############################################################################
#
#  AgentInfo
#
###############################################################################
    
class AgentInfo(object):
    """Contains all variables that describe the state and behavior of an agent 
    in a particular round.
    
    The functionality of the AgentInfo object is not directly integrated into 
    the AgentBase class (defined below) because this makes handling of the 
    agent information by the statistcs classes easier as well as loading
    and storing the simulation data. 
    
    Variables (should be considered as "read only" by descendant objects): 
        world           - WorldInfo object: the world the agent belongs to

        account         - int: the accumulated results from all the previous 
                          rounds.   
        allegiance      - string: the institution to which the agent belongs
        contribution    - int: amount of tokens that an agent contributed for
                          the provision of the public good in the last round
        profit          - int: the net profit of the agent in the voluntary
                          contribution stage, i.e. sum of tokens kept and
                          the individual benefit from the public good
        sanctPositive   - dictionary (agentNr, tokens) of positive sanctions
                          given by the agent
        sanctNegative   - dictionary (agentNr, tokens) of negative sanctions 
                          dealt out by the agent
        recievedSanct   - int: the value received from positive and negative
                          sanctioning by others (e.g.  received_positive - 3 * 
                          received negative, however, the precise formula depends
                          on the institutions)
        commendations   - int: the number of positive sanctions received by the
                          agent
        punishments     - int: the number of negative sanctions received by the
                          agent
                          
    Properties (read only):
        netProfit       - int: profit from the voluntary contribution stage 
                          plus (or minus) the received sanctions
        overallResult   - int: overall result from the voluntary contribution 
                          stage and the sanctioning stage, which is the sum of 
                          the profit from the voluntary contribution stage, the 
                          sanctions received and the sanctioning tokens
                          that were not used up.
        sanctioning     - int: total number of tokens spent for either positive 
                          sanctions or negative sanctions
    """
      
    def __init__(self, source = None, world = None, keys = None):
        """Constructor for AgentInfo. All variables are initialized with 0 or,
        if given, with the values of 'source'. 'source' can either be another
        agent or a dictionary of (variable, value) pairs or a list of values.
        classId is an identifier for the class the agent belongs to. By 
        default, i.e. if 'None' it evaluates to the class name."""
        self.world = world
            
        if isinstance(source, AgentInfo):
            for key in self.variables():
                self.__dict__[key] = source.__dict__[key]
        elif isinstance(source, dict):
            self.__dict__.update(source)
        elif isinstance(source, list) or isinstance(source, tuple):
            if keys == None:
                keys = self.variables()
            self.__dict__.update(dict(zip(keys, source))) 
        else:
            self.account, self.allegiance, self.contribution, self.profit, \
            self.sanctPositive, self.sanctNegative,\
            self.receivedSanct, self.commendations, self.punishments \
            = 0, SFI, 0, 0, {}, {}, 0, 0, 0

    @property
    def netProfit(self):
        """Returns the net profit from the voluntary contribution stage plus 
        (or minus for that matter) the received sanctions."""
        return self.profit + self.receivedSanct
    
    @property
    def overallResult(self):
        """Returns the overall result from the voluntary contribution stage and
        the sanctioning stage, which is the sum of the profit from the voluntary
        contribution stage, the sanctions received and the sanctioning tokens
        that were not used up."""
        assert self.world != None, "Agent info object not connected to world!"
        return self.netProfit + self.world.sanctionTokens - self.sanctioning
     
    @property
    def sanctioning(self):
        """Returns the total number of tokens spent for either positive 
        sanctions or negative sanctions."""
        return sum(self.sanctPositive.values()) \
               + sum(self.sanctNegative.values())

    @classmethod
    def variables(cls):
        """Returns a list of the names of all true variables of an AgentInfo 
        object in alphabetical order. (References (e.g. world) or 
        class variables are not included.)"""
        return ("account", "allegiance", "commendations", "contribution", 
                "profit", "punishments", "receivedSanct", "sanctPositive", 
                "sanctNegative")
    
    def values(self):
        """Returns the values of all true variables of the AgentInfo object 
        (except the world reference) as list that is ordered according to the
        alphabetical order of the variable names."""
        return [self.__dict__[v] for v in self.variables()]
        #return [self.allegiance, self.commendations, self.contribution, 
        #        self.profit, self.punishments, self.receivedSanct, 
        #        self.sanctioning]
  
    def asDict(self):
        """Returns the relevant agent info (true variables, no references,
        properties or world object) as dictionary."""
        return dict(zip(self.variables(), self.values())) 


assert set(AgentInfo().variables()).issubset(set(AgentInfo().__dict__.keys())),\
        "Self-Test failed: Variable names of AgentInfo do not match variables!"
    


###############################################################################
#
#  PublicInfo
#
###############################################################################


class PublicInfo(object):
    """Contains a snapshot of the publically available anonymised information 
    about a single agent.
    
        allegiance      - string: the institution to which the agent belongs
        contribution    - int: amount of tokens that an agent contributed for
                          the provision of the public good in the last round
        profit          - int: the net profit of the agent in the voluntary
                          contribution stage, i.e. sum of tokens kept and
                          the individual benefit from the public good
        recievedSanct   - int: the value received from positive and negative
                          sanctioning by others (e.g.  received_positive - 3 * 
                          received negative, however, the precise formula depends
                          on the institutions)
        commendations   - int: the number of positive sanctions received by the
                          agent
        punishments     - int: the number of negative sanctions received by the
                          agent
        netProfit       - int: profit from the voluntary contribution stage 
                          plus (or minus) the received sanctions
        overallResult   - int: overall result from the voluntary contribution 
                          stage and the sanctioning stage, which is the sum of 
                          the profit from the voluntary contribution stage, the 
                          sanctions received and the sanctioning tokens
                          that were not used up.
        sanctioning     - int: total number of tokens spent for either positive 
                          sanctions or negative sanctions
    """
    
    def __init__(self, source):
        """Initializes the object with the data from either an agent or an, 
        AgentInfo or PublicInfo object."""
        if isinstance(source, PublicInfo):
            for key in self.variables():
                self.__dict__[key] = source.__dict__[key]            
        else: # assume instance of AgentInfo
            assert isinstance(source, AgentInfo)
            sourceVariables = set(source.variables())
            for key in self.variables():
                if key in sourceVariables:
                    self.__dict__[key] = source.__dict__[key]
            self.netProfit = source.netProfit
            self.overallResult = source.overallResult
            self.sacntioning = source.sanctioning
            
    def variables(self):
        """Returns a list of the names of all variables of an PublicInfo 
        object in alphabetical order."""
        return ("allegiance", "commendations", "contribution", 
                "netProfit", "overallResult", "profit", "punishments", 
                "receivedSanct", "sanctioning")
    
    def values(self):
        """Returns the values of all variables of the PublicInfo object 
        as list that is ordered according to the alphabetical order of the 
        variable names."""
        return [self.__dict__[v] for v in self.variables()]



###############################################################################
#
#  AgentBase
#
###############################################################################


class AgentBase(AgentInfo):
    """Abstract Base class for all agents.
    
    Variables: 
        See also the AgentInfo class. All the variables there should 
        be considered as read-only by the agent object itself. They are managed
        exclusively by other objects, i.e. the world object, institutions etc. !
    
        agentId - string: uniquely identifying an agent
        classId - string: an identifier for the class the agent belongs
                  to. (By default set to self.__class__.__name__) May be 
                  overwritten in order to group agents
        history - list of AgentInfo object: records the agent's state during
                  all previous rounds of the experiment.
                     
        All Variables will be initialized with zero, except self.world (None)
        and self.allegiance (randomly either SI or SFI).
        
        To implement an agent, derive from this class and implement methods:
        chooseInstitution(), contribute() and sanction().
    """
    agent_counter = 1
    
    def __str__(self):
        return self.agentId
    
    def __init__(self):
        AgentInfo.__init__(self)
        self.classId = self.__class__.__name__        
        self.agentId = "%4i" % AgentBase.agent_counter+"."+self.__class__.__name__
        AgentBase.agent_counter += 1
        self.history = []
                
    def connect(self, worldInfo):
        """Connects the agent to the world."""
        self.world = worldInfo
      
    def roundComplete(self):
        """Notifies the agent that the current round is finished."""
        self.history.append(AgentInfo(self))
        
    # Abstract methods that must be overridden by the contrete Agent classes

    def chooseInstitution(self):
        """Returns eihter 'SI' or 'SFI' depending on whether the player choses
        the sanctioning (SI) or the sanction free (SFI) institution for the 
        next round.""" 
        raise NotImplementedError    
    
    def contribute(self, tokens):
        """Returns the number of tokens from a given income
        of 'tokens' that the agent contributes to the provision
        of a public good."""
        raise NotImplementedError
        
    def sanction(self, tokens, otherAgentIndices):
        """Returns the sanction that an agent exerts with max 'tokens'.
        Return value must be a tuple of two dictionaries (positive, negative).
        that contain the (anonymized) indices of the other 
        agents within the same institution as keys and the tokens spent for
        sanctioning as values.
        """
        raise NotImplementedError
        
