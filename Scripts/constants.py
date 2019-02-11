import os
import six
from matplotlib import colors as plotcolors
import random
##INITIALIZE DIMENSIONS, FLAGS, DATA STORAGE ARRAYS, AND CONSTRAINTS
##DIMENSIONS
projectName='Monterey'
countyCode='27'
NFARM=31
if NFARM==0: NFARM=1 #must be at least 1 aggregation region
times = range(1988,2017)

##FLAGS
relative = False #SPecifying a local path for data instead of relative
modelLU = True
newProject=True
ModelLU=True
firstTime=True
checkFlag=False #this is a general error flag
debug=False
showPlot=False
pre1990=True
filterCrop=True
writeApplications=True
##DATA STORAGE ARRAYS
files=list()
growthTime=dict() #?
ranch=dict()#?
TRS=dict()#?
primaryFarmLookup=dict()
TRSClimateLookup=dict()
farmClimateLookup=dict()
cropDict=dict()
cropAcreDict=dict()
CAF=dict()

##PATHS
if not relative:
    basePath= r'C:\WesSVN\USGS\CalPIP2\Projects\{}'.format(projectName)
    base_path = basePath
    plotDirectory = r'C:\WesSVN\USGS\CalPIP2\Projects\{}\Output\Plots'.format(projectName)
    joinDirectory= r'C:\WesSVN\USGS\CalPIP2\Projects\{}\Output\CalPIPJoin'.format(projectName)
    lookupDirectory=r'C:\WesSVN\USGS\CalPIP2\Data\LookUp'.format(projectName)
    dataDirectory=r'C:\WesSVN\USGS\CalPIP2\Data\Before1990'.format(projectName)
    dataDirectory1990=r'C:\WesSVN\USGS\CalPIP2\Data\After1990'.format(projectName)
    projectData=r'C:\WesSVN\USGS\CalPIP2\Projects\{}\ExtractedData'.format(projectName)
else:
    basePath= r'..\Projects\{}'.format(projectName)
    base_path = basePath
    plot_path = r'..\Projects\{}\Output\Plots'.format(projectName)
    joinDirectory= r'..\Projects\{}\Output\CalPIPJoin'.format(projectName)
    lookupDirectory=r'..\Data\LookUp'.format(projectName)
    dataDirectory=r'..\Data\Before1990'.format(projectName)
    dataDirectory1990=r'..\Data\After1990'.format(projectName)
    projectData=r'..\Projects\{}\Extracted_Data'.format(projectName)
    ##RELATED PATHS FOR USE OF CALPIP FOR FMP
    #FMPOutput
    FMPOutBasePath= r'D:\LandUse\LU Processing'
    FMPOutFilePath= r'D:\LandUse\LU Processing\OUTPUT'
    FMPOutOutputPath= r'D:\LandUse\LU_Processed\FMP_Input'
    #computeCropAreas
    FMPInputBasePath=r'D:\LandUse\LU_Processed\FMP_Input'
    TRSPath=r'D:\LandUse\LU Processing\CalPIPJoin'
#set directory copy files and create lookup dictionary
outputDirectory= os.path.join(basePath, 'Output')



for farm in range(1,NFARM):
   # CAF[farm]=[3,8] #for month
   CAF[farm]=['period1','period2']
allCropGroups=['Ag_Trees','Artichokes','Cane-Bush Berries','Carrots','Celery','Citrus and subtropical','Corn','Crucifers-Cabbages',
            'Cucumber-Melons-Squash','Deciduous fruits and nuts','Field Crops','Grain Crops','Legumes','Lettuce','Nurseries-Outdoor','Onions-Garlic',
            'Root Vegetables','Rotational 30-day','Strawberries','Tomato-Peppers','Vineyards']
selectedCropGroups=['Artichokes','Cane-Bush Berries','Carrots','Celery','Corn','Crucifers-Cabbages','Cucumber-Melons-Squash','Field Crops',
                   'Grain Crops','Legumes','Lettuce','Onions-Garlic','Root Vegetables','Rotational 30-day','Tomato-Peppers']
#These are groups associated with NLCD/LAAND USE DATA SET categories
CropGroups1992=['Deciduous fruits and nuts','Vineyards','Strawberries','Artichokes','Unspecified Irrigated Row Crops','Nurseries-Indoor','Quarries','Barren-Burned','Semiagricultural ','Golf Course Turf/Parks','Water','Beach-Dunes','Upland Grasslands/Shrub Lands','Woodlands','Citrus and subtropical','Urban']
CropGroups1997=['Unspecified Irrigated Row Crops','Rotational 30-day','Tomato-Peppers','Lettuce','Strawberries','Artichokes','Crucifers-Cabbages','Legumes','Carrots','Onions-Garlic','Root Vegetables','Celery','Cucumber-Melons-Squash','Cane-Bush Berries','Field Crops','Corn','Deciduous fruits and nuts','Citrus and subtropical','Vineyards','Pasture','Golf Course Turf/Parks','Grain Crops','Water','Nurseries-Outdoor','Semiagricultural' ,'Barren-Burned','Upland Grasslands/Shrub Lands']
CropGroups2000=['Field Crops','Deciduous fruits and nuts','Artichokes','Legumes','Crucifers-Cabbages','Cane-Bush Berries','Carrots','Celery','Corn','Semiagricultural','Citrus and subtropical','Idle-Fallow','Nurseries-Outdoor','Grain Crops','Lettuce','Cucumber-Melons-Squash','Woodlands','Unspecified Irrigated Row Crops','Pasture','Upland Grasslands/Shrub Lands','Onions-Garlic','Tomato-Peppers','Root Vegetables','Rotational 30-day','Strawberries','Golf Course Turf/Parks']
annual=['Strawberries','Corn','Cane-Bush Berries','Deciduous fruits and nuts','Citrus and subtropical','Vineyards','Nurseries-Outdoor','Ag_Trees']
annual1983=['Corn','Cane-Bush Berries','Nurseries-Outdoor']
filterGroup=['Artichokes','Nurseries-Outdoor','Legumes','Onions-Garlic','Cucumber-Melons-Squash', 'Celery','Tomato-Peppers'] 
lastYearRead=0
cropPlotLimit=2015
timeidx=0
skipList=[16003]
LUList=['Celery',
'Cucumber-Melons-Squash',
'Legumes',
'Lettuce',
'Rotational 30-day',
'Crucifers-Cabbages',
'Carrots',
'Onions-Garlic',
'Root Vegetables',
'Tomato-Peppers',
'Strawberries',
'Corn',
'Field Crops',
'Grain Crops',
'Cane-Bush Berries',
'Deciduous fruits and nuts',
'Citrus and subtropical',
'Vineyards',
'Nurseries-Outdoor',
'Nurseries-Indoor',
'Artichokes',
'Pasture',
'Semiagricultural ',
'Ag_Trees'
]

##SIMULATION CONSTANTS:
modelUnits = ['Days', 'Meters', 'Meters$\mathregular{^3}$/s', 'Kilometers', 'Years', 'Kg/s', 'Months', 'Acres']  #modelUnits= [time, space, discharge]

##UTILITIES
def find_between( s, first, last ):
    #this function returns the string between two characters
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ''
colorList=list()
cropColors=dict()

colorSkip = [(u'antiquewhite', u'#FAEBD7'),
(u'beige', u'#F5F5DC'),
(u'ghostwhite', u'#F8F8FF'),
(u'lightyellow', u'#FFFFE0'),
(u'cornsilk', u'#FFF8DC'),
(u'floralwhite', u'#FFFAF0'),
(u'honeydew', u'#F0FFF0'),
(u'lightcyan', u'#E0FFFF'),
(u'mintcream', u'#F5FFFA'),
(u'moccasin', u'#FFE4B5'),
(u'oldlace', u'#FDF5E6'),
(u'papayawhip', u'#FFEFD5'),
(u'white', u'#FFFFFF'),
(u'blanchedalmond', u'#FFEBCD'),
(u'palegoldenrod', u'#EEE8AA'),
(u'lightgray', u'#D3D3D3'),
(u'lemonchiffon', u'#FFFACD'),
(u'lavenderblush', u'#FFF0F5'),
(u'whitesmoke', u'#F5F5F5'),
(u'aliceblue', u'#F0F8FF'),
(u'gainsboro', u'#DCDCDC'),
(u'linen', u'#FAF0E6'),
(u'mistyrose', u'#FFE4E1'),
(u'coral', u'#FF7F50'),
(u'lime', u'#00FF00'),
(u'lightgoldenrodyellow', u'#FAFAD2'),
(u'rosybrown', u'#BC8F8F'),
(u'skyblue', u'#87CEEB'),
(u'limegreen', u'#32CD32'), 
(u'azure', u'#F0FFFF'),
(u'seashell', u'#FFF5EE'),
(u'lavender', u'#E6E6FA')
]

def getColors(ncolors):
    allcolors = list(six.iteritems(plotcolors.cnames))
    random.shuffle(allcolors)
    colors=allcolors[:ncolors]
    count=0
    for color in colors:
       if color in colorSkip:
           random.shuffle(allcolors)
           colors[count]=allcolors[1]
           while colors[count] in colorSkip:
                random.shuffle(allcolors)
                colors[count]=allcolors[1]
       count+=1
    #colorFile=os.path.join(base_path, 'colors.out')
    #with open (colorFile, 'w') as fout:
    #    for color in colors:
    #        fout.write(str(color)+'\n')
    return colors

def getUniqueColor():
    colorFound=False
    allcolors = list(six.iteritems(plotcolors.cnames))
    for color in allcolors:
        if color not in colorSkip:
            if color not in colorList:
                uniqueColor = color
                colorList.append(uniqueColor)
                colorFound=True
                break
    if not colorFound:
        print('not enough colors--extra values are set to black')
        uniqueColor='k'
    return uniqueColor

