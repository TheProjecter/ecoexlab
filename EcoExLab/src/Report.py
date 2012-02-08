"""Report    - Reporting of experiment results in human readable form.

Created on 10.04.2011

@author: eckhart

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

import os, webbrowser
import numpy
from Statistics import SI_MEMBERS, SFI_MEMBERS, AV_CONTRIB_SI, AV_CONTRIB_SFI, \
        HIGH_CONTRIBUTORS, FREE_RIDERS, PAYOFF_HC, PAYOFF_FR, NO_PUNISH_HC, \
        PUNISH_HC, PAYOFF_NOP_HC, PAYOFF_P_HC, AGENT_STATS, AGENT_CLASS_STATS, \
        MEAN, DEVIATION, AG_SI, AG_SFI, AG_CONTRIB, AG_SANCT, AG_PAYOFF, \
        AG_PUNISH, AG_COMMEND
from Chronicles import Chronicles, TITLE, DATE, EXPERIMENTERS, DESCRIPTION, KEYS
from Plotting import Plotter




class ReportPage(object):
    """Class that helps generating an html report. Takes care of creating
    a table of contents and the like. Currently supports two levels of 
    sections and subsections.
    """
    def __init__(self):
        """Creates a new report page object."""
        self.top = []
        self.menu = []
        self.sections = [] # list of lists
        self.anchor = 1
        self.inSubSection = False

    def addTop(self, html):
        """Adds some html code to the top section before the menu."""
        self.top.append(html)
        
    def section(self, name):
        """Adds a new section to the page.
        """
        anc = "anchor_"+str(self.anchor)
        self.anchor += 1
        if self.inSubSection:
            self.menu.append('</ol>')
            self.inSubSection = False
        self.menu.append('<li><a href="#'+anc+'">'+name+'</a></li>')
        self.sections.append(['<h2 id="'+anc+'">'+name+'</h2>'])
        
    def subsection(self, name):
        """Adds a new subsection to the page.
        """
        if not self.inSubSection:
            self.menu.append('<ol>')
            self.inSubSection = True        
        anc = "anchor_"+str(self.anchor)
        self.anchor += 1
        self.menu.append('<li><a href="#'+anc+'">'+name+'</a></li>')
        self.sections.append(['<h2 id="'+anc+'">'+name+'</h2>'])        
        
        
    def add(self, html):
        """Adds some html code to the main part of the page (under the current
        section)."""
        self.sections[-1].append(html)
                
    def writeToDisk(self, path):
        """Writes the html page to the file 'path'."""
        with open(path, "w") as f:
            f.write('<html>\n<body>\n')
            
            f.write('\n'.join(self.top))
            
            f.write('<hr  id="menu" />\n')
            f.write('<ol>')
            f.write('\n'.join(self.menu))
            if self.inSubSection:
                f.write('</ol>')
            f.write('</ol>')              
            f.write('<hr />\n<br />\n')                    

            for section in self.sections:
                section.append('<div  style="text-align:right" ><a href="#menu">top^</a></div>')
                f.write('\n'.join(section))
            
            f.write('</body>\n</html>\n')



def PC(data):
    "Converts ratio values (0-1) into percentage values (0-100)."
    if isinstance(data, numpy.ndarray):
        return data*100.0
    else:
        return numpy.array(data)*100.0   



class Report(object):
    """Generates human readable reports from experiment statistics.
    """
    
    def __init__(self, chronicles):
        """Initializes a new Report object with an ExperimentStatistics
        object."""
        self.chronicles = chronicles
        self.image_file_types = [".png", ".eps"] #, ".pdf", ".svg"]
        
    def plot_choice_contrib(self, results, imageFilePath):
        """Plots a graph that depcits the institution choice and the
        contributions of the players/agents from 'results' to one
        or more image files, taking 'imageFilePath' as base name.
        """
        plotter = Plotter(imageFilePath, self.image_file_types, "right")
        plotter.beginDoublePlot("Period",
                "Percentage in total subject population", 
                "Contribution in percent of endowment", 
                (0, self.chronicles.world.maxRounds), 
                (0,100), (0,100))    
        data = PC([results[SI_MEMBERS], results[SFI_MEMBERS]])
        plotter.barPlot([SI_MEMBERS, SFI_MEMBERS], data, yaxis = "left")               
        plotter.linePlot([AV_CONTRIB_SI], PC([results[AV_CONTRIB_SI]]), yaxis = "right")
        plotter.linePlot([AV_CONTRIB_SFI], PC([results[AV_CONTRIB_SFI]]), yaxis = "right")
        plotter.endPlot()
        
    def plot_behavior_payoff(self, results, imageFilePath):
        """Plots a graph that depicts the behavior and the
        payoff of the players/agents from 'results' to one
        or more image files, taking 'imageFilePath' as base name.
        """        
        plotter = Plotter(imageFilePath, self.image_file_types, "right")
        plotter.beginDoublePlot("Period", 
                "Percentage in total subject population", 
                "Payoffs in MUs", 
                (0, self.chronicles.world.maxRounds), 
                (0,100), (30,60))    
        data = PC([results[FREE_RIDERS], results[HIGH_CONTRIBUTORS]])
        plotter.barPlot([FREE_RIDERS, HIGH_CONTRIBUTORS], data, yaxis = "left")               
        plotter.linePlot([PAYOFF_HC], [results[PAYOFF_HC]], yaxis = "right")
        plotter.linePlot([PAYOFF_FR], [results[PAYOFF_FR]], yaxis = "right")
        plotter.endPlot()
        
    def plot_payoff_punishment(self, results, imageFilePath):
        """Plots a graph that depicts the payoff and number of punishers
        and non-punishers from the 'results' to one or more image files
        at 'imageFilePath'.
        """    
        plotter = Plotter(imageFilePath, self.image_file_types, "right",
                          condense_factor = 5)
        plotter.beginDoublePlot("Periods", 
                "Percentage of high contributers in SI", 
                "Payoffs in MUs", 
                (0, self.chronicles.world.maxRounds), 
                (0,100), (30,60))
        data = PC([results[PUNISH_HC], results[NO_PUNISH_HC]])
        plotter.barPlot([PUNISH_HC, NO_PUNISH_HC], data, yaxis = "left")        
        plotter.linePlot([PAYOFF_NOP_HC], [results[PAYOFF_NOP_HC]], yaxis = "right")            
        plotter.linePlot([PAYOFF_P_HC], [results[PAYOFF_P_HC]], yaxis = "right")
        plotter.endPlot()
        
    def plot_agent_payoff(self, stats, imageFilePath, deviation = None):
        """Plots the agent statistics for either a single agent or for a group
        of agents."""
        plotter = Plotter(imageFilePath, self.image_file_types, "right")        
        plotter.beginDoublePlot("Period", 
                "Percentage total agent class", 
                "Payoffs in MUs", 
                (0, self.chronicles.world.maxRounds), 
                (0,100), None)
        data = PC([stats[AG_SI], stats[AG_SFI]])
        plotter.barPlot([AG_SI, AG_SFI], data, yaxis = "left")
        if deviation: 
            error = deviation[AG_PAYOFF]
        else:
            error = None
        plotter.linePlot([AG_PAYOFF], stats[AG_PAYOFF], error , "right")
        plotter.endPlot()
        
    def plot_agent_contrib(self, stats, imageFilePath, deviation = None):
        """Plots the contributions, sanctions and received punishements
        or commendations of an agent."""
        plotter = Plotter(imageFilePath, self.image_file_types, "right")
        plotter.beginDoublePlot("Period",
                "Coercions received", 
                "Contribs/Sanctions in percent of endowment", 
                (0, self.chronicles.world.maxRounds), 
                None, (0,100))
        if deviation:
            error = [deviation[AG_PUNISH], deviation[AG_COMMEND]]
        else:
            error = None   
        plotter.barPlot([AG_PUNISH, AG_COMMEND],
                        [stats[AG_PUNISH], stats[AG_COMMEND]],
                        errorBars = None, yaxis = "left") # graph gets too confusiung if errorBars are plotted here
        if deviation:
            error = PC([deviation[AG_CONTRIB], deviation[AG_SANCT]])
        else:
            error = None
        plotter.linePlot([AG_CONTRIB, AG_SANCT], 
                         PC([stats[AG_CONTRIB], stats[AG_SANCT]]), 
                         errorBars = error, yaxis = "right")
        plotter.endPlot()
        
               
    def infoParagraph(self, keyword, info):
        """Returns the entry associated with 'keyword' from the info 
        dictionary as HTML code formatted as a single paragraph."""
        if keyword in info.keys():
            return('<p><i>'+keyword+'</i> : ' + info[keyword] + '</p>\n')
        else:
            return ''
        
    def infoTable(self, keywordList, info):
        """Returns the entries from dictionary 'info' listed in 'keywordList' 
        as HTML Table."""
        table = ['<table border="0" cellspacing="10" summary="parameters">']
        valid_keys = info.keys()
        for kw in keywordList:
            if kw in valid_keys:
                entry = info[kw]
                if isinstance(entry, list) or isinstance(entry, tuple):
                    entry = ", \n".join(entry)
                else:
                    entry = str(entry)
                table.append('<tr><td><i>' + kw + '</i> : </td>'+\
                             '<td>' + entry + '</td></tr>')
        table.append('</table>')
        return "\n".join(table)
     
        
    def htmlReport(self, path):
        """Stores an html report. 'path' is the complete path and file name 
        of the main page. All intermediate directories will be created, 
        if non existent.
        """              
        
        if not path.lower().endswith(".html"):
            path += ".html"
        imgDir = os.path.splitext(path)[0]
        if not os.path.isdir(imgDir):
            os.mkdir(imgDir)
        
        info = self.chronicles.info()
        results = self.chronicles.evaluation()
               
        page = ReportPage()
        
        if TITLE in info.keys(): page.addTop('<h1>'+info[TITLE]+'</h1>')
        page.addTop(self.infoParagraph(DATE, info))
        page.addTop(self.infoParagraph(EXPERIMENTERS, info))
        page.addTop(self.infoParagraph(DESCRIPTION, info))
        page.addTop('<hr />\n')
        page.addTop(self.infoTable(KEYS, info))
           
        page.section("Institution Choice and Contributions")
        imgPath = os.path.join(imgDir, "choice_contrib.png")
        self.plot_choice_contrib(results, imgPath)
        page.add('<p><img src="'+imgPath+'"></p>\n')
            
        page.section("Behavioral Patterns and Payoff")
        imgPath = os.path.join(imgDir, "behavior_payoff.png")
        self.plot_behavior_payoff(results, imgPath)
        page.add('<p><img src="'+imgPath+'"></p>\n')
            
        page.section("Impact of Punishment on Payoff")
        imgPath = os.path.join(imgDir, "impact_punishment.png")
        self.plot_payoff_punishment(results, imgPath)         
        page.add('<p><img src="'+imgPath+'"></p>\n')             
        
#        page.section("Agent Class Statistics")
#        for className, stats in results[AGENT_CLASS_STATS].items():
#            page.subsection(className + " Class Statistics")
#            
#            imgPath = os.path.join(imgDir, className.strip()+"_payoff.png")
#            self.plot_agent_payoff(stats[MEAN], imgPath, stats[DEVIATION])
#            page.add('<p><img src="'+imgPath+'"></p>\n')
#            
#            imgPath = os.path.join(imgDir, className.strip()+"_contrib.png")
#            self.plot_agent_contrib(stats[MEAN], imgPath, stats[DEVIATION])
#            page.add('<p><img src="'+imgPath+'"></p>\n')            
            
        page.section("Detailed Agent Statistics")
        items = results[AGENT_STATS].items()
        items.sort()
        lastName = ""
        for name, stats in items:
            currentName = name[name.find(".")+1:]
            if currentName == lastName:
                continue
            else:
                lastName = currentName
            page.subsection(name + " Statistics")
            
            imgPath = os.path.join(imgDir, name.strip()+"_payoff.png")
            self.plot_agent_payoff(stats, imgPath)
            page.add('<p><img src="'+imgPath+'"></p>\n')
            
            imgPath = os.path.join(imgDir, name.strip()+"_contrib.png")
            self.plot_agent_contrib(stats, imgPath)
            page.add('<p><img src="'+imgPath+'"></p>\n') 
        
        page.writeToDisk(path)



def selftest():
    with open("../test/Test.json", "r") as f:
        s = f.read()
        chronicles = Chronicles("Report.selftest()", "Eckhart Arnold", 
                                "Self-test of the Report.py module with artificially generated data.")
        chronicles.fromJSON(s)
        report = Report(chronicles)
        report.htmlReport("../test/report.html")
        webbrowser.open("../test/report.html")
            
if __name__ == "__main__":
    selftest()
                
    