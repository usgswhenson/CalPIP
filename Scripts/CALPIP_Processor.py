#'''this script reads in CalPIP data tables and summarizes crop rotations. 
#Created by W. Henson 11/1/16'''
#updated by anav Mittal 2/1/19
import os
import numpy as np
import datetime
import pandas as pd
import numpy  as np
import datetime
import zipfile
from timeStepValue import TimeStepValueContainer
from plot import *
import copy
import constants
import shutil


####################################################################
# CLASSES
####################################################################
class Crop(object):
    def __init__(self):
        self.longName = str()
        self.name = str()
        self.acresPlanted = list()
        self.firstDate = None #list of datetime objects
        self.lastDate = None #list of datetime objects
        self.applicationDates = list()
        self.applicationChemical=dict()
        self.plantOrder = int()
        self.firstDay=int()
        self.lastDay=int()
        self.ranchIDs=dict()
        self.TRSs=dict()
        self.regions=dict()
        self.year=0
        self.planted=False

####################################################################
# FUNCTIONS
####################################################################

def aggregateCropData(df, year):
    ranchDict=dict()
    cropDict=dict()
    firstRead=True
    count=0
    ranchLU=list()
    pseudoRanchID=0
    #test= df=df[df['site_code'] == '16004']
    for index, R in df.iterrows():
        cropExists=False
       
        #R is a named tupple of each row
        if  pd.isnull(R.tship_dir)or R.tship_dir=='0' or pd.isnull(R.range_dir) or R.range_dir.isdigit():
            #print ('null value')
            continue
        try:
            TRS=R.township.strip() + R.tship_dir.strip() + R.range.strip() + R.range_dir.strip() + R.section.strip()
        except:
            print("test")
        if not constants.pre1990:
            if  pd.isnull(R.site_loc_id):
                #print ('null value')
                continue
            if  pd.isnull(R.grower_id):
                #print ('null value')
                continue
            ranchID=TRS+(R.site_loc_id).strip() + str(R.grower_id).strip()

            if pd.isnull(R.chem_code):
                chemCode = -999
            else:
                chemCode = int(R.chem_code)

            if  pd.isnull(R.site_code):
                #print ('null value')
                continue
            cropID=int(R.site_code)
        else:
            if  pd.isnull(R.commodity_code):
                #print ('null value')
                continue
            cropID=int(R.commodity_code)

            if  pd.isnull(R.commodity_code):
                #print ('null value')
                continue
            cropID=int(R.commodity_code)

            if year > 1983:
                if pd.isnull(R.chemical_code):
                    chemCode = -999
                else:
                    chemCode = int(R.chemical_code)
            else:
                if pd.isnull(R.chemical_no):
                    chemCode = -999
                else:
                    chemCode = int(R.chemical_no)

        if  pd.isnull(R.applic_dt):
            #print ('null value')
            continue
        else:
            date=R.applic_dt
            if constants.pre1990:              
                date=parseCalpipDate(date, year)
            try:
                test=str(date)
            except:
                print('date is not entered')
        try:
            region=findregionByTRS(TRS)
        except:
            #print('TRS is not in Found in Active Model Domain')
            continue
        

        if year<1990:
            if  pd.isnull(R.acre_unit_treated): 
                #print ('null value')
                continue
            acreage=float(R.acre_unit_treated)/100
        else:
            if  pd.isnull(R.acre_planted): 
                #print ('null value')
                continue
            acreage=float(R.acre_planted)
       

        if firstRead:
            fmt='%m/%d/%Y'
            day, month,year=extractDayMonthYear(date, fmt)
            firstRead=False
        try:
            crop=cropDict[cropID]
            cropExists=True
        except:
            cropExists=False
        if cropExists:
            crop=cropDict[cropID]
            crop.applicationDates.append(date)
            crop.acresPlanted.append(acreage)
            chemName=chemAlias[chemCode][1]
            try:
                crop.applicationChemical[TRS].append(chemName)
            except:
                crop.applicationChemical[TRS]=list()
                crop.applicationChemical[TRS].append(chemName)
            if not constants.pre1990:
                try:
                    crop.ranchIDs[ranchID][0].append(acreage)
                    crop.ranchIDs[ranchID][1].append(date)
                except: 
                    racres=list()
                    rapplicationDates=list()
                    crop.ranchIDs[ranchID]=[racres, rapplicationDates, region ]
                    crop.ranchIDs[ranchID][0].append(acreage)
                    crop.ranchIDs[ranchID][1].append(date)
                try:
                    crop.TRSs[TRS][0].append(acreage)
                    crop.TRSs[TRS][1].append(date)
                    crop.TRSs[TRS][2].append(ranchID)
                except:
                    tacres=list()
                    tapplicationDates=list()
                    tranches=list()
                    crop.TRSs[TRS]=[tacres, tapplicationDates, tranches, region]
                    crop.TRSs[TRS][0].append(acreage)
                    crop.TRSs[TRS][1].append(date)
                    crop.TRSs[TRS][2].append(ranchID)
                try:
                    crop.regions[region][0].append(acreage)
                    crop.regions[region][1].append(date)
                    crop.regions[region][2].append(ranchID) 
                except:
                    facres=list()
                    fapplicationDates=list()
                    franch=list()
                    crop.regions[region]=[facres, fapplicationDates, franch]
                    crop.regions[region][0].append(acreage)
                    crop.regions[region][1].append(date)
                    crop.regions[region][2].append(ranchID)   
            else:
                try:
                    crop.TRSs[TRS][0].append(acreage)
                    crop.TRSs[TRS][1].append(date)
                    #crop.applicationDates[TRS].append(chemCode)
                except:
                    tacres=list()
                    tapplicationDates=list()
                    tranches=list()
                    dum=999
                    crop.TRSs[TRS]=[tacres, tapplicationDates, dum, region]
                    crop.TRSs[TRS][0].append(acreage)
                    crop.TRSs[TRS][1].append(date)
                try:
                    crop.regions[region][0].append(acreage)
                    crop.regions[region][1].append(date)
                except:
                    facres=list()
                    fapplicationDates=list()
                    franch=list()
                    crop.regions[region]=[facres, fapplicationDates]
                    crop.regions[region][0].append(acreage)
                    crop.regions[region][1].append(date)
                         
        if not cropExists:
            crop = Crop()
            crop.cropID=cropID #same as site_code
            crop.year=year
            crop.name=cropAlias[cropID][1]
            crop.longName = cropAlias[cropID][0]
            crop.LUCategory = cropAlias[cropID][2]
            crop.planted=True
            crop.acresPlanted.append(acreage)
            crop.applicationDates.append(date)
            racres=list()
            rapplicationDates=list()
            facres=list()
            fapplicationDates=list()
            crop.applicationChemical[TRS]=list()
            crop.applicationChemical[TRS].append(chemCode)
            if not constants.pre1990:
                crop.ranchIDs[ranchID]=[racres, rapplicationDates, region]
                crop.ranchIDs[ranchID][0].append(acreage)
                crop.ranchIDs[ranchID][1].append(date)
                tranches=list()
                tacres=list()
                tapplicationDates=list()
                crop.TRSs[TRS]=[tacres, tapplicationDates, tranches]
                crop.TRSs[TRS][0].append(acreage)
                crop.TRSs[TRS][1].append(date)
                crop.TRSs[TRS][2].append(ranchID)
                franch=list()
                crop.regions[region]=[facres, fapplicationDates, franch]
                crop.regions[region][0].append(acreage)
                crop.regions[region][1].append(date)
                crop.regions[region][2].append(ranchID)
            else:
                tranches=list()
                tacres=list()
                tapplicationDates=list()
                crop.TRSs[TRS]=[tacres, tapplicationDates]
                crop.TRSs[TRS][0].append(acreage)
                crop.TRSs[TRS][1].append(date)
                crop.regions[region]=[facres, fapplicationDates]
                crop.regions[region][0].append(acreage)
                crop.regions[region][1].append(date)
            cropDict[cropID]=crop

        if crop.LUCategory=='Rotational to Group':
            if ranchID not in ranchLU:
                print "rotation to group"
                ranchLU.append(ranchID)
        if not constants.pre1990:
            day, month,year=extractDayMonthYear(date, fmt)
            try:
                ranchDict[ranchID][0][month][0].append(cropID)
                ranchDict[ranchID][0][month][1].append(acreage)
                ranchDict[ranchID][0][month][2].append(date)
            except:
                ranchDict=createRanchDict(ranchDict, ranchID)
                ranchDict[ranchID][0][month][0].append(cropID)
                ranchDict[ranchID][0][month][1].append(acreage)
                ranchDict[ranchID][0][month][2].append(date)
                ranchDict[ranchID][1]=region

    updateCropColors(cropDict)
    return cropDict, ranchDict

def parseCalpipDate(date, year):
    month=date[:2]
    day=date[2:4]
    year=str(year)
    #assert date[-1:]==year[-1:], 'year does not match'
    date=month+'/'+day+'/'+year
    return date

def filterCropDict(cropDict, year):
    print ("filtering crop data")
    fmt='%m/%d/%Y'
    test=list()# try this first with all crop groups then selected
    checkDict=dict()
    checkstr1=''
    checkstr2=''
    for cropIDX in cropDict.keys():
        crop=cropDict[cropIDX]
        group = crop.LUCategory
        filterGroup=constants.filterGroup 
        if group not in filterGroup: continue
        for TRS in crop.TRSs.keys():
            checkDict[TRS]=list()
            astor=list()
            dstor=list()
            daystor=list()
            monthstor=list()
            rstor=list()
            trsstor=list()
            chemstor=list()
            for idx in range (0, len(crop.TRSs[TRS][0])):
                day, month,year=extractDayMonthYear(crop.TRSs[TRS][1][idx], fmt)
                acre=crop.TRSs[TRS][0][idx]
                if not constants.pre1990:
                    ranch=crop.TRSs[TRS][2][idx]
                    checkstr1=str(ranch)+'_'+str(month)+'_'+str(acre)
                else:
                    checkstr1=str(TRS)+'_'+str(month)+'_'+str(acre)
                    ranch=0
                chemName=crop.applicationChemical[TRS][idx]
                if checkstr1 not in checkDict[TRS]:
                    checkDict[TRS].append(checkstr1)
                    trsstor.append(TRS)
                    daystor.append(day)
                    monthstor.append(month)
                    astor.append(acre)
                    dstor.append(crop.TRSs[TRS][1][idx])
                    rstor.append(ranch)
                    chemstor.append(crop.applicationChemical[TRS][idx])
            crop.TRSs[TRS][0]=(list(copy.deepcopy(astor)))
            crop.TRSs[TRS][1]=(list(copy.deepcopy(dstor)))
            if not constants.pre1990:
                crop.TRSs[TRS][2]=(list(copy.deepcopy(rstor)))
            test.append([crop.name, group, trsstor, rstor,dstor, daystor, monthstor, year, astor, chemstor])
    file=os.path.join(outputDirectory, str(year)+"cropFiltertest.txt")
    print("writing "+file)
    with open ( file, 'w') as fout:
        fout.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t'.format('CROP','group', 'TRS','ranch', 'date', 'day', 'month', 'year', 'acre', 'chem'))
        fout.write('\n')
        for value in xrange (0, len(test)):
            for item in xrange (0,len(test[value][2])):
                fout.write ('{0}\t{1}\t'.format(test[value][0],test[value][1]))
                fout.write ('{0}\t'.format(test[value][2][item]))
                fout.write ('{0}\t'.format(test[value][3][item]))
                fout.write ('{0}\t'.format(test[value][4][item]))
                fout.write ('{0}\t'.format(test[value][5][item]))
                fout.write ('{0}\t'.format(test[value][6][item]))
                fout.write ('{0}\t'.format(test[value][7]))
                fout.write ('{0}\t'.format(test[value][8][item]))
                fout.write ('{0}\t'.format(test[value][9][item]))
                fout.write ('\n')
    return cropDict

def writeAllApplications(year):
    print ("filtering crop data")
    fmt='%m/%d/%Y'
    test=list()
    with open (os.path.join(outputDirectory,str(year)+'ALL_Applications.txt'), 'w') as fout:
       print ('writing all applications')
       fout.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n'.format('CROP','group', 'TRS','ranch', 'date', 'day', 'month', 'year', 'acre', 'chem'))
       for cropIDX in cropDict.keys():
           crop=cropDict[cropIDX]
           group = crop.LUCategory
           for TRS in crop.TRSs.keys():
               astor=list()
               dstor=list()
               daystor=list()
               monthstor=list()
               rstor=list()
               trsstor=list()
               chemstor=list()
               for idx in range (0, len(crop.TRSs[TRS][0])):
                   day, month,year=extractDayMonthYear(crop.TRSs[TRS][1][idx], fmt)
                   acre=crop.TRSs[TRS][0][idx]
                   if not constants.pre1990:
                       ranch=crop.TRSs[TRS][2][idx]
                   else:
                       ranch=0
                   chemName=crop.applicationChemical[TRS][idx]
                   fout.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n'.format(crop.name, group, TRS, ranch, crop.TRSs[TRS][1][idx], day, month, year, acre, chemName))
    return
def filterRanchDict(ranchDict):
    #THIS FILTERS SO SAME RANCH PLOT MONTH NOT ADDED TO ACREAGE
    fmt='%m/%d/%Y'
    for ranch in ranchDict.keys():
        #ranchDict[ranchID][0][month][0].append(cropID)
        #ranchDict[ranchID][0][month][1].append(acreage)
        #ranchDict[ranchID][0][month][2].append(date)
        astor=list()
        dstor=list()
        rstor=list()
        for idx in range (0, len(ranchDict[ranchID][0][month][0])):
            day, month,year=extractDayMonthYear(ranchDict[ranchID][0][month][2][idx], fmt)
            acre=ranchDict[ranchID][0][month][1][idx]
            if idx < (len(ranchDict[ranchID][0][month][0])-1):
                day2, month2,year2=extractDayMonthYear(ranchDict[ranchID][0][month][2][idx+1], fmt)
                acre2=ranchDict[ranchID][0][month][1][idx+1]
                if month==month2 and acre==acre2:
                    continue
                else:
                    astor.append(acre)
                    dstor.append(ranchDict[ranchID][0][month][2][idx])
            else:
                astor.append(acre)
                dstor.append(ranchDict[ranchID][0][month][2][idx])
                rstor.append(ranch)   

#        crop.TRSs[TRS][0]=list(astor)
#        crop.TRSs[TRS][1]=list(dstor)
#        crop.TRSs[TRS][2]=list(rstor)
    return ranchDict

def createRanchDict(ranchDict, ranchID):
    #ranchDict[ranchID][0][month][0].append(cropID)
    #create ranch data structure
    monthCrop=dict()
    regionID=0
    if ranchID not in ranchDict.keys():
        for month in range(1,13):
            crops=list()
            acres=list()
            dates=list()
            monthCrop[month]=[crops, acres, dates]
        ranchDict[ranchID]=[monthCrop,regionID]
    return ranchDict

def createTRSDict(TRSLU,TRS):
    #ranchDict[ranchID][0][month][0].append(cropID)
    #create ranch data structure
    monthCrop=dict()
    regionID=0
    statList=['area', 'count', 'fraction']
    if TRS not in TRSLU.keys():
        for month in range(1,13):
            monthlyfractions=dict()
            monthCrop[month]=dict()
        monthCrop['total']=dict()
        monthCrop['period1']=dict() #this is the period over which cropped acreased will be aggregated
        monthCrop['period2']=dict()

        for key in monthCrop.keys():
            skipPeriod=False
            for cropIDX in cropDict.keys():
                if cropAlias[cropIDX][2] in selectedCropGroups:
                    group=cropAlias[cropIDX][2]
                    if key!='period1' and key !='period2':
                        skipPeriod=True
                    if skipPeriod:
                        monthCrop[key][cropIDX]=dict()
                        monthCrop[key][group]=dict()
                        for stat in statList:
                            monthCrop[key][cropIDX][stat]=0
                            monthCrop[key][group][stat]=0
                    else:
                        monthCrop[key][group]=dict()
                        for stat in statList:
                            monthCrop[key][group][stat]=0
        TRSLU[TRS]=[monthCrop,regionID]
    return TRSLU 

def aggregateByTRS(year, cropDict, cropAlias, selectedCropGroups, annualCrops, outFile1, outFile2, outFile3, outFile4):
    #THIS FUNCTION AGGREAGATES SELECTED CROPS INTO EACH TRS
    fmt='%m/%d/%Y'
    TRSLU=dict()
    groups=dict()
    writeGroup=True #whether to write output by group or crop
    #all crops with subannual rotation where fields could be reused
    for cropIDX in cropDict.keys():
        if cropAlias[cropIDX][2] in selectedCropGroups: #if this statement is removed and block shifted writes out all crop names
            crop=cropDict[cropIDX]
            group=cropAlias[cropIDX][2]
            for TRS in crop.TRSs.keys():
                TRSLU=createTRSDict(TRSLU,TRS)
                TRSLU[TRS][1]=primaryregionLookup[TRS]
                for month in xrange(1,13):
                    TRSLU[TRS][0][month][group]['area']=0
                for idx in range(0, len(crop.TRSs[TRS][1])):
                    try:
                        day, month,year=extractDayMonthYear(crop.TRSs[TRS][1][idx], fmt)
                    except:
                        print 'day month year has issue in aggregate by trs for '+ str(cropIDX)
                        print crop.name
                        print group,day, month,year

                    if cropIDX in TRSLU[TRS][0][month]: 
                        TRSLU[TRS][0][month][cropIDX]['area']+=crop.TRSs[TRS][0][idx]
                        TRSLU[TRS][0]['total'][cropIDX]['area']+=crop.TRSs[TRS][0][idx]
                        TRSLU[TRS][0]['total'][group]['area']+=crop.TRSs[TRS][0][idx]
                        TRSLU[TRS][0][month][group]['area']+=crop.TRSs[TRS][0][idx]
                        TRSLU[TRS][0][month][group]['count']+=1
                    else:
                        TRSLU[TRS][0][month][cropIDX]['area']=0.


    periods=['period1', 'period2']

    annualCropExists=dict()
    annualCropArea=dict()
    for group in selectedCropGroups:
        annualCropExists[group]=dict()
        annualCropArea[group]=dict()
        groupStore[year][group]=0.
        for TRS in TRSLU:
            annualCropExists[group][TRS]=False #these ciould be integrated with RSLU[TRS][0][month][group]['area'] as above at a later time
            annualCropArea[group][TRS]=dict()
            annualCropArea[group][TRS]['area']=0
    for TRS in TRSLU:
        groups[TRS]=dict()
        for month in range(1,13):
            if month <=6:
                period = periods[0]
            else:
                period = periods[1]
            sumAcres=0.0
            sumStore=dict()
            agWeight=1.0
            adjFraction=1.0
            adjFraction=agWeight*adjFraction
            groups[TRS][month]=list()
            for group in selectedCropGroups:
                if group in annualCrops:
                    if month==1: #check that crop does not exist for entire year
                        area = 0.
                        count= 0
                        for monthcheck in range(1,13):
                            if group in TRSLU[TRS][0][monthcheck].keys() and TRSLU[TRS][0][monthcheck][group]['area'] > 0.:
                                annualCropExists[group][TRS]=True
                                area+=TRSLU[TRS][0][monthcheck][group]['area']
                                if TRSLU[TRS][0][monthcheck][group]['area'] > 0.0 : count+=1
                        if annualCropExists[group][TRS]== True:
                            try:
                                if count > 0: annualCropArea[group][TRS]['area']=area/12 #count  #test this to keep overest_ area/count
                            except:
                                print ("test")
                if annualCropExists[group][TRS]==True:
                    TRSLU[TRS][0][month][group]['area']=annualCropArea[group][TRS]['area']
                    if TRSLU[TRS][0][month][group]['count']==0:
                        TRSLU[TRS][0][month][group]['count']=1
                    if group not in groups[TRS][month]: groups[TRS][month].append(group)
                    sumAcres+=annualCropArea[group][TRS]['area']
                elif group in TRSLU[TRS][0][month].keys():
                    if TRSLU[TRS][0][month][group]['area'] > 0:
                        sumAcres+=TRSLU[TRS][0][month][group]['area']
                        if group not in groups[TRS][month]: groups[TRS][month].append(group)
            for group in groups[TRS][month]:
                if sumAcres<=640 and sumAcres > 0.0 :
                    TRSLU[TRS][0][month][group]['count']+=1
                    TRSLU[TRS][0][month][group]['fraction']=TRSLU[TRS][0][month][group]['area']/640
                elif sumAcres > 640:
                    area = 640 * TRSLU[TRS][0][month][group]['area']/sumAcres
                    TRSLU[TRS][0][month][group]['area'] = area
                    TRSLU[TRS][0][month][group]['fraction'] = TRSLU[TRS][0][month][group]['area']/640
                    TRSLU[TRS][0][month][group]['count']+=1
                elif sumAcres == 0.0:
                    continue
                TRSLU[TRS][0][period][group]['area']+=TRSLU[TRS][0][month][group]['area']
                TRSLU[TRS][0][period][group]['count']+=1

    for TRS in TRSLU:
        for period in periods:
            sumAcres=0.
            plantedGroups=[x for x in TRSLU[TRS][0][period].keys() if TRSLU[TRS][0][period][x]['area'] > 0]
            for group in plantedGroups:
                print(TRS, period, group, str(sumAcres), str(TRSLU[TRS][0][period][group]['area']),str(TRSLU[TRS][0][period][group]['count']))
                sumAcres+=TRSLU[TRS][0][period][group]['area']
            for group in plantedGroups:
                if sumAcres<=640 and sumAcres > 0.0 :
                    try:
                        if group in annualCrops:
                            TRSLU[TRS][0][period][group]['fraction']=(TRSLU[TRS][0][period][group]['area'])/640.
                        else:
                            TRSLU[TRS][0][period][group]['fraction']=(TRSLU[TRS][0][period][group]['area'])/640. #
                        groupStore[year][group]+=TRSLU[TRS][0][period][group]['fraction']*640
                    except:
                        print ('test')
                elif sumAcres > 640:
                    area = 640 * TRSLU[TRS][0][period][group]['area']/sumAcres
                    TRSLU[TRS][0][period][group]['area'] = area
                    if group in annualCrops:
                        TRSLU[TRS][0][period][group]['fraction'] = (TRSLU[TRS][0][period][group]['area'])/640.
                    else:
                        TRSLU[TRS][0][period][group]['fraction'] = (TRSLU[TRS][0][period][group]['area'])/640.
                    groupStore[year][group]+=TRSLU[TRS][0][period][group]['fraction']*640      
                elif sumAcres == 0.0:
                    continue        
    with open (outFile1, 'w') as fout:
        for TRS in TRSLU:
            region=primaryregionLookup[TRS]
            for month in range (1,13):
                fout.write ('{0}\t{1}\t{2}\t'.format(region, TRS, month))
                if writeGroup:
                    for group in groups[TRS][month]:
                        try:
                            if TRSLU[TRS][0][month][group]['area']>0.0:
                                fout.write('{0}\t'.format(group))
                                fout.write('{:.4f}\t'.format(TRSLU[TRS][0][month][group]['area']))
                        except:
                            print "check"
                else:
                    for cropIDX in TRSLU[TRS][0][month].keys():
                        cropName=cropAlias[cropIDX][1]
                        fout.write('{0}\t'.format(cropName))
                        fout.write('{:.4f}\t'.format(TRSLU[TRS][0][month][cropIDX]['area']))
                fout.write('\n')

    with open (outFile2, 'w') as fout: #%area each month
        for TRS in TRSLU:
            region=primaryregionLookup[TRS]
            for month in range (1,13):
                sumAcres=0.
                fout.write ('{0}\t{1}\t{2}\t'.format(region, TRS, month))
                if writeGroup:
                    for group in groups[TRS][month]: #*** limit these to planted groups
                        if TRSLU[TRS][0][month][group]['fraction'] > 0.0:
                            fout.write('{0}\t'.format(group))
                            fout.write('{:.4f}\t'.format((TRSLU[TRS][0][month][group]['fraction'])))
                else:
                    for cropIDX in TRSLU[TRS][0][month].keys():
                        if TRSLU[TRS][0][month][cropIDX]['fraction'] > 0.0:
                            cropName=cropAlias[cropIDX][1]
                            fout.write('{0}\t'.format(cropName))
                            fout.write('{:.4f}\t'.format(TRSLU[TRS][0][month][cropIDX]['fraction']))
                fout.write('\n')
                             
    with open (outFile3, 'w') as fout: #%total area
        for TRS in TRSLU:
            oneGroup=False #this indicates whether at least one group is in 
            region=primaryregionLookup[TRS]
            fout.write ('{0}\t{1}\t'.format(region, TRS))
            sumTotal=0.
            groupList=[]
            if writeGroup:
                for group in TRSLU[TRS][0]['total'].keys():
                        sumTotal+=TRSLU[TRS][0]['total'][group]['area']
                        groupList.append(group)
                for group in groupList:#*** limit these to planted groups
                    if sumTotal > 0.0:
                        fout.write('{0}\t'.format(group))
                        if sumTotal > 640*12.:
                           print (str(sumTotal))
                           print('sumTotal > 7680')
                           sumTotal=7680 
                        fout.write('{:.4f}\t'.format(TRSLU[TRS][0]['total'][group]['area']/sumTotal))
            else:
                for cropIDX in TRSLU[TRS][0]['total'].keys(): #compute total sum
                    sumTotal+=TRSLU[TRS][0]['total'][cropIDX]['area']
                for cropIDX in TRSLU[TRS][0]['total'].keys():
                    if sumTotal > 0.0:
                        cropName=cropAlias[cropIDX][1]
                        fout.write('{0}\t'.format(cropName))
                        fout.write('{:.4f}\t'.format(TRSLU[TRS][0]['total'][cropIDX]['area']/sumTotal))
                fout.write('\n')

    for month in constants.CAF[1]:
        headers=['Region', 'TRS']
        nRotCrop=21
        for  i in range(1, nRotCrop+1):
            headers.append('CROP'+str(i))
            headers.append('ACRE'+str(i))
        outFile=outFile4 + '_'+str(month)+'.txt'         
        with open (outFile, 'w') as fout: #%total area
            for idx in range (0, len(headers)):
                fout.write('%s' % headers[idx]+'\t')
            fout.write('\n')
            for TRS in TRSLU:
                #oneGroup=False
                region=primaryregionLookup[TRS]
                if len(TRSLU[TRS][0]['total'].keys())>0: #TRS has selected crop groups
                    fout.write ('{0}\t{1}\t'.format(region, TRS))
                    sumAcres=0.
                    if writeGroup: #cropIDx logic is not been tested in here...todo check that sum <=1.0
                        for group in selectedCropGroups:
                            if group in TRSLU[TRS][0][month].keys() and TRSLU[TRS][0][month][group]['fraction']>0.:
                                fout.write('{0}\t'.format(group))
                                fout.write('{:.4f}\t'.format(TRSLU[TRS][0][month][group]['fraction']))
                    else:
                        for cropIDX in TRSLU[TRS][0][month].keys():
                            if cropIDX not in selectedCropGroups:
                                cropName=cropAlias[cropIDX][1]
                                fout.write('{0}\t'.format(cropName))
                                fout.write('{:.4f}\t'.format(TRSLU[TRS][0][month][cropIDX]['fraction']))
                    fout.write('\n')
    return TRSLU   

def cropRotationFrequency(df):
    #This function plots crop frequency by month by region
    #this assumes that writeacres is false in writeRotationsbyregion function
    regionList=list()   
    for index, R in df.iterrows():
        if R.Region not in regionList:
            regionList.append(R.Region)
    for region in regionList:
        valueContainers=list()
        monthDict=dict()
        cropList=list()
        for month in range(1,13):
            monthDict[month]=dict()
        plotFile=os.path.join(plotDirectory,str(year)+" region "+str(region)+ "monthlyFrequency.png")
        newDF=df[df['Region']==region]
        test=[newDF[c].value_counts() for c in list(newDF.select_dtypes(include=['O']).columns)]
        month=0
        for idx in range(2, len(test)):
            month+=1
            item=test[idx]
            for idx2 in range (0,len(item)):
                crop=item.index[idx2]
                freq=float(item[idx2])/float(newDF.shape[0])  
                monthDict[month][crop]=freq
        for month in range(1,13): #determine names of ind crops/groups
            for key in monthDict[month].keys():
                if key not in cropList:
                    cropList.append(key)
        if len(cropList)>4: print("more than 4 crops in month")
        #to remove fallow items from plot
        cropList.remove('-999')
        for crop in cropList:
            values=list()
            errors=list()
            for month in range(1,13):
                if crop in monthDict[month].keys():
                    values.append(monthDict[month][crop])
                    errors.append(0.0) 
                else:
                    values.append(0.0)
                    errors.append(0.0) 
            valueContainers.append([values, errors])
        varNames=range(1,13)
        row=(len(cropList)+len(cropList)%2)/2
        panelBarPlot (len(cropList),2, row, valueContainers, plotFile, varNames, cropList, varNames)     
 
def writeRotationsbyregion(cropDict, outFile):
    #if limitation of acreage is desired will have to pull lines from version 204?
    fmt='%m/%d/%Y'
    months=[1,2,3,4,5,6,7,8,9,10,11,12]
    cropGroup=['Rotational to Group','Celery, Green Beans-Squash-Cucumbers-Tomatoes', 'Root vegetable group', 'Onions, Garlic, Corn']
    cropGroup2=['Rotational 30 Day', 'Lettuce','Crucifers','Celery, Melons, Beans, and Squash','Tomato','Cucumber']
    ranchList=list()
    writeAcres=False
    printByGroup=True
    noValueString=-999
    with open (outFile,'w') as fout:
        if writeAcres:
            headers=['Region','Ranch',' Crop', ' Acres'] #this version writes out acres and dates too write i version out like this in future
        else:
            headers=['Region','Ranch',' Crop']
        fout.write(headers[0]+"\t"+headers[1]+"\t")
        for idx in range(1,13):
            for idx2 in range (2,len(headers)):
                fout.write(str(idx)+headers[idx2]+"\t")
        fout.write('\n')
        for region in range (1,32):
            for ranch in ranchDict.keys():
                if ranchDict[ranch][1]==region:
                    monthDict=dict()
                    cropAdded=False
                    for month in months:
                        crops=list()
                        cropIDXList=list()
                        acres=list()
                        date=list()

                        if len(ranchDict[ranch][0][month][0]) > 0:
                            tempDict=dict()
                            for idx in range (0, len(ranchDict[ranch][0][month][0])):#for the number of crops in that month
                                cropIDX=ranchDict[ranch][0][month][0][idx]
                                crop=cropDict[cropIDX]
                                if printByGroup:
                                    if cropAlias[cropIDX][2] in selectedCropGroups:#print out crop group instead of crop name
                                       if cropIDX in tempDict.keys():
                                           tempDict[cropIDX].append(ranchDict[ranch][0][month][1][idx])
                                       else:
                                           tempDict[cropIDX]=list()
                                       if idx==len(ranchDict[ranch][0][month][0])-1: #last time in loop
                                            for idx2 in tempDict.keys():
                                                cropAdded=True
                                                crops.append(cropAlias[cropIDX][2])
                                                acres.append(sum(tempDict[cropIDX]))
                                                #date.append(ranchDict[ranch][0][month][2][idx])
                                else:
                                    if crop.LUCategory in cropGroup: #crop in LU category **** this needs to be fixed im sure
                                       if cropIDX in tempDict.keys():
                                           tempDict[cropIDX].append(ranchDict[ranch][0][month][1][idx])
                                       else:
                                           tempDict[cropIDX]=list()
                                       if idx==len(ranchDict[ranch][0][month][0])-1: #last time in loop
                                            for idx2 in tempDict.keys():
                                                cropAdded=True
                                                crops.append(crop.name)
                                                acres.append(sum(tempDict[cropIDX]))
                                                #date.append(ranchDict[ranch][0][month][2][idx])
                        else:
                            crops.append(noValueString)
                            acres.append(noValueString)
                            #date.append(" ")

                        #monthDict[month]=[crops, acres, date]
                        monthDict[month]=[crops, acres]
                    maxCrop=0
                    for month in months:
                        if len(monthDict[month][0])>maxCrop:
                            maxCrop=len(monthDict[month][0])
                    if cropAdded:
                        for idx in range(0, maxCrop):
                            count=0
                            fout.write('{0}\t{1}\t'.format(region, ranch))
                            for month in months:
                                if len(monthDict[month][0])>0 and idx<= len(monthDict[month][0])-1 :
                                    name = monthDict[month][0][idx]
                                    acres = monthDict[month][1][idx]
                                    #date = monthDict[month][2][idx]
                                    if writeAcres:
                                        fout.write('{0}\t{1}\t'.format(name, acres))
                                    else:
                                        fout.write('{0}\t'.format(name))
                                else:
                                    for idx2 in range (0, maxCrop):
                                        name=noValueString
                                        acres=noValueString
                                        date=noValueString
                                    if writeAcres:
                                        fout.write('{0}\t{1}\t'.format(name, acres))
                                    else:
                                        fout.write('{0}\t'.format(name))
                        
                                if count==len(monthDict[month][0])and count<maxCrop: #Check these bounds
                                    for idx3 in range (count, maxCrop+1):
                                        name=noValueString
                                        acres=noValueString
                                        date=noValueString
                            fout.write('\n')
                            count+=1

    return
 
def writeRotationsbyregion1974(cropDict, outFile):#######REWRITE#####
    #if limitation of acreage is desired will have to pull lines from version 204?
    fmt='%m/%d/%Y'
    months=[1,2,3,4,5,6,7,8,9,10,11,12]
    cropGroup=['Rotational to Group','Celery-Green Beans-Squash-Cucumbers-Tomatoes', 'Root vegetable group', 'Onions, Garlic, Corn']
    cropGroup2=['Rotational 30 Day', 'Lettuce','Crucifers','Celery, Melons, Beans, and Squash','Tomato','Cucumber']
    ranchList=list()
    writeAcres=False
    printByGroup=True
    noValueString=-999
    with open (outFile,'w') as fout:
        if writeAcres:
            headers=['Region', 'TRS',' Crop', ' Acres'] #this version writes out acres and dates too write i version out like this in future
        else:
            headers=['Region','TRS', 'Crop']
        fout.write(headers[0]+"\t"+headers[1]+"\t")
        for idx in range(1,13):
            for idx2 in range (2,len(headers)):
                fout.write(str(idx)+headers[idx2]+"\t")
        fout.write('\n')
        for region in range (1,32):
            for TRS in TRSLU.keys():
                if TRSLU[TRS][1]==region:
                    monthDict=dict()
                    cropAdded=False
                    for month in months:
                        crops=list()
                        cropIDXList=list()
                        acres=list()
                        date=list()
                        try:
                            test=TRSLU[TRS][0][month][0]
                        except:
                            print('test')
                        if len(TRSLU[TRS][0][month][0]) > 0:
                            tempDict=dict()
                            for idx in range (0, len(TRSLU[TRS][0][month][0])):#for the number of crops in that month
                                cropIDX=TRSLU[TRS][0][month][0][idx]
                                crop=cropDict[cropIDX]
                                if printByGroup:
                                    if cropAlias[cropIDX][2] in selectedCropGroups:#print out crop group instead of crop name
                                       if cropIDX in tempDict.keys():
                                           tempDict[cropIDX].append(TRSLU[TRS][0][month][1][idx])
                                       else:
                                           tempDict[cropIDX]=list()
                                       if idx==len(TRSLU[TRS][0][month][0])-1: #last time in loop
                                            for idx2 in tempDict.keys():
                                                cropAdded=True
                                                crops.append(cropAlias[cropIDX][2])
                                                acres.append(sum(tempDict[cropIDX]))
                                                #date.append(ranchDict[ranch][0][month][2][idx])
                                else:
                                    if crop.LUCategory in cropGroup: #crop in LU category **** this needs to be fixed im sure
                                       if cropIDX in tempDict.keys():
                                           tempDict[cropIDX].append(TRSLU[TRS][0][month][1][idx])
                                       else:
                                           tempDict[cropIDX]=list()
                                       if idx==len(TRSLU[TRS][0][month][0])-1: #last time in loop
                                            for idx2 in tempDict.keys():
                                                cropAdded=True
                                                crops.append(crop.name)
                                                acres.append(sum(tempDict[cropIDX]))
                                                #date.append(ranchDict[ranch][0][month][2][idx])
                        else:
                            crops.append(noValueString)
                            acres.append(noValueString)
                            #date.append(" ")

                        #monthDict[month]=[crops, acres, date]
                        monthDict[month]=[crops, acres]
                    maxCrop=0
                    for month in months:
                        if len(monthDict[month][0])>maxCrop:
                            maxCrop=len(monthDict[month][0])
                    if cropAdded:
                        for idx in range(0, maxCrop):
                            count=0
                            fout.write('{0}\t{1}\t'.format(region, TRS))
                            for month in months:
                                if len(monthDict[month][0])>0 and idx<= len(monthDict[month][0])-1 :
                                    name = monthDict[month][0][idx]
                                    acres = monthDict[month][1][idx]
                                    #date = monthDict[month][2][idx]
                                    if writeAcres:
                                        fout.write('{0}\t{1}\t'.format(name, acres))
                                    else:
                                        fout.write('{0}\t'.format(name))
                                else:
                                    for idx2 in range (0, maxCrop):
                                        name=noValueString
                                        acres=noValueString
                                        date=noValueString
                                    if writeAcres:
                                        fout.write('{0}\t{1}\t'.format(name, acres))
                                    else:
                                        fout.write('{0}\t'.format(name))
                        
                                if count==len(monthDict[month][0])and count<maxCrop: #Check these bounds
                                    for idx3 in range (count, maxCrop+1):
                                        name=noValueString
                                        acres=noValueString
                                        date=noValueString
                            fout.write('\n')
                            count+=1
    return 

def updateCropColors(cropDict):
    if constants.firstTime:
        for cropID in sorted(cropDict.keys()):
            if cropDict[cropID].planted:
                cropDict[cropID].color=constants.getUniqueColor()
                constants.cropColors[cropID]=cropDict[cropID].color
            else:
                print ("crop is not planted but is in list")
                constants.checkFlag=True
                cropDict[cropID].color='k'
    else:
        for cropID in sorted(cropDict.keys()):
            if cropID in constants.cropColors.keys():
                cropDict[cropID].color=constants.cropColors[cropID]
            else:
                cropDict[cropID].color=constants.getUniqueColor()
                constants.cropColors[cropID]=cropDict[cropID].color
    return 

def cropStatistics(cropDict):
    for key in cropDict.keys():
        updateFirstDay(cropDict[key])
        updateLastDay(cropDict[key])
    return

def computeregionStatistics(cropDict, statsFile):
    #this function creates a table of YEAR region CROP FIRST_APP_DAY FIRST_APP_DATE LAST_APP_DAY LAST_APP_DAY
    regionStats=dict()
    fmt='%m/%d/%Y'
    for cropIDX in cropDict.keys():
        crop=cropDict[cropIDX]
        for region in crop.regions.keys():
            climate=regionClimateLookup[region]
            if region not in regionStats.keys():
                regionStats[region]=dict()
            if crop.LUCategory not in regionStats[region].keys():
                regionStats[region][crop.LUCategory]=list()
            d=crop.regions[region][1]
            #sort date list
            dsort=sorted(d, key=lambda x: datetime.datetime.strptime(x, fmt))
            firstDate=dsort[0]
            day,month, year=extractDayMonthYear(firstDate,fmt)
            minJulianDay=extractDayOfYear(firstDate, fmt)
            lastDate=dsort[-1]
            day2,month2, year2=extractDayMonthYear(lastDate,fmt)
            if year!= year2:
                print "check data"
            maxJulianDay=extractDayOfYear(lastDate, fmt)
            regionStats[region][crop.LUCategory].append([crop.name,minJulianDay,firstDate, maxJulianDay,lastDate, climate])
    #statsFile=os.path.join(outDirectory, 'regionStats.txt')
    if os.path.exists(statsFile):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not
    with open(statsFile, append_write) as fout:
        headers=['YEAR', 'REGION', 'LU', 'CROP', 'FIRST_APP_DAY', 'FIRST_APP_DATE','LAST_APP_DAY', 'LAST_APP_DAY', 'CLIMATE']
        if append_write=='w':
            for idx in range (0, len(headers)):
                fout.write('%s' % headers[idx]+'\t')
        for region in regionStats.keys():
            for LU in regionStats[region].keys():
                for idx in range (0, len(regionStats[region][LU])):
                    fout.write('{0}\t{1}\t{2}\t'.format(year, region, LU))
                    for idx2 in range(0, len(regionStats[region][LU][idx])):
                        fout.write('%s' % regionStats[region][LU][idx][idx2]+'\t')
                    fout.write('\n')

def readregionTRSTable(FILE):
    regionLookup=dict()
    regionClimateLookup=dict()
    TRSClimateLookup=dict()
    DTYP={}
    #DTYP['CELLNUM'    ] =np.int32
    DTYP['TRS'        ] =str
    DTYP['REGION_ID'    ] =np.int32
    DTYP['ZONE_IHM'   ] =np.int32
    df = pd.read_csv(FILE,dtype=DTYP)
    for index, R in df.iterrows():
        if  pd.isnull(R.TRS):
            print ('null value for township and range skipping row')
            continue
        if  R.REGION_ID in [0,31]:
            #print ('region ID '+str(R.REGION_ID)+' is not being evaluated')
            continue
        regionLookup[R.TRS]=R.REGION_ID
        regionClimateLookup[R.REGION_ID]=R.ZONE_IHM #not used yet but in table
        TRSClimateLookup[R.TRS]=R.ZONE_IHM
    return regionLookup, regionClimateLookup, TRSClimateLookup

def findregionByTRS(TRS):
    if TRS in primaryregionLookup.keys():
        region=primaryregionLookup[TRS]
    return region

def getCrop(cropID):
    crop=cropDict(cropID)
    return Crop

def readAlias(aliasFile1, aliasFile2):
    cropAlias1974=dict()
    cropAlias1990=dict()
    cropGroups=dict()
    groupColors=dict()
    #todo relate site code to crop name and alias.... eg. alias[sitecode]=[cropname, simplified cropname]
    count=0
    # read aliases into memory
    with open (aliasFile1, 'r') as fin:
        for line in fin:
            count+=1
            words = [tok.strip() for tok in line.split(",")]
            if len(words) == 0 or count==1:
                continue
            else:
               cropAlias1990[int(words[0].strip())]=[words[1].strip(), words[2].strip(), words[3].strip()] #words{1]= crop name DB words{2]= cropNamePlot words{3]=LU_category
    cropAlias1974=copy.deepcopy(cropAlias1990)
    with open (aliasFile2, 'r') as fin:
        count=0
        for line in fin:
            count+=1
            words = [tok.strip() for tok in line.split(",")]
            if len(words) == 0 or count==1:
                continue
            else:
               cropAlias1974[int(words[0].strip())]=[words[1].strip(), words[2].strip(), words[3].strip()] #words{1]= crop name DB words{2]= cropNamePlot words{3]=LU_category
    for cropIDX in cropAlias1990.keys():
        groupName=cropAlias1990[cropIDX][2] 
        if groupName not in cropGroups.keys():
            cropGroups[groupName]=list()
            groupColors[groupName]='k'
        cropGroups[groupName].append(cropIDX)
    return cropAlias1974, cropAlias1990, cropGroups, groupColors

def readChemicalAlias(aliasFile):
    chemicalAlias=dict()
    count=0
    # read aliases into memory
    with open (aliasFile, 'r') as fin:
        for line in fin:
            count+=1
            words = [tok.strip() for tok in line.split(",")]
            if len(words) == 0 or count==1:
                continue
            else:
               chemicalAlias[int(words[0].strip())]=[words[1].strip(), words[2].strip()] 
               #words{1]= chem group words{2]= chemName
    return chemicalAlias

def aggregateByDate():
    return

def aggregateByregion(cropDict, cropAlias, year):
    #this function aggregates crop acreage by month
    print 'Aggregating data by region for all crops'
    regionDict=dict() #data structure not filled out...
    plotDict=dict()
    regionList=list()
    for regionID in range (1, 32):
        plotDict[regionID]=TimeSeries(os.path.join (constants.plotDirectory,str(year)+'CropAcresregion_'+str(regionID)+'.png'),processor='Crop1')
    for cropIDX in cropDict.keys():
        if cropIDX in constants.skipList:
            continue
        crop=cropDict[cropIDX]
        monthAcres=dict()
        times=list()
        values=list()
        for key in sorted(crop.regions.keys()):
            if key not in regionList:
                regionList.append(key)
            for month in range(1,13):
                monthAcres[month]=list()
            for idx in range(0, len(crop.regions[key][0])):
                acres=crop.regions[key][0][idx]
                time=crop.regions[key][1][idx]
                fmt='%m/%d/%Y'
                #try:
                day, month, year=extractDayMonthYear(time, fmt)
                #except:
                #    print('test')
                if year>=1990:
                    ranch=crop.regions[key][2][idx]
                    #test acreage
                    for idx2 in (0, idx):
                        acres2=crop.regions[key][0][idx2]
                        time2=crop.regions[key][1][idx2]
                        ranch2=crop.regions[key][2][idx2]
                        day2, month2,year2=extractDayMonthYear(time2, fmt)
                        if month2==month and ranch2==ranch and acres2==acres:
                            if idx == idx2:
                                continue
                            else:
                                #print("pesticide applied same ranch same month same acreage")
                                continue
                        else:                           
                            try:
                                monthAcres[month].append(acres) 
                            except:
                                constants.checkFlag=True
                                print('Issue with acres in aggregate regions')
                else:
                    try:
                        monthAcres[month].append(acres) 
                    except:
                        constants.checkFlag=True
                        print('Issue with acres in aggregate regions')
            for month in monthAcres.keys():
                if len(monthAcres[month])==0:
                    monthAcres[month]=0.
                else:
                    monthAcres[month]=sum(monthAcres[month]) 
            for month in sorted(monthAcres.keys()):
                times.append(month)
                values.append(monthAcres[month]/100) 
                acreContainer = TimeStepValueContainer(crop.color, caseNum=cropIDX)
                acreContainer.populate_valueContainer(times, values)
            plotDict[key].addPlotData(acreContainer, cropAlias[cropIDX][1]) 
    for regionID in sorted(regionList):
        plotDict[regionID].generatePlot('Region '+str(regionID)+' Total Crop Acreage')
    return

def aggregateByregionGroup(cropDict, cropAlias, cropGroups, year):
    # THIS FUNCTION DOES NOT GENERATE PLOTS PROPERLY
    #this function aggregates crop acreage by month and crop group... need to modify this further...
    print 'Aggregating data by region for all crop groups'
    regionDict=dict() #data structure not filled out...
    plotDict=dict()
    regionList=list()
    for regionID in range (1, 32):
        path=r'D:\LandUse\CalPIP\Data\Before1990\Output'
        plotDict[regionID]=TimeSeries(os.path.join(constants.plotDirectory,(str(year)+'CropAcresregionGrouped_'+str(regionID)+'.png')),processor='Crop1')
        for group in cropGroups.keys(): # for each crop
            monthAcres=dict()
            times=list()
            values=list()
            for cropIDX in cropGroups[group]:
                if cropIDX in constants.skipList:
                    continue
                if cropIDX not in cropGroups[group]:
                    continue
                if cropIDX not in cropDict.keys():
                    continue
                try:
                    crop=cropDict[cropIDX]
                except:
                    print('test')
                if regionID not in crop.regions.keys():
                    continue
                if groupColors[group]=='k':
                    groupColors[group]=crop.color
                for month in range(1,13):
                    monthAcres[month]=list()
                for idx in range(0, len(crop.regions[regionID][0])): #for region in crop
                    acres=crop.regions[regionID][0][idx]
                    time=crop.regions[regionID][1][idx]
                    fmt='%m/%d/%Y'
                    day, month,year=extractDayMonthYear(time, fmt)
                    if year>=1990:
                        ranch=crop.regions[regionID][2][idx]
                        #test acreage
                        for idx2 in (0, idx):
                            acres2=crop.regions[regionID][0][idx2]
                            time2=crop.regions[regionID][1][idx2]
                            ranch2=crop.regions[regionID][2][idx2]
                            day2, month2,year2=extractDayMonthYear(time2, fmt)
                            if month2==month and ranch2==ranch and acres2==acres:
                                if idx == idx2:
                                    continue
                                else:
                                    #print("pesticide applied same ranch same month same acreage")
                                    continue
                            else:                           
                                try:
                                    monthAcres[month].append(acres) 
                                except:
                                    constants.checkFlag=True
                                    print('Issue with acres in aggregate regions')
                    else:                           
                        try:
                            monthAcres[month].append(acres) 
                        except:
                            constants.checkFlag=True
                            print('Issue with acres in aggregate regions')
                for month in monthAcres.keys():
                    if len(monthAcres[month])==0:
                        monthAcres[month]=0.
                    else:
                        monthAcres[month]=sum(monthAcres[month]) 
                if len(monthAcres.keys())>0:
                    for month in sorted(monthAcres.keys()):
                        times.append(month)
                        values.append(monthAcres[month]/100) 
                        acreContainer = TimeStepValueContainer(groupColors[group], caseNum=group)
                        acreContainer.populate_valueContainer(times, values)
                    plotDict[regionID].addPlotData(acreContainer, cropAlias[cropIDX][2]) 
    for regionID in range(1,32):
        plotDict[regionID].generatePlot('Region '+str(regionID)+' Total Crop Acreage By Crop Group')
    return

def aggregateByLU(cropDict, cropAlias, year):
    #this function aggregates crop acreage by land use, month, and region 
    LUList=constants.LULIST
    regionDict=dict()
    plotDict=dict()
    #to enable plotting for all LU categories
    #for cropID in cropDict.keys():
    #    if cropDict[cropID].LUCategory not in LUList:
    #        LUList.append(cropDict[cropID].LUCategory)
    for regionID in range (1, 32):
        for LU in LUList:
            plotIDX=str(regionID)+" "+LU
            plotAdded=False
            for cropIDX in cropDict.keys():
                if cropIDX in constants.skipList:
                    continue
                if cropAlias[cropIDX][2]!=LU:
                    continue
                crop=cropDict[cropIDX]
                if regionID in sorted(crop.regions.keys()):
                    if crop.LUCategory==LU:
                        if not plotAdded:
                            plotDict[plotIDX]=TimeSeries(os.path.join(constants.plotDirectory, str(year)+LU+'_Acresregion_'+str(regionID)+'.png'),processor='Crop1')
                            plotAdded=True
                        if cropIDX==70: print ('check')
                        monthAcres=dict()
                        times=list()
                        values=list()
                        for month in range(1,13):
                            monthAcres[month]=list()
                        for idx in range(0, len(crop.regions[regionID][0])):
                            acres=crop.regions[regionID][0][idx]
                            time=crop.regions[regionID][1][idx]
                            fmt='%m/%d/%Y'
                            try:
                                day, month, test=extractDayMonthYear(time, fmt)
                            except:
                                print('check value')
                            if test>=1990:
                                ranch=crop.regions[regionID][2][idx]
                                for idx2 in (0, idx):
                                    acres2=crop.regions[regionID][0][idx2]
                                    time2=crop.regions[regionID][1][idx2]
                                    ranch2=crop.regions[regionID][2][idx2]
                                    day2, month2,year2=extractDayMonthYear(time2, fmt)
                                    if month2==month and ranch2==ranch and acres2==acres:
                                        if idx == idx2:
                                            continue
                                        else:
                                            #print("pesticide applied same ranch same month same acreage")
                                            continue
                                    else:                           
                                        try:
                                            monthAcres[month].append(acres) 
                                        except:
                                            print('check')
                            else:                           
                                try:
                                    monthAcres[month].append(acres) 
                                except:
                                    print('check')
                        for month in monthAcres.keys():
                            if len(monthAcres[month])==0:
                                monthAcres[month]=0.
                            else:
                                monthAcres[month]=sum(monthAcres[month])
                        sumcheck=0
                        for month in sorted(monthAcres.keys()):
                            times.append(month)
                            values.append(monthAcres[month]/100)
                            sumcheck+=monthAcres[month]
                        if sumcheck>0.:
                            acreContainer = TimeStepValueContainer(crop.color, caseNum=cropIDX)
                            acreContainer.populate_valueContainer(times, values)
                            try:
                                plotDict[plotIDX].addPlotData(acreContainer, crop.name) 
                            except:
                                print ('uggh')

    for regionID in sorted(plotDict.keys()):
        plotDict[regionID].generatePlot('Region '+str(regionID)+' Total Group Acreage')
    return

def extract(infile):
    #this function extracts a 10000 line portion of the gridded output for debugging
    linestore=list()
    outfile=os.path.join(basePath, 'extract.out')
    linecount=0
    with open(infile, 'r') as fin:
        for line in fin:
            linecount+=1
            if linecount==10000:
                break
            linestore.append(line)
    with open(outfile, 'w') as fout:
        for idx in range(0, len(linestore)):
            fout.write(linestore[idx])
            #fout.write('\n')

def getMonth(date):
    return
def getDeltaDays(date1,date2):
    return

def aggregateByRanch():
    return

def writeTestOutput(outFile, cropDict): #currently cropDicted by TRS
    #current just as debug..
    TRS='18S06E02'
    outFile=outFile.strip('.txt')
    cropID=13005
    regionIDs=[1, 2, 3, 8, 9, 10, 11]
    for regionID in regionIDs:
        file=outFile+'_'+str(regionID)+'.txt'
        data=cropDict[cropID].regions[regionID]
    
        with open(file, 'w') as fout:
            #print data[0]
            #print data[1]
            fout.write('ACREAGE'+'\t')
            fout.write('DATE'+'\t')
            fout.write('RANCHID'+'\t')
            #fout.write('CROP4'+'\t')
            #fout.write('CROP5'+'\t')
            #fout.write('CROP6'+'\t')
            #fout.write('CROP7'+'\t')
            #fout.write('CROP8'+'\t')
            #fout.write('CROP9'+'\t')
            #fout.write('CROP10'+'\t')
            fout.write('\n')
            #for idx in range (0, len(data[0])):
            #    value=data[0][idx]
            #    fout.write('%s' %value+'\t')
            #fout.write('\n')
            #for idx in range (0, len(data[1])):
            #    value=data[1][idx]
            #    fout.write('%s' %value+'\t')
            #fout.write('\n')
            #for idx in range (0, len(data[2])):
            #    value=data[2][idx]
            #    fout.write('%s' %value+'\t')
            #fout.write('\n')
            for idx in range (0, len(data[2])):
                value=data[0][idx]
                value1=data[1][idx]
                value2=data[2][idx]
                fout.write('{0}\t{1}\t{2}\n'.format(value, value1, value2))
            fout.write('\n')



            #for idx in range (0, len(data)):
            #    crop=data[idx]
            #    fout.write('%s' %crop.lastDay+'\t')
            #    fout.write('\n')

    return

def updateFirstDay(crop):
    fmt = '%m/%d/%Y'
    applicationDays=list()
    for date in crop.applicationDates:
        day=extractDayOfYear(date, fmt)
        applicationDays.append(day)
    crop.firstDay=min(applicationDays)
    return

def updateLastDay(crop):
    fmt = '%m/%d/%Y'
    applicationDays=list()
    for date in crop.applicationDates:
        day=extractDayOfYear(date, fmt)
        applicationDays.append(day)
    crop.lastDay=max(applicationDays)
    return

def extractDayOfYear(dateString, fmt):
    date = datetime.datetime.strptime(dateString, fmt)
    tt = date.timetuple()
    day = tt.tm_yday
    return day

def extractDayMonthYear(dateString, fmt):
    import calendar
    checkList=['02/29', '06/31']
    #this assumes'/' spearated with month day year
    if '02/29' in dateString:
        test=dateString.split('/')
        y=int(test[2])
        if not calendar.isleap(y):
            month=2
            day=28
            year=y
        else:
            month=2
            day=29
            year=y            
    elif '06/31' in dateString:
        test=dateString.split('/')
        y=int(test[2])
        month=6
        day=30
        year=y
    else:
        try:
            date = datetime.datetime.strptime(dateString, fmt)
            month=date.month
            year=date.year
            day = date.day
        except:
            print "Day not in month"
            data=dateString.split('/')
            month=int(data[0])
            day=int(data[1])-1
            year=int(data[2])
            print dateString
            print month, day, year

        if month==12:
            if '12/31' in dateString:
                if constants.lastYearRead-1==year:
                    year=constants.lastYearRead
        constants.lastYearRead=year
    return day, month, year

def avg_time(times):
    avg = 0
    for elem in times:
        avg += elem.second + 60*elem.minute + 3600*elem.hour
    avg /= len(times)
    rez = str(avg/3600) + ' ' + str((avg%3600)/60) + ' ' + str(avg%60)
    return dtm.datetime.strptime(rez, "%H %M %S") 
#http://stackoverflow.com/questions/19681703/average-time-for-datetime-list


def Frame2Decimal(frame):
    #EXPECTS DATETIME AND CONVERTS TO DECIMAL YEAR THAT TAKES INTO ACCOUNT LEAP YEARS
    #
    #if str(frame).strip().upper() =='NAN': return 'NaN'
    #
    if type(frame) is datetime.date:
        FRAC = 0.5
    else:
        TIM = frame.timetuple()
        FRAC = TIM.tm_hour/24. + TIM.tm_min/1440. + TIM.tm_sec/86400.
    #
    YR = frame.year
    #
    if (YR%4==0 and YR%100!=0) or YR%400:  #TRUE WHEN A LEAP YEAR
        return YR + (frame.timetuple().tm_yday - 1. + FRAC)/366.
    else:
        return YR + (frame.timetuple().tm_yday - 1. + FRAC)/365.

def Frame2Datetime(frame):
    if frame.strip().upper() == 'NAN':
        return 'NaN'
    else:
        return datetime.datetime.strptime(frame,'%m/%d/%Y')

def Frame2Date(frame):
    if type(frame) is datetime.datetime:
        return frame.date()
    elif frame.strip().upper() == 'NAN':
        return 'NaN'
    else:
        return datetime.datetime.strptime(frame,'%m/%d/%Y')

def rotationCSV2DataFrame(FILE):
    ####################################################################
    #TODO VERIFY THAT THIS FORMAT IS USED PRIOR TO 1990
    DTYP={}
    DTYP['region'] =str
    DTYP['Ranch'] =str
    DTYP['1 Crop'] =str
    DTYP['1 Acres'] =str
    DTYP['2 Crop'] =str
    DTYP['2 Acres'] =str
    DTYP['3 Crop'] =str
    DTYP['3 Acres'] =str
    DTYP['4 Crop'] =str
    DTYP['4 Acres'] =str
    DTYP['5 Crop'] =str
    DTYP['5 Acres'] =str
    DTYP['6 Crop'] =str
    DTYP['6 Acres'] =str
    DTYP['7 Crop'] =str
    DTYP['7 Acres'] =str
    DTYP['8 Crop'] =str
    DTYP['8 Acres'] =str
    DTYP['9 Crop'] =str
    DTYP['9 Acres'] =str
    DTYP['10 Crop'] =str
    DTYP['10 Acres'] =str
    DTYP['11 Crop'] =str
    DTYP['11 Acres'] =str
    DTYP['12 Crop'] =str
    DTYP['12 Acres'] =str
    df = pd.read_csv(FILE,dtype=DTYP,sep='\t')

    return df

def rotationCSV2DataFrame1974(FILE):
    ####################################################################
    #TODO VERIFY THAT THIS FORMAT IS USED PRIOR TO 1990
    DTYP={}
    DTYP['region'] =str
    DTYP['TRS'] =str
    DTYP['1 Crop'] =str
    DTYP['1 Acres'] =str
    DTYP['2 Crop'] =str
    DTYP['2 Acres'] =str
    DTYP['3 Crop'] =str
    DTYP['3 Acres'] =str
    DTYP['4 Crop'] =str
    DTYP['4 Acres'] =str
    DTYP['5 Crop'] =str
    DTYP['5 Acres'] =str
    DTYP['6 Crop'] =str
    DTYP['6 Acres'] =str
    DTYP['7 Crop'] =str
    DTYP['7 Acres'] =str
    DTYP['8 Crop'] =str
    DTYP['8 Acres'] =str
    DTYP['9 Crop'] =str
    DTYP['9 Acres'] =str
    DTYP['10 Crop'] =str
    DTYP['10 Acres'] =str
    DTYP['11 Crop'] =str
    DTYP['11 Acres'] =str
    DTYP['12 Crop'] =str
    DTYP['12 Acres'] =str
    df = pd.read_csv(FILE,dtype=DTYP,sep='\t')

    return df

def CSV2DataFrame(FILE):
    ####################################################################
    #TODO VERIFY THAT THIS FORMAT IS USED PRIOR TO 1990
    DTYP={}
    DTYP['use_no'       ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64 #=np.int32 changed because of NAN issue
    DTYP['prodno'       ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64 #=np.int32 changed because of NAN issue
    DTYP['chem_code'    ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64 #=np.int32 changed because of NAN issue
    DTYP['prodchem_pct' ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64
    DTYP['lbs_chm_used' ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64
    DTYP['lbs_prd_used' ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64
    DTYP['amt_prd_used' ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64
    DTYP['unit_of_meas' ] =str
    DTYP['acre_planted' ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64
    DTYP['unit_planted' ] =str
    DTYP['acre_treated' ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64
    DTYP['unit_treated' ] =str
    DTYP['applic_cnt'   ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64 #=np.int32 changed because of NAN issue
    DTYP['applic_dt'    ] =str
    DTYP['applic_time'  ] =str
    DTYP['county_cd'    ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64 #=np.int32 changed because of NAN issue
    DTYP['base_ln_mer'  ] =str
    DTYP['township'     ] =str   #np.int32 cannot have null values
    DTYP['tship_dir'    ] =str
    DTYP['range'        ] =str   #np.int32 cannot have null values
    DTYP['range_dir'    ] =str
    DTYP['section'      ] =str   #np.int32 cannot have null values
    DTYP['site_loc_id'  ] =str
    DTYP['grower_id'    ] =str
    DTYP['license_no'   ] =str
    DTYP['planting_seq' ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64 #=np.int32 changed because of NAN issue
    DTYP['aer_gnd_ind'  ] =str
    DTYP['site_code'    ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64 #=np.int32 changed because of NAN issue
    DTYP['qualify_cd'   ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64 #=np.int32 changed because of NAN issue
    DTYP['batch_no'     ] =str #np.float64 #=np.int32 changed because of NAN issue=np.float64 #=np.int32 changed because of NAN issue
    DTYP['document_no'  ] =str #np.float64 #=np.int32 changed because of NAN issue
    DTYP['summary_cd'   ] =str
    DTYP['record_id'    ] =str   #mix numbers and letters
    DTYP['comtrs'       ] =str
    DTYP['error_flag'   ] =str
    df = pd.read_csv(FILE,dtype=DTYP)
    #THESE ARE OPTIONAL CONVERSIONS TO THE TIME FUNCTIONS DEVELOPED BY SCOTT
    #df.loc[:,'applic_dt'] = df.loc[:,'applic_dt'].map(Frame2Datetime)
    #df.loc[:,'DYEAR']     = df.loc[:,'applic_dt'].map(Frame2Decimal)
    #for R in df.itertuples(index=False):
    #    print R
        #R is a named tupple of each row.  can be accessed
    #print R.use_no #value by column name
    #print df.use_no # column titled use_no
    #print df.loc[0,:] #row, col e.g. row 0 all columns of data
    #.iloc= by index
    #loc is not positional only works for name
    return df

def CSV2DataFrame1984(FILE, countyCode): ###START HERE###
    ####################################################################
    #TODO VERIFY THAT THIS FORMAT IS USED PRIOR TO 1990
    DTYP={}                            
    DTYP['year'                  ] =str
    DTYP['record_id'             ] =str
    DTYP['process_dt'            ] =str
    DTYP['batch_no'              ] =str
    DTYP['county_cd'             ] =str
    DTYP['section'               ] =str
    DTYP['township'              ] =str
    DTYP['tship_dir'             ] =str
    DTYP['range'                 ] =str
    DTYP['range_dir'             ] =str
    DTYP['base_ln_mer'           ] =str
    DTYP['applic_dt'             ] =str
    DTYP['commodity_code'        ] =str
    DTYP['application_method'    ] =str
    DTYP['acre_unit_treated'     ] =str
    DTYP['type_unit'             ] =str
    DTYP['epa_registration_num'           ] =str
    DTYP['total_product_applied'          ] =str
    DTYP['unit_of_meas'           ] =str
    DTYP['decimal_fraction'           ] =str
    DTYP['type_code' ] =str
    DTYP['use_code'          ] =str
    DTYP['formulation'      ] =str
    DTYP['chemical_code'           ] =str
    DTYP['class_code'            ] =str
    DTYP['percent'             ] =str
    DTYP['total_lbs_ai'              ] =str
    try:
        df = pd.read_csv(FILE,sep='\t',dtype=DTYP)
    except:
        print('dataframe comma separated')
    qstring='county_cd != '+str(countyCode)
    #newDF=df[df['region']==region]
    df=df[df['county_cd'] == countyCode]
    return df

def CSV2DataFrame1974(FILE,countyCode): ###START HERE###
    ####################################################################
    #TODO VERIFY THAT THIS FORMAT IS USED PRIOR TO 1990
    DTYP={}                            
    DTYP['year'                  ] =str
    DTYP['record_id'             ] =str
    DTYP['process_dt'            ] =str
    DTYP['batch_no'              ] =str
    DTYP['county_cd'             ] =str
    DTYP['section'               ] =str
    DTYP['township'              ] =str
    DTYP['tship_dir'             ] =str
    DTYP['range'                 ] =str
    DTYP['range_dir'             ] =str
    DTYP['base_ln_mer'           ] =str
    DTYP['applic_dt'             ] =str
    DTYP['commodity_code'        ] =str
    DTYP['application_method'    ] =str
    DTYP['acre_unit_treated'     ] =str
    DTYP['type_unit'             ] =str
    DTYP['mfg_firm_no'           ] =str
    DTYP['label_seq_no'          ] =str
    DTYP['revision_no'           ] =str
    DTYP['reg_firm_no'           ] =str
    DTYP['total_product_applied' ] =str
    DTYP['unit_of_meas'          ] =str
    DTYP['decimal_fraction'      ] =str
    DTYP['document_no'           ] =str
    DTYP['summary_cd'            ] =str
    DTYP['type_code'             ] =str
    DTYP['use_code'              ] =str
    DTYP['form_code'             ] =str
    DTYP['chemical_no'           ] =str
    DTYP['class_code'            ] =str
    DTYP['percent'               ] =str
    DTYP['chem_alpha_cd'         ] =str
    DTYP['commodity_alpha'       ] =str
    DTYP['total_lbs_ai'          ] =str
    try:
        df = pd.read_csv(FILE,sep='\t',dtype=DTYP)
    except:
        print('dataframe comma separated')
    qstring='county_cd != '+str(countyCode)
    #newDF=df[df['region']==region]
    df=df[df['county_cd'] == countyCode]
    return df

def compileCALPIPLookup(zipDirectory, outputDirectory):
    #this function looks through the  pur_ zip files to find the
    lookupDict=dict()
    zipFiles=list()
    outFile=os.path.join(outputDirectory, 'lookup.txt')
    walkedPath = list(os.walk(zipDirectory))[0]
    for item in walkedPath[2]:
        if '.txt' in item:
            continue
        zipFiles.append (os.path.join(zipDirectory, item))
    logFile=os.path.join(outputDirectory, 'lookup_errorlog.txt')
    with open (logFile, 'w') as fout:
        for file in zipFiles:
            with zipfile.ZipFile(file) as z:
                with z.open('site.txt') as f:
                    firstLine=True
                    for line in f:
                        if firstLine:
                            firstLine=False
                            continue
                        words = [tok.strip() for tok in line.split(",")]
                        if words[0] in lookupDict.keys():
                            continue
                        else:
                            lookupDict[int(words[0])]=words[1]

    with open (outFile, 'w') as fout:
        fout.write( 'CropID'+" , " +'CropName')
        for key in sorted(lookupDict):
            value=lookupDict[key]
            fout.write('{0} , {1}\n'.format(key, value))
    return lookupDict

def compileTotalCropAcres(cropDict, cropAcreDict, year):
    #this function makes the crop acre dictionary
    for cropID in sorted(cropAcreDict):
        try:
            crop=cropDict[cropID]
            cropAcreDict[cropID][year]=sum(crop.acresPlanted)
            #print(crop.acresPlanted)
            cropAcreDict[cropID]['total']+=sum(crop.acresPlanted)
        except:
            #print('cropID is in lookup but not in model domain this year')
            cropAcreDict[cropID][year]=0.
            dum=1
        
    return cropAcreDict

def writeAllCropApplications(outFile, cropDict, cropID, regionID=None):
    crop=cropDict[cropID]
    with open (outFile,'w') as fout:
        fout.write( 'Date'+" , " +'Acres Applied'+'\n')
        if regionID is not None:
            if regionID in crop.regions[regionID]:
                for idx in range(0, len (crop.regions[regionID][0])):
                        value=crop.regions[regionID][0]
                        acre=crop.regions[regionID][1]
                        fout.write('{0} , {1}\n'.format(value, acre))
        else:
            for idx in range(0, len (crop.acresPlanted)):
                    value=crop.applicationDates[idx]
                    acre=crop.acresPlanted[idx]
                    fout.write('{0} , {1}\n'.format(value, acre))


def writeCropAcres(cropAlias,cropAcreDict, times, annualFile):
     with open (annualFile, 'w') as fout:
        fout.write( 'CropID'+" , " +'CropGroup'+" , " +'CropName')
        for year in sorted(times):
            fout.write (" , "+str(year))
        fout.write('\n')
        for key in sorted(cropAcreDict):
            value=cropAlias[key][2]
            value2=cropAlias[key][1]
            fout.write('{0} , {1}, {2}'.format(key, value, value2))
            for year in sorted(times):
                acre=cropAcreDict[key][year]
                fout.write (" , "+ str(acre))
            fout.write('\n')

def extractCropData(inDirectory, outDirectory):
    zipList=list()
    walkedPath = list(os.walk(inDirectory))[0]
    for item in walkedPath[2]:
        if '.txt' in item:
            continue
        zipList.append (os.path.join(inDirectory, item))
    for file in zipList:
        year=(file.strip('.zip'))[-2:]
        if 'After1990' in inDirectory:
            curFile='udc'+year+'_{}.txt'.format(countyCode)
        else:
            curFile='pur'+year+'.txt'
        if os.path.isfile(os.path.join(outDirectory, curFile)):
            print('Extracted Data Exists -- Check New Project Flag')
        else:
            with zipfile.ZipFile(file) as z:
                with z.open(curFile) as zf:
                    with open(os.path.join(outDirectory, curFile),'wb') as f:
                        shutil.copyfileobj(zf,f)                              
    return

####################################################################
# INPUT VARIABLES AND DATA STRUCTURES
####################################################################
basePath=constants.basePath
outputDirectory=constants.outputDirectory
joinDirectory= constants.joinDirectory
plotDirectory=constants.plotDirectory
lookupDirectory=constants.lookupDirectory
countyCode=constants.countyCode

####################################################################
#INITIALIZE LOOKUP--ONLY NEED ONCE IF LOOKUP NOT PRESENT
####################################################################
if constants.newProject:
    print('Creating initial data for first run...')
    inDirectory= constants.dataDirectory
    inDirectory2= constants.dataDirectory1990
    extractCropData(inDirectory, constants.projectData)
    extractCropData(inDirectory2, constants.projectData)
    if not os.path.exists(constants.outputDirectory): os.mkdir(constants.outputDirectory)
    if not os.path.exists(constants.plotDirectory): os.mkdir(constants.plotDirectory)
    if not os.path.exists(constants.joinDirectory): os.mkdir(constants.joinDirectory)
    #only need to run to create lookup file
    #lookupDict=compileCALPIPLookup(inDirectory, outDirectory) 

####################################################################
#Executable code
####################################################################
fileList= list()
fileStore=list()
order=dict()
groupStore=dict()
cropAcreDict=dict()


print('Reading lookup tables...')  
primaryregionLookup, regionClimateLookup,TRSClimateLookup = readregionTRSTable(os.path.join(constants.lookupDirectory, 'SpatialregionClimateTRS.csv'))
cropAlias1974, cropAlias1990, cropGroups, groupColors = readAlias(os.path.join(constants.lookupDirectory, 'cropLookupComplete.csv'),os.path.join(constants.lookupDirectory, 'cropLookup1974Exceptions.csv'))
chemAlias=readChemicalAlias(os.path.join(constants.lookupDirectory, 'chemicalLookup.csv'))
constants.colorList=list()
walkedPath = list(os.walk(constants.projectData))[0]
if len(walkedPath) == 0:
    raise Exception('Directory is missing')
for item in walkedPath[2]:
    fileList.append (os.path.join(constants.projectData, item))

for file in fileList:
    if 'pur' in file:
        year="19"+ file.strip('.txt')[-2:]
        year=int(year)
        order[year]=file
    else:
        year=file[:-7][-2:]
        if '9' in year and '09' not in year:
            year="19"+year
        else:
            year="20"+year
    year=int(year)
    order[year]=file
annualFile = os.path.join(constants.outputDirectory,'cropAcreageByYear.txt')

for year in constants.times:
    file=order[year]
    groupStore[year]=dict()
    annualCrops=list()
    if constants.pre1990:
        cropAlias=cropAlias1974
    else:
        cropAlias=cropAlias1990
    if constants.ModelLU: 
        if year >= 1992: 
            annual=constants.annual1983
            selectedCropGroups=constants.selectedCropGroups
        elif year > 1983 and year < 1992:
            annual=constants.annual1983
            selectedCropGroups=constants.selectedCropGroups
        else:
            annual=constants.annual
            selectedCropGroups=constants.allCropGroups
    else: #For comparison between calpip and TRS FROM NLCD/LAND USE DATASETS
        if year==1992: selectedCropGroups=constants.selectedCropGroups1992
        if year==1997: selectedCropGroups=constants.selectedCropGroups1997
        if year==2000: selectedCropGroups=constants.selectedCropGroups2000

    for crop in selectedCropGroups:
        if crop in annual:
            annualCrops.append(crop)
  
    for cropID in sorted(cropAlias.keys()):
        cropAcreDict[cropID]=dict()
        cropAcreDict[cropID][year]=0. #stores annual crop data
        cropAcreDict[cropID]['total']=0. #stores total acreage through time

    if year>1973 and year <1984:
        constants.pre1990=True
        print("Reading "+file)
        df=CSV2DataFrame1974(file, countyCode)

    elif year>1983 and year <1990:
        constants.pre1990=True
        print("Reading "+file)
        df=CSV2DataFrame1984(file, countyCode)

    elif year>=1990:
        constants.pre1990=False
        print("Reading "+file)
        df=CSV2DataFrame(file)

    print('Aggregating crop data...')
    cropDict, ranchDict=aggregateCropData(df, year)
    if constants.filterCrop: cropDict=filterCropDict(cropDict, year)
    if constants.writeApplications: writeAllApplications(year)
    
    #create new region statstics file
    statsFile=os.path.join(outputDirectory, 'regionStats.txt')
    if os.path.exists(statsFile):
        os.remove(statsFile)
    outFile1=os.path.join(outputDirectory, str(year)+' TRSCropAcres.txt')
    outFile2=os.path.join(outputDirectory, str(year)+' TRSCropPctMonth.txt')
    outFile3=os.path.join(outputDirectory, str(year)+' TRSCropPCTtotal.txt')
    outFile4=os.path.join(joinDirectory, str(year)+' TRSCropPCTCAF')
    TRSLU=aggregateByTRS(year, cropDict, cropAlias, selectedCropGroups, annualCrops, outFile1, outFile2, outFile3, outFile4)
    outFile=os.path.join(outputDirectory, str(year)+'_CropRotationTable.txt')

#write out group acreages from calPIP only
outFile5=os.path.join(basePath,'allgroupAcreage.txt')
selectedCropGroups=['Ag_Trees','Artichokes','Cane-Bush Berries','Carrots','Celery','Citrus and subtropical','Corn','Crucifers-Cabbages','Cucumber-Melons-Squash','Deciduous fruits and nuts','Field Crops','Grain Crops','Legumes','Lettuce','Nurseries-Outdoor','Onions-Garlic','Root Vegetables','Rotational 30-day','Strawberries','Tomato-Peppers','Vineyards']
with open (outFile5, 'w') as fout:
    fout.write ('{0}\t'.format('YEAR'))
    for group in selectedCropGroups:
        fout.write ('{0}\t'.format(group))
    fout.write('\n')
    for year in constants.times:
        fout.write ('{0}\t'.format(year))
        for group in selectedCropGroups:
            if group in groupStore[year].keys():
                fout.write('{:.4f}\t'.format(groupStore[year][group]))
            else:
                fout.write('0.0000')
                fout.write('\t')
        fout.write('\n')
if constants.checkFlag: print("Check Flag was initiated-Evaluate error messages to find condition")





###OLDER CODES REMOVE LATER
#print('Writing out crop acreages')

#totalFile=os.path.join( outputDirectory ,'totalCropAcreage.txt')
#writeCropAcres(cropAlias, cropAcreDict, times, annualFile)

    ##This writes out all crop applications for a specific cropID
    ##outFile=os.path.join(outputDirectory, 'MushroomCropApplication2.txt')
    ##writeAllCropApplications(outFile, cropDict, 61007)
    ##this function plots crop acreage by month for all crops
    #aggregateByregion(cropDict,cropAlias, year)
    ##this function plots crop acreageby month region and crop Group
    #aggregateByregionGroup(cropDict, cropAlias, cropGroups, year)
    ##this function aggregates crop acreage by land use, month, and region
    #aggregateByLU(cropDict, cropAlias, year)
    ##The following function aggregates crop acreage by TRS and writes out data for GIS joins
    

#print('Computing crop statistics...')
#cropStatistics(cropDict)
##outFile=os.path.join(basePath, file.strip('.txt')+'_TEST.txt')
#outFile=os.path.join(basePath, 'cropbyregion.txt')
#print("Writing "+outFile)
#writeTestOutput(outFile,cropDict)

    #if year<1990:
    #    writeRotationsbyregion1974(cropDict, outFile)
    #    df2=rotationCSV2DataFrame1974(outFile)
    #else:
    #    writeRotationsbyregion(cropDict, outFile)
    #    df2=rotationCSV2DataFrame(outFile)
    #cropRotationFrequency(df2)
    #computeregionStatistics(cropDict, statsFile)
    #extract(os.path.join(outputDirectory, str(year)+'_CropRotationTable.txt'))




#writeGrowthTimeOutput(outFile)
#outFile=os.path.join(basePath, file.strip('.dat')+'_rotation.txt')
#print("Writing "+outFile)
#writeRotationOutput(outFile)





