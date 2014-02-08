"""Statistics - A class that collects some statistical data for a 
list of AgentInfo objects and contains some useful toolbox methods
to evaluate lists of AgentInfo objects. 

Created on 08.04.2011

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

from Agent import SI, SFI, ALL
try:
    import numpy
    NaN = numpy.NaN
except ImportError:
    NaN = float('nan')


###############################################################################
#
#  statistical functions returning values
#
###############################################################################

def mean(values):
    """Returns the mean value of a list of values or zero if the list is 
    empty."""
    n = len(values)
    if n == 0: return 0.0
    return sum(values) / float(len(values))

def median(values):
    """Returns the median value of a list of values of zero if the list is
    empty. 
    ATTENTION: the order of the elements of the list will be
    changed by the function.
    """
    n = len(values)
    if n == 0: return 0.0
    values.sort()
    if n % 2 == 0:
        return (values[n//2-1] + values[n//2]) / 2.0
    else:
        return float(values[n//2])
    
    
###############################################################################
#
# statistical functions returning agents
#
###############################################################################    

    
def extremeAgents(infoList, valueList, cmpFunc):
    """Returns the list of agent info(s) with an extreme value in the
    value list according to the comparison function 'cmpFunc'. compFunc(a,b)
    must return 1, 0, -1 where 0 means equal, 1 means more extreme (e.g. 
    higher than) and -1 means less extreme (e.g. lower than)."""
    assert len(infoList) == len(valueList)
    l = len(valueList)
    if l > 0:
        pivot = valueList[0]
        result = [infoList[0]]
        for i in range(1, l):
            c = cmpFunc(valueList[i], pivot)
            if c > 0:
                result = [infoList[i]]
                pivot = valueList[i]
            elif c == 0:
                result.append(infoList[i])
        return result
    else:
        return []        

    
def maxAgents(infoList, valueList):
    """Returns a list containing the agent info(s) with the highest value in the
    value list."""
    return extremeAgents(infoList, valueList, lambda a,b: (a > b) - (a < b))


def minAgents(infoList, valueList):
    """Returns a list containing the agent info(s) with the lowest value in the
    value list."""
    return extremeAgents(infoList, valueList, lambda a,b: (a < b) - (a > b))


        
def nearestAgents(infoList, valueList, pivotValue):
    """Returns a list of those AgentInfo objects for which the value in the 
    value list either contains the pivot value or, if no value matches the 
    pivot value, the list of objects which have the highest value below or 
    the lowest value above the pivot value (in this order).
    """
    assert len(infoList) == len(valueList)
    l = len(valueList)
    if l > 0:
        pa = pivotValue
        pb = pivotValue        
        if pivotValue not in valueList:
            for v in valueList:
                if v < pivotValue:
                    if v > pa or pa == pivotValue:
                        pa = v
                elif v > pivotValue:
                    if v < pb or pb == pivotValue:
                        pb = v
        head = [infoList[i] for i in range(l) if valueList[i] == pa]
        tail = [infoList[i] for i in range(l) if valueList[i] == pb]
        return head + tail            
    else:
        return []

    
def closestAgents(infoList, valueList, pivotValue):
    """Returns a list of those AgentInfo objects for which the value in the 
    value list is closest to the pivot value. If the value list contains
    the pivot value, only agents with the pivot value will be returned.
    """
    assert len(infoList) == len(valueList)
    l = len(valueList)
    if l > 0:
        minDelta = abs(pivotValue - valueList[0])
        result = [infoList[0]]
        for i in range(l):
            delta = abs(pivotValue - valueList[i])
            if delta < minDelta:
                result = [infoList[i]]
                minDelta = delta
            elif delta == minDelta:
                result.append(infoList[i])
        return result
    else:
        return[]
            
            
def meanAgents(infoList, valueList):
    """Returns a list containing the agent info(s) with the mean value in the
    value list. If no agents exactly match the mean value than agents closest
    to the mean will be picked."""
    return closestAgents(infoList, valueList, mean(valueList))


def medianAgents(infoList, valueList):
    """Returns a list of agent info(s) for which the value is the equal to the 
    median value of the value list or, if the value list does not contain the
    median, either the highest below or the smallest above the median value of 
    value list."""
    return nearestAgents(infoList, valueList, median(valueList))
    


###############################################################################
#
# statistics for one round
#
###############################################################################

class RoundStatistics(object):
    """A class that gathers agent data for one round of the game
    and provides toolbox methods to evaluate lists of AgentInfo objects.
    
    Variables:
        roundNr    - int: the round for which the statistics were gathered
        infoLists  - dictionary string (agent allegiance keys) -> tuples of
                     AgentInfo objects: contains agent info lists for 1)
                     all agents, 2) agents in the sanctioning institution (SI)
                     and 3) agents in the sanction free institution
    """
    
    def __init__(self, agentInfoList, roundNr):
        self.roundNr = roundNr
        self.infoLists = {ALL: agentInfoList, 
                SI: tuple(ag for ag in agentInfoList if ag.allegiance == SI),
                SFI: tuple(ag for ag in agentInfoList if ag.allegiance == SFI)}
        self.cache = {}

    def agentInfos(self, allegiance):
        """Returns a list of agent infos of either all agents or
        the agents in the sanctioning of sanction free institution.
        """
        return self.infoLists[allegiance]

    def valueList(self, allegiance, variable):
        """Returns the list of values of the agents with 'allegiance'
        have in a particular 'variable'."""
        if variable[-2:] == "()":
            return [agInfo.__getattribute__(variable)() \
                    for agInfo in self.infoLists[allegiance]]
        else:
            return [agInfo.__getattribute__(variable) \
                    for agInfo in self.infoLists[allegiance]]
        
    def value(self, func, allegiance, variable):
        """Applies the statistical function 'func' to a particular 'variable' 
        of the AgentInfo objects in the list defined by 'allegiance'. Plus: 
        Caches and returns the result! Example: s._calculate(mean, SI, PROFIT)
        returns the mean profit of the agents in the sanctioning institution.
        """
        key = str(func) + allegiance + variable
        if key in self.cache:
            return self.cache[key]
        else:
            values = self.valueList(allegiance, variable)
            result = func(values)
            self.cache[key] = result
            return result
        
    def agents(self, func, allegiance, variable):
        """Returns a tuple of AgentInfo objects that the function 'func' picks
        from the list of the agents with 'allegiance' acording to the values
        of a prticular 'variable'. 
        'func' must have the form: func(info list, value list) -> info list.
        """
        key = str(func) + allegiance + variable
        if key in self.cache:
            return self.cache[key]
        else:
            values = self.valueList(allegiance, variable)
            result = tuple(func(self.infoLists[allegiance], values))
            self.cache[key] = result
            return result
                     
    
###############################################################################
#
#  Agent Statistics
#
###############################################################################    
    
AG_SI            = "SI member"
AG_SFI           = "SFI member"
AG_CONTRIB       = "Agent's contribution"           # ratio
AG_SANCT         = "Agent's amount of sanctioning"  # ratio
AG_PAYOFF        = "Agent's payoff"                 # money units
AG_PUNISH        = "Punishments received by agent"  # ratio to number of agents
AG_COMMEND       = "Commendations received by agent" # ratio to number of agents
    
AGSTAT_KEYS = (AG_SI, AG_SFI, AG_CONTRIB, AG_SANCT, AG_PAYOFF, AG_PUNISH,
               AG_COMMEND)    
    
class AgentStatistics(object):
    """A class that collects the data of an agent throughout the 
    game, i.e. for all rounds of the game. (In contrast RoundStatistics obejcts 
    collect the data for all agents in one round.)
    
    Variables (public, but read only!):
        statistics    - a dictionary (str, numpy.array) that contains the time 
                        series of each of the variables above.
        name          - a name assigned to the agent when creating the
                        AgentStatistics object
                        
    """
    def __init__(self, infoSeries, name):
        """Initializes AgentStatistics object with the series of agent info
        objects, one for each round. 'name' is (any) name or number
        for the agent."""
        assert len(infoSeries) > 0

        self.name = name
        
        s = {}
        s[AG_SI] = [1.0 if info.allegiance == "SI" else 0.0 \
                    for info in infoSeries]
        s[AG_SFI] = [1.0 - si for si in s[AG_SI]]
        s[AG_PAYOFF] = [float(info.overallResult) for info in infoSeries]        
        s[AG_CONTRIB] = [float(info.contribution) / info.world.contribTokens\
                         for info in infoSeries]
        s[AG_SANCT] = [float(info.sanctioning) / info.world.sanctionTokens\
                         for info in infoSeries]
        s[AG_PUNISH] = [float(info.punishments) for info in infoSeries]
        s[AG_COMMEND] = [float(info.commendations) for info in infoSeries]
        for k,v in s.items():
            s[k] = numpy.array(v)        
        self.statistics = s
    

MEAN = "mean"
DEVIATION = "deviation"


class AgentClassStatistics(object):
    """A class that collects the statistical data for several agents.
    Useful when trying to evaluate the performance of all agents of a 
    particular type or group.
    
    Variables (public, read only):
        name        - a name for the agent group, assigned when creating the
                      AgentTypeStatistics object
        statistics  - a dictionary (str, dict(str, numpy.array) that contains
                      for each of the above keys another dictionary that
                      contains the mean values (key MEAN) and the 
                      standard deviation (key DEVIATION) of the respective 
                      variable.
        statsList   - a list of AgentStatistics objects from which the 
                      group statistics where compiled.
    """

    def __init__(self, agentStatisticsList, name):
        """Initializes the object with a list of agent statistics object
        with the agent statistics' list and an arbitrary class name."""
        self.name = name
        self.statsList = agentStatisticsList
        self.statistics = { MEAN: {}, DEVIATION: {}}
        for k in AGSTAT_KEYS:
            a = [s.statistics[k] for s in self.statsList]
            self.statistics[MEAN][k] = numpy.mean(a, axis=0)
            self.statistics[DEVIATION][k] = numpy.std(a, axis=0)
        
        
###############################################################################
#
# statistics for a game of several rounds
#
###############################################################################

# evaluation data keys:
SI_MEMBERS        = "Subjects choosing SI"          # ratio of all agents
SFI_MEMBERS       = "Subjects choosing SFI"         # ratio of all agents
AV_CONTRIB_SI     = "Average contribution in SI"    # ratio of endowment
AV_CONTRIB_SFI    = "Average contribution in SFI"   # ratio of endowment
HIGH_CONTRIBUTORS = "High contributers in SI"       # ratio of all agents
FREE_RIDERS       = "Free-riders in SFI"            # ratio of all agents
PAYOFF_HC         = "Average payoff of high contributors in SI"  # money units
PAYOFF_FR         = "Average payoff of free-riders in SFI"       # money units
NO_PUNISH_HC      = "High contributers & non-punishers"     # ratio of all agents
PUNISH_HC         = "High contributers & punishers"         # ratio of all agents
PAYOFF_NOP_HC     = "Average payoff of high contributers & non-punishers"   # money units
PAYOFF_P_HC       = "Average payoff of high contributers & punishers"       # money units

AGENT_STATS       = "Detailed Agent statistics"
AGENT_CLASS_STATS = "Detailed Agent class statistics"

# list of keys in a meaningful order
EXPSTAT_KEYS = (SI_MEMBERS, SFI_MEMBERS, AV_CONTRIB_SI, AV_CONTRIB_SFI, 
                HIGH_CONTRIBUTORS, FREE_RIDERS, PAYOFF_HC, PAYOFF_FR, 
                NO_PUNISH_HC, PAYOFF_NOP_HC, PAYOFF_P_HC,
                AGENT_STATS, AGENT_CLASS_STATS)

class ExperimentStatistics(object):
    """Computes data over all rounds of the simulation/experiment.
    
    Variables (protected):
        statList    - list of RoundStatistics objects, one for each round
        statistics  - dictionary with various statistical data for the whole 
                      experiment or simulation. See constant EXPSTAT_KEYS for the
                      entries of this dictionary.
        contribTokens - stores the number of tokens for contribution (needed 
                      to calculate some of the statistics)
        sanctionTokens - stores the number of tokens for sanctioning (needed
                      to calculate some of the statistis)
        agentNames   - list of strings: the name of each agent
        agentClasses - list of strings: the classId of each agent
        numAgents    - the number of agents
        agStats      - list of AgentStatistics objects, one for each agent. The
                       list will be created when calling the evaluation() 
                       method
        agClassStats - AgentStatistic for groups of Agents. The list
                       will be created when calling the evaluation() method
    """
    
    def __init__(self, contribTokens, sanctionTokens, agentNames, agentClasses):
        self.statList = []
        self.statistics = {}
        self.contribTokens = contribTokens
        self.sanctionTokens = sanctionTokens
        self.agentNames = agentNames
        self.agentClasses = agentClasses
        self.numAgents = -1
        self.agStats = []
        self.agClassStats = {}
    
    def add(self, infoList, roundNr):
        assert roundNr == len(self.statList), "wrong round number"
        assert self.statistics == {}, "evaluation already done"
        assert self.numAgents < 0 or self.numAgents == len(infoList), \
                "different number of agents"                    
        self.numAgents = len(infoList)          
        self.statList.append(RoundStatistics(infoList, roundNr))
    
    def roundStats(self, roundNr):
        """Returns the RoundStatistics object for a specific round."""
        return self.statList[roundNr]
    
    def agentStats(self, agentNr):
        """Returns the statistics for one agent. ('agentNr' ought to be the
        position of the agent in the world agent list)."""
        assert len(self.agStats) > 0, "evaluation() must be called first."
        return self.agStats[agentNr]
        
    def agentClassStats(self, className):
        """Returns the statistcs for a group of agents."""
        assert len(self.agClassStats) > 0, "evaluation() must be called first."
        return self.agClassStats[className]
         
    def _agentEvaluation(self):
        """Creates the agent statistics (fills object variables 'agentStats' 
        and 'agGroupStats'). Returns a tuple of two statistics directories:
        (agent statistics, agent class statistics)."""
        assert len(self.statList) > 0
        
        agentLists = [[info] for info in self.statList[0].agentInfos(ALL)]
        for st in self.statList[1:]:
            infos = st.agentInfos(ALL)
            for i in range(len(agentLists)):
                agentLists[i].append(infos[i])
        self.agStats = [AgentStatistics(agList, name) \
                        for agList, name in zip(agentLists, self.agentNames)]
        
        self.agClassStats = dict([(ac, []) for ac in self.agentClasses])
        for agClass, agStat in zip(self.agentClasses, self.agStats):
            self.agClassStats[agClass].append(agStat)
        for k, v in self.agClassStats.items():
            self.agClassStats[k] = AgentClassStatistics(v, k)
        
        agsDict = dict([(n, s.statistics) \
                        for n, s in zip(self.agentNames, self.agStats)])
        agcDict = dict([(c, self.agClassStats[c].statistics) \
                        for c in self.agentClasses])      
        return (agsDict, agcDict)             
    
    def evaluation(self):
        """Calculates the global statistical data for the experiment 
        and returns it as dictionary with the entries listed in EXPSTAT_KEYS.
        """
        assert len(self.statList) > 0, "Nothing to evaluate yet"

        def highContributors(agList):
            return [ag for ag in agList \
                    if ag.contribution >= 3*self.contribTokens/4]
        def freeRiders(agList):
            return [ag for ag in agList \
                    if ag.contribution <= 1*self.contribTokens/4]        
        def nonPunishers(agList):
            return [ag for ag in agList if ag.allegiance == SI and \
                    ag.sanctioning == 0]
        def punishers(agList):
            return [ag for ag in agList if ag.allegiance == SI and \
                    ag.sanctioning > 0] 

        if self.statistics != {}:
            return self.statistics
        
        maxContrib = float(self.contribTokens)        
        HCLists = [highContributors(s.agentInfos(SI)) for s in self.statList]
        FRLists = [freeRiders(s.agentInfos(SFI)) for s in self.statList]
        PLists = [punishers(l) for l in HCLists]
        NPLists = [nonPunishers(l) for l in HCLists]        
        
        si_members = [len(s.agentInfos(SI)) / float(self.numAgents) \
                      for s in self.statList]
        self.statistics[SI_MEMBERS] = si_members
        self.statistics[SFI_MEMBERS] = [1.0 - si_members[i] \
                                        for i in range(len(si_members))]
        
        self.statistics[AV_CONTRIB_SI] = \
                [sum([ag.contribution for ag in s.agentInfos(SI)]) / \
                 (maxContrib * len(s.agentInfos(SI))) \
                 if len(s.agentInfos(SI)) > 0 else NaN for s in self.statList]
        self.statistics[AV_CONTRIB_SFI] = \
                [sum([ag.contribution for ag in s.agentInfos(SFI)]) / \
                 (maxContrib * len(s.agentInfos(SFI))) \
                 if len(s.agentInfos(SFI))> 0 else NaN for s in self.statList]
                
        self.statistics[HIGH_CONTRIBUTORS] = \
                [len(hc) / float(self.numAgents) for hc in HCLists]
        self.statistics[FREE_RIDERS] = \
                [len(fr) / float(self.numAgents) for fr in FRLists]
        self.statistics[PAYOFF_HC] = \
                [sum(ag.overallResult for ag in hc) / float(len(hc)) \
                 if len(hc) > 0 else NaN for hc in HCLists]
        self.statistics[PAYOFF_FR] = \
                [sum(ag.overallResult for ag in fr) / float(len(fr)) \
                 if len(fr) > 0 else NaN for fr in FRLists]        
                
        self.statistics[NO_PUNISH_HC] = \
                [len(nonPunishers(highContributors(s.agentInfos(SI)))) / \
                 float(len(s.agentInfos(SI))) \
                 if len(s.agentInfos(SI)) > 0 else NaN for s in self.statList]
        self.statistics[PUNISH_HC] = \
                [len(punishers(highContributors(s.agentInfos(SI)))) / \
                 float(len(s.agentInfos(SI))) \
                 if len(s.agentInfos(SI)) > 0 else NaN for s in self.statList]
                
        self.statistics[PAYOFF_NOP_HC] = \
                [sum([ag.overallResult for ag in np]) / float(len(np)) \
                 if len(np) > 0 else NaN for np in NPLists]
        self.statistics[PAYOFF_P_HC] = \
                [sum([ag.overallResult for ag in p]) / float(len(p)) \
                 if len(p) > 0 else NaN for p in PLists]
                
        agStatsDict, agClassStatsDict = self._agentEvaluation()
        self.statistics[AGENT_STATS] = agStatsDict
        self.statistics[AGENT_CLASS_STATS] = agClassStatsDict

        return self.statistics

