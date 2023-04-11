#Import relevant libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

'''
This code is to be run after SHLVICE is run, with DeltaXg20s values in place and extra puckprotections dropped.
'''


#Load data into a dataframe
#Path needs to be changed based on where you have the file saved
data = pd.read_excel(r'C:\Users\jaden\PycharmProjects\pythonProject\SHLVICEv3.xlsx')

#Get indices of puckprotections and checks
truepuckprotectionindices = data.index[(data['eventname'] == 'puckprotection')].tolist()
truechecks = data.index[(data['eventname'] == 'check')].tolist()


#Set up empty data frames
checks = pd.DataFrame()
protections = pd.DataFrame()

checks["isstick"] = ''
checks["issbody"] = ''
checks["iscop"] = ''
checks['DeltaXg20s'] = ''
checks['location'] = ''
checks["eventsafter"] = ''
checks["S/F"] = ''
checks["X/Y"] = ''
checks["xgafter"] = ''
checks['timeafter'] = ''


protections["isdeke"] = ''
protections["isbody"] = ''
protections['issuccessful'] = ''
protections["iscop"] = ''
protections['DeltaXg20s'] = ''
protections['location'] = ''
protections["eventsafter"] = ''
protections["S/F"] = ''
protections["X/Y"] = ''
protections["xgafter"] = ''
protections["timeafter"] = ''

n = 0
k = 0
for check in truechecks:
    #checker is an empty list that will become the kth row of checks once it is full
    checker = []
    #Add type of check
    checker += [data.loc[check, "type"] == "stick"]
    checker += [data.loc[check,"type"] == "body"]
    #Get team in possession during check
    team = data.loc[check, "teaminpossession"]
    n = 1
    #Skip ahead to next event with a team in possession
    while n <= 3800 and np.isnan(data.loc[check + n, "teaminpossession"]):
        n += 1
    #Add change in possession as false if no cop, true if cop
    if team == data.loc[check + n, "teaminpossession"]:
        checker += [False]
    else:
        checker += [True]
    #Add DeltaXg20s and xy coords to checker
    checker += [data.loc[check, "DeltaXg20s"]]
    checker += [[data.loc[check,'xadjcoord'],data.loc[check,'yadjcoord']]]
    team = data.loc[check + n, "teaminpossession"]
    #Events after, SF and xy are the list of events, successes/fails of those events and xy coords of the events on the ensuing possession
    eventsafter = []
    SF = []
    xy = []
    #xg is the sum of the xg a team gets on the ensuing possession
    xg = 0
    #time is the compiledgametime at the time of the check
    time = data.loc[check + n - 1, "compiledgametime"]
    #While still in the same possession
    while (data.loc[check + n, "teaminpossession"] == team or np.isnan(data.loc[check + n, "teaminpossession"])) and data.loc[check + n, 'eventname'] != "faceoff":
        #Add events, S/F and xy coords.
        eventsafter += [data.loc[check + n, 'eventname']]
        SF += [data.loc[check + n, 'outcome']]
        xy += [[data.loc[check,'xadjcoord'],data.loc[check,'yadjcoord']]]
        #Filter for nan in xg column
        if not np.isnan(data.loc[check + n, 'xg']):
            #add xg to sum
            xg += data.loc[check + n, 'xg']
        n += 1
    #Add data to checker
    checker += [eventsafter]
    checker += [SF]
    checker += [xy]
    checker += [xg]
    #Add the length of possession to checker
    checker += [data.loc[check+n - 1,"compiledgametime"] - time]
    #Make checker the kth row of checks.
    checks.loc[k] = checker
    k += 1
k = 0

#Named check because I copy pasted than changed a few lines, didnt wanna rename everything to protection
for check in truepuckprotectionindices:
    #checker is an empty list that will become the kth row of protections once it is full
    checker = []
    #Add type of check
    checker += [data.loc[check, "type"] == "deke"]
    checker += [data.loc[check,"type"] == "body"]
    #Add success of check to row
    checker += [data.loc[check, "outcome"] == "successful"]
    #Get team in possession during check
    team = data.loc[check, "teaminpossession"]
    n = 1
    #Skip ahead to next event with a team in possession
    while n <= 3800 and np.isnan(data.loc[check + n, "teaminpossession"]):
        n += 1
    # Add change in possession as false if no cop, true if cop
    if team == data.loc[check + n, "teaminpossession"]:
        checker += [False]
    else:
        checker += [True]
    #Add DeltaXg20s and xy coords to checker
    checker += [data.loc[check, "DeltaXg20s"]]
    checker += [[data.loc[check,'xadjcoord'],data.loc[check,'yadjcoord']]]
    team = data.loc[check + n, "teaminpossession"]
    #Events after, SF and xy are the list of events, successes/fails of those events and xy coords of the events on the ensuing possession
    eventsafter = []
    SF = []
    xy = []
    #xg is the sum of the xg a team gets on the ensuing possession
    xg = 0
    #time is the compiledgametime at the time of the check
    time = data.loc[check + n - 1, "compiledgametime"]
    #While still in the same possession
    while (data.loc[check + n, "teaminpossession"] == team or np.isnan(data.loc[check + n, "teaminpossession"])) and data.loc[check + n, 'eventname'] != "faceoff":
        #Add events, S/F and xy coords.
        eventsafter += [data.loc[check + n, 'eventname']]
        SF += [data.loc[check + n, 'outcome']]
        xy += [[data.loc[check,'xadjcoord'],data.loc[check,'yadjcoord']]]
        #Filter for nan in xg column
        if not np.isnan(data.loc[check + n, 'xg']):
            #add xg to sum
            xg += data.loc[check + n, 'xg']
        n += 1
    #Add data to checker
    checker += [eventsafter]
    checker += [SF]
    checker += [xy]
    checker += [xg]
    #Add the length of possession to checker
    checker += [data.loc[check+n - 1,"compiledgametime"] - time]
    #Make checker the kth row of protections.
    protections.loc[k] = checker
    k += 1

#Save Checks and Protections to excel sheets incase I want to look at them later
writer = 'SHLchecks' + '.xlsx'
checks.to_excel(writer)
writer = 'SHLprotections' + '.xlsx'
protections.to_excel(writer)

def getmean(checks,property, isabs, checker, useupper):
    '''
    Checks is the dataframe we're processing
    property is the column of the dataframing we're analyzing
    isabs is whether or not we are looking at the absolute value of the property
    checker is the final word in the label in the return function
    useuppper is whether or  not we consider the upper bound of the box plot
    Returns:
        a - Label for each data in list
        b - mean of each data in list
        c - confidence interval bound for each data in list
    '''
    #This is because I wrote this later, and didn't wanna go back and rename the column because idk
    if checker == 'checks':
        isbody = 'issbody'
    else:
        isbody = 'isbody'
    #Create empty dataframes for different scenarios. Ignore the C at the start.
    #pt stood for possession time, but now its just whatever the property were looking at today
    Cbodycoppt = pd.DataFrame()
    Cbodycoppt['pt'] = ''
    Cbodynocoppt = pd.DataFrame()
    Cbodynocoppt['pt'] = ''
    Cstickcoppt = pd.DataFrame()
    Cstickcoppt['pt'] = ''
    Csticknocoppt = pd.DataFrame()
    Csticknocoppt['pt'] = ''
    Cbodycop = 0
    Cbodynocop = 0
    Cstickcop = 0
    Csticknocop = 0
    #Determine first and third quantile of the dataset
    if isabs or not useupper:
        Q1 = abs(checks[property]).quantile(0.25)
        Q3 = abs(checks[property]).quantile(0.75)
    else:
        Q1 = (checks[property]).quantile(0.25)
        Q3 = (checks[property]).quantile(0.75)
    #Determine Inter-Quantile Range
    IQR = Q3 - Q1
    #Go through every row of the dataframe
    for check in range(len(checks[isbody])):
        #Consider either both lower or lower and upper bounds of coded box plot to exclude outliers.
        if useupper:
            #Use either absolute or not absolute data.
            if isabs:
                timesig = not ((abs(checks[property][check]) < (Q1 - 1.5 * IQR)) or (abs(checks[property][check]) > (Q3 + 1.5 * IQR)))
            else:
                timesig = not (((checks[property][check]) < (Q1 - 1.5 * IQR)) or ((checks[property][check]) > (Q3 + 1.5 * IQR)))
        else:
            #Use either absolute or not absolute data.
            #if isabs:
            timesig = not ((abs(checks[property][check]) < (Q1 - 1.5 * IQR)))
            #else:
                #timesig = not (((checks[property][check]) < (Q1 - 1.5 * IQR)))
        #check if row is a body maneuver
        if checks[isbody][check] and timesig:
            #check if row is a change in possession
            if checks['iscop'][check]:
                #update corresponding dataframe
                Cbodycoppt.loc[Cbodycop, 'pt'] = checks.loc[check, property]
                Cbodycop += 1
            else:
                #update corresponding dataframe
                Cbodynocoppt.loc[Cbodynocop, 'pt'] = checks.loc[check, property]
                Cbodynocop += 1
        #if row is not body maneuver it must be a stick maneuver
        elif timesig:
            #check if row is a change in possession
            if checks['iscop'][check]:
                #update corresponding dataframe
                Cstickcoppt.loc[Cstickcop, 'pt'] = checks.loc[check, property]
                Cstickcop += 1
            else:
                #update corresponding dataframe
                Csticknocoppt.loc[Csticknocop, 'pt'] = checks.loc[check, property]
                Csticknocop += 1
        #I just like having the pass for organizational sake.
        else:
            pass
    #Either absolute or not absolute data
    if not isabs:
        #print the different values before you return them
        print("The average " + property + " on possession after a cop from a Body maneuver is " + str(Cbodycoppt['pt'].mean()) + " +- " + str(Cbodycoppt['pt'].std()))
        print("The average " + property + " on possession after no cop from a Body maneuver is " + str(Cbodynocoppt['pt'].mean()) + " +- " + str(Cbodynocoppt['pt'].std()))
        print("The average " + property + " on possession after a cop from a Stick maneuver is " + str(Cstickcoppt['pt'].mean()) + " +- " + str(Cstickcoppt['pt'].std()))
        print("The average " + property + " on possession after no cop from a Stick maneuver is " + str(Csticknocoppt['pt'].mean()) + " +- " + str(Csticknocoppt['pt'].std()))
        #Print empty line because i prefer it that way
        print()
        #Set up return values
        a = ['CopBody' + checker[0], 'NoCopBody' + checker[0], 'CopStick' + checker[0], 'NoCopStick' + checker[0]]
        b = [(Cbodycoppt['pt']).mean(), (Cbodynocoppt['pt']).mean(), (Cstickcoppt['pt']).mean(),
             (Csticknocoppt['pt']).mean()]
        c = [1.96 * (Cbodycoppt['pt']).std() / (len(Cbodycoppt['pt']) ** 0.5),
             1.96 * (Cbodynocoppt['pt']).std() / (len(Cbodynocoppt['pt']) ** 0.5),
             1.96 * (Cstickcoppt['pt']).std() / (len(Cstickcoppt['pt']) ** 0.5),
             1.96 * (Csticknocoppt['pt']).std() / (len(Csticknocoppt['pt']) ** 0.5)]
    else:
        #print the different values before you return them
        print("The average " + property + " on possession after a cop from a Body maneuver is " + str(
            abs(Cbodycoppt['pt']).mean()) + " +- " + str(1.96*abs(Cbodycoppt['pt']).std()/(len(Cbodycoppt['pt'])**0.5)))
        print("The average " + property + " on possession after no cop from a Body maneuver is " + str(
            abs(Cbodynocoppt['pt']).mean()) + " +- " + str(1.96*abs(Cbodynocoppt['pt']).std()/(len(Cbodynocoppt['pt'])**0.5)))
        print("The average " + property + " on possession after a cop from a Stick maneuver is " + str(
            abs(Cstickcoppt['pt']).mean()) + " +- " + str(1.96*abs(Cstickcoppt['pt']).std()/(len(Cstickcoppt['pt'])**0.5)))
        print("The average " + property + " on possession after no cop from a Stick maneuver is " + str(
            abs(Csticknocoppt['pt']).mean()) + " +- " + str(1.96*abs(Csticknocoppt['pt']).std()/(len(Csticknocoppt['pt'])**0.5)))
        #Print empty line because i prefer it that way
        print()
        #Set up return values
        a = ['CopBody' + checker[0], 'NoCopBody' + checker[0], 'CopStick' + checker[0], 'NoCopStick' + checker[0]]
        b = [abs(Cbodycoppt['pt']).mean(), abs(Cbodynocoppt['pt']).mean(), abs(Cstickcoppt['pt']).mean(),abs(Csticknocoppt['pt']).mean()]
        c = [1.96*abs(Cbodycoppt['pt']).std()/(len(Cbodycoppt['pt'])**0.5), 1.96*abs(Cbodynocoppt['pt']).std()/(len(Cbodynocoppt['pt'])**0.5), 1.96*abs(Cstickcoppt['pt']).std()/(len(Cstickcoppt['pt'])**0.5), 1.96*abs(Csticknocoppt['pt']).std()/(len(Csticknocoppt['pt'])**0.5)]
    #Return Values
    return a, b, c

#use getmean on timeafter checks
timeachecks, timebchecks, timecchecks = getmean(checks, 'timeafter', True, 'checks', True)
#use getmean on timeafter protections
timeaprotections, timebprotections, timecprotections = getmean(protections, 'timeafter', True, 'protections', True)
#use getmean on deltaxg20s checks
deltaachecks, deltabchecks, deltacchecks = getmean(checks, 'DeltaXg20s', False, 'checks', True)
#use getmean on deltaxg20s Protections
deltaaprotections, deltabprotections, deltacprotections = getmean(protections, 'DeltaXg20s', False, 'protections', True)

#Combine dataframes into both
checks.rename(columns = {'issbody':'isbody'}, inplace = True)
protections.rename(columns = {'isdeke':'isstick'}, inplace = True)
protections.drop('issuccessful', axis = 1, inplace = True)
both = pd.concat([checks,protections])
both.reset_index(inplace = True)

deltaa, deltab, deltac = getmean(both, 'DeltaXg20s', False, 'both', True)

#Print graphs of seperate and combined data (figures 1 and 2 respectively)
plt.figure(1)
plt.bar((deltaachecks[0:2] + deltaaprotections[0:2] + deltaachecks[2:4] + deltaaprotections[2:4]), (deltabchecks[0:2] + deltabprotections[0:2] + deltabchecks[2:4] + deltabprotections[2:4] ))
plt.xlabel("Event")
plt.ylabel("Mean DeltaXg45s")
plt.title("VICE Results Separated")
plt.errorbar((deltaachecks[0:2] + deltaaprotections[0:2] + deltaachecks[2:4] + deltaaprotections[2:4]), (deltabchecks[0:2] + deltabprotections[0:2] + deltabchecks[2:4] + deltabprotections[2:4] ), yerr= (deltacchecks[0:2] + deltacprotections[0:2] + deltacchecks[2:4] + deltacprotections[2:4]), fmt="o", color="r")

plt.figure(2)
plt.bar((deltaa),(deltab))
plt.xlabel("Event")
plt.ylabel("Mean DeltaXg45s")
plt.title("VICE Results Combined")
plt.errorbar((deltaa),(deltab), yerr = deltac ,fmt="o", color="r")

print("Done DeltaXg20s Graphs")
plt.show()
