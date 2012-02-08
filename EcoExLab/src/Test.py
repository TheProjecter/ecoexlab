"""Test

Created on 07.04.2011

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

from random import randint, random
import webbrowser

from Agent import AgentBase, AgentInfo, SI, SFI
from Game import PublicGoodsGame
from World import World
from Statistics import median, mean
from Chronicles import Chronicles
from Report import Report

       

###############################################################################
#
#  contribute mixins classes
#
###############################################################################

class RandomContribution(AgentBase):
    def contribute(self, tokens):
        return randint(0, tokens)
    

class ModerateEgoistContribution(AgentBase):
    def contribute(self, tokens):
        if self.world.roundNr == 0:
            return randint(0, tokens/2)
               
        stats = self.world.statistics
        if self.history[-1].allegiance != self.allegiance:
            # just changed the allegiance: if in Rome do as the Romans do
            return stats.value(mean, self.allegiance, "contribution")
        
        if self.allegiance == SFI:
            mProfit = stats.value(median, SFI, "profit")
            mContrib = stats.value(mean, SFI, "contribution")            
            if mProfit >= self.profit:
                return self.contribution*2/3
            elif mProfit < self.profit:
                return max(int(mContrib), self.contribution)
                
        else:
            if self.receivedSanct < 0:
                contribList = stats.valueList(SI, "contribution")
                contribList.remove(self.contribution)
                pcr = self.world.game.perCapitaReturn(contribList + [tokens],
                                                      tokens)
                if pcr > self.netProfit:
                    return tokens
                else:
                    return self.contribution
            else:
                if self.receivedSanct > 0:
                    return self.contribution
                else:
                    return self.contribution * 9 / 10              

                
class SimpleHeuristicsContribution(AgentBase):
    def contribute(self, tokens):
        if self.world.roundNr == 0:
            return randint(tokens/2, tokens)        
        
        if self.history[-1].allegiance != self.allegiance:
            return self.world.statistics.value(mean, self.allegiance, "contribution")        
        
        if self.allegiance == SI:
            if self.netProfit > self.contribution:
                return self.contribution
            else:
                if self.receivedSanct < 0:
                    return min(tokens, self.contribution*2)
                else:
                    return self.contribution/2
                
        else: 
            return self.contribution/2
            

            
###############################################################################
#
# sanction mixin classes
#
###############################################################################            

class NoSanctions(AgentInfo):
    def sanction(self, tokens, agentList):
        return ({}, {})    


def selectForSanction(dictionary, tokens, infos, otherIndices, selector, 
                      strength):
    """Adds the nr from agents from 'agentList' to the dictionary with a
    sanction value of 'strength' (or less if not enough tokens are available)
    if 'selector' returns True for the agent. Returns the number of 
    tokens left.""" 
    baddies = set([i for i in otherIndices if infos[i].allegiance == SI \
                   and selector(infos[i].contribution)])
    if len(baddies) > 0:
        punishment = max(1, min(strength, tokens / len(baddies)))
        for i in otherIndices:
            if i in baddies and i not in dictionary and tokens >= punishment:
                dictionary[i] = punishment
                tokens -= punishment
    return tokens

class StepwiseSanctions(AgentBase):
    def sanction(self, tokens, otherAgentIndices):
        initialTokens = tokens
        positive = {}
        negative = {}
        q1 = self.world.contribTokens / 4
        q2 = self.world.contribTokens * 2 / 4
        q3 = self.world.contribTokens *3 / 4 
        q4 = self.world.contribTokens
        infos = self.world.anonymizedInfos
        tokens = selectForSanction(negative, tokens, infos, otherAgentIndices,    
                                   lambda c: c < q1, 2)
        tokens = selectForSanction(negative, tokens, infos, otherAgentIndices,
                                   lambda c: c >= q1 and c < q2, 1)
        
        tokens = tokens/3 # commendations are considered less important
        if tokens < initialTokens/3:
            tokens = selectForSanction(positive, tokens, infos, 
                                       otherAgentIndices, lambda c: c == q4, 2)
            tokens = selectForSanction(positive, tokens, infos, 
                                       otherAgentIndices, 
                                       lambda c: c >= q3 and c < q4, 1)
            
        tokens = selectForSanction(negative, tokens, infos, otherAgentIndices,                       
                                   lambda c: c >= q2 and c < q3, 1)        
        
        return (positive, negative)


###############################################################################
#
# choose institution mixin classes
#
############################################################################### 


class RandomChoice(AgentBase):
    def chooseInstitution(self):
        if randint(0,1):
            return SI
        else:
            return SFI
    

class ProfitBasedChoice(AgentBase):
    def chooseInstitution(self):
        if self.world.roundNr == 0:
            return SI if randint(0,1) else SFI
        else:
            sfiProfit = self.world.statistics.value(median, SFI, "profit")
            siProfit = self.world.statistics.value(median, SI, "profit")
            if sfiProfit > siProfit and random() < 0.3:
                return SFI
            elif sfiProfit < siProfit and random() < 0.3:
                return SI
            else:
                return self.allegiance    
    
    
###############################################################################
#
# agent classes
#
###############################################################################    

class Random(RandomContribution, NoSanctions, RandomChoice, AgentBase):
    pass

class ModerateEgoist(ModerateEgoistContribution, NoSanctions, ProfitBasedChoice, AgentBase):
    pass

class SimpleHeuristics(SimpleHeuristicsContribution, NoSanctions, ProfitBasedChoice, AgentBase):
    pass

class EgoistPunisher(StepwiseSanctions, ModerateEgoist, AgentBase):
    pass

class SimpleHeuristicsPunisher(StepwiseSanctions, SimpleHeuristics, AgentBase):
    pass


def Simulation(fileName):
    chronicles = Chronicles("Test Simulation", "Eckhart Arnold", 
                            "A Test of the 'Augmented Experiment' Prototype with a simulation.")
    world = World(chronicles)
    agents = [Random() for i in range(2)] + \
             [ModerateEgoist() for i in range(10)] + \
             [EgoistPunisher() for i in range(10)] + \
             [SimpleHeuristics() for i in range(10)] + \
             [SimpleHeuristicsPunisher() for i in range(10)]
             
    world.setup(agents, PublicGoodsGame(1.6), 30, 20, 20)
    world.run()
    #report = Report(chronicles)
    with open(fileName, "w") as f:
        f.write(chronicles.toJSON())

def readChroniclesTest(fileName):
    with open(fileName, "r") as f:
        s = f.read()
        chronicles = Chronicles()
        chronicles.fromJSON(s)    

def reportTest(fileName):
    with open(fileName, "r") as f:
        s = f.read()
        chronicles = Chronicles()
        chronicles.fromJSON(s)
        report = Report(chronicles)
        report.image_file_types = [".png"]
        report.htmlReport("../test/report.html")
        webbrowser.open("../test/report.html")

if __name__ == "__main__":
    print("Test simulation...")
    Simulation("../test/Test.json")
    print("Simulation finished. Now preparing report...")
    readChroniclesTest("../test/Test.json")
    reportTest("../test/Test.json")
    print("finished.")
