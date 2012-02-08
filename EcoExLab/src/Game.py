"""PublicGoodsGame - The public goods games

The agent interface can be implementes by computer agent classes 
with a programmed strategy or it can be implemented by a class
conntecting to a user interface that asks a human agent for her or
his choices.

Created on 31.03.2011

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


class PublicGoodsGameBase(object):
    """Abstract base class for public good games. Implementing classes
    must override the "protected" method '_mcpr(self, total, n)' which
    is to return the marginal per capita return for net contributions
    of 'total' and 'n' individuals. 
    """
       
    def __str__(self):
        return self.__class__.__name__
       
    def _selftest(self):
        assert self._validate(self._mcpr(0.5, 1000), 1000), \
                + "Marginal per capita return value of " \
                + "is out of the definitional bounds of a public " \
                + "goods game; must be smaller than 1 and greater than 1/n!"       
       
    def _validate(self, mcpr, n):
        """Returns true, if 'ret' is a valid per capita return within the
        bounds of a public goods game: 1 > ret > 1/n."""
        return n > 0 and (mcpr < 1 and mcpr > 1.0/n)

    def _mcpr(self, r, n):
        """Abstract method that returns the marginal per capita return of
        the public goods game.
        
        Parameters:
            r    - float 0.0 to 1.0: the average contribution ratio
            n    - the number of agents participating in the game
        """
        raise NotImplementedError

    def perCapitaReturn(self, contributions, maxContrib):
        """Returns the per capita return for the list of individual 
        'contributions'. 'max_contrib' is the highest possible contribution
        per individual."""
        n = len(contributions)                
        assert n >= 1, "Bowling alone? "                
                
        S = float(sum(contributions))                
        r = S / float(maxContrib*n)
        mcpr = self._mcpr(r, n)
                
        return mcpr*S
        
        
        
class PublicGoodsGame(PublicGoodsGameBase):
    """A public goods game defined by a marginal per capita return
    of g/n, where g > 1.0 ("gain factor") defines the 
    surplus of cooperation and n is the number of players."""
    
    def __str__(self):
        return "PublicGoodsGame(gain_factor = %f)" % (self.gain,)
    
    def __init__(self, gain_factor):
        assert 1.0 < gain_factor, "'gain_factor' " + str(gain_factor) + " <= 1.0"
        PublicGoodsGameBase.__init__(self)
        self.gain = gain_factor
        self.minN = int(gain_factor)+1
        self._selftest()
    
    def _mcpr(self, r, n):        
        return self.gain / n

