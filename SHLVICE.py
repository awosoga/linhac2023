#Import relevant libraries
import pandas as pd
import numpy as np

#Set X Zones and Y Zones. Details found in getzone function
xzone = [[-100,-86,-70,5,-55],[-55,-55,-25,5,-25],[-25,-25,-25,5,0],[-78,-78,-70,5,-55],
         [-55,-55,-25,5,-25],[-25,-25,-25,5,0],[-86,-78,-70,3,-70],[-78,-78,-70,5,-55],
         [-100,-86,-70,5,-55],[-55,-55,-25,5,-25],[-25,-25,-25,5,0]]
yzone = [[43,0,43,20],[43,20,43,13],[43,20,43,20],[13,13,20,0],
         [20,-20, 13,-13],[20,-20,20,-20],[0,0,13,-13],[-13,-13,0,-20],
         [0,-43,-20,-43],[-20,-43,-13,-43],[-20,-43,-20,-43]]

#Below is the matching zone to the coordinates for x and y.
#all DZ unless specified [OuterNorthWest,WestPoint,SouthEastBoardsNZ,WestOuterSlot,CenterPoint,SouthCenterNZ,inner slot,EastOuterSlot,OutsideNorthEast,EastPoint,SouthwestBoardsNZ]

def getzone(x,y,xzones,yzones):
    #x,y are the x and y coordinates of the point we are getting the zone for.
    '''
    xzone[0] = start x (left)
    xzone[1] = start x2 (right)
    xzone[2] = end x (left of right)
    xzone[3] = zone type : 5 = zero or one line of change (everything but innner slot), 3 = two lines of change (inner slot) (Arbitrary number choice)
    xzone[4] = x2 end (right of right)
    yzone[0] = start y (above)
    yzone[1] = start y2 (below)
    yzone[2] = end y1 (above)
    yzone[3] = end y2 (below)
    returns corresponding zone
    '''
    #i is the zone index, where xzone and yzone having matching xy pairs at each index.
    i = 0
    #xyfound will stop the loop once the correct zone is found.
    xyfound = False
    #negx determines if the x value was greater than zero. This is because the zones are symmetric about x = 0.
    negx = False
    if x > 0:
        x *= -1
        negx = True
    while i < len(xzones) + 1 and not xyfound:

        if i == len(xzones):
            #If the number of zones has been exceeded, print the xy coords of the zone not found.
            print(x,y)
        else:
            xzone = xzones[i]
            yzone = yzones[i]
        #Differentiate between zone type
        if xzone[3] == 3:
            #Check if zone is in bounds for a type 3 zone
            if ((x <= xzone[1] and x >= xzone[0]) and ((yzone[0] + (yzone[2] - yzone[0])/(xzone[1] - xzone[0])*(x-xzone[0])) >= y and (yzone[1] + (yzone[3] - yzone[1])/(xzone[1] - xzone[0])*(x-xzone[0])) <= y)) or ((x <= xzone[2] and x >= xzone[1]) and (yzone[2] - 1*((yzone[2] - yzone[0])/(xzone[2] - xzone[1]))*(x-xzone[1]) >= y and yzone[3] - 1*((yzone[3] - yzone[1])/(xzone[2] - xzone[1]))*(x-xzone[1]) <= y)):
                xyfound = True
        elif xzone[3] == 5:
            #check if zone is in bounds for a type 5 zone
            if ((x <= xzone[1] and x >= xzone[0]) and (y <= yzone[0] and y >= yzone[1])) or ((x <= xzone[4] and x >= xzone[2]) and (y <= yzone[2] and y >= yzone[3])) or ((x < xzone[2] and x > xzone[1]) and ((yzone[0] + (yzone[2] - yzone[0])/(xzone[2] - xzone[1])*(x-xzone[1])) >= y and (yzone[1] + (yzone[3] - yzone[1])/(xzone[2] - xzone[1])*(x-xzone[1])) <= y)):
                xyfound = True
        else:
            pass
        #Increment zone number
        i += 1
    #Go back one zone because i += 1 at the end of loop.
    zone = i - 1
    #If x was greater than zero, flip the zone about 2*number of zones.
    if negx:
        zone = 2*len(xzones) - i
    #if x < 0 and x > -25 and y < -20 and y > -40:
        #print((x <= xzone[1] and x >= xzone[0]) and (y <= yzone[0] and y >= yzone[1]),((x <= xzone[4] and x >= xzone[2]) and (y <= yzone[2] and y >= yzone[3])),((x <= xzone[2] and x >= xzone[1]) and (((yzone[0] + (yzone[2] - yzone[0])/(xzone[2] - xzone[1]))*(x-xzone[1])) >= y and (yzone[1] + (yzone[3] - yzone[1])/(xzone[2] - xzone[1])*(x-xzone[1])) <= y)))
    #Return the zone number for the zone that the coordinates belong to.
    return zone

#Shift is the variable that determines how far we look ahead when determining DeltaXg20s
shift = 45


#Load data into a dataframe
#Path needs to be changed based on where you have the file saved
data = pd.read_excel(r'C:\Users\jaden\PycharmProjects\pythonProject\turnover_probabilities.xlsx')

#Get index if every check
checkindices = data.index[(data['eventname'] == 'check')].tolist()
#get index of every puckprotection
puckprotectionindices = data.index[(data['eventname'] == 'puckprotection')].tolist()

#Code to get rid of the failed puckprotections that match checks
for check in checkindices:
    #Time and Team not used
    time = data.loc[check, "compiledgametime"]
    team = data.loc[check, "teaminpossession"]
    #Check for puckprotection as event before check
    if data.loc[check-1,'eventname'] == "puckprotection" and data.loc[check-1,"outcome"] == "failed":
        data.drop(check-1, inplace = True)
    #Check for puckprotection as event after check
    elif data.loc[check + 1, 'eventname'] == "puckprotection" and data.loc[check+1,"outcome"] == "failed":
        data.drop(check + 1, inplace = True)
    #If no puck protection matching the check, get rid of the check
    else:
        data.drop(check, inplace = True)

#Reset data indices with dropped rows.
data.reset_index(inplace = True)
data.drop("index", axis = 1, inplace = True)

#Get indices for the start of every period
startend = data.index[(data['compiledgametime'] == 0) | (data['compiledgametime'] == 1200) | (data['compiledgametime'] == 2400)| (data['compiledgametime'] == 3600)].tolist()
n = len(startend)
startendadjusted = []
#because faceoffs are paired, drop every other faceoff time from startend so that we only havev the index of the relevant faceoff
for i in range(n):
    if i % 2 == 0:
        startendadjusted += [startend[i]]

#Slice data into periods based on start and end times
periods = []
for i in range(len(startendadjusted) - 1):
    periods += [data[startendadjusted[i]:startendadjusted[i+1]]]

#Set empty list to get list of events while doing other things
events = []
#Go through each period
for period in periods:
    #Reset period indices since they've been sliced
    period.reset_index(inplace = True)
    #Add extra columns
    period['Xg20s'] = np.nan
    period['DeltaXg20s'] = np.nan
    period['isshot'] = np.nan
    #Get final time of last event in period
    time = period['compiledgametime'][len(period['compiledgametime']) - 1]
    i = 0
    #Look ahead until the time were looking ahead goes past the end of the period
    while period['compiledgametime'][i] < time - shift:
        #add event to events if its not there already
        if period.loc[i,'eventname'] not in events:
            events += [period.loc[i,'eventname']]
        #Get intial data based on intial positin and stuff
        period.loc[i, 'isshot'] = 0
        xg = 0
        time2 = period['compiledgametime'][i] + shift
        k = i
        j = i
        #print(time2)
        team = period['teaminpossession'][i]
        teamid = period['teamid'][i]
        #If there is no team associated with the event, we ignore it.
        if np.isnan(team):
            pass
        else:
            #look ahead shift length
            while period.loc[k, 'compiledgametime'] < time2:
                #Can't add nan to xg tally
                if not np.isnan(period['xg'][k]):
                    # print(data.loc[i, 'xg'])
                    if team == period.loc[k, 'teaminpossession']:
                        xg += period.loc[k, 'xg']
                    else:
                        pass
                        #xg -= period.loc[k, 'xg']
                #Increment k forwards
                k += 1
        #Again, if no team in possession, no team to get a shot
        if np.isnan(team):
            pass
        else:
            #check if team got a shot in the next shift seconds
            while j < k:
                if not np.isnan(period['xg'][j]):
                    # print(data.loc[i, 'xg'])
                    if team == period.loc[j,'teaminpossession']:
                        period.loc[i,'isshot'] = 1
                #increment j
                j += 1
        # set period at xg ahead to be xg
        period.loc[i, 'Xg20s'] = xg
        #increment i
        i += 1
    #Now just go to end of period, since time left in period exceeds shift length
    #Do everything the same otherwise
    while i < len(period['compiledgametime']):
        if period.loc[i,'eventname'] not in events:
            events += [period.loc[i,'eventname']]
        period.loc[i, 'isshot'] = 0
        xg = 0
        k = i
        j = i
        team = period['teaminpossession'][i]
        teamid = period['teamid'][i]
        if np.isnan(team):
            pass
        else:
            while k < len(period['compiledgametime']):
                if not np.isnan(period['xg'][k]):
                    # print(data.loc[i, 'xg'])
                    if team == period.loc[k,'teaminpossession']:
                        xg += period.loc[k, 'xg']
                    else:
                        pass
                        #xg -= period.loc[k, 'xg']
                k += 1
        if np.isnan(team):
            pass
        else:
            while j < k:
                if not np.isnan(period['xg'][j]):
                    # print(data.loc[i, 'xg'])
                    if team == period.loc[j,'teaminpossession']:
                        period.loc[i,'isshot'] = 1
                j += 1
        period.loc[i, 'Xg20s'] = xg
        i += 1
    i = 0

#I just want to know how far into the code we have run.
print("Done searching Periods")

#Set empty dataframes with events as columns and zones as rows.
eventnum = pd.DataFrame()
shotgot = pd.DataFrame()

for event in events:
    shotgot[event] = ''
    eventnum[event] = ''
for i in range(2*len(xzone)):
    shotgot.loc[i] = np.nan
    eventnum.loc[i] = np.nan

#Go through each
for period in periods:
    i = 0
    #Go through each event in each period
    while i < len(period) - 1:
        #get zone of event
        zone = getzone(period['xadjcoord'][i],period['yadjcoord'][i], xzone, yzone)
        #Add/Set number of times event happened in each zone
        if np.isnan(eventnum.loc[(zone),period['eventname'][i]]):
            eventnum.loc[(zone),period['eventname'][i]] = 1
        else:
            eventnum.loc[(zone),period['eventname'][i]] += 1
        #Add/Set number of times a shot resulted from a play in each zone
        if period['isshot'][i]:
            if np.isnan(shotgot.loc[(zone),period['eventname'][i]]):
                shotgot.loc[(zone), period['eventname'][i]] = 1
            else:
                shotgot.loc[(zone), period['eventname'][i]] += 1
        i += 1

#get proportion by dividing the two matrices
shotprob = shotgot/eventnum
writer = 'SHLShotProb' + '.xlsx'
shotprob.to_excel(writer)

print("Done ShotProb")
#Go through each period
for period in periods:
    i = 0
    #The commented out code doesn't work the way I want it to, but I left it here incase I can make it work later.
    '''
    while i < len(period['Xg20s']) - 1:
        if True:
            #get zone for event
            x = period.loc[i, 'xadjcoord']
            y = period.loc[i, 'yadjcoord']
            zone = getzone(x,y,xzone,yzone)
            #get shift xg for that play times the probability of that event laeding to a shot
            xg1 = period.loc[i, "Xg20s"]
            xg1 *= shotprob.loc[zone, period.loc[i,'eventname']]
            k = i - 1
            #go back to last event with a team in possesion or start of period
            nanistrue = True
            while nanistrue and k > 0:
                if not np.isnan(period['teaminpossession'][k]):
                        nanistrue = False
                k -= 1
            k += 1
            xg2 = period.loc[k, "Xg20s"]
            #If team in possesion is different, xg2 should be negative
            if period.loc[i, 'teaminpossession'] != period.loc[k, "teaminpossession"]:
                xg2 *= -1
            x = period.loc[k, 'xadjcoord']
            y = period.loc[k, 'yadjcoord']
            zone = getzone(x,y,xzone,yzone)
            xg2 *= shotprob.loc[zone, period.loc[k, 'eventname']]
            #Set DeltaXg20s
            period.loc[i,'DeltaXg20s'] = xg1 - xg2
        i += 1
    '''
    #go through each event in each period
    while i < len(period['Xg20s']) - 1:
        if not np.isnan(period['teaminpossession'][i]):
            # get zone for event
            z = i + 1
            nanistrue = True
            #go ahead to next event that has a team in possession
            while nanistrue and z < len(period['Xg20s']):
                if not np.isnan(period['teaminpossession'][z]):
                    nanistrue = False
                z += 1
            z -= 1
            #get zone for that event
            x = period.loc[z, 'xadjcoord']
            y = period.loc[z, 'yadjcoord']
            zone = getzone(x, y, xzone, yzone)
            #get shift xg for that play times the probability of that event laeding to a shot for that event
            xg1 = period.loc[z, "Xg20s"]
            xg1 *= shotprob.loc[zone, period.loc[z, 'eventname']]
            #Times probability of keeping possession
            xg1 *= 1 - period.loc[z, "lose_poss_prob"]
            k = i - 1
            # go back to last event with a team in possesion or start of period
            nanistrue = True
            while nanistrue and k > 0:
                if not np.isnan(period['teaminpossession'][k]):
                    nanistrue = False
                k -= 1
            k += 1
            xg2 = period.loc[k, "Xg20s"]
            # If team in possesion is different, xg2 should be negative
            if period.loc[z, 'teaminpossession'] != period.loc[k, "teaminpossession"]:
                xg2 *= -1
            x = period.loc[k, 'xadjcoord']
            y = period.loc[k, 'yadjcoord']
            zone = getzone(x, y, xzone, yzone)
            xg2 *= shotprob.loc[zone, period.loc[k, 'eventname']]
            xg2 *= 1 - period.loc[k, "lose_poss_prob"]
            # Set DeltaXg20s as the difference of xg1 (event after) and xg2 (event before
            period.loc[i, 'DeltaXg20s'] = xg1 - xg2
        i += 1


print("Done DeltaXg20s")

#Combine all periods into one dataframe
data2 = pd.concat(periods)
#get number of checks that have a nonzero deltaxg20s
yo = data2.index[(data2['DeltaXg20s'] != 0) & (data2['eventname'] == 'check')].tolist()
#get number of puckprotections that have a nonzero deltaxg20s
yo2 = data2.index[(data2['DeltaXg20s'] != 0) & (data2['eventname'] == 'puckprotection')].tolist()
print(len(yo), len(yo2))
#Save data
writer = 'SHLVICEv3' + '.xlsx'
data2.to_excel(writer)
