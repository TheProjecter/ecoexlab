"""Chronicles - Functions for recording the history of the experiment or
simulation and analysing its data.

Created on 04.04.2011

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


import time, json

from Agent import AgentInfo
from World import World
from Statistics import ExperimentStatistics


class ChroniclesInterface(object):
    """Interface through which the world object reports its progress.
    """
    def setupComplete(self, world):
        """Notifies the chronicles object that the world setup is complete.
        Connects chronicles object to the world object."""
        raise NotImplementedError 
    
    def roundComplete(self):
        """Notifies the chronicles of the completion of the round."""
        raise NotImplementedError
    
    def evaluation(self):
        """Evaluates the simulation or experimental data."""
        raise NotImplementedError
    
    def toJSON(self):
        """Converts the data stored in the chronicles object to a JSON string.
        """
        raise NotImplementedError
    
    def fromJSON(self, s):
        """Initializes the chronicles object with the data from a JSON string.
        """
        raise NotImplementedError


TITLE = "Title"
DATE = "Date Stamp"
EXPERIMENTERS = "Experimenters"
DESCRIPTION = "Description"

KEYS = ["Date Stamp", "Agents", "Game", "Institutions", "Number of Rounds",
        "Tokens for Contribution", "Tokens for Sanctioning"]

class Chronicles(ChroniclesInterface):
    """The standard chronicles object: Follows the simulation's or experiment's
    progress in the world object. Allows saving and(!) loading of the collected
    data in a simple JSON format. Produces a simulation statistics.
    """

    def __init__(self, title = "?", experimenters = "N.N.", description = "-"):
        ChroniclesInterface.__init__(self)
        self.world = None        
        self.rounds = []
        self.statistics = None
        self.setupInfo = { TITLE : title,
                           EXPERIMENTERS : experimenters,
                           DESCRIPTION : description }
        
    def connect(self, world):
        self.world = world
        
    def setupComplete(self, world):
        assert self.world == None, "setup already reported"
        assert world.roundNr < 0, "simulation is already running"
        
        self.world = world
        self.statistics = ExperimentStatistics(self.world.contribTokens, 
                                               self.world.sanctionTokens, 
                                               [ag.agentId for ag in world.agents],
                                               [ag.classId for ag in world.agents])
        
        self.setupInfo[DATE] = time.strftime("%Y-%m-%d %H:%M")
        
        self.setupInfo["Agents"] = [ag.agentId for ag in self.world.agents]
        self.setupInfo["Agent classes"] = [ag.classId \
                                           for ag in self.world.agents]
        self.setupInfo["Game"] = str(self.world.game)
        self.setupInfo["Institutions"] = [str(self.world.SI), str(self.world.SFI)]
        self.setupInfo["Number of Rounds"] = self.world.maxRounds
        self.setupInfo["Tokens for Contribution"] = self.world.contribTokens
        self.setupInfo["Tokens for Sanctioning"] = self.world.sanctionTokens
        self.setupInfo["Basic Variables"] = list(AgentInfo().variables())
        
        
    def roundComplete(self):
        assert self.world, "missing world object"
        assert self.setupInfo != {}, "setupComplete() must be called first"
        assert self.world.roundNr >= 0, "simulation has not even started"

        # gather a non-anonymized list of AgentInfo objects
        infoList = tuple(AgentInfo(agent) for agent in self.world.agents)
        self.rounds.append(infoList)        
        self.statistics.add(infoList, self.world.roundNr)
        
    def stats(self):
        """Returns the ExperimentStatistics object."""
        assert self.statistics, "no statistics object before world was setup"
        return self.statistics
    
    def info(self):
        """Returns a dictionary with information on the experiment setup."""
        assert self.setupInfo != {}, "setupComplete() hasn't been called"
        return self.setupInfo
        
    def evaluation(self):
        """Evaluates the simulation's or experiment's data and returns a
        report. 
        """
        assert len(self.rounds) == self.world.maxRounds, \
                "simulation is still running"
        return self.statistics.evaluation()
        
    
    def toJSON(self):
        """Converts the data stored in the chronicles object to a JSON string.
        """
        assert len(self.rounds) > 0, "no simulation has been recorded"
        r = [[ag.values() for ag in rd] for rd in self.rounds]
        d = {"Setup": self.setupInfo, "Results": r}
        return json.dumps(d, sort_keys=True, indent=2)


    def fromJSON(self, s):
        """Initializes the chronicles object with the data from a JSON string.
        """
        assert len(self.setupInfo) <= 5, "chronicles object already in use"
        
        def buildMockWorld(setupInfo, results):
            assert len(results) > 0, "no results stored in JSON file !?"
            mockWorld = World(self)
            mockWorld.contribTokens = setupInfo["Tokens for Contribution"]
            mockWorld.sanctionTokens = setupInfo["Tokens for Sanctioning"]
            mockWorld.maxRounds = setupInfo["Number of Rounds"]
            mockWorld.roundNr = mockWorld.maxRounds
            mockWorld.numAgents = len(results[0])
            return mockWorld            
               
        d = json.loads(s)                
        self.setupInfo = d["Setup"]
        variables = self.setupInfo["Basic Variables"]
        assert set(variables) == set(AgentInfo.variables()), \
                "Unmatched variables, possibly due to version update. "+\
                "Uncomment this line at your own risk!"        
        results = d["Results"]
        self.world = buildMockWorld(self.setupInfo, results)
        self.rounds = [[AgentInfo(values, self.world, variables) \
                        for values in rd] for rd in results]
        self.statistics = ExperimentStatistics(self.setupInfo["Tokens for Contribution"],
                                               self.setupInfo["Tokens for Sanctioning"],
                                               self.setupInfo["Agents"],
                                               self.setupInfo["Agent classes"])
        for i, infoList in enumerate(self.rounds):
            self.statistics.add(infoList, i)
