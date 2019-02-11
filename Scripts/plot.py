from timeStepValue import TimeStepValueContainer
import random
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as plotcolors
import six
import constants


# Constant strings for the plot class
#  These are indexes to the legendAttribues dictionary
labelspacing = 'labelspacing'
loc = 'loc'
fontsize = 'fontsize'
ncol = 'ncol'
shadow = 'shadow'
legendaxesscale = 'legendaxesscale'
bbox_to_anchor = 'bbox_to_anchor'
# End constants

class Axis(object):
    def __init__(self, isX, min, max, label=''):
        self.axis = 'x' if isX else 'y'
        self.min = min
        self.max = max
        self.label = label

class Plotter(object):
    def __init__(self, xAxis, yAxis):
        self.valueContainers = dict()
        self.x = xAxis
        self.y = yAxis
        self.title = ''
        self.legendAttributes = dict()
        self.earlyData=False

    def initializeFigure(self):
        print 'Initializing Plot...'
        figure = plt.figure()
        figure.add_axes([0.1, 0.1, 0.8, 0.8])  # left, bottom, width, height (range 0 to 1)
        self.subplots = plt.subplots()
    
    def getColors(self, ncolors):
        colors = list(six.iteritems(plotcolors.cnames))
        random.shuffle(colors)
        return colors[:ncolors]
    
    def minMax(self, scale=1.):
        totYmin = totYmax = 0
        totXmin = totXmax = 0
        for container in self.valueContainers.values():
            mintime, minval=container.getMinTimeAndValue(scale=scale)
            time, maxval=container.getMaxTimeAndValue(scale=scale)
            maxtime, val=container.getLastTimeAndValue(scale=scale)
            if minval < totYmin:
                totYmin = minval
            if maxval > totYmax:
                totYmax = maxval
            if mintime < totXmin:
                totXmin = mintime
            if maxtime > totXmax:
                totXmax = maxtime   
        return (totXmin, totXmax), (totYmin, totYmax)
    
    def setAxesRanges(self, scale= 1., processor=None):
        if self.earlyData:
            xminmax, yminmax = self.minMax(scale=scale)
            self.y.min = 0
            self.x.min = 0
            self.x.max = 14
            self.y.max = yminmax[1]
        elif processor is not None:
            if processor=='Radius':
                xminmax, yminmax = self.minMax(scale=scale)
                self.y.min = 0
                self.x.min = 0
                self.x.max = constants.maxradplot
                self.y.max = yminmax[1]
            if processor=='Transport':
                xminmax, yminmax = self.minMax(scale=scale)
                self.y.min = 0
                self.x.min = 0
                self.x.max = constants.transportPlotYears
                self.y.max = yminmax[1]
            if processor=='Dissolution':
                xminmax, yminmax = self.minMax(scale=scale)
                self.y.min = 0
                self.x.min = 0
                self.x.max = constants.dissolutionPlotYears
                self.y.max = yminmax[1]
            if processor=='Crop1':
                xminmax, yminmax = self.minMax(scale=scale)
                self.y.min = 0
                self.x.min = 0
                self.x.max = 12
                self.y.max = yminmax[1]
            if processor=='Crop2':
                xminmax, yminmax = self.minMax(scale=scale)
                self.y.min = 0
                self.x.min = 1974
                self.x.max = constants.cropPlotLimit
                self.y.max = 1.1*yminmax[1]
        else:
            xminmax, yminmax = self.minMax(scale=scale)
            self.y.min = yminmax[0]
            self.y.max = yminmax[1]
            self.y.min = 0.99 * self.y.min
            self.y.max = 1.01 * self.y.max
            self.x.min = xminmax[0]
            self.x.max = xminmax[1]

    def addPlotData (self, valueContainer, seriesName, earlyData=None):
        if valueContainer.getValueCount() == 0:
            print('Skipping Case {} for plot: there are no data...'.format(seriesName))
            return
        self.earlyData=earlyData
        self.valueContainers[seriesName] = valueContainer

    def plotData(self, scale=1.0):
        for seriesName in sorted(self.valueContainers.keys()):
            container = self.valueContainers[seriesName]
            color = container.getColor()
            xvals = container.getScaledTimes(scale=scale)
            yvals = container.getScaledValues()
            self.subplots[1].plot(xvals, yvals, color, label=str(seriesName))

    def generatePlot(self, title, scale=1.0, processor=None, skipLegend=None): #currently scale axis refers to x axis only
        self.title = title
        self.initializeFigure()
        self.setAxesRanges(scale, processor)      
        self.plotData(scale) 
        self.finalizeFigure(skipLegend,processor) #TODO need to update  these so legend is scaled to number of entries           


    def initializeLegendProperties(self):
        # These are the default legend parameters
        # Override this method in the inherited class
        self.legendAttributes[loc] = 'center right'
        self.legendAttributes[ncol] = 1 
        self.legendAttributes[fontsize] = 8
        self.legendAttributes[labelspacing] = 1
        self.legendAttributes[legendaxesscale] = 0.7
        self.legendAttributes[shadow] = True
        self.legendAttributes[bbox_to_anchor] = (1.5,0.5)


    def finalizeFigure(self, skipLegend=None, processor=None):
        assert self.title is not '', 'You have not declared a title'
        fig, plotArea = self.subplots
        print 'Finalizing Plot...'
        plotArea.set_xlabel(self.x.label)
        plotArea.set_ylabel(self.y.label)
        plotArea.set_title(self.title)
        if skipLegend is None :
            self.initializeLegendProperties()
            if processor is not None:
                if 'Crop' in processor:
                    self.legendAttributes[loc] = 'center right'
                    self.legendAttributes[fontsize] = 4
                    self.legendAttributes[legendaxesscale] = 0.7
                    self.legendAttributes[bbox_to_anchor] = (1.6,0.5)
            box = plotArea.get_position()
            plotArea.set_position([box.x0, 
                               box.y0, 
                               box.width * self.legendAttributes[legendaxesscale],
                               box.height])
            plotArea.legend(loc=self.legendAttributes[loc],
                        ncol=self.legendAttributes[ncol],
                        fontsize=self.legendAttributes[fontsize],
                        labelspacing=self.legendAttributes[labelspacing],
                        shadow=self.legendAttributes[shadow],
                        bbox_to_anchor=self.legendAttributes[bbox_to_anchor])
        plt.ticklabel_format(style='sci', axis='y', scilimits=(-4,4))
        plt.ticklabel_format(style='sci', axis='x', scilimits=(-4,4))
        plt.xlim([self.x.min, self.x.max])
        plt.ylim([self.y.min, self.y.max])
        print ('Saving plot to {}...'.format(self.plotFile))
        fig.savefig(self.plotFile, dpi=300)
        if constants.showPlot: plt.show()
        plt.clf()
        plt.cla()
        plt.close('all')

         
def regression(valueContainers, names, type, scale=1): #negative values occur when flux < 0 need to ignore these...
    linearRegression = TimeSeries(type+'_LinearRegression_Case_' +str(valueContainers[0].caseNum)+'.jpg')
    for idx, container in enumerate(valueContainers):
        linearRegression.addPlotData(container, str(names[idx]))
    linearRegression.generatePlot(type + ' Linear Regression Fit For Case '+ str(valueContainers[0].caseNum), scale=scale)
    if constants.showPlot: plt.show()
    plt.close()

def twoSeriesScatterplot(xvarname,yvarname,behavioral, nonbehavioral, labels, caseNum): #TODO generalize into plot function
    plotFileName=str(yvarname) +'_vs_'+str(xvarname)+str(caseNum)+'comparative.jpg'
    plotFile=os.path.join(constants.plot_path, plotFileName)
    x1 = behavioral[0]
    y1 = behavioral[1]
    color1 = ['b']
    x2 = nonbehavioral[0]
    y2 = nonbehavioral[1]
    color2 = ['g']
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.scatter(x1, y1, s=50, c='b', marker='s', label=labels[0])
    ax1.scatter(x2,y2, s=10, c='r', marker='o', label=labels[1])
    plt.xlabel(xvarname)
    plt.ylabel(yvarname)
    plt.title('Scatter plot of '+ yvarname+' and '+xvarname)
    plt.legend(loc='upper right')
    print ('Saving plot to {}...'.format(plotFile))
    fig.savefig(plotFile, dpi=300)
    if constants.showPlot: plt.show() 
    plt.close()
    return

def scatterplot(xvarname,yvarname,data, labels, caseNum): #TODO generalize into plot function
    plotFileName=str(yvarname) +'_vs_'+str(xvarname)+str(caseNum)+'.jpg'
    plotFile=os.path.join(constants.plot_path, plotFileName)
    x1 = data[0]
    y1 = data[1]
    color1 = ['b']
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.scatter(x1, y1, s=50, c='b', marker='s', label=labels[0])
    plt.xlabel(xvarname)
    plt.ylabel(yvarname)
    plt.title('Scatter plot of '+ yvarname+' and '+xvarname)
    plt.legend(loc='upper right')
    print ('Saving plot to {}...'.format(plotFile))
    fig.savefig(plotFile, dpi=300)
    if constants.showPlot: plt.show() 
    plt.close()


def panelPlot (plotFile, nPanel, nrow, ncol, valueContainers, labelContainer, errorContainers=None, markerContainers=None):
    ## Description 
    # This is designed to make a 4 panel plot. Each panel has 3 lines separately defined by lists of XY data points.
    #this implementation assumes the mean value is being passed in the value container adn min max and stdev in errorContainers

    ## Modules ## Inputs ##
    #valueContainer must be same size and npanel
    # DATA (Each data variable below is a list of lists of x or y values)
    X_lists=list()
    Y_lists=list()
    xmax=list()
    Error_Fill_Color=dict()
    # ANNOTATIONS/LABELS
    Panel_Titles = labelContainer['titles'] #these assume that axes labels are the same
    Panel_XAxis_Labels = labelContainer['xaxis']
    Panel_YAxis_Labels = labelContainer['yaxis']
    Panel_Legend_Locs = labelContainer['legend_loc'] # Location Codes : http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.legend
    if 'panelLabel' in labelContainer.keys():
        Panel_Labels = labelContainer['panelLabel']
    else:
        Panel_Labels = ['']
    # SETTINGS
    Figure_Size = (5,5)

    Panel_Label_Box = dict(boxstyle = 'square', facecolor = 'white', alpha = 1)
    Panel_Label_Loc = [.05, .95] # % of axis
    Panel_Label_FontSize = 10
    Add_Background_Box = False # Change to False to make box invisible... ooo Magic!

    ## Parameters/Constants ##
    if not Add_Background_Box:
        Panel_Label_Box = dict(alpha = 0)
 
    ## Code ##
    # Create the figure, then create 4 axes/panels for future plotting
    fig = plt.figure(figsize = Figure_Size)
    Panels = [plt.subplot(nrow,ncol,i) for i in range(1,len(valueContainers)+1)] #check these ranges

    for panel in range (0, nPanel):
        Y_lists=list()
        X_lists=list()
        containers=valueContainers[panel] #allows for more than 1 data series per panel
        if errorContainers is not None:
            errorContainer=errorContainers[panel]
        #here i make some assumptions that are application specific ie max and min are part of same error container and std
        colors=['lightgray', 'darkgray', 'dimgray']
        if len(errorContainer.keys())> 0:
            if len(errorContainer.keys())> 3: print("only 3 colors of gray shaded error allowed")
            for key in errorContainer.keys():
                if 'max' in key or 'min' in key:
                    Error_Fill_Color['range'] = colors[0]
                    Error_Fill_Alpha = .3
                else:
                    Error_Fill_Color['stdev'] = colors[1]

        for container in containers:
            ylist=list()
            X_lists.append (sorted(container.values.keys()))
            for key in sorted(container.values.keys()):
                ylist.append(container.values[key])
            Y_lists.append (ylist)
        Error_X = X_lists[0] # upper and lower error bars must share x values. 
        xmax.append(max(X_lists[0]))

        if markerContainers is not None:
            Label_lists = markerContainers[panel]['labels']
            Marker_Styles = markerContainers[panel]['markers'] #['+','.','o', '*'] 
            Marker_Sizes = markerContainers[panel]['sizes']

        #Plot Panel
        # plot max and min
        #for analyte in range(0, len(containers)):
        #    ymin=[errorContainer['minval'][1][x]for x in range(0, len(errorContainer['minval'][1]))]
        #    #print(ymin)
        #    ymax=[errorContainer['maxval'][1][x] for x in range(0, len(errorContainer['maxval'][1]))]
        #    #print(ymax)
        #    ytotmax=max(ymax) #this will have to be modified if more than one panel...
        #    #print(ytotmax)
        #    Panels[panel].fill_between(Error_X, ymin, ymax, color = Error_Fill_Color['range'], alpha = Error_Fill_Alpha)

        #plot std deviations
        for analyte in range(0, len(containers)):
            ymin=[errorContainer['mean'][1][x] - errorContainer['stdev'][1][x] for x in range(0, len(errorContainer['stdev'][1]))]
            #print(ymin)
            ytotmin=min(ymin)
            if ytotmin<0.: ytotmin=0.
            ymax=[errorContainer['mean'][1][x] + errorContainer['stdev'][1][x] for x in range(0, len(errorContainer['stdev'][1]))]
            #print(ymax)
            ytotmax=max(ymax) # if minima and amxima are plotted again will need to modify this statement
            Panels[panel].fill_between(Error_X, ymin, ymax, color = Error_Fill_Color['stdev'], alpha = Error_Fill_Alpha)
        if markerContainers is None:
            for x, y in zip(X_lists, Y_lists):
                Panels[panel].plot(x,y, color='black')
        else:
            for x, y, llabel, mstyle, msize in zip(X_lists, Y_lists, Label_lists, Marker_Styles, Marker_Sizes):
                Panels[panel].plot(x,y, marker = mstyle, markersize = msize, label = llabel, color='black')
        # Label those sexy panels!
    idx=0
    
    for panel, title, xlbl, ylbl, legloc, plbl in zip(Panels, Panel_Titles, Panel_XAxis_Labels, Panel_YAxis_Labels, Panel_Legend_Locs, Panel_Labels):
        panel.set_title(title, fontsize=12)  
        panel.set_xlabel(xlbl, fontsize=10)
        panel.set_ylabel(ylbl, fontsize=10)
        panel.set_xlim([0, xmax[idx]])
        panel.set_ylim([0,1.1*ytotmax])
        if 'MORRIS' in constants.simName or 'Silver' in constants.simName:  #hack for SSLIKE
            if 'Chemograph' in plotFile:
                panel.set_ylim([0,1.1*ytotmax])
            else:
                panel.set_ylim([0.99*ytotmin,1.01*ytotmax])
        idx+=1
        panel.legend(loc = legloc)
        panel.text(Panel_Label_Loc[0], Panel_Label_Loc[1], plbl, transform = panel.transAxes, fontsize = Panel_Label_FontSize, verticalalignment = 'top', bbox = Panel_Label_Box) 
        #plt.subplot.xlim([0, max(X_lists[0])])
        #plt.subplot.ylim([0, 1.1])
        #plt.subplot.xlim([0, max(X_lists[0])])
        #plt.subplot.ylim([0, 1.1])
    print ('Saving plot to {}...'.format(plotFile))
    fig.savefig(plotFile, dpi=300, bbox_inches='tight')
    if constants.showPlot: plt.show()
    plt.close()

def panelBarPlot (nPanel,ncol, nrow, valueContainers, plotFile, varNames, Panel_Titles, Panel_Labels):
    ###NOT COMPLETE###
    #THIS HAS BEEN ADAPTED SPECIFICALLY FOR SOBOL SENSITIVITY PLOTS
    ## Description 
    # This program is designed to make an npanel bar plot. 
    #valueContainer must be same size and npanel
    # ANNOTATIONS/LABELS
    #Panel_Legend_Locs = [4,4,4,4 ] # Location Codes : http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.legend

    # SETTINGS
    Figure_Size = (15,10)
    Panel_Label_Box = dict(boxstyle = 'square', facecolor = 'white', alpha = 1)
    Panel_Label_Loc = [.95, .95] # % of axis (current--right hand corner)
    Panel_Label_FontSize = 14
    Add_Background_Box = False # Change to False to make box invisible... ooo Magic!
 
    ## Code ##
    # Create the figure, then create 4 axes/panels for future plotting
    fig = plt.figure(figsize = Figure_Size)
    Panels = [plt.subplot(nrow,ncol,i) for i in range(1,len(valueContainers)+1)] 
    ## necessary variables
    nval = len(varNames)
    ind = np.arange(nval)             # the x locations for the groups
    width = 1./nval                      # the width of the bars
    rects=list()
    for panel in range (0, nPanel):
        locWidth=0.
        valMaxList=list()
        valMinList=list()
        ## the data
        ymax=0.
        data=valueContainers[panel]
        values=data[0]
        errors=data[1] #TODO need to check error structure coming out of sobol
        valmax=max([x+y for x,y in zip(values, errors)])
        valmin=min([x-y for x,y in zip(values, errors)])
        locWidth=locWidth+width
        ## the bars
        rects.append(Panels[panel].bar(ind+locWidth, values, width,
                        color='Black',
                        yerr=errors,
                        error_kw=dict(elinewidth=2,ecolor='dimgray')))
            
        valMaxList.append(valmax)
        valMinList.append(valmin)
        ymin=0.7*min(valMinList)

        ymax=1.1*max(valMaxList)
        #print(ymax)
        # axes and labels
        Panels[panel].set_xlim(0,len(ind))
        Panels[panel].set_ylim(ymin,ymax)
        #Panels[panel].ticklabel_format(axis='y', style='sci', scilimits=(-3,3)) #this block sets labels to be in sci notation
        #if panel==4 or panel== 5:
        xTickMarks = varNames
        Panels[panel].set_xticks(ind+1.5*width)
        Panels[panel].set_xticklabels(xTickMarks, fontsize=16)
        #Panels[panel].setp(xtickNames, fontsize=12)
        #else:
        #    #dum=1
        #    Panels[panel].xaxis.set_ticklabels([])
            
        ## add a legend to each plot
        #Panels[panel].legend([x[0] for x in rects], varNames )#comment to remove legend and uncomment below to add entire figure legend
        #This block adjusts axes plot area by 10% to facilitate lower legend
        #box = Panels[panel].get_position()
        #Panels[panel].set_position([box.x0, box.y0 + box.height * 0.1,
        #         box.width, box.height * 0.9])

    for panel, title, plbl in zip(Panels, Panel_Titles,Panel_Labels):
        panel.set_title(title, fontsize=12)  
        panel.legend(loc = 1) #comment to remove legend and uncomment below to add entire figure legend
        panel.text(Panel_Label_Loc[0], Panel_Label_Loc[1], plbl, transform = panel.transAxes, fontsize = Panel_Label_FontSize, verticalalignment = 'top', bbox = Panel_Label_Box) 

    # Put a legend below entire figure
    #plt.figlegend((rects1[0], rects2[0], rects3[0], rects4[0]),varNames, loc='lower center', ncol=3, fontsize=16)
                  #, bbox_to_anchor=(0.5, -0.05),
          #fancybox=True, shadow=True, ncol=3)

    print ('Saving plot to {}...'.format(plotFile))
    fig.savefig(plotFile, dpi=300)
    #plt.show()
    plt.close()

    
#THIS CODE WILL ALLOW YOU TO SPCIFY FINAL FIGURE SIZE
#If you've already got the figure created you can quickly do this:

#fig = matplotlib.pyplot.gcf()
#fig.set_size_inches(18.5, 10.5)
#fig.savefig('test2png.png', dpi=100)
#To propagate the size change to an existing gui window add forward=True

#fig.set_size_inches(18.5, 10.5, forward=True)


#def plotlnQt(valueContainers, logvalueContainers, names, scale=1): #todo fix this function
#    lnQtplot = lnQt('lnQt_' +str(valueContainers[0].caseNum)+'.jpg')
#    for idx, container in enumerate(valueContainers):
#        lnQt.addPlotData(container, '')

#    for idx, container in enumerate(logvalueContainers):
#        lnQt.addPlotData(container, '')
##http://matplotlib.org/examples/api/two_scales.html

#    linearRegression.generatePlot('ln(Q) vs T '+ str(valueContainers[0].caseNum), scale=scale)
#    if constants.showPlot: plt.show()
#    plt.close()

def xyPlot(plotType,valueContainer, dataName, yvarname, scale=1.0): #todo ask c how to generalize plot types...
    XY = PDF(str(yvarname)+' Case_' +str(valueContainer.caseNum)+'.jpg')
    XY.addPlotData(valueContainer, str(dataName))
    XY.generatePlot(str(yvarname) +' Case_'+ str(valueContainer.caseNum), scale=scale)
    if constants.showPlot: plt.show()
    plt.close()

def xyPlots(valueContainers, dataNames, yvarname, scale=1.0): 
    XY = TimeSeries(str(yvarname)+' Case_' +str(valueContainers[0].caseNum)+'.jpg')
    for idx, container in enumerate(valueContainers):
        XY.addPlotData(container, str(dataNames[idx]))
    XY.generatePlot(str(yvarname) +' Case_'+ str(valueContainers[0].caseNum), scale=scale)
    if constants.showPlot: plt.show()
    plt.close()

class TimeSeries(Plotter):
    def __init__(self, plotFileName, processor=None):
        if processor is not None:
            if processor=='Dissolution' or processor=='Transport': 
                units = constants.modelUnits[4]
            elif 'Crop'in processor:
                units = constants.modelUnits[7]
        else:
            units = constants.modelUnits[0]
        x = Axis(isX=True, min=0, max=0, label='Time in {}'.format(units)) #modelUnits= [time, space, discharge]
        y = Axis(isX=False, min=0, max=0, label='Discharge in {}'.format(constants.modelUnits[2]))
        if processor=='Transport':
            y = Axis(isX=False, min=0, max=0, label='Tracer Mass Flux in {}'.format(constants.modelUnits[5])) #todo perhaps update this with some unit of measure...
        if processor=='Crop1':
            x = Axis(isX=True, min=1, max=0, label='Month Planted')
            y = Axis(isX=False, min=0, max=0, label='Total Crop Area in {}'.format(constants.modelUnits[7])) #todo perhaps update this with some unit of measure...
        self.plotFile = os.path.join(constants.plot_path, plotFileName)
        if processor=='Crop2':
            x = Axis(isX=True, min=1975, max=2015, label='Year')
            y = Axis(isX=False, min=0, max=0, label='Total Crop Area in {}'.format(constants.modelUnits[7])) #todo perhaps update this with some unit of measure...
        self.plotFile = os.path.join(constants.plot_path, plotFileName)
        super(TimeSeries,self).__init__(xAxis=x, yAxis=y)

    
    def initializeLegendProperties(self):
        super(TimeSeries,self).initializeLegendProperties()
        self.legendAttributes[ncol] = 2 if len(self.valueContainers) > 20 else 1

class lnQt(Plotter):
    def __init__(self, plotFileName):
        x = Axis(isX=True, min=0, max=0, label='Time') 
        y = Axis(isX=False, min=0, max=0, label='Flux')
        self.plotFile = os.path.join(constants.plot_path, plotFileName)
        super(lnQt,self).__init__(xAxis=x, yAxis=y)
    
    def initializeLegendProperties(self):
        super(PDF,self).initializeLegendProperties()
        self.legendAttributes[ncol] = 3 if len(self.valueContainers) > 10 else 1

class PDF(Plotter):
    def __init__(self, plotFileName):
        x = Axis(isX=True, min=0, max=0, label='Value') 
        y = Axis(isX=False, min=0, max=0, label='Probability')
        self.plotFile = os.path.join(constants.plot_path, plotFileName)
        super(PDF,self).__init__(xAxis=x, yAxis=y)
    
    def initializeLegendProperties(self):
        super(PDF,self).initializeLegendProperties()
        self.legendAttributes[ncol] = 3 if len(self.valueContainers) > 10 else 1
                

class Transects(Plotter):
    def __init__(self, plotFileName): #todo make model units a list with two items
        x = Axis(isX=True, min=0, max=0, label='Distance in {}'.format(constants.modelUnits[3]))
        y = Axis(isX=False, min=0, max=0, label='Hydraulic Head in {}'.format(constants.modelUnits[1]))
        self.plotFile = os.path.join(constants.plot_path, plotFileName) #todo why is this plotfile name twice???
        super(Transects,self).__init__(xAxis=x, yAxis=y)

    def initializeLegendProperties(self):
        super(Transects,self).initializeLegendProperties()
        self.legendAttributes[ncol] = 3 if len(self.valueContainers) > 10 else 1

          

        ##########THESE ARE DEPRECATED AND HAVE TO BE UPDATED AS NEEDED#####################
#class DrainPlot(Plotter):
#    def __init__(self, drainContainer, modelUnits, isComparative, plotFileName):
#        self.drainContainer = drainContainer
#        x = Axis(isX=True, min=0, max=0, label='Time in Days')
#        y = Axis(isX=False, min=0, max=0, label='Discharge in {}'.format(modelUnits))
#        self.plotFile = os.path.join(plotFileName, plotFileName)
#        Plotter.__init__(self, isComparative=isComparative, xAxis=x, yAxis=y)


#    def generateAggregateDrainPlot(self, scale, drainsToInclude=None): #*** need to generize this as a function copy this funtion
#        if not self.drainContainer.hasDrains():
#            print ('There are no drains.  Bypassing plot creation')
#            return

#        drainsToInclude = self.drainContainer.getDrainNames(drainsToInclude)

#        allDrains = self.drainContainer.isAllDrains(drainsToInclude)
#        self.title = 'Total Spring Flow' if allDrains else 'Silver Springs Flow'
#        seriesLabel = 'All Springs' if allDrains else 'Silver Springs'

#        self.initializeFigure()

#        totalRates, minMax = self.drainContainer.getAggregatedDrainRates(drainsToAggregate=drainsToInclude,
#            scale=scale)
#        self.setAxesRanges(minMax=minMax, xMax=len(totalRates))
#        self.plotData(range(0,len(totalRates)), totalRates, 'b', seriesLabel)

#        self.finalizeFigure()



#class HeadPlot(Plotter):

#    def __init__(self, nodeContainer, modelUnits, isComparative, plotFileName):
#        self.nodeContainer = nodeContainer
#        x = Axis(isX=True, min=0, max=0)
#        y = Axis(isX=False, min=0, max=0)
#        self.modelUnits = modelUnits
#        self.plotFileName = plotFileName
#        Plotter.__init__(self, isComparative=isComparative, xAxis=x, yAxis=y)

#    def plotHeadforStep(self, period, step, layer):
#        title = 'Hydraulic Heads for Layer ' + str(layer)
#        self.initializeFigure()

#        plotData = np.array(self.nodeContainer.getNodeDataForPeriodAndStep(period=period, step=step, layer=layer))
#        plotData = np.reshape(plotData, (self.nodeContainer.nrow, self.nodeContainer.ncol))
#        npcheckfile = 'C:\Users\Wesley\ownCloud\Projects\CFP\models\CLN\NDM_SI_MC\NPCheck.txt'
#        np.savetxt(npcheckfile, plotData, fmt='%.18e', delimiter=',')
#        # specify levels from vmim to vmax
## levels = np.arange(-1, 2.1, 0.2)
##
## # plot
## fig = plt.figure()
## ax = fig.add_subplot(111)
## plt.contourf(lon, lat, noise, levels=levels)
## plt.colorbar(ticks=levels)
## plt.show()

#        fig = plt.figure()
#        ax1 = plt.subplot(1,1,1)
#       #levels =np.arrange(0, 10,20, 30, 40, 50, 60 ,70, 80, 90, 100)
#        pb = ax1.imshow(plotData, interpolation='None')
#        plt.colorbar(pb)
#        plt.title(title)

#        plotFileName = self.plotFileName.format(period=period, step=step, layer=layer)
#        print ('Saving to ' + plotFileName)
#        fig.savefig(plotFileName, dpi=300)

#class BudgetPlot(Plotter):
#    def __init__(self, budgetContainer, modelUnits, isComparative, basePath):
#        self.budgetContainer = budgetContainer
#        x = Axis(isX=True, min=0, max=0, label='Time in Days')
#        y = Axis(isX=False, min=0, max=0, label='Discharge in {}'.format(modelUnits))
#        self.basePath = basePath
#        Plotter.__init__(self, isComparative=isComparative, xAxis=x, yAxis=y)


#    def generateAggregateBudgetPlot(self, scale, itemName, isIn):
#        if not self.budgetContainer.budgetItemExists(itemName):
#            print ('Budget item does not exist.  Bypassing plot')
#            return

#        self.title = 'Spring Flux'
#        seriesLabel = 'Constant Head Flux'
#        self.plotFile = os.path.join(self.basePath, itemName + '_' + ('in' if isIn else 'out') + '.png')

#        self.initializeFigure()

#        totalRates, minMax = self.budgetContainer.getBudgetRates(itemName=itemName, isIn=isIn, scale=scale)
#        self.setAxesRanges(minMax=minMax, xMax=len(totalRates))
#        self.plotData(range(0,len(totalRates)), totalRates, 'b', seriesLabel)

#        self.finalizeFigure(legLoc=1)

    
        


