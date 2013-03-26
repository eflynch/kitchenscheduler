# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------
# Name:         kitchen.py
# Author:       Evan Lynch
#
# Copyright:    Copyright © 2013 Evan F. Lynch
# License:      Not Released, but do what you want; especially if you are yfnkm.
#--------------------------------------------------------------------------------
'''
Greetings yfnkm,
    
    Are you still using cast iron pans? In my day there was a bit of controversy about
their continued use since, as you probably know, they tend to get a might rusty and
unsavory after a few seasons of mistreatment at the hands of underinformed or
overworked pikans. Well, in any case, since you happen to be reading this here kitchen.py
documentation, I can only assume that you are preparing to generate a calendar for the
young folks of the day in order to make sure all the cookin' and the cleanin' gets done.

    Well, a couple a things that you should be aware of before you start I might as well
mention here up front. Most of the code that does the thing that you want is in assigner.py,
so if you don't have that in this directory or in your python path, then you are going to
have some trouble. Second thing is that assigner.py needs to use numpy, so you also have
to have that one installed.

    Last, I'll do a little explainin' about how to make this thing work. You are going to
want to write a python script that imports kitchen.py and does some important things:

1)  First you've got to generate a ConstraintsTable with all the preference information for
    the young folks and their preferred jobs. the method down below called parseCSV is for 
    doing just that, but its highly specific to the kind of google form I was using at the time.
    So, you might be wise to rewrite it to bring it up to your own highly specific standards.

2)  Second, you've got to make any appropriate changes to your constraints table that you want.
    What I used to do is select who the big cooks would be outright, and maybe make exception
    for myself as well. Then if you need to add some less standard jobs like "bread maker"
    or "Sausage Collector," then you've got to put those in too. Keep in mind that when you
    add a job, you've also got to give it someone or at least make some people acquire a taste
    for it.

3)  Third, you've got to generate a solution with the assigner module. That ain't such a
    tricky thing, but there are some important things to do. You'll notice a sort of silly
    little attribute in the Scheduler class called "extraProcessing". Well it don't really
    do that much on the whole, and you might be wonderin' why its in there at all. Well.
    It's made just for you yfnkm, 'cause its for putting in a function to combine pairs of
    young folks that only want to be on half meal plan. It so happens that just such a
    function has been added down below. Its called "combineHalfers." Now you might look at
    that function and decide it isn't quite what you expected it to be, and well, maybe
    thats true. But, it works tolerable well, and well, that works reasonable okay for me.

4)  Fourth, you've got to take a look at what you've done. Now, down there you'll see a
    another function that might come in handy. Its called printSolution, and it was 
    especially made for yours truly to see what I hath wrought. Its reasonably
    self-explanatory so I'll just suppose you'll have a gander at it yourself if it becomes
    a useful thing for you to do.

Well, thats just about the gist of it. I'll go ahead and give you an example, and some of the
accompanying files might be just be useful to ya.

                                                                        ---yfnkm of yor



import kitchen as k
import csv

# Well write here is where I import the data file that I got from the Googles
f = open('sp13-2.csv')
f = csv.reader(f, dialect='excel')
table = k.parseCSV(f,prefBias=2)
# and you see that prefBias=2 thing. Thats how much a young persons preferred day to cook
# is going to be promoted in the lottery. I think 2 is a tolerable number.


#Add Extra People - These folks didn't make it into the googles for whatever
#uniteresting reason.
table.addPerson('Evan Lynch')
table.addPerson('Danny Manesh')
table.addPerson('Mary Foster')
table.addPerson('Tom Watts')
table.addPerson('Brandon Sorbom')

#Add Extra Jobs - And these jobs are all the irrefular ones.
table.addAssignment('Fridge Ninja II',table.getCandidates('Fridge Ninja'))
table.addAssignment('Friday Cleaner III',table.getCandidates('Friday Cleaner II'))
table.addAssignment('Friday Tiny Cook',table.getCandidates('Friday Little Cook'))
# Look how these first three are taken the candidates of standard jobs.
#table.addAssignment('Bread Maker')
#table.addAssignment('Dessert Maker')
table.addAssignment('Steward I')
table.addAssignment('Steward II')
#table.addAssignment('Monday Morning Big Cook')
#table.addAssignment('Monday Morning Little Cook')
#table.addAssignment('Monday Morning Cleaner')


#Make Selections - And then I assigned a few folks to specific things I wanted them
#to have
table.selectPair('Brandon Sorbom','Steward I')
table.selectPair('Tom Watts','Steward II')
table.selectPair('Evan Lynch','Sunday Big Cook')
table.selectPair('Danny Manesh','Sunday Little Cook')
table.selectPair('Mary Foster','Fridge Ninja')
#table.selectPair('Maddie Hickman','Monday Morning Big Cook')
#table.selectPair('Kaity','Monday Morning Little Cook')
#table.selectPair('Ranbel Sun','Monday Morning Cleaner')


#Choose Big Cooks - and here I used a "rectangularConstraint" to insure our food
#was going to be tolerable in the end
bigCooks = ['dhaval','Evan Lynch','Albert Carter','Danny Cooper','Jeremy','Deena Wang','Daniel Gonzalez','Jonathan Lee Marcus','Danny Clark','Eben']
table.addRectangularConstraint(bigCooks,[b for b in k.standardJobsList if 'Big Cook' in b])
#table.selectPair('','Friday Big Cook')

#Last thing I done is do the actual scheduling with the Scheduler
s = k.Scheduler(table,order=1e3,extraProcessing=k.combineHalfers)
sol = s.optimalSolution(allowIncomplete = 'standard')
if sol is not None:
    k.printSolution(sol)


'''
from assigner import ConstraintsTable
from assigner import Scheduler
from copy import deepcopy

standardJobsList = ["Monday Big Cook",
                    "Tuesday Big Cook",
                    "Wednesday Big Cook",
                    "Thursday Big Cook",
                    "Friday Big Cook",
                    "Saturday Big Cook",
                    "Sunday Big Cook",
                    "Monday Little Cook",
                    "Tuesday Little Cook",
                    "Wednesday Little Cook",
                    "Thursday Little Cook",
                    "Friday Little Cook",
                    "Saturday Little Cook",
                    "Sunday Little Cook",
                    "Monday Cleaner I",
                    "Tuesday Cleaner I",
                    "Wednesday Cleaner I",
                    "Thursday Cleaner I",
                    "Friday Cleaner I",
                    "Saturday Cleaner I",
                    "Sunday Cleaner I",
                    "Monday Cleaner II",
                    "Tuesday Cleaner II",
                    "Wednesday Cleaner II",
                    "Thursday Cleaner II",
                    "Friday Cleaner II",
                    "Saturday Cleaner II",
                    "Sunday Cleaner II",
                    "Fridge Ninja"]

def combineHalfers(table):
    tables = []
    for i in range(6):
        tab = deepcopy(table)
        halfers = []
        for p in tab.peopleList:
            if '(half)' in p:
                halfers.append(p)

        if len(halfers) % 2 == 1:
            lim = 1
        else:
            lim = 0
            print "Even Number!"
        while len(halfers)>lim:
            p = halfers.pop()
            q = tab.lotteryPeople(p,halfers)
            tab.combinePeople(p,q)
            halfers.remove(q)
        tables.append(tab)
    return tables

def printSolution(solution):
    outTab = """
    | Job | Monday          | Tuesday         | Wednesday       | Thursday        | Friday          | Saturday        | Sunday          |
    -------------------------------------------------------------------------------------------------------------------------------------
    | Big | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} |
    | Ltl | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} |
    | CL1 | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} |
    | CL2 | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} | {:15s} |
    -------------------------------------------------------------------------------------------------------------------------------------
    Fridge Ninja: {:15s}"""
    (pairs,peopleNotUsed,assignmentsNotAssigned) = solution.outputPairs()
    peeps = []
    longPeeps = []
    for j in standardJobsList:
        if j in pairs:
            p = pairs[j]
            if len(p) > 30:
                longPeeps.append((j,p))
            peeps.append(p[:15])
        else:
            peeps.append('-----------')
    for j in pairs:
        if j not in standardJobsList:
            outTab = outTab + "\n    "+j+": "+pairs[j]
    print outTab.format(*peeps)
    print "Truncated Names:"
    for j,p in longPeeps:
        print "    %s was assigned to %s" % (p,j)
    print "Null Assignments:"
    for p in peopleNotUsed:
        print "    %s was not assigned" % p
    print "Non Assignments:"
    for j in assignmentsNotAssigned:
        print "    %s was not assigned" % j



def parseCSV(f,table = None,prefBias = 2):
    if table is None:
        table = ConstraintsTable()
        for j in standardJobsList:
            table.addAssignment(j)

    peopleSoFar = []

    for i,r in enumerate(f):
        if r[0] == 'Timestamp':
            continue
        if r[1] == "":
            continue
        name = r[1]
        email = r[2]
        big_cook_days = r[3]
        big_cook_pref = r[4]
        little_cook_days = r[5]
        little_cook_pref = r[6]
        cleaning_days = r[7]
        cleaning_pref = r[8]
        ninja = r[9]
        half = r[10]
        notes = r[11]

        if 'Half' in half:
            name = name+' (half)'
        
        table.addPerson(name)

        if 'Ninja' in ninja:
            table.addPreference(name,'Fridge Ninja',1)
        for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:
            if day in big_cook_pref:
                table.addPreference(name,day+' Big Cook',prefBias)
            elif day in big_cook_days:
                table.addPreference(name,day+' Big Cook',1)
            
            if day in little_cook_pref:
                table.addPreference(name,day+' Little Cook',prefBias)
            elif day in little_cook_days:
                table.addPreference(name,day+' Little Cook',1)

            if day in cleaning_pref:
                table.addPreference(name,day+' Cleaner I', prefBias)
                table.addPreference(name,day+' Cleaner II', prefBias)
            if day in cleaning_days:
                table.addPreference(name,day+' Cleaner I', 1)
                table.addPreference(name,day+' Cleaner II', 1)

    return table