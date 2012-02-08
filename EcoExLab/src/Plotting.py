"""Plotting    - Wrapper for matplotlib to create graphical plots of the 
                 results of economic experiments or simulations that 
                 are essentially a game constiting of a number of rounds.

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

import os
import matplotlib, numpy
matplotlib.use("Agg")
from matplotlib import pyplot


class Plotter(object):
    """Helper class that provides plotting functions for different
    types of plots. Uses matplotlib as backend.
    """
    def __init__(self, filepath, filetypes = (".png", ".eps"), 
                 legend_location = "right", condense_factor = 0):
        """Constructor for Plotter-objets.
        
        'filepath' is the pathe where the plotted image will be stored.
        'filetypes' is a tuple of filetype extensions. For each of the
        listed filetypes an image file with the plot will be stored.
        
        If 'condense_factor' is greater 1 than 'condense_factor' number of 
        data points will be averaged into one data point. Keep in mind: 
        The number of data points on the xaxis must be divisible by 
        'condense_factor'
        
        'legend_location' can either be "right" (of the graph) or at the 
        "bottom" of the graph.        
        """
        assert isinstance(condense_factor, int), "Parameter 'condense_factor' "+\
                str(condense_factor) + " is not an integer!"         
         
        # lineStyle format: (fmtString, color, markerfacecolor)
        self.lineStyles = [('o', '-', 'black', 'white'), ('^', '-', 'black', 'black')]
        self.barColors = ["#C0C0C0", "white"]
        
        self.lineIndex = 0
        self.barIndex = 0
        
        self.filepath = filepath
        self.filetypes = filetypes
        
        self.xlabel =""
        self.left_ylabel = ""
        self.right_ylabel = ""
        
        self.xlim = None
        self.left_ylim = None
        self.right_ylim = None
        
        self.figure = None
        self.left_axis = None
        self.right_axis = None
        
        self.plots = []
        self.plotNames = []

        self.xvalues = 0       # number of x values, set when the first data is plotet and should always be the same
        self.condense_factor = condense_factor  # number of data points on the x-axis that shall be condensed into 1 point
        
        if legend_location == "right":
            self.layout_axes = [0.1, 0.1, 0.5, 0.8]
            self.layout_hstretch = 1.3
            self.layout_vstretch = 1.0
            self.layout_legend_anchor = (1.2, 0.5)
            self.layout_legend_location = 6  # 'center left'
            self.layout_legend_linebreak = 12
            self.layout_legend_vspacing = 3
            self.layout_legend_columns = 1
        elif legend_location == "bottom":
            self.layout_axes = [0.1, 0.2, 0.8, 0.6]
            self.layout_hstretch = 1.0
            self.layout_vstretch = 1.3
            self.layout_legend_anchor = (0.5, -0.15)
            self.layout_legend_location = 9  # 'lower center'
            self.layout_legend_linebreak = 32
            self.layout_legend_vspacing = 1.0
            self.layout_legend_columns = 2            
        else:
            raise ValueError("Illegal legend location: '"+legend_location+"'"+\
                             " must either be 'right' or 'bottom'.") 
        
        
    def _condensed(self, data, steps):
        """Reduces a two-dimensional matrix (or a one dimensional array) so 
        that in each row a package of 'steps' numers is reduced to one number
        representing the average value of the package.
        """
        if data.flatten()[0] == None: return data
        assert data.ndim in [1,2], "data must be one or two-dimensional"
        assert data.shape[data.ndim-1] % steps == 0, \
                "steps %i not a divisor of array length %i" % \
                (steps, data.shape[data.ndim-1])
        
        def condense(a, steps):
            """condense a one dimensional array"""
            b = a.reshape((a.shape[0]/steps, steps))
            return numpy.array([p[numpy.where(~numpy.isnan(p))].mean() \
                                for p in b])
        
        if data.ndim == 2:
            return numpy.array([condense(row, steps) for row in data])
        else: 
            return condense(data, steps)
        
         
    def beginPlot(self, xlabel, ylabel, xlim, ylim):
        """Starts a new plot. 'filepath' is a filename (including the
        path) to which the image will be written when calling 'endPlot'. 
        The image will also (if 'filepath' does not contain an extension: 
        only) be stored in all of the formats the extension of which is
        listed in filetypes. 'xlabel' and 'ylabel' contain the labels
        of the x- and y-axis. 'xlim' and 'ylim' may contain the limits
        for x- and y-values or 'None'. If they contain 'None' then the limits
        are determined automatically.
        """
        assert self.figure == None, \
                "Need to finish the last plot with endPlot() first!"

        self.xlabel, self.left_ylabel = xlabel, ylabel
        self.right_ylabel = ""
        self.xlim, self.left_ylim = xlim, ylim
        self.right_ylim = None

        self.figure = pyplot.figure()
        
        if self.layout_hstretch != 1.0:
            self.figure.set_figwidth(self.layout_hstretch \
                                     * self.figure.get_figwidth())
        if self.layout_vstretch != 1.0:
            self.figure.set_figheight(self.layout_vstretch \
                                      * self.figure.get_figheight())
                    
        self.left_axis = self.figure.add_axes(self.layout_axes) #self.figure.add_subplot(111)
        self.right_axis = None
        
        self.plots = []        
        self.plotNames = []
        self.lineIndex = 0
        self.barIndex = 0
    
    
    def beginDoublePlot(self, xlabel, left_ylabel, right_ylabel,
                        xlim, left_ylim, right_ylim):
        """Starts a new plot. Same as begin plot, only that this plot contains
        a second y-axis on the right hand side. See method 'beginPlot' for
        a description of the parameters.
        """
        self.beginPlot(xlabel, left_ylabel, xlim, left_ylim)
        self.right_ylabel = right_ylabel
        self.right_ylim = right_ylim
        self.right_axis = self.left_axis.twinx()
        
        
    def endPlot(self):
        """Finishes a plot and saves the image(s) of the plot to the disk.
        """
        def add_linebreaks(label, lineWidth):
            sl = label.split(" ")
            dl = [sl[0]]
            chCnt = len(sl[0])
            for s in sl[1:]:
                chCnt += len(s)
                if chCnt > lineWidth and chCnt - len(s) > 3:
                    dl.append("\n")
                    chCnt = len(s)
                else:
                    dl.append(" ")
                dl.append(s)
            return "".join(dl)
                        
        assert self.figure, "Plotting must be started with beginPlot() first!"
        
        if self.left_ylim: self.left_axis.set_ylim(self.left_ylim)
        if self.right_ylim: self.right_axis.set_ylim(self.right_ylim)
        
        if self.xlabel: self.left_axis.set_xlabel(self.xlabel)
        if self.left_ylabel: self.left_axis.set_ylabel(self.left_ylabel)
        if self.right_ylabel: self.right_axis.set_ylabel(self.right_ylabel)
        
        if self.condense_factor <= 1:
            if self.xlim: self.left_axis.set_xlim(self.xlim)                            
            ticks = list(self.left_axis.get_xticks()[1:])
            if ticks[0] >= 5: ticks.insert(0, 1.0)
            ticks = numpy.array(ticks)
            labels = tuple([str(int(t)) for t in ticks])
        else:
            if self.xlim: 
                self.left_axis.set_xlim(self.xlim[0]/self.condense_factor,
                                        self.xlim[1]/self.condense_factor)          
            nticks = self.xvalues / self.condense_factor
            ticks = numpy.arange(1, nticks+1, dtype = float)
            labels = tuple([str(i)+"-"+str(i+self.condense_factor-1) \
                            for i in range(1, self.xvalues+1, 5)])
            minorTicks = ticks - 1
            self.left_axis.set_xticks(minorTicks, minor=True)
            
        self.left_axis.set_xticks(ticks - 0.5)
        try:
            self.left_axis.xaxis.set_tick_params(which="major", length=0)
        except AttributeError: # old version of matplotlib
            for tickline in self.left_axis.get_xticklines():
                tickline.set_markersize(0)
        self.left_axis.xaxis.set_ticks_position('bottom')
        self.left_axis.set_xticklabels(labels)
        
        for i in range(len(self.plotNames)):
            self.plotNames[i] = add_linebreaks(self.plotNames[i], 
                                               self.layout_legend_linebreak)
        
        l = self.left_axis.legend(self.plots, self.plotNames,
                                  bbox_to_anchor = self.layout_legend_anchor, 
                                  borderaxespad=0., 
                                  labelspacing = self.layout_legend_vspacing,
                                  ncol = self.layout_legend_columns,
                                  loc = self.layout_legend_location)
        l.draw_frame(False)            
        
        filepath, ext = os.path.splitext(self.filepath)
        extensions = list(self.filetypes)
        if ext and ext not in extensions:
            extensions.append(ext)        
        for ext in extensions:
            self.figure.savefig(filepath+ext)   


    def _selectAxis(self, yaxis):
        """Returns the proper axis object, depending on whether 'yaxis' has the
        string value "left" or "right". (Checks for illegal values via assert.)
        """
        assert yaxis == "left" or (yaxis == "right" and self.right_axis), \
           "Axis '"+str(yaxis)+"' does not exist!"
        
        if yaxis == "left":
            return self.left_axis, self.left_ylim
        else:
            return self.right_axis, self.right_ylim

    def _normDataFormat(self, data, errorBars):
        """Returns a tuple (data, errorBars) where 'data' and 'errorBars' are
        always two dimensional numpy array, no matter whether 'data' was a 
        list or an array of one or two dimentsions and 'errorBars' was None, 
        or a (nested) list or array of one or two dimensions."""
        if not isinstance(data, numpy.ndarray): 
            data = numpy.array(data)
        if errorBars != None and not isinstance(errorBars, numpy.ndarray): 
            errorBars = numpy.array(errorBars)
        if data.ndim == 1: 
            data = data.reshape((1, data.shape[0]))
            if errorBars != None:
                errorBars = errorBars.reshape((1, data.shape[1]))
        if errorBars == None: 
            errorBars = numpy.array([[None]*data.shape[1]])
        return (data, errorBars)

    def linePlot(self, names, data, errorBars = None, yaxis = "left"):
        """Plots one or several graphs. 'names' is list of names of the graphs,
        'data' is a one or two dimensional array that contains the data.
        """
        withoutErrorBars = errorBars == None
        data, errorBars = self._normDataFormat(data, errorBars)
        assert withoutErrorBars or data.shape == errorBars.shape, \
            "Mismatch between data shape %s and error bars shape %s" \
            % (str(data.shape), str(errorBars.shape))
        assert self.figure, "Plotting must be started with beginPlot() first!"
        assert self.xvalues == data.shape[1] or self.xvalues == 0,\
            "Mismatched number of data points between this "+\
            "(%i) and previous plot (%i)!" % (data.shape[1], self.xvalues)

        self.xvalues = data.shape[1]
        if self.condense_factor > 1: 
            data = self._condensed(data, self.condense_factor)
            errorBars = self._condensed(errorBars, self.condense_factor)

        ax, ylim = self._selectAxis(yaxis)
        xvals = numpy.arange(len(data[0]), dtype=float)+0.5
        
        for i in range(len(names)):
            style = self.lineStyles[(i+self.lineIndex) % len(self.lineStyles)]
            
            if ylim and False: # could be confusing, therefore turned off
                indices = numpy.where(numpy.isnan(data[i]) | \
                                      (data[i] < ylim[0]) | \
                                      (data[i] > ylim[1]))[0]
            else:
                indices = numpy.where(numpy.isnan(data[i]))[0]
                                  
            indices = numpy.concatenate((indices, numpy.array([len(data[i])])))
            start = 0; pl = []
            for idx in indices:
                if idx - start > 0:
                    if withoutErrorBars:
                        pl = ax.plot(xvals[start:idx], data[i][start:idx], 
                                     marker = style[0], linestyle = style[1], 
                                     color = style[2], 
                                     markerfacecolor = style[3])
                    else:
                        pl = ax.errorbar(xvals[start:idx], data[i][start:idx], 
                                     marker = style[0], linestyle = style[1], 
                                     color = style[2], 
                                     markerfacecolor = style[3],
                                     yerr = errorBars[i][start:idx])
                start = idx+1
                
            if len(pl) > 0: 
                self.plots.append(pl[0])
                self.plotNames.append(names[i])           
            # pyplot.legend(tuple(names), loc="upper left")      
        self.lineIndex += len(names)
       
       
    def barPlot(self, names, data, errorBars = None, yaxis = "left"): 
        """Plots several graphs as bars. 'names' is list of names of the 
        graphs, 'data' is a one or two dimensional array that contains the 
        data. If data contains more than one row of data then the bars are
        stacked upon each other. (In order not to stack the graphs of 
        several bar graphs, barPlot() must be called several times.)
        """
        withoutErrorBars = errorBars == None        
        data, errorBars = self._normDataFormat(data, errorBars)
        assert withoutErrorBars or data.shape == errorBars.shape, \
            "Mismatch between data shape %s and error bars shape %s" \
            % (str(data.shape), str(errorBars.shape))                 
        assert self.figure, "Plotting must be started with beginPlot() first!"
        assert self.xvalues == data.shape[1] or self.xvalues == 0,\
            "Mismatched number of data points between this " + \
            "(%i) and previous plot (%i)!" % (data.shape[1], self.xvalues)

        self.xvalues = data.shape[1]
        if self.condense_factor > 1: 
            data = self._condensed(data, self.condense_factor)
            errorBars = self._condensed(errorBars, self.condense_factor)            
            barw = 0.5
        else:
            barw = 1
        offset = (1-barw)/2

        data[numpy.where(numpy.isnan(data))] = 0.0

        ax = self._selectAxis(yaxis)[0]
        for i in range(len(names)):
            if i == 0:
                bottom = numpy.zeros(len(data[i]), dtype = numpy.float)
            else:
                bottom += data[i-1]
            color = self.barColors[(i+self.barIndex) % len(self.barColors)] 
            pl = ax.bar(numpy.arange(len(data[i]))+offset, data[i], width=barw, 
                        bottom = bottom, facecolor = color)
            self.plots.append(pl[0])
            self.plotNames.append(names[i])
        self.barIndex += len(names)



def selftest():
    def PC(data):
        "Converts ratio values (0-1) into percentage values (0-100)."
        return numpy.array(data)*100.0   

    SI_MEMBERS        = "Subjects choosing SI"
    SFI_MEMBERS       = "Subjects choosing SFI"
    AV_CONTRIB_SI     = "Average contribution in SI"
    AV_CONTRIB_SFI    = "Average contribution in SFI"
    HIGH_CONTRIBUTORS = "High contributers in SI"
    FREE_RIDERS       = "Free-riders in SFI"
    PAYOFF_HC         = "Average payoff of high contributors in SI"
    PAYOFF_FR         = "Average payoff of free-riders in SFI"
    NO_PUNISH_HC      = "High contributers & non-punishers"
    PUNISH_HC         = "High contributers & punishers"
    PAYOFF_NOP_HC     = "Average payoff of high contributers & non-punishers"
    PAYOFF_P_HC       = "Average payoff of high contributers & punishers"    
    
    av_contrib_si = [numpy.NaN]+9*[0.2]+[0.0]+[1.0]+8*[0.4]+10*[0.7]
    av_contrib_sfi = 15*[0.5] + [numpy.NaN]*2 + 3*[1.0] + 3*[0.3] + [0.0, 1.0] + 5*[0.1]
            
    si_members = [0.4]*4+[0.0]+10*[0.3]+[1.0,0.0]+8*[0.7]+5*[0.3]
    sfi_members = [1.0-sim for sim in si_members]
    results = {}
    results[SI_MEMBERS] = si_members
    results[SFI_MEMBERS] = sfi_members
    results[AV_CONTRIB_SI] = av_contrib_si
    results[AV_CONTRIB_SFI] = av_contrib_sfi
    
    plotter = Plotter("../test/Plotting_Test1.png", 
                      legend_location = "right")
    plotter.beginDoublePlot("Period", 
            "Percentage in total subject population", 
            "Contribution in percent of endowment", 
            (0, 30), (0,100), (0,100))  
    data = PC([results[SI_MEMBERS], results[SFI_MEMBERS]])
    plotter.barPlot([SI_MEMBERS, SFI_MEMBERS], data, yaxis = "left")               
    plotter.linePlot([AV_CONTRIB_SI], PC([results[AV_CONTRIB_SI]]), yaxis = "right")
    plotter.linePlot([AV_CONTRIB_SFI], PC([results[AV_CONTRIB_SFI]]), yaxis = "right")
    plotter.endPlot()
    
    def rnd(a,b):
        return numpy.random.random()*(b-a)+a
    
    punish_hc = [rnd(0.3, 0.5) for i in range(30)]
    no_punish_hc = [rnd(0.3, 0.5) for i in range(30)]
    payoff_p_hc = [numpy.random.randint(40, 50) for i in range(30)]
    payoff_nop_hc = [numpy.random.randint(45, 60) for i in range(30)]
    results[PUNISH_HC] = punish_hc
    results[NO_PUNISH_HC] = no_punish_hc
    results[PAYOFF_P_HC] = payoff_p_hc
    results[PAYOFF_NOP_HC] = payoff_nop_hc
    
    plotter = Plotter("../test/Plotting_Test2.png", legend_location = "right",
                      condense_factor = 5)
    plotter.beginDoublePlot("Periods", 
            "Percentage of high contributers in SI", 
            "Payoffs in MUs", 
            (0, 30), (0,100), None)
    data = PC([results[PUNISH_HC], results[NO_PUNISH_HC]])
    plotter.barPlot([PUNISH_HC, NO_PUNISH_HC], data, yaxis = "left")               
    plotter.linePlot([PAYOFF_P_HC], [results[PAYOFF_P_HC]], yaxis = "right")
    plotter.linePlot([PAYOFF_NOP_HC], [results[PAYOFF_NOP_HC]],
                     errorBars = [[r/25.0 * numpy.random.random() \
                                   for r in results[PAYOFF_NOP_HC]]], 
                     yaxis = "right")
    plotter.endPlot()    
    
    with open("../test/Test_Plotting.html", "w") as f:
        f.write('<html>\n<body>\n')
        f.write('<p><img src="Plotting_Test1.png"></p>\n')
        f.write('<p><img src="Plotting_Test2.png"></p>\n')        
        f.write('</body>\n</html>\n')
        
    if "startfile" in dir(os):
        eval('os.startfile("../test/Test_Plotting.html")')
    else:
        browsers = ["firefox ","chrome ","safari ", "opera ", "epiphany ",
                     "konqueror ", "icedove ", "seamonkey ", "camino "]
        browsers.reverse()
        while os.system(browsers.pop() + "../test/Test_Plotting.html &") != 0:
            pass
    
if __name__ == "__main__":
    selftest()
    