__author__ = 'Wesley'
import numpy as np
from scipy.optimize import curve_fit
import constants
import math

class TimeStepValueContainer:
    def __init__(self, color, caseNum=None, processor=None):
        self.values = dict()
        self.color = color
        if caseNum is not None:
           self.caseNum = caseNum
        self.processor=processor

    def populate_valueContainer(self,xval, yval):
        valueDict = dict(zip(xval,yval))
        self.values=valueDict
        
    def addValue(self, value, time, caseNum=None):
        if type(value) is str:
            try:
                value = float(value)
            except:
                #print ('float value is strange for '+ filename + '\n')
                #print ('trying to convert  '+ value)
                value=value.split('+', 1)[0]+'E+'+ value.split('+', 1)[1]
                value = float(value)
                if caseNum not in constants.badFloatlog:
                    constants.badFloatlog.append(caseNum)

        if float(value) > 1e5:
            #print ('value is '+ str(value) + ' for ' + filename + ' time = ' + str(round((float(time)/86400),3))+ ' days \n')
            if caseNum not in constants.largeFloatlog:
                constants.largeFloatlog.append(caseNum)

        if float(value) < 0 and self.processor is 'Flow':
            #print ('value is '+ str(value) + ' for ' + filename + ' time = ' + str(round((float(time)/86400),3))+ ' days \n')
            if caseNum not in constants.negFloatlog:
                constants.negFloatlog.append(caseNum)

        if type(time) is str:
            time = float(time)
        self.values[time] = value

    def getScaledValues(self, scale=1.):
        return [self.values[x] * scale for x in sorted(self.values.keys())]
    
    def getSemiLogValues(self, scale=1.):
        return [log(self.values[x] * scale) for x in sorted(self.values.keys())]

    def getScaledTimes(self, scale=1.):
        return list(sorted([x *scale for x in self.values.keys()]))

    def getValueCount(self):
        return len(self.values.keys())
    
    def getFirstValue(self, scale=1.):
        return self.values[sorted(self.values.keys())[0]] *scale  

    def getLastValue(self, scale=1.):
        return self.values[sorted(self.values.keys())[-1]]*scale
    
    def getFirstTimeAndValue(self, scale=1.):
        firstTime = sorted(self.values.keys())[0]
        firstTimeStor=firstTime
        firstTime=firstTime * scale
        return firstTime, self.values[firstTimeStor]
    
    def getLastTimeAndValue(self, scale=1.):
        lastTime = sorted(self.values.keys())[-1]
        lastTimeStor=lastTime
        lastTime= lastTime * scale
        return lastTime, self.values[lastTimeStor]

    def getMinTimeAndValue(self, scale=1.):
        minval = min(self.values.values())
        foundMinTime=[]
        for x in sorted(self.values.items()):
            if x[1] == minval:
                foundMinTime.append(x[0])
        mintime = min(foundMinTime) * scale
        return  mintime, minval

    def getMaxTimeAndValue(self, scale=1.):
        maxtime=0
        maxval=-999
        mintime, minval=self.getFirstTimeAndValue(scale=scale)
        for x in sorted(self.values.items()):
            if x[0] >= mintime :
               if x[1] > maxval:
                maxval=x[1]
                maxtime=x[0]
        maxtime = maxtime * scale
        return maxtime, maxval
  
    def getRsquared(self, yval, yfit):
        # coefficient of determination, plot text
        yval=np.array(yval)
        yfit=np.array(yfit)
        variance = np.var(yval)
        residuals = np.var(yfit - yval)
        Rsqr = np.round(1-residuals/variance, decimals=2)

        return Rsqr

    def getNashSuttclife(self,s,o):
        #Nash Sutcliffe efficiency coefficient
        #input:
        #s: simulated
        #o: observed
        #output:ns: Nash Sutcliffe efficient coefficient
        s,o = filter_nan(s,o)

        return 1 - sum((s-o)**2)/sum((o-np.mean(o))**2)

    def getNearestValue(self,time, scale=1.0):
        #this returns next value after time
        values=[self.values[x] for x in sorted(self.values.keys())]
        times=list(sorted([x *scale for x in self.values.keys()]))
        for idx in range(0, len(values)):
            if times[idx]<time:
                continue
            else:
                value=values[idx]
                break
        return value

    def getNearestTime(self,value, scale=1.0, minTime=None):
        #This function assumes monotonic decreasing function f(t) and 
        #will return nearest time before from desired value if value 
        #is not coincident with that time
        values=self.getScaledValues()
        times=self.getScaledTimes()
        time=times[-1]
        #Mintime assumes you have a peak value first
        if minTime is not None:
            for idx in range(0, len(values)):
                if times[idx]<minTime:
                    continue 
                else:
                    if idx==0:
                        continue
                    if idx==len(values)-1:
                        print("Desired Value not found, returning last time")
                        break
                    if values[idx-1]>value and values[idx+1]< value:
                        time=times[idx]
        else:
            for idx in range(0, len(values)-1): # this assumes rising limb or monotonically increasing f(t)
                if idx==0:
                    continue
                if idx==len(values):
                    print("Desired Value not found, returning last time")
                    break
                if values[idx-1]<value and values[idx+1]> value:
                    time=times[idx]
        return time

    def returnTruncatedTimesandValues(self, truncValue, scale=1.0, timeTrunc=None, valTrunc=None, minTime=None):
        truncatedVals=list()
        truncatedTimes=list()
        if valTrunc is None and timeTrunc is None:
            print("truncation method must be specified")
            return truncatedTimes, truncatedVals
        if valTrunc is not None and timeTrunc is not None:
            print("one truncation method must be specified")
            return truncatedTimes, truncatedVals
        if valTrunc is not None: #truncate when a value is reached
            if minTime is None:
                print("minTime might need to be specified when truncation on value")
            times=self.getScaledTimes(scale=scale)
            values=self.getScaledValues()
            timeEnd=self.getNearestTime(truncValue, minTime)

            for idx in range(0, len(values)):
                if times[idx]<timeEnd:
                    truncatedTimes.append(times[idx])
                    truncatedVals.append(values[idx])

        else: #return series truncated on time
            times=self.getScaledTimes(scale=scale)
            values=self.getScaledValues()
            timeEnd=truncValue
            for idx in range(0, len(values)):
                if times[idx]<=timeEnd:
                    truncatedTimes.append(times[idx])
                    truncatedVals.append(values[idx])

        return truncatedTimes, truncatedVals


    def getBestFitLine(self, scale=1.0, xval=None, yval=None, sparsefit=None):
        # Return something like (slope, intercept) for linear right now add later for more methods
        # todo need to change this so it only takes a container and gets fitting function name
        # inputs are already scaled from function calling this
        if xval is None:
            xval = self.getScaledTimes(scale=scale) #scale applied only ao alpha is in units of seconds: scaling is supposed to occur outside
            yval = self.getScaledValues() #will need to change this if not linear regression

        yfit = list()
        x = np.array(xval)
        y = np.array(yval)
        p=np.polyfit(x, y, deg=1, full=True) 
        coefficients=p[0]
        a= coefficients[0]
        b= coefficients[1]
        
        if sparsefit:
            xvals=np.array(self.values.keys()) #update xvals after initial line so yfits are generated for each xval

        for x in xval:
            yfit.append(self.fit_linfunc(x, a, b)) #todo generalize this so another function can be set
        
        return a, b, yfit

    def fit_linfunc(self, x, a, b):
            return a*x + b

    def getSparseFitLine(self):
      
        x1,y1 = self.getFirstTimeAndValue(scale=1.0)
        x2,y2 = self.getlastTimeAndValue(scale=1.0)
        
        xval = [x1, x2]
        yval = [y1, y2]

        return self.getBestFitLine(xval, yval,sparsefit=true)
        # Get a line for first and last value pairs

    def getMeanValue(self):
        yvals=self.getScaledValues()
        try:
            mean = sum(yvals)/self.getValueCount()
        except:
            print('Sum or value count value is zero for case')         
            mean = 0.
        return mean

    def checkStaticflow(self):
        diff=0.0
        flat=False
        yvals=self.getScaledValues()
        mean=self.getMeanValue()
        diffstor=0.0
        tol= 0.1
        for val in yvals:
            diff=abs(val-mean)
            if diff > diffstor: diffstor = diff
        if diffstor < tol : flat=True
        #print(self.getMeanValue(), diffstor)
        return flat

    def isEmpty(self):
        empty=True
        if len(self.getScaledValues()) > 0:
            empty=False
        return empty

    def getColor(self):
        return self.color[0]
    

                   
 
class SpatialValueContainer(TimeStepValueContainer):
    def __init__(self):
        super(SpatialValueContainer, self).__init__()
        