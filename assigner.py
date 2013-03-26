# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------
# Name:			assigner.py
# Author:		Evan Lynch
#
# Copyright:	Copyright © 2013 Evan F. Lynch
# License:		Not Released, but do what you want.
#--------------------------------------------------------------------------------
'''
This module contains two classes for assigning a set of people to a set of assignments.
The kind of problem this is meant to tackle is, for example, assigning 50 people to
50 jobs in a community kitchen based on their preferences and constraints. This module
uses a lot of array based calculations and so it requires that you have "numpy" installed
and in your $PYTHONPATH.

To you use this module, create an instance of ConstraintsTable which will contain the list
of assignments, the list of people, and the list of constraints and preferences. You can
initialize it with a list of assignments or people or both or neither. In any case, you
then need to put in the constraints by calling ConstraintsTable().addPreference() for each
preference.

Once the ConstraintsTable is prepared, create an instance of Scheduler() passing the
constraints table as an argument. Then call Scheduler().optimalSolution() which will
return what the Scheduler class has determined to be the optimal solution in the form
of a fully constrained instance of ConstraintsTable. Scheduler also has a handy method
for printing what the assignments from a fully constrained ConstraintsTable called
showSolution().

Scheduler uses a randomized greedy algorithm to compute solutions. In each iteration, it
selects a candidate for an assignment from a list by a lottery weighted by preference. Tuning
the preference scale has an enormous effect on the number of solutions this algorithm finds. In
general, preference values that are small (1-5) seem to work better.
'''
import numpy as _np
from copy import deepcopy

class ConstraintsTable:
	'''
	This class contains the list of assignments, people, and the preference and
	constraint information for your assignment optimization.
	'''
	def __init__(self, assignmentsList = [],peopleList=[]):
		'''
		Optionally initialize with a list of assignments and people.
		'''
		self.assignmentsList = assignmentsList
		self.peopleList = peopleList
		self.array = _np.zeros((len(self.peopleList)+1,1+len(self.assignmentsList)))

	def addPerson(self,name,constraints = None):
		'''
		Adds a person to the ConstraintsTable. The optional constraints argument
		must be a well-formed one-dimensional array with length equal to the
		number of assignments in the table.
		'''
		if constraints is None:
			constraints = _np.array([0]*len(self.assignmentsList))
		r = _np.array([0]+(list(constraints)))
		if name in self.peopleList:
			self.array[self.peopleList.index(name)+1,:] = r
		else:
			self.array = _np.vstack([self.array,r])
			self.peopleList.append(name)

	def addPreference(self,person,assignment,degree):
		'''
		Adds to the table the information, "person prefers assignment with power degree."
		This information is encoded as an integer:
		0 is the constraint "this person cannot take this assignment"
		1 is the prefernce "this person prefers this assignment with unit preference"
		n is the preference "this person prefers this assignment to power n"
		'''
		i = self.peopleList.index(person)+1
		j = self.assignmentsList.index(assignment)+1
		self.array[i,j] = degree

	def removePerson(self,name):
		'''
		Removes a person and their preference information from the table.
		'''
		i = self.peopleList.index(name)+1
		self.array = _np.delete(self.array,i,0)
		self.peopleList.remove(name)

	def getConstraints(self,person):
		'''
		Returns a 1D array with length len(self.assignmentsList) which contains person's
		preference and constraint information.
		'''
		i = self.peopleList.index(person)+1
		return self.array[i,1:]

	def addAssignment(self,assignment,candidates=None):
		'''
		Adds an assignment to the table. The candidates argument must be a well-formed
		1D array with an entry for each person in the personList in order of the
		personList.
		'''
		if candidates is None:
			c =_np.zeros((len(self.peopleList)+1,1))
		else:
			c = _np.vstack([_np.array([0]),_np.ndarray.transpose(candidates[None])])
		self.array = _np.hstack([self.array,c])
		self.assignmentsList.append(assignment)

	def combineAssignments(self,assignment1,assignment2):
		'''
		Adds a new assignment to the table with a concatenated name "assignment1
		and assignment2" with candidate array equal to the element-wise product
		of the two candidate arrays. This also removes assignment1 and assignment2
		from the table.
		'''
		name = assignment1+' and '+assignment2
		c1 = self.getCandidates(assignment1)
		c2 = self.getCandidates(assignment2)
		candidates = c1*c2
		self.removeAssignment(assignment1)
		self.removeAssignment(assignment2)
		self.addAssignment(name,candidates)

	def removeAssignment(self,name):
		'''
		Removes an assignment and candidate information from the table.
		'''
		i = self.assignmentsList.index(name)
		self.array = _np.delete(self.array,i+1,1)
		self.assignmentsList.remove(name)

	def markAssignment(self,name):
		'''
		Marks an assignment by placing an infinity at the top of the column in the array.
		This is in particular used by Scheduler() to mark assignments that have been made.
		'''
		i = self.assignmentsList.index(name)+1
		self.array[0,i] = float("inf")

	def markPerson(self,person):
		'''
		Marks a person by placing an infinity at the begging of the row in the array.
		This is in particular used by Scheduler() to mark people that have been assigned.
		'''
		i = self.peopleList.index(person)+1
		self.array[i,0] = float("inf")

	def comparePeople(self,person1,person2):
		'''
		Returns the dot product of the preference arrays of two people.
		'''
		i1 = self.peopleList.index(person1)
		i2 = self.peopleList.index(person2)
		return _np.sum(self.array[i1,1:]*self.array[i2,1:])

	def combinePeople(self,person1,person2):
		'''
		Adds a new person to the table with a concatenated name "person1 and person2"
		with preference array equal to the element-wise product of the two preference
		arrays. This also removes person1 and person2 from the table.
		'''
		name = person1+' and '+person2
		c1 = self.getConstraints(person1)
		c2 = self.getConstraints(person2)
		constraints = c1*c2
		self.removePerson(person1)
		self.removePerson(person2)
		self.addPerson(name,constraints)

	def lotteryPeople(self,person,people):
		'''
		Returns the name of a p in people based on a lottery weighted by the result of
		self.comparePeople(person,p).
		'''
		peopleWeights = _np.array([self.comparePeople(person,p) for p in people])
		lottery = _np.random.rand(len(people))*_np.sqrt(peopleWeights)
		choice = max(people, key = lambda x: lottery[people.index(x)])
		return choice

	def selectPair(self,person,assignment):
		'''
		Forces person to have unit preference for assignment and no other assignments.
		Removes all other candidates from assignment, and marks person and assignment.
		'''
		i = self.peopleList.index(person)+1
		j = self.assignmentsList.index(assignment)+1
		self.array[i,:] = 0
		self.array[:,j] = 0
		self.array[i,j] = 1
		self.markPerson(person)
		self.markAssignment(assignment)

	def addRectangularConstraint(self,people,assignments):
		'''
		Makes appropriate changes to constraints table to force all assignments within
		the list "assignments" to go to people in the list "people".
		'''
		peopleIndices = [self.peopleList.index(p)+1 for p in people]
		assignmentIndices = [self.assignmentsList.index(j)+1 for j in assignments]
		for p in range(1,self.shape[0]+1):
			if p in peopleIndices:
				continue
			self.array[p,assignmentIndices] = 0

	def mostConstrainedAssignment(self,allowIncompleteAssignment=False,skipMarked = False):
		'''
		Returns the assignment which is most constrained. i.e. with the fewest
		candidates weighted by preference. Returns None if the mostConstrainedAssignment
		has zero candidates if allowIncompleteAssignment is false. Otherwise
		returns the assignment with no candidates.
		'''
		if skipMarked:
			constraintLevels = _np.ndarray.sum(self.array[:,1:],axis=0)
		else:
			constraintLevels = _np.ndarray.sum(self.array[1:,1:],axis=0)

		if 0 in constraintLevels and not allowIncompleteAssignment:
			return None

		assignment = min(self.assignmentsList, key = lambda x: constraintLevels[self.assignmentsList.index(x)])
		return assignment

	def getCandidates(self,assignment):
		'''
		Returns the array of candidates for assignment.
		'''
		j = self.assignmentsList.index(assignment)+1
		return self.array[1:,j]

	def lotteryAssignment(self,assignment):
		'''
		Returns a person from the candidates of assignment based on a lottery weighted
		by their preferences.
		'''
		candidates = self.getCandidates(assignment)
		lottery = _np.random.rand(len(candidates))*candidates
		if max(lottery) == 0.0:
			return None
		person = max(self.peopleList, key = lambda x: lottery[self.peopleList.index(x)])
		return person

	def outputPairs(self):
		'''
		Returns a dictionary of {assignment:person} pairs for each marked and unit constrained
		assignment, a list of people not given an assignment, and a list of unassigned
		assignments.
		'''
		assignments = self.assignmentsList
		people = self.peopleList
		peopleUsed = []
		assignmentsAssigned = []
		pairs = {}
		for i in range(len(self.array)-1):
			for j in range(len(self.array[0,:])-1):
				if self.array[i+1,j+1] == 1 and self.array[i+1,0] == float("inf"):
					pairs[assignments[j]] = people[i]
					peopleUsed.append(people[i])
					assignmentsAssigned.append(assignments[j])
		peopleNotUsed = [p for p in people if p not in peopleUsed]
		assignmentsNotAssigned = [j for j in assignments if j not in assignmentsAssigned]
		return (pairs,peopleNotUsed,assignmentsNotAssigned)

	def outputSolution(self):
		'''
		Returns self.
		'''
		return self

	def _getDetermined(self):
		'''
		Helper function for determined property which checks to see if all assignments
		have been marked. Returns True if all assignments have been marked or if all
		people have been marked. Returns False otherwise.
		'''
		if 0 in list(self.array[0,1:]):
			if 0 in list(self.array[1:,0]):
				return False
			else:
				return True
		else:
			return True

	def _getShape(self):
		'''
		Helper function for shape property which returns the number of people and
		number of assignments.
		'''
		p = len(self.array)-1
		a = len(self.array[0])-1
		return (p,a)

	determined = property(_getDetermined)

	shape = property(_getShape)


class Scheduler:
	'''
	This class implements the scheduling algorithm.
	'''
	def __init__(self,table=None,constraintsList = [], order = 1e4, extraProcessing = None):
		'''
		The constraints list should be a list of people assignment pairs. The order argument
		is the number of solutions that will be attempted. The extraProcessing argument is an
		optional function that will be called on the table just before performing a scheduling.
		It should return a list of tables.
		'''
		if table is None:
			table = ConstraintsTable()
		self.table = table
		self.tables = []
		self.solutions = []
		self.order = order
		self.constraintsList = []
		self.scoreMemo = {}
		self.extraProcessing = extraProcessing

	def generateSolutions(self,allowIncomplete='standard'):
		'''
		This is the main scheduling algorithm. If allowIncomplete is True, then solutions
		that do not assign all assignments will be allowed (there will be self.order 
		successful solutions). If allowIncomplete is False, then solutions which do
		not assign all assignments will be ignored. If allowIncomplete is 'standard'
		then solutions which do not assign all assignments will only be allowed if there
		are not enough people to fill all assignments.
		'''
		numSolved = 0
		numFailed = 0
		self.scoreMemo = {}
		solutions = []
		self.tables = []

		if self.extraProcessing is None:
			tables = [self.table]
		else:
			tables = self.extraProcessing(self.table)

		for i,table in enumerate(tables):
			self.tables.append(deepcopy(table))
			print "%s people for %s assignments" % table.shape
			if allowIncomplete is 'standard':
				if table.shape[0] < table.shape[1]:
					allowIncomplete = True
				else:
					allowIncomplete = False

			for loopNumber in range(int(self.order)):
				t = deepcopy(table)
				solved = True
				while (not t.determined):
					j = t.mostConstrainedAssignment(allowIncomplete,skipMarked = True)
					if j is None:
						solved = False
						break
					p = t.lotteryAssignment(j)
					if p is None:
						t.markAssignment(j)
					else:
						t.selectPair(p,j)
				if solved:
					numSolved +=1
					solutions.append((i,t.outputSolution()))
				else:
					numFailed +=1
		print "%s solutions found. %s solutions failed." %(numSolved,numFailed)
		return solutions

	def showSolution(self,solution):
		'''
		Prints in a human readable way the result of solution.outputPairs(). For some 
		specific applications, a better output might be preffered.
		'''
		(pairs,peopleNotUsed,assignmentsNotAssigned) = solution.outputPairs()
		assignments = solution.assignmentsList

		for j in assignments:
			if j in pairs:
				print j,pairs[j]
		for p in peopleNotUsed:
			print p,"not assigned"
		for j in assignmentsNotAssigned:
			print j,"not assigned"

	def evaluateSolution(self,solution):
		'''
		Returns the dot product of a solution table with self.table.
		'''
		i,sol = solution
		if str(sol.array) in self.scoreMemo:
			return self.scoreMemo[str(sol.array)]

		product = sol.array[1:,1:] * self.tables[i].array[1:,1:]
		self.scoreMemo[str(sol.array)] = _np.sum(product)
		return _np.sum(product)


	def optimalSolution(self,allowIncomplete = 'standard'):
		'''
		Returns the best solution generated by generateSolutions based on
		evaluateSolutions as a metric.
		'''
		solutions = self.generateSolutions(allowIncomplete)
		if solutions == []:
			print "No solutions found"
			return None
		bestSolution = max(solutions,key = self.evaluateSolution)
		print "Best solution scored", self.evaluateSolution(bestSolution)
		return bestSolution[1]

